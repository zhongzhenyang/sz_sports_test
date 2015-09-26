# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
import itertools
from ...core import AppError
from ...services import competition_service, competition_fixture_service, \
    competition_team_service, match_highlight_service
from ...helpers.flask_helper import json_response
from ... import models
from ... import errors

bp = Blueprint('user_competitions', __name__, url_prefix='/user/competitions')


@bp.route('/', methods=['GET'])
def competition_list_page():
    return render_template('frontend/competitions.html')


@bp.route('/list', methods=['GET'])
def list_competition():
    limit = int(request.args.get("limit", "10"))
    offset = int(request.args.get("offset", "0"))
    athletic_item_id = int(request.args.get('athletic_item_id')) if request.args.get('athletic_item_id') else None
    c_name = request.args.get('name', None)
    c_type = int(request.args.get('c_type')) if request.args.get('c_type') else None
    c_status = int(request.args.get('status')) if request.args.get('status') else None
    c_loc_state = request.args.get('loc_state', None)
    c_loc_city = request.args.get('loc_city', None)
    c_loc_county = request.args.get('loc_county', None)
    c_date_published_orderby = int(request.args.get('date_published_orderby')) if request.args.get(
        'date_published_orderby') else -1

    count, competitions = competition_service.paginate_competition(offset=offset, limit=limit,
                                                                   athletic_item_id=athletic_item_id, c_name=c_name,
                                                                   c_type=c_type, c_status=c_status,
                                                                   c_loc_state=c_loc_state, c_loc_city=c_loc_city,
                                                                   c_loc_county=c_loc_county,
                                                                   c_date_published_orderby=c_date_published_orderby)
    return json_response(success=True, count=count,
                         results=[competition.__json__(include_keys=['athletic_item', 'registered_teams']) for
                                  competition in competitions])


@bp.route('/<int:competition_id>/register')
def competition_register_page(competition_id):
    competition = models.Competition.from_cache_by_id(competition_id)
    if not competition:
        raise AppError(error_code=errors.competition_id_noexistent)
    return render_template('frontend/competitionDetail.html', competition=competition)


@bp.route('/<int:competition_id>')
def competition_page(competition_id):
    competition = models.Competition.from_cache_by_id(competition_id)
    if not competition:
        raise AppError(error_code=errors.competition_id_noexistent)
    return render_template('frontend/competitionDetailIng.html', competition=competition)


@bp.route('/published-by-me', methods=['GET'])
@login_required
def competition_published_by_me():
    limit = int(request.args.get("limit", "10"))
    offset = int(request.args.get("offset", "0"))
    account_id = current_user._get_current_object().id
    count, competitions = competition_service.paginate_competition_by_manager(account_id, offset=offset, limit=limit)
    return json_response(success=True, count=count,
                         results=[competition.__json__(include_keys=['athletic_item']) for competition in competitions])


@bp.route('/apply-challenge', methods=['GET'])
@login_required
def apply_challenge_page():
    """
        向另一支球队申请挑战
    """
    p1_team_id = int(request.args.get('p1'))
    p2_team_id = int(request.args.get('p2'))
    p1_team = models.Team.from_cache_by_id(p1_team_id)
    p2_team = models.Team.from_cache_by_id(p2_team_id)
    return render_template('frontend/challenge.html', p1_team=p1_team, p2_team=p2_team)


@bp.route('/apply-challenge', methods=['POST'])
@login_required
def apply_challenge():
    """
        向另一支球队申请挑战
    """
    account_id = current_user._get_current_object().id
    competition = competition_service.apply_challenge(account_id, **request.json)
    return json_response(competition=competition)


@bp.route('/create-activity', methods=['GET'])
@bp.route('/<int:competition_id>/edit-activity', methods=['GET'])
@login_required
def edit_activity_page(competition_id=None):
    athletic_items = models.AthleticItem.from_cache_by_all()
    if competition_id:
        competition = models.Competition.from_cache_by_id(competition_id)
    else:
        competition = {}

    return render_template('frontend/competitionUpdate.html', athletic_items=athletic_items, competition=competition)


@bp.route('/create-activity', methods=['POST'])
@login_required
def create_activity():
    """
        创建活动
    """
    account_id = current_user._get_current_object().id
    competition = competition_service.create_activity(account_id, **request.json)
    return json_response(competition=competition)


@bp.route('/<int:competition_id>/update', methods=['POST'])
@login_required
def update_competition(competition_id):
    """
        修改竞赛资料
    """
    account_id = current_user._get_current_object().id
    competition = competition_service.update_competition(account_id, competition_id, **request.json)
    return json_response(competition=competition)


@bp.route('/<int:competition_id>/apply-league', methods=['POST'])
@login_required
def apply_league(competition_id):
    """
        申请将活动提升为联赛
    """
    account_id = current_user._get_current_object().id
    competition_service.apply_league(account_id, competition_id)
    return json_response(success=True)


@bp.route('/<int:competition_id>/set-status', methods=['POST'])
@login_required
def set_competition_status(competition_id):
    """
        设置竞赛的状态,0:报名; 1: 进行中;2: 结束
        挑战赛和活动的起始状态为 1
    """
    account_id = current_user._get_current_object().id
    status = int(request.form.get('status'))
    competition = competition_service.set_status(account_id, competition_id, status)
    return json_response(competition=competition)


@bp.route('/<int:competition_id>/set-stage', methods=['POST'])
@login_required
def set_competition_stage(competition_id):
    """
        设置竞赛的阶段,挑战赛和活动的阶段数为1,可选阶段为0
        联赛的阶段数为3,可选阶段为1,2,3
    """
    account_id = current_user._get_current_object().id
    stage = int(request.form.get('stage'))
    competition = competition_service.set_stage(account_id, competition_id, stage)
    return json_response(competition=competition)


@bp.route('/<int:competition_id>/register-status', methods=['GET'])
@login_required
def register_status(competition_id):
    """
        查询报名状态,status 为 yes or no
    """
    account_id = current_user._get_current_object().id
    status = competition_team_service.get_register_status(account_id, competition_id)
    return json_response(status=status)


@bp.route('/<int:competition_id>/do-register', methods=['POST'])
@login_required
def do_register(competition_id):
    """
        活动或者联赛报名
    """
    account_id = current_user._get_current_object().id
    team = competition_team_service.do_register(account_id, competition_id)
    return json_response(team=team)


@bp.route('/<int:competition_id>/undo-register', methods=['POST'])
@login_required
def undo_register(competition_id):
    """
        取消报名
    """
    account_id = current_user._get_current_object().id
    competition_team_service.undo_register(account_id, competition_id)
    return json_response(success=True)


@bp.route('/<int:competition_id>/teams', methods=['GET'])
def competing_teams(competition_id):
    """
        获取该赛事下的所有参赛队伍
    """
    competition = models.Competition.from_cache_by_id(competition_id)
    if not competition:
        raise AppError(error_code=errors.competition_id_noexistent)
    c_teams = competition._competings.all()
    competition_individual = competition.options.get('individual', None) == 'true'
    c_teams_data = []
    for c_team in c_teams:
        c_team_data = c_team.__json__()
        team = c_team.team
        if competition_individual:
            team_data = {'id': team.id, 'name': team.creator.fullname, 'logo': team.creator.user_profile}
        else:
            team_data = {'id': team.id, 'name': team.name, 'logo': team.logo}
        c_team_data['team'] = team_data
        c_teams_data.append(c_team_data)
    return json_response(success=True, results=c_teams_data)


@bp.route('/<int:competition_id>/highlights', methods=['GET'])
def highlights(competition_id):
    """
        获取该赛事下的精彩瞬间
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))

    competition = models.Competition.from_cache_by_id(competition_id)
    if not competition:
        raise AppError(error_code=errors.competition_id_noexistent)

    if offset == 0 and limit == 10:
        data = competition.recent_highlights
    else:
        data = match_highlight_service.paginate_highlight_by_competition(competition_id, offset, limit)
    return json_response(
        results=[dict(id=highlight.id, date_recorded=highlight.date_recorded, details=highlight.details) for highlight
                 in data]
    )


@bp.route('/<int:competition_id>/fixtures', methods=['GET'])
def competition_fixtures(competition_id):
    """
        获取该赛事下的某一阶段的所有比赛
    """
    stage = int(request.args.get('stage'))
    competition = models.Competition.from_cache_by_id(competition_id)
    if not competition:
        raise AppError(error_code=errors.competition_id_noexistent)
    competition_individual = competition.options.get('individual', None) == 'true'
    c_teams = competition.competings_by_stage(stage)
    c_teams_data = []
    for c_team in c_teams:
        c_team_data = c_team.__json__(include_keys=['current_rank'])
        team = c_team.team
        if competition_individual:
            team_data = {'id': team.id, 'name': team.creator.fullname, 'logo': team.creator.user_profile}
        else:
            team_data = {'id': team.id, 'name': team.name, 'logo': team.logo}
        c_team_data['team'] = team_data
        c_teams_data.append(c_team_data)

    fixtures = competition_fixture_service.find_by_competition_and_stage(competition_id, stage)
    return json_response(c_teams=c_teams_data, fixtures=fixtures)


@bp.route('/<int:competition_id>/ranks', methods=['GET'])
def ranks(competition_id):
    """
        获取该赛事下的某一阶段的参赛队伍的排名
    """
    stage = int(request.args.get('stage'))
    competition = models.Competition.from_cache_by_id(competition_id)
    if not competition:
        raise AppError(error_code=errors.competition_id_noexistent)

    competition_individual = competition.options.get('individual', None) == 'true'
    c_teams = competition.competings_by_stage(stage)
    rank_ids = [c_team.current_rank.id for c_team in c_teams]
    rank_additions = models.CompetitionTeamRankAddition.query.filter(models.CompetitionTeamRankAddition.rank_id.in_(rank_ids)).all()
    rank_additions = dict([(rank_addition.rank_id, rank_addition) for rank_addition in rank_additions])
    c_teams_data = []
    for c_team in c_teams:
        c_team_data = c_team.__json__(include_keys=['current_rank'])
        team = c_team.team
        if competition_individual:
            team_data = {'id': team.id, 'name': team.creator.fullname, 'logo': team.creator.user_profile}
        else:
            team_data = {'id': team.id, 'name': team.name, 'logo': team.logo}
        c_team_data['team'] = team_data
        c_team_data['rank_addition'] = rank_additions.get(c_team.current_rank.id, None)
        c_teams_data.append(c_team_data)


    data = sorted(c_teams_data,
           key=lambda e: (
               e['current_rank'].pts,
               (e['rank_addition'].goals_for - e['rank_addition'].goals_against) if e.get('rank_addition') else 0,
               e['rank_addition'].goals_for if e.get('rank_addition') else 0), reverse=True)
    return json_response(c_teams=data)


@bp.route('/<int:competition_id>/next-stage-teams', methods=['GET'])
def next_stage_teams(competition_id):
    """
        获取该赛事下的晋级下一阶段的参赛队伍
    """
    teams_per_group = int(request.args.get('teams_per_group', '2'))
    stage = int(request.args.get('stage'))

    competition = models.Competition.from_cache_by_id(competition_id)
    if not competition:
        raise AppError(error_code=errors.competition_id_noexistent)
    c_teams = competition.competings_by_stage(stage - 1)

    competition_individual = competition.options.get('individual', None) == 'true'

    rank_ids = [c_team.current_rank.id for c_team in c_teams]
    rank_additions = models.CompetitionTeamRankAddition.query.filter(models.CompetitionTeamRankAddition.rank_id.in_(rank_ids)).all()
    rank_additions = dict([(rank_addition.rank_id, rank_addition) for rank_addition in rank_additions])
    c_teams_data = []
    for c_team in c_teams:
        c_team_data = c_team.__json__(include_keys=['current_rank'])
        team = c_team.team
        if competition_individual:
            team_data = {'id': team.id, 'name': team.creator.fullname, 'logo': team.creator.user_profile}
        else:
            team_data = {'id': team.id, 'name': team.name, 'logo': team.logo}
        c_team_data['team'] = team_data
        c_team_data['rank_addition'] = rank_additions.get(c_team.current_rank.id, None)
        c_teams_data.append(c_team_data)

    c_teams_data = sorted(c_teams_data, key=lambda e: e['current_rank'].group)
    results = {}
    for key, value in itertools.groupby(c_teams_data, key=lambda t: t['current_rank'].group):
        results[key] = list(v for v in value)
    results = dict(
        [
            (group, sorted(group_teams_data,
                           key=lambda d: (
                               d['current_rank'].pts,
                               (d['rank_addition'].goals_for - d['rank_addition'].goals_against) if d.get('rank_addition') else 0,
                               d['rank_addition'].goals_for if d.get('rank_addition') else 0),
                           reverse=True)[:teams_per_group]
            ) for (group, group_teams_data) in results.items()])
    return json_response(results=results)
