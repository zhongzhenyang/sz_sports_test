# coding:utf-8

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from ..core import db, Deleted, FromCache, regions, after_commit
from ..helpers.sa_helper import JsonSerializableMixin


class AthleticItem(db.Model, Deleted, JsonSerializableMixin):
    __tablename__ = 'athletic_items'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(32), unique=True)
    logo = db.Column(db.String(256))
    enabled = db.Column(db.Boolean(), default=True)
    intro = db.Column(db.UnicodeText(), nullable=True)
    options = db.Column(JSON())
    _athletes = db.relationship('Athlete', lazy='dynamic')
    _teams = db.relationship('Team', lazy='dynamic')
    _competitions = db.relationship('Competition', lazy='dynamic')

    @classmethod
    def from_cache_by_id(cls, athletic_item_id):
        return AthleticItem.query. \
            options(FromCache('model', 'athletic_item:%d' % athletic_item_id)). \
            filter(AthleticItem.id == athletic_item_id). \
            first()

    @classmethod
    def from_cache_by_all(cls):
        return AthleticItem.query. \
            options(FromCache('model', 'athletic_item:all')). \
            filter(AthleticItem.enabled == True, AthleticItem._deleted == False). \
            all()

    def __eq__(self, other):
        if isinstance(other, AthleticItem) and other.name == self.name:
            return True
        else:
            return False

    def __ne__(self, other):
        return self.__eq__(other)

    def __hash__(self):
        return self.__hash__(self.name)

    def __repr__(self):
        return u"<AthleticItem(id=%s)>" % self.id


@sa.event.listens_for(AthleticItem, 'after_insert')
@sa.event.listens_for(AthleticItem, 'after_update')
@sa.event.listens_for(AthleticItem, 'before_delete')
def on_athletic_item_update(mapper, connection, athletic):

    def do_after_commit():
        regions['model'].delete_multi(
            [
                'athletic_item:%d' % athletic.id,
                'athletic_item:all',
            ]
        )
    after_commit(do_after_commit)
