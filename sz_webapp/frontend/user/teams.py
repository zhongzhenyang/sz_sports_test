# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
from ...core import AppError, db
from ...services import team_service, match_highlight_service
from ...helpers.flask_helper import json_response
from ... import models
from ... import errors

bp = Blueprint('user_teams', __name__, url_prefix='/user/teams')


@bp.route('/<int:team_id>', methods=['GET'])
def show_team_page(team_id):
    team = models.Team.from_cache_by_id(team_id)
    if not team:
        raise AppError(error_code=errors.team_id_nonexistent)

    current_team_member = None  # 当前登录用户 的 team_member
    if current_user.is_authenticated():
        current_account_id = current_user._get_current_object().id
        current_athlete = models.Athlete.from_cache_by_account_id_and_athletic_item_id(current_account_id,
                                                                                       team.athletic_item_id)
        if current_athlete:
            current_team_member = current_athlete.current_team

    return render_template('frontend/team.html', team=team, current_team_member=current_team_member)


@bp.route('/create', methods=['GET'])
@bp.route('/<int:team_id>/update', methods=['GET'])
@login_required
def edit_team_page(team_id=None):
    if team_id:
        team = models.Team.from_cache_by_id(team_id)
    else:
        team = {}
    return render_template('frontend/teamUpdate.html', team=team)


@bp.route('/create', methods=['POST'])
@login_required
def create_team():
    """
        创建球队
    """
    current_account_id = current_user._get_current_object().id
    team = team_service.create_team(current_account_id, **request.json)
    return json_response(team=team)


@bp.route('/<int:team_id>/update', methods=['POST'])
@login_required
def update_team(team_id):
    """
        修改球队信息
    """
    current_account_id = current_user._get_current_object().id
    team = team_service.update_team(current_account_id, team_id, **request.json)
    return json_response(team=team)


@bp.route('/<int:team_id>/dismiss', methods=['POST'])
@login_required
def dismiss_team(team_id):
    """
        解散球队
    """
    current_account_id = current_user._get_current_object().id
    team_service.dismiss_team(current_account_id, team_id)
    return json_response(success=True)


@bp.route('/<int:team_id>/update-creator', methods=['POST'])
@login_required
def update_creator(team_id):
    """
        更新球队创建者
    """
    current_account_id = current_user._get_current_object().id
    new_creator_id = int(request.form.get('new_creator_id'))
    team = team_service.update_team_creator(current_account_id, team_id, new_creator_id)
    return json_response(team=team)


@bp.route("/<int:team_id>/highlights", methods=['GET'])
def highlights(team_id):
    """
        获取和球队相关的精彩瞬间
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))

    team = models.Team.from_cache_by_id(team_id)
    if not team:
        raise AppError(error_code=errors.team_id_nonexistent)

    if offset == 0 and limit == 10:
        data = team.recent_highlights
    else:
        data = match_highlight_service.paginate_highlight_by_team(team_id, offset, limit)
    return json_response(
        results=[dict(id=highlight.id, date_recorded=highlight.date_recorded, details=highlight.details) for highlight
                 in data]
    )


@bp.route("/<int:team_id>/competitions", methods=['GET'])
def team_competition_page(team_id):
    team = models.Team.from_cache_by_id(team_id)
    return render_template('frontend/moreCompetition.html', team=team)


@bp.route("/<int:team_id>/competitions/more", methods=['GET'])
def more_account_competitions(team_id):
    """
        获取球队参加的赛事
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))

    competition_teams = db.session.query(models.CompetitionTeam). \
        join(models.Competition,
             db.and_(models.Competition.id == models.CompetitionTeam.competition_id, models.Competition.c_type != 0)). \
        filter(models.CompetitionTeam.team_id == team_id). \
        order_by(models.Competition.date_started.desc()).offset(offset).limit(limit).all()
    return json_response(results=[competition_team.__json__(include_keys=['competition', 'prize', 'latest_rank', 'latest_rank.addition'])
                                  for competition_team in competition_teams])


@bp.route("/<int:team_id>/fixtures", methods=['GET'])
def team_competition_fixture_page(team_id):
    team = models.Team.from_cache_by_id(team_id)
    return render_template('frontend/moreCompetitionResult.html', team=team)


@bp.route("/<int:team_id>/fixtures/more", methods=['GET'])
def more_team_competition_fixtures(team_id):
    """
        获取球队参加的比赛记录
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))
    competition_fixtures = db.session.query(models.CompetitionFixture). \
        select_from(models.CompetitionTeam). \
        join(models.Competition, models.Competition.id == models.CompetitionTeam.competition_id). \
        join(models.CompetitionFixture,
             db.and_(models.CompetitionTeam.team_id == team_id,
                     db.or_(models.CompetitionFixture.p1 == models.CompetitionTeam.id,
                            models.CompetitionFixture.p2 == models.CompetitionTeam.id))). \
        order_by(models.CompetitionFixture.date_started.desc()).offset(offset).limit(limit).all()

    data = []
    for fixture in competition_fixtures:
        fixture_data = fixture.__json__()
        p1_team = fixture.p1_competition_team.team
        p2_team = fixture.p2_competition_team.team
        if fixture.competition.options.get('individual', None) == 'true':
            fixture_data['p1_team'] = {'id': p1_team.id, 'name': p1_team.creator.fullname, 'logo': p1_team.creator.user_profile}
            fixture_data['p2_team'] = {'id': p2_team.id, 'name': p2_team.creator.fullname, 'logo': p2_team.creator.user_profile}
        else:
            fixture_data['p1_team'] = {'id': p1_team.id, 'name': p1_team.name, 'logo': p1_team.logo}
            fixture_data['p2_team'] = {'id': p2_team.id, 'name': p2_team.name, 'logo': p2_team.logo}
        data.append(fixture_data)
    return json_response(results=data)
