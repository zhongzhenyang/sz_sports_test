# coding:utf-8

from sqlalchemy.dialects.postgresql import JSON
from ..core import db, get_model, FromCache
from ..helpers.sa_helper import UTCDateTime, JsonSerializableMixin
from ..helpers.datetime_helper import utc_now


class Message(db.Model, JsonSerializableMixin):
    __tablename__ = "messages"

    id = db.Column(db.Integer(), primary_key=True)
    sender_id = db.Column(db.Integer(), db.ForeignKey("accounts.id", ondelete="cascade"))
    receiver_id = db.Column(db.Integer(), db.ForeignKey("accounts.id", ondelete="cascade"))
    category = db.Column(db.SmallInteger())
    status = db.Column(db.SmallInteger(), default=0)  # 0:pending, 1:finished
    body = db.Column(JSON())
    dt_sent = db.Column(UTCDateTime(), default=utc_now)
    dt_handle = db.Column(UTCDateTime(), nullable=True)
    result = db.Column(db.SmallInteger(), nullable=True)  # 1:同意, -1:拒绝
    error_code = db.Column(db.String(5), nullable=True)

    @property
    def sender(self):
        account_model = get_model('Account')
        return db.session.query(account_model).options(FromCache('model', 'account:%d' % self.sender_id)). \
            filter_by(id=self.sender_id).first()

    @property
    def receiver(self):
        account_model = get_model('Account')
        return db.session.query(account_model).options(FromCache('model', 'account:%d' % self.receiver_id)). \
            filter_by(id=self.receiver_id).first()


    def __eq__(self, other):
        if isinstance(other, Message) and self.id == other.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<Message(id=%s)>" % self.id
