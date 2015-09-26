# coding:utf-8

import sqlalchemy as sa
from ..core import db, get_model, FromCache, regions, after_commit
from ..helpers.sa_helper import JsonSerializableMixin


class CompetitionTeam(db.Model, JsonSerializableMixin):
    __tablename__ = "competition_teams"

    id = db.Column(db.Integer(), primary_key=True)
    competition_id = db.Column(db.Integer(), db.ForeignKey('competitions.id'))
    team_id = db.Column(db.Integer(), db.ForeignKey('teams.id'))
    ranks = db.relationship('CompetitionTeamRank', lazy='dynamic')
    current_rank = None

    __table_args__ = (
        db.UniqueConstraint('competition_id', 'team_id'),
    )

    @property
    def latest_rank(self):
        rank = db.session.query(CompetitionTeamRank). \
            options(FromCache('model', 'competition_team:%d:latest_rank')). \
            filter(CompetitionTeamRank.c_team_id == self.id). \
            order_by(CompetitionTeamRank.stage.desc()).first()
        return rank

    @property
    def prize(self):
        competition_team_prize_model = get_model('CompetitionTeamPrize')
        competition_team_prize = db.session.query(competition_team_prize_model). \
            options(FromCache('model', 'competition_team:%d:prize' % self.id)). \
            filter_by(competition_team_id=self.id).first()
        if competition_team_prize:
            return competition_team_prize.prize
        else:
            return None

    @property
    def competition_team_members(self):
        return db.session.query(CompetitionAthlete). \
            options(FromCache('model', 'competition_team:%d:members' % self.id)). \
            filter_by(competition_team_id=self.id).all()

    @property
    def competition_team_member_accounts(self):
        account_model = get_model('Account')
        team_member_model = get_model('TeamMember')
        athlete_model = get_model('Athlete')
        return db.session.query(account_model). \
            select_from(CompetitionTeam). \
            join(CompetitionAthlete, sa.and_(CompetitionAthlete.competition_team_id == CompetitionTeam.id, CompetitionTeam.id == self.id)). \
            join(team_member_model, team_member_model.team_id == CompetitionTeam.team_id). \
            join(athlete_model, team_member_model.athlete_id == athlete_model.id). \
            join(account_model, athlete_model.account_id == account_model.id).all()

    @property
    def team(self):
        team_model = get_model('Team')
        return db.session.query(team_model). \
            options(FromCache('model', 'team:%d' % self.team_id)). \
            filter_by(id=self.team_id).first()

    @property
    def competition(self):
        competition_model = get_model('Competition')
        return db.session.query(competition_model). \
            options(FromCache('model', 'competition:%d' % self.competition_id)). \
            filter_by(id=self.competition_id).first()

    @classmethod
    def from_cache_by_id(cls, competition_team_id):
        return CompetitionTeam.query. \
            options(FromCache('model', 'competition_team:%d' % competition_team_id)). \
            filter(CompetitionTeam.id == competition_team_id). \
            first()

    def __eq__(self, other):
        if isinstance(other, CompetitionTeam) and \
                        self.competition_id == other.competition_id and \
                        self.team_id == other.team_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.competition_id) + hash(self.team_id) * 13

    def __repr__(self):
        return u"<CompetitionTeam(competition_id=%s,team_id=%s)>" % (self.competition_id, self.team_id)


class CompetitionAthlete(db.Model):
    __tablename__ = 'competition_athletes'

    competition_team_id = db.Column(db.Integer(), db.ForeignKey('competition_teams.id'), primary_key=True)
    team_member_id = db.Column(db.Integer(), db.ForeignKey('team_members.id'), primary_key=True)

    @property
    def team_member(self):
        team_member_model = get_model('TeamMember')
        return db.session.query(team_member_model). \
            options(FromCache('model', 'team_member:%d' % self.team_member_id)). \
            filter_by(id=self.team_member_id).first()

    def __eq__(self, other):
        if isinstance(other, CompetitionAthlete) and \
                        self.competition_team_id == other.competition_team_id and \
                        self.team_member_id == other.team_member_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.competition_team_id) + hash(self.team_member_id) * 13

    def __repr__(self):
        return u"<CompetitionTeam(competition_team_id=%s,team_member_id=%s)>" % (
            self.competition_team_id, self.team_member_id)


class CompetitionTeamRank(db.Model, JsonSerializableMixin):
    __tablename__ = 'competition_team_ranks'

    id = db.Column(db.Integer(), primary_key=True)
    c_team_id = db.Column(db.Integer(), db.ForeignKey('competition_teams.id'))
    stage = db.Column(db.SmallInteger())
    pts = db.Column(db.Integer(), default=0)
    group = db.Column(db.String(16), name='c_group', nullable=True)

    __table_args__ = (
        db.UniqueConstraint('c_team_id', 'stage'),
    )

    @property
    def addition(self):
        return db.session.query(CompetitionTeamRankAddition). \
            options(FromCache('model', 'team_rank:%d:addition' % self.id)). \
            filter_by(rank_id=self.id).first()

    def __eq__(self, other):
        if isinstance(other, CompetitionTeamRank) and self.c_team_id == other.c_team_id and \
                        self.stage == other.stage:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.c_team_id) + hash(self.stage) * 13

    def __repr__(self):
        return u"<CompetitionTeamRank(c_team_id=%s,stage=%s)>" % (self.c_team_id, self.stage)


class CompetitionTeamRankAddition(db.Model, JsonSerializableMixin):
    __tablename__ = "competition_team_rank_additions"

    rank_id = db.Column(db.Integer(), db.ForeignKey("competition_team_ranks.id", ondelete='cascade'), primary_key=True)
    played = db.Column(db.SmallInteger())
    won = db.Column(db.SmallInteger())
    drawn = db.Column(db.SmallInteger())
    lost = db.Column(db.SmallInteger())
    goals_for = db.Column(db.SmallInteger())
    goals_against = db.Column(db.SmallInteger())

    @classmethod
    def from_cache_by_id(cls, rank_id):
        return CompetitionTeamRankAddition.query. \
            options(FromCache('model', 'team_rank:%d:addition' % rank_id)). \
            filter(CompetitionTeamRankAddition.rank_id == rank_id).first()

    def __eq__(self, other):
        if isinstance(other, CompetitionTeamRankAddition) and self.rank_id == other.rank_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.rank_id)

    def __repr__(self):
        return u"<CompetitionTeamRankAddition(rank_id=%s)>" % self.rank_id


@sa.event.listens_for(CompetitionTeam, 'after_insert')
@sa.event.listens_for(CompetitionTeam, 'after_update')
def on_competition_team_insert_or_update(mapper, connection, competition_team):
    def do_after_commit():
        invalidate_on_competition_team(competition_team)

    after_commit(do_after_commit)


@sa.event.listens_for(CompetitionTeam, 'before_delete')
def on_competition_team_delete(mapper, connection, competition_team):
    invalidate_on_competition_team(competition_team)


def invalidate_on_competition_team(competition_team):
    regions['model'].delete('competition_team:%d' % competition_team.id)
    regions['model'].delete('competition:%d:registered_teams' % competition_team.competition_id)

    if competition_team.competition.c_type != 0:
        regions['model'].delete('team:%d:recent_competitions' % competition_team.team_id)
        athlete_model = get_model('Athlete')
        team_member_model = get_model('TeamMember')
        account_athlete_id_pairs = db.session.query(athlete_model.id, athlete_model.account_id). \
            join(team_member_model,
                 team_member_model.athlete_id == athlete_model.id). \
            join(CompetitionAthlete,
                 CompetitionAthlete.team_member_id == team_member_model.id). \
            filter(CompetitionAthlete.competition_team_id == competition_team.id).all()
        account_recent_competitions_keys = ['account:%d:recent_competitions' % account_id for (athlete_id, account_id) in account_athlete_id_pairs]
        if account_recent_competitions_keys:
            regions['model'].delete_multi(account_recent_competitions_keys)

        athlete_recent_competitions_keys = ['athlete:%d:recent_competitions' % athlete_id for (athlete_id, account_id) in account_athlete_id_pairs]
        if athlete_recent_competitions_keys:
            regions['model'].delete_multi(athlete_recent_competitions_keys)

    if competition_team.competition.c_type == 2:
        competition_prize_model = get_model("CompetitionTeamPrize")
        competition_prizes = competition_prize_model.query. \
            filter(competition_prize_model.competition_team_id == competition_team.id).all()
        for c_prize in competition_prizes:
            db.session.delete(c_prize)


@sa.event.listens_for(CompetitionAthlete, 'after_insert')
@sa.event.listens_for(CompetitionAthlete, 'before_delete')
def on_competition_athlete(mapper, connection, competition_athlete):
    def do_after_commit():
        regions['model'].delete('competition_team:%d:members' % competition_athlete.competition_team_id)

    after_commit(do_after_commit)


@sa.event.listens_for(CompetitionTeamRank, 'after_insert')
@sa.event.listens_for(CompetitionTeamRank, 'after_update')
@sa.event.listens_for(CompetitionTeamRank, 'before_delete')
def on_competition_team_rank(mapper, connection, competition_team_rank):
    def do_after_commit():
        regions['model'].delete('competition_team:%d:latest_rank' % competition_team_rank.c_team_id)
        competition_id = db.session.query(CompetitionTeam.competition_id). \
            filter(CompetitionTeam.id == competition_team_rank.c_team_id).scalar()
        regions['model'].delete('competition:%d[stage:%d]:competings' % (competition_id, competition_team_rank.stage))

    after_commit(do_after_commit)


@sa.event.listens_for(CompetitionTeamRankAddition, 'after_insert')
@sa.event.listens_for(CompetitionTeamRankAddition, 'after_update')
@sa.event.listens_for(CompetitionTeamRankAddition, 'before_delete')
def on_competition_team_rank_addition(mapper, connection, competition_team_rank_addition):
    def do_after_commit():
        regions['model'].delete('team_rank:%d:addition' % competition_team_rank_addition.rank_id)

    after_commit(do_after_commit)
