# coding:utf-8

from flask import current_app, request, redirect, render_template
from flask_login import current_user, login_user
from ..helpers.flask_helper import _endpoint_url, json_response


def login():
    success = False
    user_manager = current_app.user_manager
    _next = request.args.get('next', None)
    if current_user.is_authenticated():
        success = True

    if not success:
        data = {}
        if request.method == 'POST':
            login_form = user_manager.login_form(request.form)
            if login_form.validate():
                account, account_email = user_manager.find_user_by_email(login_form.email.data)
                remember_me = True if login_form.remember_me.data else False
                success = login_user(account, remember=remember_me)
                if not success and not account.active:
                    info = u'该用户账户已被禁用'

            else:
                info = u'用户名或密码错误'
                data.update(login_form.errors.items())

            if not success and not request.is_xhr:
                data.setdefault('info', info)
                data.setdefault('next', _next)

    if request.is_xhr:
        if success:
            return json_response(success=True, results=current_user._get_current_object().__json__(include_keys=['user']))
        else:
            return json_response(success=False, info=info)
    else:
        if success:
            if not _next:
                account = current_user._get_current_object()
                if account.role == 'admin':
                    _next = _endpoint_url('admin_home.home_page')
                else:
                    _next = _endpoint_url('user_home.home_page', account_id=account.id)
            return redirect(_next)
        else:
            return render_template('frontend/login.html', data=data)
