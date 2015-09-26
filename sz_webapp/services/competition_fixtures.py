# coding:utf-8

import datetime
import uuid
from ..core import BaseService, AppError, db, get_model, after_commit
from ..models import Competition, CompetitionTeam, CompetitionTeamRank, CompetitionTeamRankAddition, \
    CompetitionFixture, MatchGoal, MatchSection, MatchHighlight, CompetitionTeamPrize, Athlete
from .. import errors
from .. import tasks


class CompetitionFixtureService(BaseService):
    __model__ = CompetitionFixture

    def create_competition_fixture(self, account_id, competition_id, **kwargs):
        competition = Competition.query.get(competition_id)
        if not competition:
            raise AppError(error_code=errors.competition_id_noexistent)
        if competition.manager_id != account_id:
            raise AppError(error_code=errors.operation_unauthorized)
        if competition.status == 2:
            raise AppError(error_code=errors.competition_finished)

        p1 = int(kwargs.get('p1'))
        p2 = int(kwargs.get('p2'))
        if p1 == p2:
            raise AppError(error_code=errors.competition_fixture_cannot_create)

        p1_c_team = CompetitionTeam.query. \
            filter(CompetitionTeam.competition_id == competition_id, CompetitionTeam.team_id == p1).first()
        p2_c_team = CompetitionTeam.query. \
            filter(CompetitionTeam.competition_id == competition_id, CompetitionTeam.team_id == p2).first()

        competition_fixture = CompetitionFixture()
        competition_fixture.competition_id = competition_id
        competition_fixture.p1 = p1_c_team.id
        competition_fixture.p2 = p2_c_team.id
        competition_fixture.date_started = datetime.datetime.strptime(kwargs.get('date_started'), '%Y-%m-%d')
        competition_fixture.notary_id = int(kwargs.get('notary_id')) if kwargs.get('notary_id', None) else None
        competition_fixture.referee_id = int(kwargs.get('referee_id')) if kwargs.get('referee_id', None) else None
        competition_fixture.site = kwargs.get('site')
        competition_fixture.stage = competition.stage
        competition_fixture.round = int(kwargs.get('round')) if kwargs.get('round', None) else None
        competition_fixture.sn = int(kwargs.get('sn')) if kwargs.get('sn', None) else None
        competition_fixture.status = 0
        competition_fixture.addition = kwargs.get('addition')
        self.save(competition_fixture)

        p1_rank = CompetitionTeamRank.query. \
            filter(CompetitionTeamRank.c_team_id == p1_c_team.id,
                   CompetitionTeamRank.stage == competition.stage).first()
        if p1_rank is None:
            p1_rank = CompetitionTeamRank(c_team_id=p1_c_team.id, stage=competition.stage, pts=0)
        p1_rank.group = kwargs.get('group')

        p2_rank = CompetitionTeamRank.query. \
            filter(CompetitionTeamRank.c_team_id == p2_c_team.id,
                   CompetitionTeamRank.stage == competition.stage).first()
        if p2_rank is None:
            p2_rank = CompetitionTeamRank(c_team_id=p2_c_team.id, stage=competition.stage, pts=0)
        p2_rank.group = kwargs.get('group')
        db.session.add_all([p1_rank, p2_rank])
        return competition_fixture

    def update_competition_fixture(self, account_id, competition_fixture_id, **kwargs):
        competition_fixture = _check(account_id, competition_fixture_id, check_status=True)
        competition_fixture.date_started = datetime.datetime.strptime(kwargs.get('date_started'), '%Y-%m-%d')
        competition_fixture.notary_id = kwargs.get('notary_id') if kwargs.get('notary_id', None) else None
        competition_fixture.referee_id = kwargs.get('referee_id') if kwargs.get('referee_id', None) else None
        competition_fixture.site = kwargs.get('site')
        competition_fixture.stage = competition_fixture.competition.stage
        competition_fixture.round = kwargs.get('round') if kwargs.get('round', None) else None
        competition_fixture.sn = kwargs.get('sn') if kwargs.get('sn', None) else None
        return competition_fixture

    def delete_competition_fixture(self, account_id, competition_fixture_id):
        competition_fixture = _check(account_id, competition_fixture_id, check_status=True)
        self.delete(competition_fixture)

    def submit_result(self, account_id, competition_fixture_id, **kwargs):
        competition_fixture = _check(account_id, competition_fixture_id, required_competition_manager_only=False,
                                     check_status=True)

        competition_fixture.p1_score = p1_score = int(kwargs.get('p1_score'))
        competition_fixture.p2_score = p2_score = int(kwargs.get('p2_score'))
        competition_fixture.status = 1
        p1_pts, p2_pts = 0, 0
        if p1_score > p2_score:
            p1_pts = 3
        elif p1_score < p2_score:
            p2_pts = 3
        else:
            p1_pts = p2_pts = 1

        p1_rank = CompetitionTeamRank.query. \
            filter(CompetitionTeamRank.c_team_id == competition_fixture.p1,
                   CompetitionTeamRank.stage == competition_fixture.stage).first()
        p2_rank = CompetitionTeamRank.query. \
            filter(CompetitionTeamRank.c_team_id == competition_fixture.p2,
                   CompetitionTeamRank.stage == competition_fixture.stage).first()
        p1_rank.pts += p1_pts
        p2_rank.pts += p2_pts

        p1_rank_addition = CompetitionTeamRankAddition.query.get(p1_rank.id)
        if p1_rank_addition is None:
            p1_rank_addition = CompetitionTeamRankAddition(rank_id=p1_rank.id, played=0, won=0, drawn=0, lost=0,
                                                           goals_for=0, goals_against=0)

        p2_rank_addition = CompetitionTeamRankAddition.query.get(p2_rank.id)
        if p2_rank_addition is None:
            p2_rank_addition = CompetitionTeamRankAddition(rank_id=p2_rank.id, played=0, won=0, drawn=0, lost=0,
                                                           goals_for=0, goals_against=0)

        p1_rank_addition.played += 1
        p2_rank_addition.played += 1

        if p1_pts > p2_pts:
            p1_rank_addition.won += 1
            p2_rank_addition.lost += 1
        elif p1_pts < p2_pts:
            p1_rank_addition.lost += 1
            p2_rank_addition.won += 1
        else:
            p1_rank_addition.drawn += 1
            p2_rank_addition.drawn += 1
        p1_rank_addition.goals_for += p1_score
        p1_rank_addition.goals_against += p2_score
        p2_rank_addition.goals_for += p2_score
        p2_rank_addition.goals_against += p1_score

        db.session.add_all([p1_rank, p2_rank, p1_rank_addition, p2_rank_addition])
        if competition_fixture.addition:
            self._add_next_competition_fixture(competition_fixture)
            self._add_competition_prize(competition_fixture)

    def _add_next_competition_fixture(self, competition_fixture):
        addition = competition_fixture.addition
        oppo_addition = None
        next_addition = None
        name, area, sn = addition.split('-')
        if name == '8' or name == '4':
            if sn == '1':
                oppo_sn = '2'
                next_sn = '1'
            elif sn == '2':
                oppo_sn = '1'
                next_sn = '1'
            elif sn == '3':
                oppo_sn = '4'
                next_sn = '2'
            elif sn == '4':
                oppo_sn = '3'
                next_sn = '2'
            else:
                oppo_sn = None
                next_sn = None

            if oppo_sn and next_sn:
                next_name = '4' if name == '8' else '2'
                oppo_addition = "{name}-{area}-{sn}".format(name=name, area=area, sn=oppo_sn)
                next_addition = "{name}-{area}-{sn}".format(name=next_name, area=area, sn=next_sn)

        elif name == '2':
            if area == 'A':
                oppo_addition = '2-B-1'
            else:
                oppo_addition = '2-A-1'

            next_addition = '1--1'

        if oppo_addition and next_addition:
            oppo_competition_fixture = CompetitionFixture.query. \
                filter(CompetitionFixture.competition_id == competition_fixture.competition_id,
                       CompetitionFixture.addition == oppo_addition, CompetitionFixture.status == 1). \
                first()
            if oppo_competition_fixture:
                next_competition_fixture = CompetitionFixture()
                next_competition_fixture.competition_id = competition_fixture.competition_id
                next_competition_fixture.p1 = competition_fixture.p1 if competition_fixture.p1_score > competition_fixture.p2_score else competition_fixture.p2
                next_competition_fixture.p2 = oppo_competition_fixture.p1 if oppo_competition_fixture.p1_score > oppo_competition_fixture.p2_score else oppo_competition_fixture.p2
                next_competition_fixture.stage = competition_fixture.stage
                next_competition_fixture.round = competition_fixture.round
                next_competition_fixture.status = 0
                next_competition_fixture.addition = next_addition
                self.save(next_competition_fixture)

                if next_addition == '1--1':
                    next_competition_fixture_2 = CompetitionFixture()
                    next_competition_fixture_2.competition_id = competition_fixture.competition_id
                    next_competition_fixture_2.p1 = competition_fixture.p1 if competition_fixture.p1_score < competition_fixture.p2_score else competition_fixture.p2
                    next_competition_fixture_2.p2 = oppo_competition_fixture.p1 if oppo_competition_fixture.p1_score < oppo_competition_fixture.p2_score else oppo_competition_fixture.p2
                    next_competition_fixture_2.stage = competition_fixture.stage
                    next_competition_fixture_2.round = competition_fixture.round
                    next_competition_fixture_2.status = 0
                    next_competition_fixture_2.addition = '1--2'
                    self.save(next_competition_fixture_2)

    def _add_competition_prize(self, competition_fixture):
        addition = competition_fixture.addition
        if addition == '1--1':
            if competition_fixture.p1_score > competition_fixture.p2_score:
                first_prize_team, second_prize_team = competition_fixture.p1, competition_fixture.p2
            else:
                first_prize_team, second_prize_team = competition_fixture.p2, competition_fixture.p1
            db.session.add_all([CompetitionTeamPrize(competition_team_id=first_prize_team, prize='1'),
                                CompetitionTeamPrize(competition_team_id=second_prize_team, prize='2')])
        elif addition == '1--2':
            third_prize_team = competition_fixture.p1 if competition_fixture.p1_score > competition_fixture.p2_score else competition_fixture.p2
            db.session.add(CompetitionTeamPrize(competition_team_id=third_prize_team, prize='3'))

    def find_by_competition_and_stage(self, competition_id, stage):
        fixtures = CompetitionFixture.query.filter(CompetitionFixture.competition_id == competition_id,
                                                   CompetitionFixture.stage == stage).order_by(CompetitionFixture.date_started.desc()).all()
        return fixtures


class MatchGoalService(BaseService):
    __model__ = MatchGoal

    def add_match_goal(self, account_id, **kwargs):
        competition_fixture_id = int(kwargs.get('competition_fixture_id'))
        competition_fixture = _check(account_id, competition_fixture_id, required_competition_manager_only=False, check_status=False)
        team_id = int(kwargs.get('team_id'))
        c_team = CompetitionTeam.query.filter(CompetitionTeam.team_id == team_id).first()

        scorer_account_id = int(kwargs.get('scorer_id'))
        assistant_account_id = int(kwargs.get('assistant_id')) if kwargs.get('assistant_id', None) else None

        scorer_athlete = Athlete.query. \
            filter(Athlete.account_id == scorer_account_id, Athlete.athletic_item_id == competition_fixture.competition.athletic_item_id).first()

        if assistant_account_id:
            assistant_athlete = Athlete.query. \
                filter(Athlete.account_id == assistant_account_id, Athlete.athletic_item_id == competition_fixture.competition.athletic_item_id).first()
        else:
            assistant_athlete = None

        time_scored = datetime.time(*map(int, kwargs.get('time_scored').split(':')))
        goal_type = int(kwargs.get('type'))

        match_goal = MatchGoal(fixture_id=competition_fixture_id, c_team_id=c_team.id,
                               scorer_id=scorer_athlete.id, assistant_id=assistant_athlete.id if assistant_athlete else None, time_scored=time_scored,
                               type=goal_type)

        return self.save(match_goal)

    def delete_match_goal(self, account_id, competition_fixture_id, match_goal_id):
        _check(account_id, competition_fixture_id, required_competition_manager_only=False, check_status=False)
        match_goal = MatchGoal.query.get(match_goal_id)
        if match_goal is None:
            raise AppError(error_code=errors.match_goal_id_noexistent)
        self.delete(match_goal)


class MatchSectionService(BaseService):
    __model__ = MatchSection

    def add_match_section(self, account_id, **kwargs):
        competition_fixture_id = kwargs.get('competition_fixture_id')
        _check(account_id, competition_fixture_id, required_competition_manager_only=False, check_status=False)

        sn = int(kwargs.get('sn'))
        p1_goals = int(kwargs.get('p1_goals'))
        p2_goals = int(kwargs.get('p2_goals'))
        match_section = MatchSection(fixture_id=competition_fixture_id, sn=sn, p1_goals=p1_goals, p2_goals=p2_goals)
        return self.save(match_section)

    def delete_match_section(self, account_id, competition_fixture_id, match_section_id):
        _check(account_id, competition_fixture_id, required_competition_manager_only=False, check_status=False)
        match_section = MatchSection.query.get(match_section_id)
        if match_section is None:
            raise AppError(error_code=errors.match_section_id_noexistent)
        self.delete(match_section)


class MatchHighlightService(BaseService):
    __model__ = MatchHighlight

    def add_match_highlight(self, account_id, **kwargs):
        competition_fixture_id = int(kwargs.get('competition_fixture_id'))
        competition_fixture = CompetitionFixture.query.get(competition_fixture_id)
        uuid_hex = uuid.uuid1().hex
        c_teams_ids = []
        if 'team_id' in kwargs:
            team_id = int(kwargs.get('team_id'))
            c_team = CompetitionTeam.query.filter(CompetitionTeam.team_id == team_id).first()
            if c_team:
                c_teams_ids.append(c_team.id)
        else:
            c_teams_ids.append(competition_fixture.p1)
            c_teams_ids.append(competition_fixture.p2)

        date_recorded = datetime.datetime.strptime(kwargs.get('date_recorded'), '%Y-%m-%d') if kwargs.get('date_recorded') else datetime.date.today()
        details = kwargs.get('details', {})
        match_highlights = []
        for c_team_id in c_teams_ids:
            match_highlights.append(MatchHighlight(fixture_id=competition_fixture_id, c_team_id=c_team_id, creator_id=account_id,
                                                   date_recorded=date_recorded, details=details, uid=uuid_hex))

        db.session.add_all(match_highlights)

        def do_after_commit():
            tasks.thumbnail_highlight_with_width.apply_async((uuid_hex, 200))

        after_commit(do_after_commit)

    def delete_match_highlight(self, account_id, match_highlight_id):
        match_highlight = MatchHighlight.query.get(match_highlight_id)
        if match_highlight is None:
            raise AppError(error_code=errors.match_highlight_id_noexistent)
        if match_highlight.creator_id != account_id:
            raise AppError(error_code=errors.operation_unauthorized)

        match_highlights = MatchHighlight.query.filter(MatchHighlight.uid == match_highlight.uid).all()
        for _match_highlight in match_highlights:
            db.session.delete(_match_highlight)

    def set_match_highlight_status(self, match_highlight_id, status):
        match_highlight = MatchHighlight.query.get(match_highlight_id)
        match_highlights = MatchHighlight.query.filter(MatchHighlight.uid == match_highlight.uid).all()
        for _match_highlight in match_highlights:
            _match_highlight.status = status
            db.session.add(_match_highlight)

    def paginate_highlight_by_account(self, account_id, offset=0, limit=10):
        athlete_model = get_model('Athlete')
        team_member_model = get_model('TeamMember')
        return db.session.query(MatchHighlight). \
            select_from(athlete_model). \
            join(team_member_model, athlete_model.id == team_member_model.athlete_id). \
            join(CompetitionTeam, CompetitionTeam.team_id == team_member_model.team_id). \
            join(MatchHighlight,
                 db.and_(MatchHighlight.c_team_id == CompetitionTeam.id,
                         MatchHighlight.status == 1)). \
            filter(athlete_model.account_id == account_id).\
            order_by(MatchHighlight.date_recorded.desc()).offset(offset).limit(limit). \
            all()

    def paginate_highlight_by_athlete(self, athlete_id, offset=0, limit=10):
        athlete_model = get_model('Athlete')
        team_member_model = get_model('TeamMember')
        return db.session.query(MatchHighlight). \
            select_from(athlete_model). \
            join(team_member_model, athlete_model.id == team_member_model.athlete_id). \
            join(CompetitionTeam, CompetitionTeam.team_id == team_member_model.team_id). \
            join(MatchHighlight,
                 db.and_(MatchHighlight.c_team_id == CompetitionTeam.id,
                         MatchHighlight.status == 1)). \
            filter(athlete_model.id == athlete_id).\
            order_by(MatchHighlight.date_recorded.desc()).offset(offset).limit(limit). \
            all()

    def paginate_highlight_by_team(self, team_id, offset=0, limit=10):
        return db.session.query(MatchHighlight). \
            select_from(MatchHighlight). \
            join(CompetitionTeam,
                 db.and_(MatchHighlight.c_team_id == CompetitionTeam.id,
                         MatchHighlight.status == 1,
                         CompetitionTeam.team_id == team_id)). \
            order_by(MatchHighlight.date_recorded.desc()).offset(offset).limit(limit).all()

    def paginate_highlight_by_competition(self, competition_id, offset=0, limit=10):
        subquery = MatchHighlight.query.with_entities(db.func.max(MatchHighlight.id).label('id')).group_by(MatchHighlight.uid).subquery()
        return db.session.query(MatchHighlight). \
            select_from(MatchHighlight). \
            join(CompetitionFixture,
                 db.and_(MatchHighlight.fixture_id == CompetitionFixture.id,
                         MatchHighlight.status == 1,
                         CompetitionFixture.competition_id == competition_id)). \
            join(subquery, MatchHighlight.id == subquery.c.id). \
            order_by(MatchHighlight.date_recorded.desc()).offset(offset).limit(limit).all()

    def paginate_highlight_by_competition_fixture(self, competition_fixture_id, offset=0, limit=10):
        subquery = MatchHighlight.query.with_entities(db.func.max(MatchHighlight.id).label('id')).group_by(MatchHighlight.uid).subquery()
        return db.session.query(MatchHighlight). \
            join(subquery, MatchHighlight.id == subquery.c.id). \
            filter(MatchHighlight.fixture_id == competition_fixture_id, MatchHighlight.status == 1). \
            order_by(MatchHighlight.date_recorded.desc()).offset(offset).limit(limit). \
            all()


def _check(account_id, competition_fixture_id, required_competition_manager_only=True, check_status=True):
    competition_fixture = CompetitionFixture.query.get(competition_fixture_id)

    if competition_fixture is None:
        raise AppError(error_code=errors.competition_fixture_id_noexistent)

    if required_competition_manager_only:
        if competition_fixture.competition.manager_id != account_id:
            raise AppError(error_code=errors.operation_unauthorized)
    else:
        if not (competition_fixture.competition.manager_id == account_id
                or competition_fixture.notary_id == account_id
                or competition_fixture.referee_id == account_id):
            raise AppError(error_code=errors.operation_unauthorized)

    if check_status and competition_fixture.status == 1:
        raise AppError(error_code=errors.competition_fixture_finished)

    return competition_fixture
