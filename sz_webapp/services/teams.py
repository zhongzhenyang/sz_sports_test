# coding:utf-8

import datetime
from ..core import BaseService, AppError, db, after_commit
from ..models import Team, TeamMember, Athlete, CompetitionTeam, Message
from .. import errors
from .. import settings
from .. import tasks


class TeamService(BaseService):
    __model__ = Team

    def create_team(self, account_id, team_type=1, **kwargs):
        athletic_item_id = kwargs.get('athletic_item_id')
        athlete = Athlete.query.filter(Athlete.account_id == account_id,
                                       Athlete.athletic_item_id == athletic_item_id).first()
        if athlete is None or athlete.status == 0:
            raise AppError(error_code=errors.account_bind_athletic_nonexistent)

        team_count = self.count_by(filters=[Team.creator_id == account_id,
                                            Team.athletic_item_id == athletic_item_id, Team.status == 1, Team.type == 1])
        if team_count > 0:
            raise AppError(error_code=errors.team_more_one_athletic_team_by_creator)

        if team_count == 0:
            team = Team()
            self._set_team(team, **kwargs)
            team.type = team_type
            team.creator_id = account_id
            self.save(team)
            db.session.add(TeamMember(team_id=team.id, athlete_id=athlete.id, status=1))

            if team._logo:
                def do_thumbnail_team_logo():
                    tasks.thumbnail_image.apply_async(('Team', team.id, '_logo', team._logo, '200x200!'))

                after_commit(do_thumbnail_team_logo)

            if team._uniform:
                def do_thumbnail_team_uniform():
                    tasks.thumbnail_image.apply_async(('Team', team.id, '_uniform', team._uniform, '200x200!'))

                after_commit(do_thumbnail_team_uniform)

            return team

    def update_team(self, account_id, team_id, **kwargs):
        team = self._check(account_id, team_id)

        original_team_logo = team._logo
        original_team_uniform = team._uniform

        self._set_team(team, **kwargs)

        if team._logo and original_team_logo != team._logo:
            def do_thumbnail_team_logo():
                tasks.thumbnail_image.apply_async(('Team', team.id, '_logo', team._logo, '200x200!'))

            after_commit(do_thumbnail_team_logo)

        if team._uniform and original_team_uniform != team._uniform:
            def do_thumbnail_team_uniform():
                tasks.thumbnail_image.apply_async(('Team', team.id, '_uniform', team._uniform, '200x200!'))

            after_commit(do_thumbnail_team_uniform)

        return team

    def delete_team(self, team_id):
        team = self.get(team_id)
        if not team:
            raise AppError(error_code=errors.team_id_nonexistent)
        competition_teams = CompetitionTeam.query.filter(CompetitionTeam.team_id == team_id).all()
        for c_team in competition_teams:
            db.session.delete(c_team)

        self.delete(team)

    def dismiss_team(self, account_id, team_id):
        team = self._check(account_id, team_id)

        pending_message_count = Message.query.with_entities(db.func.count(Message.id)). \
            filter(Message.receiver_id == account_id, Message.status == 0).scalar()

        if pending_message_count > 0:
            raise AppError(error_code=errors.message_pending)

        team.status = -1
        self.save(team)
        for member in team._members.all():
            member.status = -1
            member.date_left = datetime.date.today()
            db.session.add(member)

    def update_team_creator(self, account_id, team_id, new_creator_id):
        team = self._check(account_id, team_id)

        pending_message_count = Message.query.with_entities(db.func.count(Message.id)). \
            filter(Message.receiver_id == account_id, Message.status == 0).scalar()

        if pending_message_count > 0:
            raise AppError(error_code=errors.message_pending)

        athlete = Athlete.query.filter(Athlete.account_id == account_id,
                                       Athlete.athletic_item_id == team.athletic_item_id).first()
        if athlete is None or athlete.status == 0:
            raise AppError(error_code=errors.account_bind_athletic_nonexistent)
        team_member = TeamMember.query.filter(TeamMember.athlete_id == athlete.id).first()
        if team_member is None:
            raise AppError(error_code=errors.team_member_athlete_nonexistent)
        if team_member.status == -1:
            raise AppError(error_code=errors.team_member_athlete_left)
        team.creator_id = new_creator_id
        return self.save(team)

    def paginate_team(self, offset=0, limit=10, **kwargs):
        filters = [Team.type == 1, Team.status == 1]
        if 'athletic_item_id' in kwargs and kwargs['athletic_item_id']:
            filters.append(Team.athletic_item_id == kwargs['athletic_item_id'])
        if 'team_name' in kwargs and kwargs['team_name']:
            filters.append(Team.name.startswith(kwargs['team_name']))
        if 'loc_state' in kwargs and kwargs['loc_state']:
            filters.append(Team.loc_state == kwargs['loc_state'])
        if 'loc_city' in kwargs and kwargs['loc_city']:
            filters.append(Team.loc_city == kwargs['loc_city'])
        if 'loc_county' in kwargs and kwargs['loc_county']:
            filters.append(Team.loc_county == kwargs['loc_county'])
        return self.paginate_by(filters=filters, orders=[Team.id.asc()], offset=offset, limit=limit)

    def _set_team(self, team, **kwargs):

        team_logo = kwargs.get('logo', None)
        if team_logo and team_logo == settings.team_default_logo:
            team_logo = None

        team_uniform = kwargs.get('uniform', None)
        if team_uniform and team_uniform == settings.team_default_uniform:
            team_uniform = None

        team.name = kwargs.get('name')
        team.logo = team_logo
        team.abbr_name = kwargs.get('abbr_name')
        team.loc_state = kwargs.get('loc_state')
        team.loc_city = kwargs.get('loc_city')
        team.loc_county = kwargs.get('loc_county')
        team.home_site = kwargs.get('home_site')
        team.athletic_item_id = kwargs.get('athletic_item_id')
        team.contact_me = kwargs.get('contact_me')
        team.uniform = team_uniform
        team.status = 1

    def _check(self, account_id, team_id):
        team = self.get(team_id)
        if team is None:
            raise AppError(error_code=errors.team_id_nonexistent)
        if team.status == -1:
            raise AppError(error_code=errors.team_dismissed)
        if team.creator_id != account_id:
            raise AppError(error_code=errors.operation_unauthorized)

        return team
