# coding:utf-8

import datetime
import sqlalchemy as sa
from ..core import BaseService, db, AppError
from ..models import Athlete, AthleticItem, Team, TeamMember, Account, User
from .. import errors


class AccountAthleticItemService(BaseService):
    __model__ = Athlete

    def bind_athletic_item(self, account_id, athletic_item_id):

        athlete = Athlete.query.filter(Athlete.account_id == account_id,
                                       Athlete.athletic_item_id == athletic_item_id).first()
        if athlete and athlete.status == 1:
            raise AppError(error_code=errors.account_bind_athletic_duplicate)

        athletic_item = AthleticItem.query.get(athletic_item_id)
        if athletic_item is None or athletic_item._deleted:
            raise AppError(error_code=errors.athletic_item_id_nonexistent)

        if not athlete:
            athlete = Athlete(account_id=account_id, athletic_item_id=athletic_item_id)

        athlete.status = 1
        self.save(athlete)

        private_team = Team.query.filter(Team.creator_id == account_id, Team.athletic_item_id == athletic_item_id,
                                         Team.type == 0).first()
        no_private_team = False
        if not private_team:
            private_team = Team(name='%d-%d-private' % (account_id, athletic_item_id), creator_id=account_id,
                                athletic_item_id=athletic_item_id, status=1, type=0)
            no_private_team = True
        else:
            private_team.status = 1

        db.session.add(private_team)
        db.session.flush()
        if no_private_team:
            db.session.add(TeamMember(team_id=private_team.id, athlete_id=athlete.id, status=1,
                                      date_joined=datetime.date.today()))

        return athlete

    def unbind_athletic_item(self, account_id, athletic_item_id):
        athlete = Athlete.query.filter(Athlete.account_id == account_id,
                                       Athlete.athletic_item_id == athletic_item_id).first()
        if athlete is None or athlete.status == 0:
            raise AppError(error_code=errors.account_bind_athletic_nonexistent)

        team_member = TeamMember.query.\
            join(Team, sa.and_(Team.id == TeamMember.team_id, Team.status == 1, Team.type == 1)). \
            filter(TeamMember.athlete_id == athlete.id).first()
        if team_member and team_member.status == 1:
            raise AppError(error_code=errors.team_member_athlete_joined)

        athlete.status = 0
        private_team = Team.query.filter(Team.creator_id == account_id, Team.athletic_item_id == athletic_item_id,
                                         Team.type == 0).first()
        if private_team:
            private_team.status = 0
            db.session.add(private_team)

        self.save(athlete)

    def update_athlete(self, account_id, athletic_item_id, **kwargs):
        athlete = Athlete.query.filter(Athlete.account_id == account_id,
                                       Athlete.athletic_item_id == athletic_item_id).first()
        if athlete is None or athlete.status == 0:
            raise AppError(error_code=errors.account_bind_athletic_nonexistent)
        athlete.info = kwargs
        return self.save(athlete)

    def paginate_athlete(self, offset=0, limit=10, **kwargs):
        filters = []
        q = db.session.query(Account).outerjoin(User, User.id == Account.id). \
            outerjoin(Athlete, Athlete.account_id == Account.id)
        if 'name' in kwargs and kwargs['name']:
            filters.append(Account.fullname.startswith(kwargs['name']))
        if 'athletic_item_id' in kwargs and kwargs['athletic_item_id']:
            filters.append(Athlete.athletic_item_id == kwargs['athletic_item_id'])
        if 'loc_state' in kwargs and kwargs['loc_state']:
            filters.append(User.loc_state == kwargs['loc_state'])
        if 'loc_city' in kwargs and kwargs['loc_city']:
            filters.append(User.loc_city == kwargs['loc_city'])
        if 'loc_county' in kwargs and kwargs['loc_county']:
            filters.append(User.loc_county == kwargs['loc_county'])
        count = q.with_entities(db.func.count(Account.id)).filter(*filters).scalar()
        if count:
            accounts = q.filter(*filters).order_by(Account.id.asc()).offset(offset).limit(limit).all()
        else:
            accounts = []
        return count, accounts
