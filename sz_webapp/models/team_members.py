# coding:utf-8


import datetime
import sqlalchemy as sa
from ..core import db, get_model, FromCache, regions, after_commit
from ..helpers.sa_helper import JsonSerializableMixin


class TeamMember(db.Model, JsonSerializableMixin):
    __tablename__ = "team_members"

    id = db.Column(db.Integer(), primary_key=True)
    team_id = db.Column(db.Integer(), db.ForeignKey('teams.id'))
    athlete_id = db.Column(db.Integer(), db.ForeignKey('athletes.id'))
    status = db.Column(db.SmallInteger(), default=0)  # -1:离开; 1:生效;
    date_joined = db.Column(db.Date(), default=datetime.date.today)
    date_left = db.Column(db.Date(), nullable=True)

    @property
    def team(self):
        team_model = get_model('Team')
        return db.session.query(team_model).options(FromCache('model', 'team:%d' % self.team_id)) \
            .filter_by(id=self.team_id).first()

    @property
    def athlete(self):
        athlete_model = get_model('Athlete')
        return db.session.query(athlete_model).options(FromCache('model', 'athlete:%d' % self.athlete_id)). \
            filter_by(id=self.athlete_id).first()

    @classmethod
    def from_cache_by_id(cls, team_member_id):
        return TeamMember.query. \
            options(FromCache('model', 'team_member:%d' % team_member_id)). \
            filter(TeamMember.id == team_member_id).first()

    def __eq__(self, other):
        if isinstance(other, TeamMember) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<TeamMember(id=%s)>" % self.id


@sa.event.listens_for(TeamMember, 'after_insert')
@sa.event.listens_for(TeamMember, 'after_update')
@sa.event.listens_for(TeamMember, 'before_delete')
def on_team_member(mapper, connection, team_member):
    def do_after_commit():
        regions['model'].delete_multi(
            [
                'team:%d:active_members' % team_member.team_id,
                'athlete:%d:current_team' % team_member.athlete_id,
                'athlete:%d:recent_teams' % team_member.athlete_id,
                'team_member:%d' % team_member.id,

            ]
        )

    after_commit(do_after_commit)