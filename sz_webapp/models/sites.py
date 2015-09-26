# coding:utf-8

import sqlalchemy as sa
import datetime
from ..core import db, Deleted, get_model, FromCache, regions, after_commit
from ..helpers.sa_helper import JsonSerializableMixin


class Site(db.Model, Deleted, JsonSerializableMixin):
    __tablename__ = "sites"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(32))
    tel = db.Column(db.String(32))
    price = db.Column(db.Numeric(precision=10, scale=2))
    intro = db.Column(db.UnicodeText(), nullable=True)
    pic = db.Column(db.String(128))
    loc_state = db.Column(db.Unicode(20), nullable=True)  # 省
    loc_city = db.Column(db.Unicode(20), nullable=True)  # 市
    loc_county = db.Column(db.Unicode(20), nullable=True)  # 区县
    loc_address = db.Column(db.Unicode(128), nullable=True)
    features = db.Column(db.Unicode(128), nullable=True)
    status = db.Column(db.SmallInteger(), default=0)  # 0: pending, 1:pass, -1:discard
    publisher_id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete='cascade'))
    athletic_item_id = db.Column(db.Integer(), db.ForeignKey('athletic_items.id', ondelete='cascade'))  # 项目
    date_published = db.Column(db.Date(), default=datetime.date.today)

    @classmethod
    def from_cache_by_id(cls, site_id):
        return Site.query. \
            options(FromCache('model', 'site:%d' % site_id)). \
            filter(Site.id == site_id).first()

    @property
    def athletic_item(self):
        athletic_item_model = get_model('AthleticItem')
        return db.session.query(athletic_item_model). \
            options(FromCache('model', 'athletic_item:%d' % self.athletic_item_id)). \
            filter_by(id=self.athletic_item_id).first()

    def __eq__(self, other):
        if isinstance(other, Site) and self.id == other.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<Site(id=%s)>" % self.id


@sa.event.listens_for(Site, 'after_update')
@sa.event.listens_for(Site, 'after_delete')
def on_athletic_item_update(mapper, connection, site):
    def do_after_commit():
        regions['model'].delete('site:%d' % site.id)

    after_commit(do_after_commit)