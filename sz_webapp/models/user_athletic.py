# coding:utf-8

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from ..core import db, get_model, FromCache, regions, after_commit
from ..helpers.sa_helper import JsonSerializableMixin


class Athlete(db.Model, JsonSerializableMixin):
    __tablename__ = "athletes"

    id = db.Column(db.Integer(), primary_key=True)
    account_id = db.Column(db.ForeignKey("accounts.id", ondelete="cascade"))
    athletic_item_id = db.Column(db.Integer(), db.ForeignKey("athletic_items.id", ondelete="cascade"))
    status = db.Column(db.SmallInteger(), default=1)  # 0:取消关注,1:关注
    info = db.Column(JSON())
    _members = db.relationship('TeamMember', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint("account_id", "athletic_item_id"),
    )

    @property
    def account(self):
        account_model = get_model('Account')
        return db.session.query(account_model).options(FromCache('model', 'account:%d' % self.account_id)). \
            filter_by(id=self.account_id).first()

    @property
    def athletic_item(self):
        athletic_item_model = get_model('AthleticItem')
        return db.session.query(athletic_item_model). \
            options(FromCache('model', 'athletic_item:%d' % self.athletic_item_id)). \
            filter_by(id=self.athletic_item_id).first()

    @property
    def current_team(self):
        team_member_model = get_model('TeamMember')
        team_model = get_model('Team')
        return db.session.query(team_member_model).\
            join(team_model, sa.and_(team_model.id == team_member_model.team_id, team_model.type == 1, team_model.status == 1)). \
            options(FromCache('model', 'athlete:%d:current_team' % self.id)). \
            filter(team_member_model.athlete_id == self.id, team_member_model.status==1).\
            order_by(team_member_model.date_joined.desc()).first()

    @property
    def recent_teams(self):
        team_member_model = get_model('TeamMember')
        return db.session.query(team_member_model). \
            options(FromCache('model', 'athlete:%d:recent_teams' % self.id)). \
            filter_by(athlete_id=self.id).order_by(sa.desc('date_joined')).limit(5).all()

    @property
    def competition_prizes(self):
        """
            用户获得的奖牌
        """
        competition_team_prize_model = get_model('CompetitionTeamPrize')
        team_member_model = get_model('TeamMember')
        competition_athlete_model = get_model('CompetitionAthlete')
        competition_team_model = get_model('CompetitionTeam')
        competition_model = get_model('Competition')
        return db.session.query(competition_team_prize_model). \
            options(FromCache('model', 'athlete:%d:prizes' % self.id)). \
            select_from(Athlete). \
            join(team_member_model,
                 sa.and_(Athlete.id == team_member_model.athlete_id,
                         Athlete.id == self.id)). \
            join(competition_athlete_model,
                 team_member_model.id == competition_athlete_model.team_member_id). \
            join(competition_team_model,
                 competition_team_model.id == competition_athlete_model.competition_team_id). \
            join(competition_team_prize_model,
                 competition_team_prize_model.competition_team_id == competition_team_model.id). \
            join(competition_model,
                 sa.and_(
                     competition_model.id == competition_team_model.competition_id,
                     competition_model.c_type == 2)). \
            order_by(competition_model.date_published.desc()). \
            all()

    @property
    def recent_competitions(self):
        team_member_model = get_model('TeamMember')
        competition_team_model = get_model('CompetitionTeam')
        competition_athlete_model = get_model('CompetitionAthlete')
        competition_model = get_model('Competition')
        return db.session.query(competition_team_model). \
            options(FromCache('model', 'athlete:%d:recent_competitions' % self.id)). \
            join(competition_athlete_model,
                 competition_athlete_model.competition_team_id == competition_team_model.id). \
            join(team_member_model,
                 sa.and_(
                     team_member_model.team_id == competition_team_model.team_id,
                     team_member_model.id == competition_athlete_model.team_member_id,
                     team_member_model.athlete_id == self.id)). \
            join(competition_model,
                 sa.and_(
                     competition_model.id == competition_team_model.competition_id,
                     competition_model.c_type != 0)). \
            order_by(competition_model.date_started.desc()).limit(5). \
            all()

    @property
    def recent_fixture(self):
        team_member_model = get_model('TeamMember')
        competition_team_model = get_model('CompetitionTeam')
        competition_fixture_model = get_model('CompetitionFixture')
        competition_athlete_model = get_model('CompetitionAthlete')
        competition_model = get_model('Competition')
        return db.session.query(competition_fixture_model). \
            options(FromCache('model', 'athlete:%d:recent_fixtures' % self.id)). \
            select_from(competition_team_model). \
            join(competition_athlete_model,
                 competition_athlete_model.competition_team_id == competition_team_model.id). \
            join(team_member_model,
                 sa.and_(
                     team_member_model.team_id == competition_team_model.team_id,
                     team_member_model.id == competition_athlete_model.team_member_id,
                     team_member_model.athlete_id == self.id)). \
            join(competition_model, competition_model.id == competition_team_model.competition_id). \
            join(competition_fixture_model,
                 sa.or_(competition_fixture_model.p1 == competition_team_model.id,
                        competition_fixture_model.p2 == competition_team_model.id)). \
            order_by(competition_fixture_model.date_started.desc()).limit(5).all()

    @property
    def recent_highlights(self):
        team_member_model = get_model('TeamMember')
        competition_athlete_model = get_model('CompetitionAthlete')
        competition_team_model = get_model('CompetitionTeam')
        match_highlight_model = get_model('MatchHighlight')

        return db.session.query(match_highlight_model). \
            options(FromCache('model', 'athlete:%d:recent_highlights' % self.id)). \
            select_from(Athlete). \
            join(team_member_model,
                 sa.and_(Athlete.id == team_member_model.athlete_id,
                         Athlete.id == self.id)). \
            join(competition_team_model,
                 competition_team_model.team_id == team_member_model.team_id). \
            join(competition_athlete_model,
                 sa.and_(competition_athlete_model.competition_team_id == competition_team_model.id,
                         competition_athlete_model.team_member_id == team_member_model.id)). \
            join(match_highlight_model,
                 sa.and_(match_highlight_model.c_team_id == competition_athlete_model.competition_team_id,
                         match_highlight_model.status == 1)). \
            order_by(match_highlight_model.date_recorded.desc()).limit(10). \
            all()

    @classmethod
    def from_cache_by_id(cls, athlete_id):
        return Athlete.query. \
            options(FromCache('model', 'athlete:%d' % athlete_id)). \
            filter(Athlete.id == athlete_id).first()

    @classmethod
    def from_cache_by_account_id_and_athletic_item_id(cls, account_id, athletic_item_id):
        return Athlete.query. \
            options(FromCache('model', 'athlete:%d-%d' % (account_id, athletic_item_id))). \
            filter(Athlete.account_id == account_id, Athlete.athletic_item_id == athletic_item_id).first()

    def __eq__(self, other):
        if isinstance(other, Athlete) and other.account_id == self.account_id \
                and other.athletic_item_id == self.athletic_item_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.account_id) + hash(self.athletic_item_id) * 13

    def __repr__(self):
        return u"<Athlete(user_id=%s,athletic_item_id=%s)>" % (self.user_id, self.athletic_item_id)


@sa.event.listens_for(Athlete, 'after_insert')
@sa.event.listens_for(Athlete, 'after_update')
@sa.event.listens_for(Athlete, 'before_delete')
def on_athlete(mapper, connection, athlete):
    def do_after_commit():
        regions['model'].delete_multi(
            [
                'account:%d:active_athletes' % athlete.account_id,
                'athlete:%d' % athlete.id,
                'athlete:%d-%d' % (athlete.account_id, athlete.athletic_item_id)
            ]
        )

    after_commit(do_after_commit)

