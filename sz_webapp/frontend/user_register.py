# coding:utf-8

from flask import current_app, request, redirect, render_template
from flask_login import current_user, login_user
from flask.ext.wtf import Form
from flask_user import signals as flask_user_signals
from wtforms import BooleanField, HiddenField, PasswordField, SubmitField, StringField
from wtforms import validators, ValidationError
from ..core import db
from ..helpers.flask_helper import _endpoint_url, json_response
from ..models import Account
from .. import errors


def unique_email_validator(form, field):
    """ Username must be unique"""
    user_manager = current_app.user_manager
    if not user_manager.email_is_available(field.data):
        raise ValidationError(u'该邮箱地址已被占用,请更改邮箱地址')


class RegisterForm(Form):
    fullname = StringField(u'姓名', validators=[validators.Required(u'姓名不能为空')])
    email = StringField(u'邮箱地址', validators=[validators.Required(u'邮箱地址不能为空'), validators.Email(u'无效的邮箱地址'), unique_email_validator])
    password = PasswordField(u'密码', validators=[validators.Required(u'密码不能为空')])


def register():
    reg_success = False
    user_logined = False
    user_manager = current_app.user_manager
    _next = request.args.get('next', None)
    if current_user.is_authenticated():
        user_logined = True
        if not _next: _next = _endpoint_url('user_home.home_page', account_id=current_user._get_current_object().id)

    data = {}

    if not user_logined:
        if request.method == 'POST':
            register_form = RegisterForm(request.form)
            if register_form.validate():
                account = Account(email=register_form.email.data, role='user')
                account.password = user_manager.hash_password(register_form.password.data)
                account.fullname = register_form.fullname.data
                db.session.add(account)
                db.session.commit()
                flask_user_signals.user_registered.send(current_app._get_current_object(), account=account)
                login_user(account)
                reg_success = True
                if not _next:
                    _next = _endpoint_url('user_home.home_page', account_id=account.id)

            else:
                data.update(register_form.errors.items())

    if request.is_xhr:
        if user_logined:
            return json_response(success=False, error_code=errors.logined_account_register,
                                 results={'account': current_user._get_current_object()})
        else:
            if reg_success:
                return json_response(success=True, results={'account': current_user._get_current_object()})
            else:
                return json_response(success=False, results=data)
    else:
        if user_logined:
            return redirect(_next)
        else:
            if reg_success:
                return redirect(_next)
            else:
                return render_template('frontend/register.html', data=data)
