# coding:utf-8

import datetime
import sqlalchemy as sa
from ..core import BaseService, AppError, db, after_commit
from ..models import Competition, CompetitionMode, LeagueApplyItem, Team, Message, AthleticItem
from .. import message_categories, errors
from .. import tasks
from ..helpers import datetime_helper


class CompetitionService(BaseService):
    __model__ = Competition

    def apply_challenge(self, account_id, **kwargs):
        athletic_item_id = kwargs.get('athletic_item_id')
        athletic_item = AthleticItem.query.get(athletic_item_id)
        if athletic_item is None or not athletic_item.enabled:
            raise AppError(error_code=errors.athletic_item_id_nonexistent)
        p1_team_id = kwargs.get('p1')
        p2_team_id = kwargs.get('p2')

        message = Message.query.filter(Message.category == message_categories.apply_challenge,
                                       Message.sender_id == account_id,
                                       Message.body['athletic_item_id'].cast(sa.String) == athletic_item_id,
                                       Message.body['p1'].cast(sa.String) == p1_team_id,
                                       Message.body['p2'].cast(sa.String) == p2_team_id).first()

        if message and message.status == 0:
            raise AppError(error_code=errors.message_pending)

        p2_team = Team.query.get(p2_team_id)

        message = Message()
        message.category = message_categories.apply_challenge
        message.sender_id = account_id
        message.receiver_id = p2_team.creator_id
        message.body = kwargs
        message.status = 0
        db.session.add(message)

    def create_challenge(self, account_id, **kwargs):
        competition = self._create_competition(account_id, 0, 1, 1, 1, **kwargs)

        from ..services import competition_team_service, competition_fixture_service

        p1_team_id = kwargs.get('p1')
        p2_team_id = kwargs.get('p2')
        competition_team_service.add_competition_team(competition, p1_team_id)
        competition_team_service.add_competition_team(competition, p2_team_id)

        competition_fixture_service.create_competition_fixture(account_id, competition.id, **kwargs)

        return competition

    def create_activity(self, account_id, **kwargs):
        competition = self._create_competition(account_id, 1, 0, 1, 1, **kwargs)

        def do_after_commit():
            tasks.set_competition_status.apply_async((competition.id, 1),
                                                     eta=datetime.datetime(competition.date_reg_end.year,
                                                                           competition.date_reg_end.month,
                                                                           competition.date_reg_end.day, tzinfo=datetime_helper.system_timezone))

        after_commit(do_after_commit)

        return competition

    def create_league(self, account_id, **kwargs):
        competition = self._create_competition(account_id, 2, 0, 3, 1, **kwargs)

        def do_after_commit():
            tasks.set_competition_status.apply_async((competition.id, 1),
                                                     eta=datetime.datetime(competition.date_reg_end.year,
                                                                           competition.date_reg_end.month,
                                                                           competition.date_reg_end.day, tzinfo=datetime_helper.system_timezone))

        after_commit(do_after_commit)
        return competition

    def _create_competition(self, manager_id, c_type, status, stage_num, stage, **kwargs):
        competition = Competition()
        competition.manager_id = manager_id
        competition.c_type = c_type
        competition.status = status
        competition.stage_num = stage_num
        competition.stage = stage
        self._set_competition(competition, **kwargs)
        self.save(competition)

        competition_logo = competition.logo
        if competition_logo:
            def do_thumbnail_competition_logo():
                tasks.thumbnail_image.apply_async(('Competition', competition.id, 'logo', competition_logo, '200x200!'))

            after_commit(do_thumbnail_competition_logo)

        return competition

    def apply_league(self, account_id, competition_id):
        competition = self.get(competition_id)
        if competition is None:
            raise AppError(error_code=errors.competition_id_noexistent)
        if competition.manager_id != account_id:
            raise AppError(error_code=errors.operation_unauthorized)
        if competition.c_type != 1:
            raise AppError(error_code=errors.competition_cannot_promote_as_league)
        if competition.in_league_apply:
            raise AppError(error_code=errors.competition_in_apply_league)
        league_apply_item = LeagueApplyItem(competition_id=competition_id)
        db.session.add(league_apply_item)

    def audit_league(self, competition_id, result):
        competition = self.get(competition_id)
        if competition is None:
            raise AppError(error_code=errors.competition_id_noexistent)
        league_apply_item = LeagueApplyItem.query.filter(LeagueApplyItem.competition_id == competition_id).first()
        if league_apply_item is None:
            raise AppError(error_code=errors.competition_not_in_apply_league)
        if result == 1:
            competition.c_type = 2
            competition.stage_num = 3
        db.session.delete(league_apply_item)

    def update_competition(self, account_id, competition_id, **kwargs):
        competition = self.get(competition_id)
        original_competition_logo = competition.logo
        new_competition_logo = kwargs.get('logo', None)
        if not competition:
            raise AppError(error_code=errors.competition_id_noexistent)

        if account_id != competition.manager_id:
            raise AppError(error_code=errors.operation_unauthorized)

        if competition.status != 0:
            raise AppError(error_code=errors.competition_started)

        self._set_competition(competition, **kwargs)
        self.save(competition)

        if new_competition_logo and new_competition_logo != original_competition_logo:
            def do_thumbnail_competition_logo():
                tasks.thumbnail_image.apply_async(('Competition', competition.id, 'logo', new_competition_logo, '200x200!'))

            after_commit(do_thumbnail_competition_logo)

        def do_after_commit():
            tasks.set_competition_status.apply_async((competition.id, 1),
                                                     eta=datetime.datetime(competition.date_reg_end.year,
                                                                           competition.date_reg_end.month,
                                                                           competition.date_reg_end.day, tzinfo=datetime_helper.system_timezone))

        after_commit(do_after_commit)

        return competition

    def delete_competition(self, competition_id):
        competition = self.get(competition_id)
        if not competition:
            raise AppError(error_code=errors.competition_id_noexistent)
        if competition.status != 0:
            raise AppError(error_code=errors.competition_started)
        competition_teams = competition._competings.all()
        for competition_team in competition_teams:
            db.session.delete(competition_team)
        self.delete(competition)

    def stick_competition(self, competition_id):
        competition = self.get(competition_id)
        if not competition:
            raise AppError(error_code=errors.competition_id_noexistent)

        if competition.stick:
            raise AppError(error_code=errors.competition_sticked)
        competition_mode = CompetitionMode(competition_id=competition_id, mode=1)
        db.session.add(competition_mode)

    def unstick_competition(self, competition_id):
        competition = self.get(competition_id)
        if not competition:
            raise AppError(error_code=errors.competition_id_noexistent)

        competition_mode = CompetitionMode.query. \
            filter(CompetitionMode.competition_id == competition_id, CompetitionMode.mode == 1).first()
        if competition_mode is None:
            raise AppError(error_code=errors.competition_unsticked)
        db.session.delete(competition_mode)

    def set_status(self, account_id, competition_id, status):
        competition = self._check(account_id, competition_id)
        competition.status = status
        return self.save(competition)

    def set_stage(self, account_id, competition_id, stage):
        competition = self._check(account_id, competition_id)
        competition.stage = stage
        return self.save(competition)

    def paginate_competition(self, offset=0, limit=10, **kwargs):
        filters = [Competition.c_type != 0]
        if 'athletic_item_id' in kwargs and kwargs['athletic_item_id']:
            filters.append(Competition.athletic_item_id == kwargs.get('athletic_item_id'))
        if 'c_name' in kwargs and kwargs['c_name']:
            filters.append(Competition.name.startswith(kwargs.get('c_name')))
        if 'c_type' in kwargs and kwargs['c_type']:
            filters.append(Competition.c_type == kwargs.get('c_type'))
        if 'c_status' in kwargs and kwargs['c_status'] is not None:
            filters.append(Competition.status == kwargs.get('c_status'))
        if 'c_loc_state' in kwargs and kwargs['c_loc_state']:
            filters.append(Competition.loc_state == kwargs.get('c_loc_state'))
        if 'c_loc_city' in kwargs and kwargs['c_loc_city']:
            filters.append(Competition.loc_city == kwargs.get('c_loc_city'))
        if 'c_loc_county' in kwargs and kwargs['c_loc_county']:
            filters.append(Competition.loc_county == kwargs.get('c_loc_county'))
        if 'c_date_published_orderby' in kwargs and kwargs['c_date_published_orderby'] == 1:
            c_date_publish_orderby = Competition.date_published.asc()
        else:
            c_date_publish_orderby = Competition.date_published.desc()
        if 'only_apply_league' in kwargs and kwargs.get('only_apply_league'):
            count = Competition.query.with_entities(db.func.count('*')). \
                select_from(Competition).join(LeagueApplyItem, LeagueApplyItem.competition_id == Competition.id). \
                filter(*filters).scalar()
            competitions = Competition.query. \
                join(LeagueApplyItem, LeagueApplyItem.competition_id == Competition.id). \
                filter(*filters).order_by(LeagueApplyItem.dt_applied.asc()).offset(offset).limit(limit).all()
            return count, competitions
        else:
            return self.paginate_by(filters=filters, orders=[c_date_publish_orderby], offset=offset,
                                    limit=limit)

    def paginate_competition_by_manager(self, manager_id, offset=0, limit=10):
        filters = [Competition.manager_id == manager_id, Competition.c_type != 0]
        return self.paginate_by(filters=filters, orders=[Competition.date_published.desc()], offset=offset, limit=limit)

    def get_competing_teams(self, competition_id, stage):
        competition = self.get(competition_id)
        with_rank_teams = competition.competings_by_stage(stage)
        return with_rank_teams

    def _set_competition(self, competition, **kwargs):
        competition.athletic_item_id = int(kwargs.get('athletic_item_id'))
        competition.name = kwargs.get('name') \
            if kwargs.get('name', None) else str(
            kwargs.get('athletic_item_id')) + '-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        competition.loc_state = kwargs.get('loc_state')
        competition.loc_city = kwargs.get('loc_city')
        competition.loc_county = kwargs.get('loc_county')
        try:
            date_started = datetime.datetime.strptime(kwargs.get('date_started'), '%Y-%m-%d')
            date_started = datetime.date(date_started.year, date_started.month, date_started.day)
        except:
            date_started = datetime.date.today()

        competition.date_started = date_started

        try:
            date_reg_end = datetime.datetime.strptime(kwargs.get('date_reg_end'), '%Y-%m-%d')
            date_reg_end = datetime.date(date_reg_end.year, date_reg_end.month, date_reg_end.day)
        except:
            date_reg_end = datetime.date.today()

        competition.date_reg_end = date_reg_end

        competition.team_num = int(kwargs.get('team_num')) if kwargs.get('team_num', None) else 0
        competition.host = kwargs.get('host')
        competition.organizer = kwargs.get('organizer')
        competition.sponsor = kwargs.get('sponsor')
        competition.site = kwargs.get('site')
        competition.logo = kwargs.get('logo')
        competition.intro = kwargs.get('intro')
        competition.requirement = kwargs.get('requirement')
        try:
            date_published = datetime.datetime.strptime(kwargs.get('date_published'), '%Y-%m-%d')
            date_published = datetime.date(date_published.year, date_published.month, date_published.day)
        except:
            date_published = datetime.date.today()
        competition.date_published = date_published

        competition.contact_me = kwargs.get('contact_me')
        competition.options = kwargs.get('options', {})

    def _check(self, account_id, competition_id):
        competition = self.get(competition_id)
        if not competition:
            raise AppError(error_code=errors.competition_id_noexistent)

        if account_id != competition.manager_id:
            raise AppError(error_code=errors.operation_unauthorized)
        return competition
