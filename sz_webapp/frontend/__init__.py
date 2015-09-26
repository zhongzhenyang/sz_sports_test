# coding:utf-8

import os
from werkzeug.local import LocalProxy
from flask import current_app, request, redirect, send_file, jsonify, render_template, send_from_directory
from flask_login import current_user
from sqlalchemy.exc import DataError

from ..core import AppError
from ..logs import init_app_logger
from .. import factory
from .. import errors


_logger = LocalProxy(lambda: current_app.logger)


def create_app(settings_override=None):
    app = factory.create_app(__name__, __path__, settings_override=settings_override)
    app.errorhandler(AppError)(on_app_error)
    app.errorhandler(404)(on_404)
    app.errorhandler(500)(on_500)

    init_user_manager(app)
    init_context_processor(app)
    init_app_logger(app, 'frontend-error.log')

    @app.route('/')
    def index():
        return redirect('login')

    @app.route('/favicon.ico')
    def favicon_ico():
        return send_file('static/favicon.ico')

    @app.route('/data/<path:path>')
    def send_data(path):
        return send_from_directory(os.path.join(app.root_path, 'data'), path)

    from flask_user import login_required
    from .. import qinius

    @app.route("/qiniu-uptoken", methods=["GET"])
    @login_required
    def get_upload_token():
        up_token = qinius.upload_token()
        return jsonify(success=True, uptoken=up_token)

    return app


def init_user_manager(app):
    from flask_user import SQLAlchemyAdapter, UserManager

    from ..core import db, FromCache
    from ..models import Account
    from .user_login import login
    from .user_register import register
    from .user_forgot_password import forgot_password
    from ..tasks import send_email
    import hashlib
    from flask.ext.wtf import Form
    from wtforms import BooleanField, HiddenField, PasswordField, SubmitField, StringField
    from wtforms import validators, ValidationError

    def hash_password(self, password):
        _md5 = hashlib.md5()
        _md5.update(password)
        return _md5.hexdigest()

    def generate_password_hash(self, password):
        _md5 = hashlib.md5()
        _md5.update(password)
        return _md5.hexdigest()

    def verify_password(self, password, user):
        return self.hash_password(password) == user.password

    def login_manager_usercallback(account_id):
        account_id = int(account_id) if isinstance(account_id, basestring) else account_id
        account = db.session.query(Account). \
            options(FromCache('model', 'account:%d' % account_id)). \
            filter(Account.id == account_id).first()
        return account

    def password_validator(form, field):
        """ Password must have one lowercase letter, one uppercase letter and one digit."""
        # Convert string to list of characters
        password = list(field.data)
        password_length = len(password)

        # Count lowercase, uppercase and numbers
        lowers = uppers = digits = 0
        for ch in password:
            if ch.islower(): lowers += 1
            if ch.isupper(): uppers += 1
            if ch.isdigit(): digits += 1

        # Password must have one lowercase letter, one uppercase letter and one digit
        is_valid = password_length >= 6 and lowers and uppers and digits
        if not is_valid:
            raise ValidationError(u'密码至少超过6位,其中要求包含一个大写字母,一个小写字母和一个数字')

    class ResetPasswordForm(Form):
        new_password = PasswordField(u'新密码', validators=[validators.Required(u'新密码不能为空')])
        retype_password = PasswordField(u'再次输入新密码', validators=[
            validators.EqualTo('new_password', message=u'两次输入的新密码匹配')])
        next = HiddenField()
        submit = SubmitField(u'修改密码')

        def validate(self):
            # Use feature config to remove unused form fields
            user_manager = current_app.user_manager
            if not user_manager.enable_retype_password:
                delattr(self, 'retype_password')
            # Add custom password validator if needed
            has_been_added = False
            for v in self.new_password.validators:
                if v == user_manager.password_validator:
                    has_been_added = True
            if not has_been_added:
                self.new_password.validators.append(user_manager.password_validator)
            # Validate field-validators
            if not super(ResetPasswordForm, self).validate():
                return False
            # All is well
            return True

    def async_send_email(recipient, subject, html_message, text_message):
        send_email.delay(recipient, subject, html_message, text_message)

    db_adapter = SQLAlchemyAdapter(db, Account)
    user_manager = UserManager(db_adapter, login_view_function=login, register_view_function=register,
                               forgot_password_view_function=forgot_password,
                               reset_password_form=ResetPasswordForm, password_validator=password_validator,
                               send_email_function=async_send_email)
    user_manager.init_app(app)
    user_manager.hash_password = hash_password.__get__(user_manager, UserManager)
    user_manager.generate_password_hash = generate_password_hash.__get__(user_manager, UserManager)
    user_manager.verify_password = verify_password.__get__(user_manager, UserManager)
    user_manager.login_manager.user_callback = login_manager_usercallback
    orig_unauthenticated_view_function = user_manager.unauthenticated_view_function

    def unauthenticated_view_function():
        if request.is_xhr:
            return jsonify({'success': False, 'error_code': errors.user_unauthenticated})
        else:
            return orig_unauthenticated_view_function()

    setattr(user_manager, 'unauthenticated_view_function', unauthenticated_view_function)

    orig_unauthorized_view_function = user_manager.unauthorized_view_function

    def unauthorized_view_function():
        if request.is_xhr:
            return jsonify({'success': False, 'error_code': errors.operation_unauthorized})
        else:
            return orig_unauthorized_view_function()

    setattr(user_manager, 'unauthorized_view_function', unauthorized_view_function)


def init_context_processor(app):
    def current_user_pending_message_count():
        from ..models import Message
        from ..core import db

        if current_user.is_authenticated():
            current_user_id = current_user._get_current_object().id
            return Message.query.with_entities(db.func.count('*')).filter(Message.receiver_id == current_user_id,
                                                                          Message.status == 0).scalar()
        else:
            return None

    def _context_processors():
        return dict(pending_message_count=current_user_pending_message_count)

    app.context_processor(_context_processors)


def on_app_error(e):
    if request.is_xhr:
        return jsonify({'success': False, 'error_code': e.error_code})
    else:
        return render_template('error/500.html', error=e)


def on_404(e):
    if request.is_xhr:
        return jsonify({'success': False, 'error_code': errors.resource_not_found})
    else:
        return render_template('error/404.html')


def on_500(e):
    _logger.exception(e)
    if request.is_xhr:
        return jsonify({'success': False, 'error_code': errors.fatal_error, 'message': e.message})
    else:
        return render_template('error/500.html', error=e)
