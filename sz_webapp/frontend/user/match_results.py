# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
from ...services import match_goal_service, match_section_service
from ...helpers.flask_helper import json_response

bp = Blueprint('user_match_results', __name__, url_prefix='/user/match-results')


@bp.route('/add-goal', methods=['POST'])
@login_required
def add_match_goal():
    """
        添加比赛进球
    """
    current_account_id = current_user._get_current_object().id
    match_goal = match_goal_service.add_match_goal(current_account_id, **request.json)
    return json_response(match_goal=match_goal)


@bp.route('/delete-goal', methods=['POST'])
@login_required
def delete_match_goal():
    """
        删除比赛进球
    """
    current_account_id = current_user._get_current_object().id
    competition_fixture_id = int(request.form.get('competition_fixture_id'))
    match_goal_id = int(request.form.get('match_goal_id'))
    match_goal_service.delete_match_goal(current_account_id, competition_fixture_id, match_goal_id)
    return json_response(success=True)


@bp.route('/add-section', methods=['POST'])
@login_required
def add_match_section():
    """
        添加分局记录
    """
    current_account_id = current_user._get_current_object().id
    match_section = match_section_service.add_match_section(current_account_id, **request.json)
    return json_response(match_section=match_section)


@bp.route('/delete-section', methods=['POST'])
@login_required
def delete_match_section():
    """
        删除分局记录
    """
    current_account_id = current_user._get_current_object().id
    competition_fixture_id = int(request.form.get('competition_fixture_id'))
    match_section_id = int(request.form.get('match_section_id'))
    match_section_service.delete_match_section(current_account_id, competition_fixture_id, match_section_id)
    return json_response(success=True)
