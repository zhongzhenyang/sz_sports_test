# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
from ...services import match_highlight_service
from ...helpers.flask_helper import json_response
from ... import models
from ... import errors

bp = Blueprint('user_highlights', __name__, url_prefix='/user/highlights')


@bp.route('/add', methods=['POST'])
@login_required
def add_highlight():
    """
        添加精彩瞬间
    """
    current_account_id = current_user._get_current_object().id
    match_highlight_service.add_match_highlight(current_account_id, **request.json)
    return json_response(success=True)


@bp.route('/delete', methods=['POST'])
@login_required
def delete_highlight():
    """
        删除精彩瞬间
    """
    current_account_id = current_user._get_current_object().id
    match_highlight_id = int(request.form.get('match_highlight_id'))
    match_highlight_service.delete_match_highlight(current_account_id, match_highlight_id)
    return json_response(success=True)


