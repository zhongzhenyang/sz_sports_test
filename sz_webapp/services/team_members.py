# coding:utf-8

import datetime
import sqlalchemy as sa
from flask_user import current_user
from ..core import BaseService, AppError, db
from ..models import TeamMember, Message, Team, Athlete
from .. import message_categories, errors
from ..helpers.datetime_helper import utc_now


class TeamMemberService(BaseService):
    __model__ = TeamMember

    def apply_team_join(self, account_id, team_id):
        team, athlete, team_member = self._check(account_id, team_id)
        if team_member and team_member.status == 1:
            raise AppError(error_code=errors.team_member_athlete_joined)
        message = Message.query.filter(Message.category == message_categories.apply_team_join,
                                       Message.sender_id == account_id,
                                       Message.body['team_id'].cast(sa.Integer) == team_id).first()
        if message and message.status == 0:
            raise AppError(error_code=errors.message_pending)

        message = Message()
        message.category = message_categories.apply_team_join
        message.sender_id = account_id
        message.receiver_id = team.creator_id
        message.body = dict(team_id=team_id)
        message.status = 0
        message.dt_sent = utc_now()
        db.session.add(message)

    def join_team(self, account_id, team_id):
        team, athlete, team_member = self._check(account_id, team_id)
        if team_member and team_member.status == 1:
            raise AppError(error_code=errors.team_member_athlete_joined)

        if team_member is None:
            team_member = TeamMember(team_id=team_id, athlete_id=athlete.id)
        team_member.status = 1
        team_member.date_joined = datetime.date.today()
        return self.save(team_member)

    def leave_team(self, account_id, team_id):
        team_member = TeamMember.query.join(Athlete, Athlete.id == TeamMember.athlete_id). \
            filter(TeamMember.team_id == team_id, Athlete.account_id == account_id).first()
        if team_member is None:
            raise AppError(error_code=errors.team_member_athlete_nonexistent)
        if team_member.status == -1:
            raise AppError(error_code=errors.team_member_athlete_left)

        team_member.status = -1
        team_member.date_left = datetime.date.today()
        return self.save(team_member)

    def get_team_member_status(self, account_id, team_id):
        team, athlete, team_member = self._check(account_id, team_id)
        if team_member and team_member.status == 1:
            status = 'yes'
        else:
            status = 'no'
        return status

    def reject_team_member(self, team_id, account_id):
        current_account_id = current_user._get_current_object().id
        team, athlete, team_member = self._check(account_id, team_id)
        if team.creator_id != current_account_id:
            raise AppError(error_code=errors.operation_unauthorized)
        if team_member is None:
            raise AppError(error_code=errors.team_member_athlete_nonexistent)
        if team_member.status == 0:
            raise AppError(error_code=errors.team_member_athlete_left)

        team_member.status = 0
        self.save(team_member)

    def _check(self, account_id, team_id):
        team = Team.query.get(team_id)
        if not team:
            raise AppError(error_code=errors.team_id_nonexistent)

        if team.status == -1:
            raise AppError(error_code=errors.team_dismissed)

        if team.type == 0:
            raise AppError(error_code=errors.team_private)

        athlete = Athlete.query.filter(Athlete.athletic_item_id == team.athletic_item_id,
                                       Athlete.account_id == account_id).first()
        if athlete is None or athlete.status == 0:
            raise AppError(error_code=errors.account_bind_athletic_nonexistent)

        team_member = TeamMember.query.filter(TeamMember.team_id == team_id,
                                              TeamMember.athlete_id == athlete.id).first()

        return team, athlete, team_member
