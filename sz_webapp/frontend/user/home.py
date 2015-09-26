# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
from ...core import AppError
from ...services import account_service, user_service
from ...helpers.flask_helper import json_response
from ... import models
from ... import errors

bp = Blueprint('user_home', __name__, url_prefix='/user/<int:account_id>/me')


@bp.route("/", methods=['GET'])
@login_required
def home_page(account_id):
    account = models.Account.from_cache_by_id(account_id)
    if not account:
        raise AppError(error_code=errors.account_id_noexistent)
    return render_template('frontend/myHome.html', account=account)

@bp.route('/messages', methods=['GET'])
@login_required
def user_messages_page(account_id):

    return render_template('frontend/myMessages.html')

@bp.route('/competitions', methods=['GET'])
@login_required
def user_competitions_page(account_id):

    return render_template('frontend/myCompetitions.html')

@bp.route('/sites', methods=['GET'])
@login_required
def user_sites_page(account_id):
    return render_template('frontend/myVenues.html')

@bp.route('/edit-info', methods=['GET'])
@login_required
def edit_user_page(account_id):
    account = models.Account.from_cache_by_id(account_id)
    if not account:
        raise AppError(error_code=errors.account_id_noexistent)
    return render_template('frontend/editInfo.html', account=account)


@bp.route('/edit-info', methods=['POST'])
@login_required
def edit_user(account_id):
    """
        更新用户信息
    """
    current_account_id = current_user._get_current_object().id
    user = user_service.create_or_update_user(current_account_id, **request.json)
    return json_response(user=user)


@bp.route('/update-password', methods=['GET'])
@login_required
def update_password_page(account_id):
    return render_template('frontend/editPwd.html')


@bp.route('/update-password', methods=['POST'])
@login_required
def update_password(account_id):
    """
        修改登录密码
    """
    current_account_id = current_user._get_current_object().id
    orig_password = request.json.get('password')
    new_password = request.json.get('new_password')
    account_service.update_password(current_account_id, orig_password, new_password)
    return json_response(success=True)
