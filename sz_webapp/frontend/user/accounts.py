# coding:utf-8

from flask import Blueprint, request, render_template, current_app
from flask_user import login_required, current_user
from ...services import account_service, user_service, user_relation_service, match_highlight_service
from ...helpers.flask_helper import json_response
from ... import models
from ... import errors
from ...core import AppError, db
from ...helpers import model_helper

bp = Blueprint('user_accounts', __name__, url_prefix='/user/accounts')


@bp.route('/who-am-i', methods=['GET', 'POST'])
def who_am_i():
    if current_user.is_authenticated():
        user = current_user._get_current_object()
        return json_response(user=user)
    else:
        return json_response(success=False)


@bp.route('/unique-email', methods=['GET'])
def unique_email():
    email = request.args.get('email')
    if email:
        user_manager = current_app.user_manager
        if user_manager.email_is_available(email):
            return "true"
    return "false"


@bp.route('/relation/add/<int:oppo_uid>', methods=['POST'])
@login_required
def add_user_relation(oppo_uid):
    """
        当前登录用户关注 oppo_uid
    """
    current_account_id = current_user._get_current_object().id
    user_relation_service.add_user_relation(current_account_id, oppo_uid)
    return json_response(success=True)


@bp.route('/relation/delete/<int:oppo_uid>', methods=['POST'])
@login_required
def delete_user_relation(oppo_uid):
    """
        当前登录用户取消关注 oppo_uid
    """
    current_account_id = current_user._get_current_object().id
    user_relation_service.delete_user_relation(current_account_id, oppo_uid)
    return json_response(success=True)


@bp.route('/relation/relation-status/<int:oppo_uid>', methods=['GET'])
@login_required
def get_related_status_for(oppo_uid):
    """
        当前用户是否已经关注了这个用户,status 为 yes or no
    """
    current_account_id = current_user._get_current_object().id
    status = user_relation_service.get_user_relation_status(current_account_id, oppo_uid)
    return json_response(status=status)


@bp.route('/<int:account_id>/relations', methods=['GET'])
def related_users(account_id):
    """
        用户所关注的人的列表
    """
    account = models.Account.from_cache_by_id(account_id)
    if not account:
        raise AppError(error_code=errors.account_id_noexistent)
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))

    related_account_ids = account.related_account_ids[offset: -1 if limit == -1 else offset + limit]
    related_accounts = model_helper.get_accounts(related_account_ids)
    return json_response(results=related_accounts)


@bp.route("/<int:account_id>/highlights", methods=['GET'])
def highlights(account_id):
    """
        获取用户精彩瞬间的图片
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))

    account = models.Account.from_cache_by_id(account_id)
    if not account:
        raise AppError(error_code=errors.account_id_noexistent)

    if offset == 0 and limit == 10:
        data = account.recent_highlights
    else:
        data = match_highlight_service.paginate_highlight_by_account(account_id, offset, limit)
    return json_response(
        results=[dict(id=highlight.id, date_recorded=highlight.date_recorded, details=highlight.details) for highlight in data]
    )


@bp.route("/<int:account_id>/competitions", methods=['GET'])
def account_competition_page(account_id):
    account = models.Account.from_cache_by_id(account_id)
    return render_template('frontend/moreCompetition.html', account=account)


@bp.route("/<int:account_id>/competitions/more", methods=['GET'])
def more_account_competitions(account_id):
    """
        获取用户赛事记录
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))

    competition_teams = db.session.query(models.CompetitionTeam). \
        select_from(models.CompetitionTeam). \
        join(models.Competition,
             db.and_(models.Competition.id == models.CompetitionTeam.competition_id, models.Competition.c_type != 0)). \
        join(models.CompetitionAthlete,
             models.CompetitionAthlete.competition_team_id == models.CompetitionTeam.id). \
        join(models.TeamMember,
             db.and_(
                 models.TeamMember.team_id == models.CompetitionTeam.team_id,
                 models.TeamMember.id == models.CompetitionAthlete.team_member_id)). \
        join(models.Athlete,
             db.and_(
                 models.Athlete.id == models.TeamMember.athlete_id,
                 models.Athlete.account_id == account_id)). \
        order_by(models.Competition.date_started.desc()).offset(offset).limit(limit).all()
    return json_response(results=[competition_team.__json__(include_keys=['competition', 'prize', 'latest_rank', 'latest_rank.addition'])
                                  for competition_team in competition_teams])


@bp.route("/<int:account_id>/fixtures", methods=['GET'])
def account_competition_fixture_page(account_id):
    account = models.Account.from_cache_by_id(account_id)
    return render_template('frontend/moreCompetitionResult.html', account=account)


@bp.route("/<int:account_id>/fixtures/more", methods=['GET'])
def more_account_competition_fixtures(account_id):
    """
        获取用户的比赛记录
    """
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))
    competition_fixtures = db.session.query(models.CompetitionFixture). \
        select_from(models.CompetitionTeam). \
        join(models.CompetitionAthlete,
             models.CompetitionAthlete.competition_team_id == models.CompetitionTeam.id). \
        join(models.TeamMember,
             db.and_(
                 models.TeamMember.team_id == models.CompetitionTeam.team_id,
                 models.TeamMember.id == models.CompetitionAthlete.team_member_id)). \
        join(models.Athlete,
             db.and_(
                 models.Athlete.id == models.TeamMember.athlete_id,
                 models.Athlete.account_id == account_id)). \
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
