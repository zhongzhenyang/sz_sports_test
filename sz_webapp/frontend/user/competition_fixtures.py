# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
from ...core import AppError
from ...services import competition_fixture_service
from ...helpers.flask_helper import json_response
from ... import models
from ... import errors

bp = Blueprint('user_competition_fixtures', __name__, url_prefix='/user/<int:competition_id>/competition-fixtures')


@bp.route('/<int:competition_fixture_id>', methods=['GET'])
def competition_fixture_page(competition_id, competition_fixture_id):
    competition = models.Competition.from_cache_by_id(competition_id)
    competition_fixture = models.CompetitionFixture.from_cache_by_id(competition_fixture_id)
    return render_template('frontend/competitionResult.html', competition=competition, competition_fixture=competition_fixture)


@bp.route('/create', methods=['GET'])
@bp.route('/<int:competition_fixture_id>/update', methods=['GET'])
@login_required
def create_competition_fixture_page(competition_id, competition_fixture_id=None):
    competition = models.Competition.from_cache_by_id(competition_id)
    if competition_fixture_id:
        competition_fixture = models.CompetitionFixture.from_cache_by_id(competition_fixture_id)
    else:
        competition_fixture = {}
    return render_template('frontend/competitionResultUpdate.html', competition=competition, competition_fixture=competition_fixture)


@bp.route('/create', methods=['POST'])
@login_required
def create_competition_fixture(competition_id):
    """
        添加一场比赛
    """
    data = request.json
    current_account_id = current_user._get_current_object().id
    competition_fixture = competition_fixture_service.create_competition_fixture(current_account_id, competition_id, **data)
    return json_response(competition_fixture=competition_fixture)


@bp.route('/<int:competition_fixture_id>/update', methods=['POST'])
@login_required
def update_competition_fixture(competition_id, competition_fixture_id):
    """
        修改一场比赛信息
    """
    current_account_id = current_user._get_current_object().id
    competition_fixture = competition_fixture_service.update_competition_fixture(current_account_id, competition_fixture_id, **request.json)
    return json_response(competition_fixture=competition_fixture)


@bp.route('/<int:competition_fixture_id>/delete', methods=['POST'])
def delete_competition_fixture(competition_id, competition_fixture_id):
    """
        删除一场比赛
    """
    current_account_id = current_user._get_current_object().id
    competition_fixture_service.delete_competition_fixture(current_account_id, competition_fixture_id)
    return json_response(success=True)


@bp.route('/<int:competition_fixture_id>/submit-result', methods=['POST'])
@login_required
def submit_competiton_fixture_result(competition_id, competition_fixture_id):
    """
        提交一次比赛结果
    """
    current_account_id = current_user._get_current_object().id
    competition_fixture_service.submit_result(current_account_id, competition_fixture_id, **request.json)
    return json_response(success=True)


@bp.route("/<int:competition_fixture_id>/participants", methods=['GET'])
def participants(competition_id, competition_fixture_id):
    """
        获取一场比赛下的所有参赛队员
    """
    competition_fixture = models.CompetitionFixture.from_cache_by_id(competition_fixture_id)
    if not competition_fixture:
        raise AppError(error_code=errors.competition_fixture_id_noexistent)
    return json_response(results={'p1_members': competition_fixture.p1_competition_team.competition_team_member_accounts,
                                  'p2_members': competition_fixture.p2_competition_team.competition_team_member_accounts})


@bp.route("/<int:competition_fixture_id>/highlights", methods=['GET'])
def highlights(competition_id, competition_fixture_id):
    """
        获取一场比赛下的所有精彩瞬间
    """
    competition_fixture = models.CompetitionFixture.from_cache_by_id(competition_fixture_id)
    if not competition_fixture:
        raise AppError(error_code=errors.competition_fixture_id_noexistent)
    return json_response(results=competition_fixture.highlights)


@bp.route("/<int:competition_fixture_id>/goals", methods=['GET'])
def goals(competition_id, competition_fixture_id):
    """
        获取一场比赛下的所有进球
    """
    competition_fixture = models.CompetitionFixture.from_cache_by_id(competition_fixture_id)
    if not competition_fixture:
        raise AppError(error_code=errors.competition_fixture_id_noexistent)

    return json_response(
        results=[goal.__json__(include_keys=['competition_team.team', 'scorer.account', 'assistant.account']) for goal in competition_fixture.goals])


@bp.route("/<int:competition_fixture_id>/sections", methods=['GET'])
def sections(competition_id, competition_fixture_id):
    """
        获取一场比赛的分节记录
    """
    competition_fixture = models.CompetitionFixture.from_cache_by_id(competition_fixture_id)
    if not competition_fixture:
        raise AppError(error_code=errors.competition_fixture_id_noexistent)
    return json_response(results=competition_fixture.sections)
