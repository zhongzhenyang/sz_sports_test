# coding:utf-8

from ..core import BaseService, AppError, db
from ..models import Message
from .. import message_categories, errors
from ..helpers import datetime_helper


class MessageService(BaseService):
    __model__ = Message

    def pending_messages_by_account(self, account_id):
        messages = Message.query.filter(Message.receiver_id == account_id, Message.status == 0).order_by(
            Message.dt_sent.desc()).all()
        return messages

    def handle_messages(self, message_id, result, account_id):
        message = self.get(message_id)
        if message is None:
            raise AppError(error_code=errors.message_id_noexistent)

        if message.receiver_id != account_id:
            raise AppError(error_code=errors.operation_unauthorized)
        handler = message_categories.get_handler(message.category)
        if handler is None:
            raise AppError(error_code=errors.message_category_cannot_handle)

        message.dt_handle = datetime_helper.utc_now()
        message.result = result
        message.status = 1

        error = None
        try:
            handler(message, result)
        except AppError, e:
            if e.error_code:
                message.error_code = e.error_code
            error = e
        except Exception, e:
            message.error_code = errors.fatal_error
            error = e

        self.save(message)
        return error
