# coding:utf-8

import datetime
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from ..core import db, Deleted, get_model, FromCache, regions, after_commit
from ..helpers.sa_helper import JsonSerializableMixin, UTCDateTime
from ..helpers.datetime_helper import utc_now


class Competition(db.Model, Deleted, JsonSerializableMixin):
    __tablename__ = "competitions"

    id = db.Column(db.Integer(), primary_key=True)
    athletic_item_id = db.Column(db.Integer(), db.ForeignKey('athletic_items.id', ondelete='cascade'))  # 项目
    name = db.Column(db.Unicode(32))  # 赛事名称
    c_type = db.Column(db.SmallInteger())  # 赛事类型, 0:挑战赛; 1:活动; 2:联赛
    loc_state = db.Column(db.Unicode(20), nullable=True)  # 省
    loc_city = db.Column(db.Unicode(20), nullable=True)  # 市
    loc_county = db.Column(db.Unicode(20), nullable=True)  # 区县
    date_started = db.Column(db.Date())
    date_reg_end = db.Column(db.Date())  # 报名截止时间
    team_num = db.Column(db.Integer(), nullable=True)  # 球队名额
    host = db.Column(db.Unicode(64), nullable=True)  # 主办方
    organizer = db.Column(db.Unicode(64), nullable=True)  # 承办方
    sponsor = db.Column(db.Unicode(512), nullable=True)  # 赞助方
    site = db.Column(db.Unicode(128), nullable=True)  # 比赛场地
    logo = db.Column(db.String(256), nullable=True)  # 赛事Logo
    intro = db.Column(db.UnicodeText(), nullable=True)  # 详细介绍
    requirement = db.Column(db.UnicodeText(), nullable=True)  # 比赛要求
    date_published = db.Column(db.Date(), default=datetime.date.today)
    manager_id = db.Column(db.Integer(), db.ForeignKey('accounts.id'))
    status = db.Column(db.SmallInteger())  # 0:报名; 1: 进行中;2: 结束
    stage_num = db.Column(db.SmallInteger())  # 阶段数
    stage = db.Column(db.SmallInteger())  # 当前阶段
    options = db.Column(JSON())  # 竞赛设置
    contact_me = db.Column(db.Unicode(128), nullable=True)  # 联系方式
    _competings = db.relationship('CompetitionTeam', lazy='dynamic')
    _fixtures = db.relationship('CompetitionFixture', lazy='dynamic')

    @property
    def manager(self):
        account_model = get_model('Account')
        return db.session.query(account_model). \
            options(FromCache('model', 'account:%d' % self.manager_id)). \
            filter_by(id=self.manager_id).first()

    @property
    def athletic_item(self):
        athletic_item_model = get_model('AthleticItem')
        return db.session.query(athletic_item_model). \
            options(FromCache('model', 'athletic_item:%d' % self.athletic_item_id)). \
            filter_by(id=self.athletic_item_id).first()

    @property
    def in_league_apply(self):
        return 0 != db.session.query(LeagueApplyItem). \
            options(FromCache('model', 'competition:%d:apply_league' % self.id)). \
            with_entities(db.func.count('*')). \
            filter(LeagueApplyItem.competition_id == self.id).scalar()

    @property
    def stick(self):
        if self.c_type == 0:
            return False
        else:
            return 0 != db.session.query(CompetitionMode). \
                options(FromCache('model', 'competition:%d:stick' % self.id)). \
                with_entities(db.func.count('*')). \
                filter(CompetitionMode.competition_id == self.id, CompetitionMode.mode == 1).scalar()

    @property
    def registered_teams(self):
        return self._competings. \
            options(FromCache('model', 'competition:%d:registered_teams' % self.id)). \
            with_entities(db.func.count('*')).scalar()

    @property
    def recent_highlights(self):
        competition_fixture_model = get_model('CompetitionFixture')
        match_highlight_model = get_model('MatchHighlight')
        subquery = match_highlight_model.query.with_entities(db.func.max(match_highlight_model.id).label('id')).group_by(match_highlight_model.uid).subquery()
        return db.session.query(match_highlight_model). \
            options(FromCache('model', 'competition:%d:recent_highlights' % self.id)). \
            select_from(match_highlight_model). \
            join(competition_fixture_model,
                 sa.and_(match_highlight_model.fixture_id == competition_fixture_model.id,
                         match_highlight_model.status == 1,
                         competition_fixture_model.competition_id == self.id)). \
            join(subquery, match_highlight_model.id == subquery.c.id) .\
            order_by(match_highlight_model.date_recorded.desc()).limit(10). \
            all()

    @classmethod
    def recent_stick_competitions(cls):
        return db.session.query(Competition). \
            options(FromCache('model', 'competition:recent_stick')). \
            join(CompetitionMode, Competition.id == CompetitionMode.competition_id). \
            filter(CompetitionMode.mode == 1).order_by(Competition.date_published.desc()).limit(5).all()

    @classmethod
    def from_cache_by_id(cls, competition_id):
        return Competition.query. \
            options(FromCache('model', 'competition:%d' % competition_id)). \
            filter(Competition.id == competition_id).first()

    def competings_by_stage(self, stage):
        competition_team_model = get_model('CompetitionTeam')
        competition_team_rank_model = get_model('CompetitionTeamRank')
        team_rank_pairs = db.session.query(competition_team_model, competition_team_rank_model). \
            select_from(competition_team_model). \
            join(competition_team_rank_model,
                 sa.and_(competition_team_rank_model.c_team_id == competition_team_model.id,
                         competition_team_model.competition_id == self.id,
                         competition_team_rank_model.stage == stage)).all()
        with_rank_teams = []
        for team, rank in team_rank_pairs:
            team.current_rank = rank
            with_rank_teams.append(team)

        return with_rank_teams

    def __eq__(self, other):
        if isinstance(other, Competition) and self.id == other.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<Competition(id=%s)>" % self.id


class CompetitionMode(db.Model):
    __tablename__ = "competition_modes"

    competition_id = db.Column(db.Integer(), db.ForeignKey("competitions.id", ondelete="cascade"), primary_key=True)
    mode = db.Column(db.SmallInteger())  # 1: 置顶

    def __repr__(self):
        return u"<CompetitionMode(competition_id=%s, mode=%s)>" % (self.competition_id, self.mode)


class LeagueApplyItem(db.Model):
    __tablename__ = "league_apply_items"

    competition_id = db.Column(db.Integer(), db.ForeignKey('competitions.id', ondelete='cascade'), primary_key=True)
    dt_applied = db.Column(UTCDateTime(), default=utc_now)


@sa.event.listens_for(Competition, 'after_update')
@sa.event.listens_for(Competition, 'before_delete')
def on_competition(mapper, connection, competition):
    def do_after_commit():
        regions['model'].delete('competition:%d' % competition.id)
        if competition.stick:
            regions['model'].delete('competition:recent_stick')

    after_commit(do_after_commit)


@sa.event.listens_for(CompetitionMode, 'after_insert')
@sa.event.listens_for(CompetitionMode, 'after_update')
@sa.event.listens_for(CompetitionMode, 'before_delete')
def on_competition_mode(mapper, connection, competition_mode):
    def do_after_commit():
        regions['model'].delete('competition:recent_stick')
        regions['model'].delete('competition:%d:stick' % competition_mode.competition_id)

    after_commit(do_after_commit)


@sa.event.listens_for(LeagueApplyItem, 'after_insert')
@sa.event.listens_for(LeagueApplyItem, 'after_update')
@sa.event.listens_for(LeagueApplyItem, 'before_delete')
def on_league_apply_item(mapper, connection, league_apply_item):
    def do_after_commit():
        regions['model'].delete('competition:%d:apply_league' % league_apply_item.competition_id)

    after_commit(do_after_commit)