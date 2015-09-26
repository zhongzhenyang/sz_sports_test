# coding:utf-8

import datetime
import sqlalchemy as sa
from sqlalchemy.dialects.postgres import JSON
from ..core import db, get_model, FromCache, regions, after_commit
from ..helpers.sa_helper import UTCDateTime, JsonSerializableMixin


class CompetitionFixture(db.Model, JsonSerializableMixin):
    __tablename__ = "competition_fixtures"

    id = db.Column(db.Integer(), primary_key=True)
    competition_id = db.Column(db.Integer(), db.ForeignKey('competitions.id', ondelete='cascade'))
    p1 = db.Column(db.Integer(), db.ForeignKey('competition_teams.id', ondelete='cascade'))
    p2 = db.Column(db.Integer(), db.ForeignKey('competition_teams.id', ondelete='cascade'))
    date_started = db.Column(db.Date(), nullable=True)
    notary_id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete='cascade'), nullable=True)
    referee_id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete='cascade'), nullable=True)
    site = db.Column(db.Unicode(128), nullable=True)  # 比赛场地
    stage = db.Column(db.SmallInteger(), nullable=True)
    round = db.Column(db.SmallInteger(), nullable=True)
    sn = db.Column(db.SmallInteger(), nullable=True)
    p1_score = db.Column(db.SmallInteger(), nullable=True)
    p2_score = db.Column(db.SmallInteger(), nullable=True)
    status = db.Column(db.SmallInteger(), default=0)  # 0:pending 1:finished
    addition = db.Column(db.String(64), nullable=True)  # 用于前端界面元素的显示

    @property
    def competition(self):
        competition_model = get_model('Competition')
        return db.session.query(competition_model). \
            options(FromCache('model', 'competition:%d' % self.competition_id)). \
            filter_by(id=self.competition_id).first()

    @property
    def p1_competition_team(self):
        competition_team_model = get_model('CompetitionTeam')
        return db.session.query(competition_team_model). \
            options(FromCache('model', 'competition_team:%d' % self.p1)). \
            filter_by(id=self.p1).first()

    @property
    def p2_competition_team(self):
        competition_team_model = get_model('CompetitionTeam')
        return db.session.query(competition_team_model). \
            options(FromCache('model', 'competition_team:%d' % self.p2)). \
            filter_by(id=self.p2).first()

    @property
    def notary(self):
        if self.notary_id:
            account_model = get_model('Account')
            return db.session.query(account_model). \
                options(FromCache('model', 'account:%d' % self.notary_id)). \
                filter_by(id=self.notary_id).first()
        else:
            return None

    @property
    def referee(self):
        if self.referee_id:
            account_model = get_model('Account')
            return db.session.query(account_model). \
                options(FromCache('model', 'account:%d' % self.referee_id)). \
                filter_by(id=self.referee_id).first()
        else:
            return None

    @property
    def goals(self):
        return db.session.query(MatchGoal). \
            options(FromCache('model', 'competition_fixture:%d:goals' % self.id)). \
            filter_by(fixture_id=self.id).order_by(MatchGoal.time_scored).all()

    @property
    def highlights(self):
        subquery = MatchHighlight.query.with_entities(db.func.max(MatchHighlight.id).label('id')).group_by(MatchHighlight.uid).subquery()
        return db.session.query(MatchHighlight). \
            options(FromCache('model', 'competition_fixture:%d:highlights' % self.id)). \
            join(subquery, MatchHighlight.id == subquery.c.id) .\
            filter(MatchHighlight.fixture_id == self.id, MatchHighlight.status == 1).\
            order_by(MatchHighlight.date_recorded.desc()).all()

    @property
    def sections(self):
        return db.session.query(MatchSection). \
            options(FromCache('model', 'competition_fixture:%d:sections' % self.id)). \
            filter_by(fixture_id=self.id).order_by(MatchSection.sn).all()

    @classmethod
    def from_cache_by_id(cls, competition_fixture_id):
        return CompetitionFixture.query. \
            options(FromCache('model', 'competition_fixture:%d' % competition_fixture_id)). \
            filter(CompetitionFixture.id == competition_fixture_id).first()

    def __eq__(self, other):
        if isinstance(other, CompetitionFixture) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<CompetitionFixture(id=%s)>" % self.id


class MatchGoal(db.Model, JsonSerializableMixin):
    __tablename__ = "match_scores"

    id = db.Column(db.Integer(), primary_key=True)
    fixture_id = db.Column(db.Integer(), db.ForeignKey('competition_fixtures.id', ondelete='cascade'))
    c_team_id = db.Column(db.Integer(), db.ForeignKey('competition_teams.id', ondelete='cascade'))
    scorer_id = db.Column(db.Integer(), db.ForeignKey('athletes.id', ondelete='cascade'))
    assistant_id = db.Column(db.Integer(), db.ForeignKey('athletes.id', ondelete='cascade'), nullable=True)
    time_scored = db.Column(db.Time())
    type = db.Column(db.SmallInteger())  # 0:普通进球, 1:点球, 2:乌龙球

    @property
    def competition_team(self):
        competition_team_model = get_model('CompetitionTeam')
        return db.session.query(competition_team_model). \
            options(FromCache('model', 'competition_team:%d' % self.c_team_id)). \
            filter_by(id=self.c_team_id). \
            first()

    @property
    def scorer(self):
        athlete_model = get_model('Athlete')
        return db.session.query(athlete_model). \
            options(FromCache('model', 'athlete:%d' % self.scorer_id)). \
            filter_by(id=self.scorer_id). \
            first()

    @property
    def assistant(self):
        if self.assistant_id:
            athlete_model = get_model('Athlete')
            return db.session.query(athlete_model). \
                options(FromCache('model', 'athlete:%d' % self.assistant_id)). \
                filter_by(id=self.assistant_id). \
                first()
        else:
            return None

    def __eq__(self, other):
        if isinstance(other, MatchGoal) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<MatchScore(id=%s)>" % self.id


class MatchHighlight(db.Model, JsonSerializableMixin):
    __tablename__ = "match_highlights"

    id = db.Column(db.Integer(), primary_key=True)
    fixture_id = db.Column(db.Integer(), db.ForeignKey('competition_fixtures.id', ondelete='cascade'))
    c_team_id = db.Column(db.Integer(), db.ForeignKey('competition_teams.id', ondelete='cascade'), nullable=True)
    creator_id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete='cascade'))
    date_recorded = db.Column(db.Date(), default=datetime.date.today)
    status = db.Column(db.SmallInteger(), default=0)  # 0: pending, 1:pass, -1:discard, -2:thumbnail_finished
    uid = db.Column(db.String(32))
    details = db.Column(JSON())

    @property
    def competition_team(self):
        competition_team_model = get_model('CompetitionTeam')
        return db.session.query(competition_team_model). \
            options(FromCache('model', 'competition_team:%d' % self.c_team_id)). \
            filter_by(id=self.c_team_id). \
            first()

    def __eq__(self, other):
        if isinstance(other, MatchHighlight) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<MatchHiglight(id=%s)>" % self.id


class MatchSection(db.Model, JsonSerializableMixin):
    __tablename__ = "match_sections"

    id = db.Column(db.Integer(), primary_key=True)
    fixture_id = db.Column(db.Integer(), db.ForeignKey('competition_fixtures.id', ondelete='cascade'))
    sn = db.Column(db.SmallInteger(), default=1)
    p1_goals = db.Column(db.SmallInteger())
    p2_goals = db.Column(db.SmallInteger())

    def __eq__(self, other):
        if isinstance(other, MatchSection) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<MatchSection(id=%s)>" % self.id


@sa.event.listens_for(CompetitionFixture, 'after_insert')
@sa.event.listens_for(CompetitionFixture, 'after_update')
def on_competition_fixture_insert_or_update(mapper, connection, competition_fixture):
    def do_after_commit():
        invalidate_on_competition_fixture(competition_fixture)

    after_commit(do_after_commit)


@sa.event.listens_for(CompetitionFixture, 'before_delete')
def on_competition_fixture_delete(mapper, connection, competition_fixture):
    invalidate_on_competition_fixture(competition_fixture)


def invalidate_on_competition_fixture(competition_fixture):
    competition_team_model = get_model('CompetitionTeam')
    regions['model'].delete('competition_fixture:%d' % competition_fixture.id)
    team_ids = db.session.query(competition_team_model.team_id). \
        filter(competition_team_model.id.in_([competition_fixture.p1, competition_fixture.p2])). \
        all()
    team_ids = [team_id for (team_id,) in team_ids]
    regions['model'].delete_multi(['team:%d:recent_fixtures' % team_id for team_id in team_ids])

    athlete_model = get_model('Athlete')
    team_member_model = get_model('TeamMember')
    competition_athlete_model = get_model('CompetitionAthlete')
    account_athlete_id_pairs = db.session.query(athlete_model.id, athlete_model.account_id). \
        join(team_member_model,
             team_member_model.athlete_id == athlete_model.id). \
        join(competition_athlete_model,
             competition_athlete_model.team_member_id == team_member_model.id). \
        filter(team_member_model.team_id.in_(team_ids)). \
        all()
    account_recent_fixtures_keys = ['account:%d:recent_fixtures' % account_id for (athlete_id, account_id) in account_athlete_id_pairs]
    if account_recent_fixtures_keys:
        regions['model'].delete_multi(account_recent_fixtures_keys)

    athlete_recent_fixtures_keys = ['athlete:%d:recent_fixtures' % athlete_id for (athlete_id, account_id) in account_athlete_id_pairs]
    if athlete_recent_fixtures_keys:
        regions['model'].delete_multi(athlete_recent_fixtures_keys)


@sa.event.listens_for(MatchGoal, 'after_insert')
@sa.event.listens_for(MatchGoal, 'after_update')
@sa.event.listens_for(MatchGoal, 'before_delete')
def on_match_score(mapper, connection, match_score):
    def do_after_commit():
        regions['model'].delete('competition_fixture:%d:goals' % match_score.fixture_id)

    after_commit(do_after_commit)


@sa.event.listens_for(MatchHighlight, 'after_insert')
def on_match_highlight_insert(mapper, connection, match_highlight):
    def do_after_commit():
        invalidate_on_match_highlight(match_highlight)

    after_commit(do_after_commit)


@sa.event.listens_for(MatchHighlight, 'before_delete')
def on_match_highlight_delete(mapper, connection, match_highlight):
    invalidate_on_match_highlight(match_highlight)


def invalidate_on_match_highlight(match_highlight):
    if match_highlight.status == 1:
        competition_athlete_model = get_model('CompetitionAthlete')
        team_member_model = get_model('TeamMember')
        athlete_model = get_model('Athlete')
        competition_team_model = get_model('CompetitionTeam')
        account_athlete_id_pairs = db.session.query(athlete_model.id, athlete_model.account_id). \
            select_from(competition_team_model). \
            join(team_member_model,
                 team_member_model.team_id == competition_team_model.team_id). \
            join(competition_athlete_model,
                 sa.and_(team_member_model.id == competition_athlete_model.team_member_id,
                         competition_athlete_model.competition_team_id == match_highlight.c_team_id)). \
            join(athlete_model,
                 team_member_model.athlete_id == athlete_model.id). \
            all()
        regions['model'].delete('competition_fixture:%d:highlights' % match_highlight.fixture_id)
        regions['model'].delete('competition:%d:recent_highlights' % match_highlight.competition_team.competition_id)
        regions['model'].delete('team:%d:recent_highlights' % match_highlight.competition_team.team_id)

        account_recent_highlights_keys = ['account:%d:recent_highlights' % account_id for (athlete_id, account_id) in account_athlete_id_pairs]
        if account_recent_highlights_keys:
            regions['model'].delete_multi(account_recent_highlights_keys)

        athlete_recent_highlights_keys = ['athlete:%d:recent_highlights' % athlete_id for (athlete_id, account_id) in account_athlete_id_pairs]
        if athlete_recent_highlights_keys:
            regions['model'].delete_multi(athlete_recent_highlights_keys)


@sa.event.listens_for(MatchSection, 'after_insert')
@sa.event.listens_for(MatchSection, 'after_update')
@sa.event.listens_for(MatchSection, 'before_delete')
def on_match_section(mapper, connection, match_section):
    def do_after_commit():
        regions['model'].delete('competition_fixture:%d:sections' % match_section.fixture_id)

    after_commit(do_after_commit)