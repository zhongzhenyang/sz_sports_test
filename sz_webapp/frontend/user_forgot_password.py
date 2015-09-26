# coding:utf-8

from flask import current_app, request, render_template
from flask_user.signals import user_forgot_password
from flask_user.emails import send_forgot_password_email
from ..helpers.flask_helper import _endpoint_url, json_response


def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        success = False
        if not email:
            info = u'邮箱不能为空'
        else:
            user_manager = current_app.user_manager
            db_adapter = user_manager.db_adapter
            user, user_email = user_manager.find_user_by_email(email)
            if user:
                # Generate reset password link
                token = user_manager.generate_token(int(user.get_id()))
                reset_password_link = _endpoint_url('user.reset_password', token=token, _external=True)

                # Send forgot password email
                send_forgot_password_email(user, user_email, reset_password_link)

                # Store token
                if hasattr(user, 'reset_password_token'):
                    db_adapter.update_object(user, reset_password_token=token)
                    db_adapter.commit()

                # Send forgot_password signal
                user_forgot_password.send(current_app._get_current_object(), user=user)
                info = u'一封重置密码邮件已经发送至 %s。请打开那封邮件，按照其指引重置您的密码。' % email
                success = True
            else:
                info = u'没有找到与该邮箱对应的用户，请检查邮箱地址是否正确。'

        if request.is_xhr:
            return json_response(success=success, info=info)
        else:
            return render_template('frontend/forgetPwd.html', success=success, info=info, email=email)
    else:
        return render_template('frontend/forgetPwd.html')
