# coding:utf-8

from ..core import BaseService, AppError
from .. import errors
from ..models import AthleticItem


class AthleticItemService(BaseService):
    __model__ = AthleticItem

    def create_athletic_item(self, **kwargs):
        name = kwargs.get('name')
        if self.count_by(filters=[AthleticItem.name == name]) > 0:
            raise AppError(error_code=errors.athletic_item_name_duplicate)
        athletic_item = AthleticItem()
        self._set_athletic_item(athletic_item, **kwargs)
        return self.save(athletic_item)

    def update_athletic_item(self, athletic_item_id, **kwargs):
        athletic_item = self.get(athletic_item_id)
        if not athletic_item:
            raise AppError(error_code=errors.athletic_item_id_nonexistent)
        new_name = kwargs.get('name')
        if new_name != athletic_item.name and self.count_by(filters=[AthleticItem.name == new_name]) > 0:
            raise AppError(error_code=errors.athletic_item_name_duplicate)

        self._set_athletic_item(athletic_item, **kwargs)
        return self.save(athletic_item)

    def delete_athletic_item(self, athletic_item_id):
        athletic_item = self.get(athletic_item_id)
        if not athletic_item:
            raise AppError(error_code=errors.athlete_item_id_nonexistent)

        athletic_item._deleted = True
        return self.save(athletic_item)

    def _set_athletic_item(self, athletic_item, **kwargs):
        athletic_item.name = kwargs.get('name')
        athletic_item.logo = kwargs.get('logo')
        athletic_item.enabled = kwargs.get('enabled')
        athletic_item.intro = kwargs.get('intro')
        athletic_item.options = kwargs.get('options')
