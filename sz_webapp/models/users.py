# coding:utf-8

import sqlalchemy as sa
from flask_user import UserMixin
from ..core import db, Deleted, get_model, FromCache, regions, after_commit
from ..helpers.sa_helper import JsonSerializableMixin
from ..settings import account_default_profile


class Account(db.Model, Deleted, JsonSerializableMixin, UserMixin):
    __tablename__ = "accounts"

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.Unicode(64), unique=True)
    fullname = db.Column(db.Unicode(32), nullable=True)
    _password = db.Column("password", db.String(128))
    role = db.Column(db.String(16), default='user')
    _athletes = db.relationship('Athlete', lazy='dynamic')
    active = db.Column(db.Boolean(), nullable=False, server_default='1')

    def __json__(self, include_keys=[], exclude_keys=[]):
        return super(Account, self).__json__(include_keys=include_keys+['user_profile'], exclude_keys=exclude_keys)

    @property
    def user(self):
        return User.query.options(FromCache('model', 'user:%d' % self.id)). \
            filter(User.id == self.id). \
            first()

    @property
    def user_profile(self):
        user = self.user
        if user and user.profile:
            return user.profile
        else:
            return account_default_profile

    @property
    def related_account_ids(self):
        """
            关注的用户的ID列表
        """
        ids = UserRelation.query.options(FromCache('model', 'account:%d:related' % self.id)). \
            with_entities(UserRelation.oppo_uid).filter(UserRelation.uid == self.id).all()
        return [account_id for (account_id,) in ids]

    @property
    def active_athletes(self):
        """
            用户关注的体育项目
        """
        athlete_model = get_model('Athlete')
        return db.session.query(athlete_model). \
            options(FromCache('model', 'account:%d:active_athletes' % self.id)). \
            filter_by(account_id=self.id, status=1). \
            all()

    @property
    def competition_prizes(self):
        """
            用户获得的奖牌
        """
        competition_team_prize_model = get_model('CompetitionTeamPrize')
        athlete_model = get_model('Athlete')
        team_member_model = get_model('TeamMember')
        competition_athlete_model = get_model('CompetitionAthlete')
        competition_team_model = get_model('CompetitionTeam')
        competition_model = get_model('Competition')
        return db.session.query(competition_team_prize_model). \
            options(FromCache('model', 'account:%d:prizes' % self.id)). \
            select_from(athlete_model). \
            join(team_member_model,
                 sa.and_(athlete_model.id == team_member_model.athlete_id,
                         athlete_model.account_id == self.id)). \
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
        """
            用户参加的最近的5场赛事,不包括挑战赛
        """
        team_member_model = get_model('TeamMember')
        competition_team_model = get_model('CompetitionTeam')
        competition_athlete_model = get_model('CompetitionAthlete')
        competition_model = get_model('Competition')
        athlete_model = get_model('Athlete')
        return db.session.query(competition_team_model). \
            options(FromCache('model', 'account:%d:recent_competitions' % self.id)). \
            join(competition_athlete_model,
                 competition_athlete_model.competition_team_id == competition_team_model.id). \
            join(team_member_model,
                 sa.and_(
                     team_member_model.team_id == competition_team_model.team_id,
                     team_member_model.id == competition_athlete_model.team_member_id)). \
            join(athlete_model,
                 sa.and_(
                     athlete_model.id == team_member_model.athlete_id,
                     athlete_model.account_id == self.id)). \
            join(competition_model,
                 sa.and_(competition_model.id == competition_team_model.competition_id,  competition_model.c_type != 0)).\
            order_by(competition_model.date_started.desc()).limit(5). \
            all()

    @property
    def recent_fixture(self):
        """
            用户最近的5场比赛
        """
        team_member_model = get_model('TeamMember')
        competition_team_model = get_model('CompetitionTeam')
        competition_fixture_model = get_model('CompetitionFixture')
        competition_athlete_model = get_model('CompetitionAthlete')
        competition_model = get_model('Competition')
        athlete_model = get_model('Athlete')
        return db.session.query(competition_fixture_model). \
            options(FromCache('model', 'account:%d:recent_fixtures' % self.id)). \
            select_from(competition_team_model). \
            join(competition_athlete_model,
                 competition_athlete_model.competition_team_id == competition_team_model.id). \
            join(team_member_model,
                 sa.and_(
                     team_member_model.team_id == competition_team_model.team_id,
                     team_member_model.id == competition_athlete_model.team_member_id)). \
            join(athlete_model,
                 sa.and_(
                     athlete_model.id == team_member_model.athlete_id,
                     athlete_model.account_id == self.id)). \
            join(competition_model, competition_model.id == competition_team_model.competition_id). \
            join(competition_fixture_model,
                 sa.or_(competition_fixture_model.p1 == competition_team_model.id,
                        competition_fixture_model.p2 == competition_team_model.id)). \
            order_by(competition_fixture_model.date_started.desc()).limit(5). \
            all()

    @property
    def recent_highlights(self):
        """
            用户最近的10个精彩瞬间
        """
        athlete_model = get_model('Athlete')
        team_member_model = get_model('TeamMember')
        competition_team_model = get_model('CompetitionTeam')
        match_highlight_model = get_model('MatchHighlight')
        return db.session.query(match_highlight_model). \
            options(FromCache('model', 'account:%d:recent_highlights' % self.id)). \
            select_from(athlete_model). \
            join(team_member_model, athlete_model.id == team_member_model.athlete_id). \
            join(competition_team_model,
                 competition_team_model.team_id == team_member_model.team_id). \
            join(match_highlight_model,
                 sa.and_(match_highlight_model.c_team_id == competition_team_model.id,
                         match_highlight_model.status == 1)). \
            filter(athlete_model.account_id == self.id).\
            order_by(match_highlight_model.date_recorded.desc()).limit(10). \
            all()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd):
        self._password = pwd

    @classmethod
    def from_cache_by_id(cls, account_id):
        return Account.query. \
            options(FromCache('model', 'account:%d' % account_id)). \
            filter(Account.id == account_id).first()

    def has_roles(self, *requirements):
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                tuple_of_role_names = requirement
                if self.role in tuple_of_role_names:
                    return True
            else:
                role_name = requirement
                if role_name == self.role:
                    return True
        return False

    def __eq__(self, other):
        if isinstance(other, Account) and self.email == other.email:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.email)

    def __repr__(self):
        return u"<Account(id=%s)>" % self.id


class User(db.Model, JsonSerializableMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete="cascade"), primary_key=True)
    birthday = db.Column(db.Date(), nullable=True)
    genre = db.Column(db.String(1), default='M')
    loc_state = db.Column(db.Unicode(20), nullable=True)  # 省
    loc_city = db.Column(db.Unicode(20), nullable=True)  # 市
    loc_county = db.Column(db.Unicode(20), nullable=True)  # 区县
    loc_address = db.Column(db.Unicode(128), nullable=True)  # 地址
    profile = db.Column(db.String(256), nullable=True)
    intro = db.Column(db.UnicodeText(), nullable=True)
    contact_me = db.Column(db.Unicode(256), nullable=True)

    def __eq__(self, other):
        if isinstance(other, User) and self.id == other.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<User(id=%s)>" % self.id


class UserRelation(db.Model):
    __tablename__ = "user_relations"

    uid = db.Column(db.Integer(), db.ForeignKey("accounts.id", ondelete="cascade"), primary_key=True)
    oppo_uid = db.Column(db.Integer(), db.ForeignKey("accounts.id", ondelete="cascade"), primary_key=True)

    def __eq__(self, other):
        if isinstance(other, UserRelation) and self.uid == other.uid and self.oppo_uid == other.oppo_uid:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.uid) + hash(self.oppo_uid) * 13

    def __repr__(self):
        return u"<UserRelation(uid=%s,oppo_uid=%s)>" % (self.uid, self.oppo_uid)


@sa.event.listens_for(Account, 'after_insert')
@sa.event.listens_for(Account, 'after_update')
@sa.event.listens_for(Account, 'before_delete')
def on_account(mapper, connection, account):
    def do_after_commit():
        regions['model'].delete('account:%d' % account.id)

    after_commit(do_after_commit)

@sa.event.listens_for(User, 'after_insert')
@sa.event.listens_for(User, 'after_update')
@sa.event.listens_for(User, 'before_delete')
def on_user(mapper, connection, user):
    def do_after_commit():
        regions['model'].delete('user:%d' % user.id)

    after_commit(do_after_commit)



@sa.event.listens_for(UserRelation, 'after_insert')
@sa.event.listens_for(UserRelation, 'before_delete')
def on_user_relation(mapper, connection, user_relation):
    def do_after_commit():
        regions['model'].delete('account:%d:related' % user_relation.uid)

    after_commit(do_after_commit)