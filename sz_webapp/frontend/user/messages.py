# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
from ...core import AppError
from ...services import message_service
from ...helpers.flask_helper import json_response
from ... import errors

bp = Blueprint('user_messages', __name__, url_prefix='/user/<int:account_id>/messages')


@bp.route('/pendings')
@login_required
def get_pending_messages(account_id):
    """
        获取待处理的消息
    """
    current_account_id = current_user._get_current_object().id
    if current_account_id != account_id:
        raise AppError(error_code=errors.operation_unauthorized)
    messages = message_service.pending_messages_by_account(current_account_id)
    messages = [message.__json__(include_keys=['sender', 'receiver']) for message in messages]
    return json_response(results=messages)


@bp.route('/<int:message_id>/handle', methods=['POST'])
@login_required
def handle_message(account_id, message_id):
    """
        处理消息,result: 1:同意, -1:拒绝
    """
    current_account_id = current_user._get_current_object().id
    result = int(request.form.get('result'))
    error = message_service.handle_messages(message_id, result, current_account_id)
    if error:
        error_code = getattr(error, 'error_code', errors.fatal_error)
        return json_response(success=False, error_code=error_code)
    else:
        return json_response(success=True)
