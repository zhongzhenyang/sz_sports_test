# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
from ...services import team_member_service
from ...helpers.flask_helper import json_response

bp = Blueprint('user_team_members', __name__, url_prefix='/user/team-members')


@bp.route('/<int:team_id>/apply-join', methods=['POST'])
@login_required
def apply_team_join(team_id):
    """
        申请加入球队
    """
    account_id = current_user._get_current_object().id
    team_member_service.apply_team_join(account_id, team_id)
    return json_response(success=True)


@bp.route('/<int:team_id>/left', methods=['POST'])
@login_required
def leave_team(team_id):
    """
        退出球队
    """
    account_id = current_user._get_current_object().id
    team_member_service.leave_team(account_id, team_id)
    return json_response(success=True)


@bp.route('/<int:team_id>/member-status', methods=['GET'])
@login_required
def team_member_status(team_id):
    """
        status为 yes or no, yes:已经加入球队,no:没有加入球队
    """
    account_id = current_user._get_current_object().id
    status = team_member_service.get_team_member_status(account_id, team_id)
    return json_response(status=status)


@bp.route('/<int:team_id>/reject', methods=['POST'])
@login_required
def reject_team_member(team_id):
    """
        球队管理者将某人踢出球队
    """
    account_id = int(request.form.get('account_id'))
    team_member_service.reject_team_member(team_id, account_id)
    return json_response(success=True)
