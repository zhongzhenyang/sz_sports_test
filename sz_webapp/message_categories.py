# coding:utf-8

from .core import db, AppError
from .models import Team, TeamMember, Athlete
from . import errors

# 申请加入球队
apply_team_join = 1

# 申请参加友谊赛
apply_challenge = 2


def _handle_apply_team_join(message, result):
    from .services import team_member_service

    team_id = message.body.get('team_id')
    proposer_id = message.sender_id
    if result == 1:
        try:
            team = Team.query.get(team_id)
            if team is None:
                raise AppError(error_code=errors.team_id_nonexistent)
            if team.status == -1:
                raise AppError(error_code=errors.team_dismissed)
            athlete = Athlete.query.filter(Athlete.account_id == proposer_id, Athlete.athletic_item_id == team.athletic_item_id).first()
            if athlete is None:
                raise AppError(error_code=errors.account_bind_athletic_nonexistent)
            team_member_service.join_team(proposer_id, team_id)
        except AppError, e:
            if e.error_code:
                message.error_code = e.error_code



def _handle_apply_challenge(message, result):
    from .services import competition_service
    proposer_id = message.sender_id
    if result == 1:
        try:
            competition_service.create_challenge(proposer_id, **message.body)
        except AppError, e:
            if e.error_code:
                message.error_code = e.error_code


_handlers = {
    apply_team_join: _handle_apply_team_join,
    apply_challenge: _handle_apply_challenge,
}


def get_handler(category):
    return _handlers.get(category)
