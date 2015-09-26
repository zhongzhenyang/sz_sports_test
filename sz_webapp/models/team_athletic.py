# coding:utf-8

import datetime
import sqlalchemy as sa
from ..core import db, Deleted, get_model, FromCache, regions, after_commit
from ..helpers.sa_helper import JsonSerializableMixin
from .. import settings


class Team(db.Model, Deleted, JsonSerializableMixin):
    __tablename__ = "teams"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(32))  # 球队名称
    _logo = db.Column('logo', db.String(256), nullable=True)  # 球队队标
    abbr_name = db.Column(db.Unicode(20), nullable=True)  # 简称
    date_created = db.Column(db.Date(), default=datetime.date.today)  # 成立时间
    loc_state = db.Column(db.Unicode(20), nullable=True)  # 省
    loc_city = db.Column(db.Unicode(20), nullable=True)  # 市
    loc_county = db.Column(db.Unicode(20), nullable=True)  # 区县
    home_site = db.Column(db.Unicode(32), nullable=True)  # 主场
    athletic_item_id = db.Column(db.Integer(), db.ForeignKey('athletic_items.id', ondelete='cascade'))  # 项目
    creator_id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete='cascade'))
    status = db.Column(db.SmallInteger(), default=1)  # 1:生效; -1:解散
    type = db.Column(db.SmallInteger())  # 0: 个人作为一支球队(在关注某些运动项目时自动创建); 1:多人组成的队伍(手动创建)
    contact_me = db.Column(db.Unicode(256), nullable=True)
    _uniform = db.Column('uniform', db.String(256), nullable=True)  # 球队队服
    _members = db.relationship('TeamMember', lazy='dynamic')
    _competings = db.relationship('CompetitionTeam', lazy='dynamic')

    def __json__(self, include_keys=[], exclude_keys=[]):
        return super(Team, self).__json__(include_keys=include_keys + ['logo', 'uniform'], exclude_keys=exclude_keys)

    @property
    def logo(self):
        if self._logo:
            return self._logo
        else:
            return settings.team_default_logo

    @logo.setter
    def logo(self, logo_image):
        self._logo = logo_image

    @property
    def uniform(self):
        if self._uniform:
            return self._uniform
        else:
            return settings.team_default_uniform

    @uniform.setter
    def uniform(self, uniform_image):
        self._uniform = uniform_image

    @property
    def creator(self):
        account_model = get_model('Account')
        return db.session.query(account_model). \
            options(FromCache('model', 'account:%d' % self.creator_id)). \
            filter_by(id=self.creator_id). \
            first()

    @property
    def athletic_item(self):
        athletic_item_model = get_model('AthleticItem')
        return db.session.query(athletic_item_model). \
            options(FromCache('model', 'athletic_item:%d' % self.athletic_item_id)). \
            filter_by(id=self.athletic_item_id). \
            first()

    @property
    def active_members(self):
        team_member_model = get_model('TeamMember')
        return db.session.query(team_member_model). \
            options(FromCache('model', 'team:%d:active_members' % self.id)). \
            filter_by(team_id=self.id, status=1). \
            all()

    @property
    def competition_prizes(self):
        """
            用户获得的奖牌
        """
        competition_team_prize_model = get_model('CompetitionTeamPrize')
        competition_team_model = get_model('CompetitionTeam')
        competition_model = get_model('Competition')
        return db.session.query(competition_team_prize_model). \
            options(FromCache('model', 'team:%d:prizes' % self.id)). \
            select_from(Team). \
            join(competition_team_model,
                 sa.and_(competition_team_model.team_id == Team.id,
                         Team.id == self.id)). \
            join(competition_team_prize_model,
                 competition_team_prize_model.competition_team_id == competition_team_model.id). \
            join(competition_model,
                 sa.and_(
                     competition_model.id == competition_team_model.competition_id,
                     competition_model.c_type == 2)). \
            order_by(competition_model.date_published.desc()). \
            all()

    # 球队最近的参加的竞赛
    @property
    def recent_competitions(self):
        competition_team_model = get_model('CompetitionTeam')
        competition_model = get_model('Competition')
        return db.session.query(competition_team_model). \
            options(FromCache('model', 'team:%d:recent_competitions' % self.id)). \
            join(competition_model,
                 sa.and_(competition_model.id == competition_team_model.competition_id,
                         competition_model.c_type != 0)). \
            filter(competition_team_model.team_id == self.id). \
            order_by(competition_model.date_started.desc()).limit(5).all()

    # 球队最近的赛程
    @property
    def recent_fixture(self):
        competition_team_model = get_model('CompetitionTeam')
        competition_fixture_model = get_model('CompetitionFixture')
        competition_model = get_model('Competition')
        return db.session.query(competition_fixture_model). \
            options(FromCache('model', 'team:%d:recent_fixtures' % self.id)). \
            select_from(competition_team_model). \
            join(competition_model, competition_model.id == competition_team_model.competition_id). \
            join(competition_fixture_model,
                 sa.and_(competition_team_model.team_id == self.id,
                         sa.or_(competition_fixture_model.p1 == competition_team_model.id,
                                competition_fixture_model.p2 == competition_team_model.id))). \
            order_by(competition_fixture_model.date_started.desc()).limit(5).all()

    @property
    def recent_highlights(self):
        competition_team_model = get_model('CompetitionTeam')
        match_highlight_model = get_model('MatchHighlight')
        return db.session.query(match_highlight_model). \
            options(FromCache('model', 'team:%d:recent_highlights' % self.id)). \
            select_from(match_highlight_model). \
            join(competition_team_model,
                 sa.and_(match_highlight_model.c_team_id == competition_team_model.id,
                         match_highlight_model.status == 1,
                         competition_team_model.team_id == self.id)). \
            order_by(match_highlight_model.date_recorded.desc()).limit(10). \
            all()

    @classmethod
    def from_cache_by_id(cls, team_id):
        return Team.query. \
            options(FromCache('model', 'team:%d' % team_id)). \
            filter(Team.id == team_id).first()

    def __eq__(self, other):
        if isinstance(other, Team) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<AthleticTeam(id=%s)>" % self.id


@sa.event.listens_for(Team, 'after_insert')
@sa.event.listens_for(Team, 'after_update')
@sa.event.listens_for(Team, 'before_delete')
def on_team(mapper, connection, team):
    def do_after_commit():
        regions['model'].delete('team:%d' % team.id)

    after_commit(do_after_commit)
