# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
from ...core import AppError, db
from ...services import account_athletic_item_service, match_highlight_service
from ...helpers.flask_helper import json_response
from ... import models
from ... import errors

bp = Blueprint('user_athletics', __name__, url_prefix='/user/<int:account_id>/athletics')


@bp.route('/<int:athletic_item_id>', methods=['GET'])
def home_page(account_id, athletic_item_id):
    athlete = models.Athlete.from_cache_by_account_id_and_athletic_item_id(account_id, athletic_item_id)
    if not athlete:
        raise AppError(error_code=errors.account_bind_athletic_nonexistent)
    return render_template('frontend/mySportsHome.html', athlete=athlete)


@bp.route('/bind', methods=['POST'])
@login_required
def bind_athletic_item(account_id):
    """
        当前用户绑定运动项目
    """
    current_account_id = current_user._get_current_object().id
    if account_id != current_account_id:
        raise AppError(error_code=errors.operation_unauthorized)
    athletic_item_id = int(request.form.get('athletic_item_id'))
    athlete = account_athletic_item_service.bind_athletic_item(current_account_id, athletic_item_id)
    return json_response(athlete=athlete)


@bp.route('/unbind', methods=['POST'])
@login_required
def unbind_athletic_item(account_id):
    """
        解除与运动项目的绑定
    """
    current_account_id = current_user._get_current_object().id
    if account_id != current_account_id:
        raise AppError(error_code=errors.operation_unauthorized)
    athletic_item_id = int(request.form.get('athletic_item_id'))
    account_athletic_item_service.unbind_athletic_item(current_account_id, athletic_item_id)
    return json_response(success=True)


@bp.route('/<int:athletic_item_id>/update', methods=['POST'])
@login_required
def update_athlete(account_id, athletic_item_id):
    """
        更新用户在该运动项目下的信息
    """
    current_account_id = current_user._get_current_object().id
    if account_id != current_account_id:
        raise AppError(error_code=errors.operation_unauthorized)
    athlete = account_athletic_item_service.update_athlete(current_account_id, athletic_item_id, **request.json)
    return json_response(athlete=athlete)


@bp.route("/<int:athletic_item_id>/highlights", methods=['GET'])
def highlights(account_id, athletic_item_id):
    """
        获取用户在该运动项目下的精彩瞬间
    :return:
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))

    athlete = models.Athlete.from_cache_by_account_id_and_athletic_item_id(account_id, athletic_item_id)
    if not athlete:
        raise AppError(error_code=errors.account_bind_athletic_nonexistent)

    if offset == 0 and limit == 10:
        data = athlete.recent_highlights
    else:
        data = match_highlight_service.paginate_highlight_by_athlete(athlete.id, offset, limit)
    return json_response(
        results=[dict(id=highlight.id, date_recorded=highlight.date_recorded, details=highlight.details) for highlight in data]
    )


@bp.route("/<int:athletic_item_id>/competitions", methods=['GET'])
def athlete_competition_page(account_id, athletic_item_id):
    athlete = models.Athlete.from_cache_by_account_id_and_athletic_item_id(account_id, athletic_item_id)
    if not athlete:
        raise AppError(error_code=errors.account_bind_athletic_nonexistent)

    return render_template('frontend/moreCompetition.html', athlete=athlete)


@bp.route("/<int:athletic_item_id>/competitions/more", methods=['GET'])
def more_athlete_competition(account_id, athletic_item_id):
    """
        获取用户在该运动项目下的赛事
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))

    athlete = models.Athlete.from_cache_by_account_id_and_athletic_item_id(account_id, athletic_item_id)
    if not athlete:
        raise AppError(error_code=errors.account_bind_athletic_nonexistent)

    competition_teams = db.session.query(models.CompetitionTeam). \
        join(models.CompetitionAthlete,
             models.CompetitionAthlete.competition_team_id == models.CompetitionTeam.id). \
        join(models.TeamMember,
             db.and_(
                 models.TeamMember.team_id == models.CompetitionTeam.team_id,
                 models.TeamMember.id == models.CompetitionAthlete.team_member_id,
                 models.TeamMember.athlete_id == athlete.id)). \
        join(models.Competition,
             db.and_(
                 models.Competition.id == models.CompetitionTeam.competition_id,
                 models.Competition.c_type != 0)). \
        order_by(models.Competition.date_started.desc()).offset(offset).limit(limit).all()
    return json_response(results=[competition_team.__json__(include_keys=['competition', 'prize', 'latest_rank', 'latest_rank.addition'])
                                  for competition_team in competition_teams])


@bp.route("/<int:athletic_item_id>/fixtures", methods=['GET'])
def athlete_competition_fixture_page(account_id, athletic_item_id):
    athlete = models.Athlete.from_cache_by_account_id_and_athletic_item_id(account_id, athletic_item_id)
    if not athlete:
        raise AppError(error_code=errors.account_bind_athletic_nonexistent)

    return render_template('frontend/moreCompetitionResult.html', athlete=athlete)


@bp.route("/<int:athletic_item_id>/fixtures/more", methods=['GET'])
def more_account_competition_fixtures(account_id, athletic_item_id):
    """
        获取用户在该运动项目下的比赛记录
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))

    athlete = models.Athlete.from_cache_by_account_id_and_athletic_item_id(account_id, athletic_item_id)
    if not athlete:
        raise AppError(error_code=errors.account_bind_athletic_nonexistent)

    competition_fixtures = db.session.query(models.CompetitionFixture). \
        select_from(models.CompetitionTeam). \
        join(models.CompetitionAthlete,
             models.CompetitionAthlete.competition_team_id == models.CompetitionTeam.id). \
        join(models.TeamMember,
             db.and_(
                 models.TeamMember.team_id == models.CompetitionTeam.team_id,
                 models.TeamMember.id == models.CompetitionAthlete.team_member_id,
                 models.TeamMember.athlete_id == athlete.id)). \
        join(models.Competition, models.Competition.id == models.CompetitionTeam.competition_id). \
        join(models.CompetitionFixture,
             db.or_(models.CompetitionFixture.p1 == models.CompetitionTeam.id,
                    models.CompetitionFixture.p2 == models.CompetitionTeam.id)). \
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
