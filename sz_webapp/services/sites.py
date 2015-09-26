# coding:utf-8

import datetime
from flask_user import current_user
from ..core import BaseService, AppError, db, after_commit
from ..models import Site
from .. import errors
from .. import tasks


class SiteService(BaseService):
    __model__ = Site

    def create_site(self, publisher_id, **kwargs):
        site = Site()
        self._set_site(site, **kwargs)
        site.publisher_id = publisher_id
        self.save(site)

        if site.pic:
            def do_thumbnail_site_pic():
                tasks.thumbnail_image.apply_async(('Site', site.id, 'pic', site.pic, '600x400!'))

            after_commit(do_thumbnail_site_pic)

        return site

    def update_site(self, site_id, **kwargs):
        site = self.get(site_id)
        original_site_pic = site.pic
        new_site_pic = kwargs.get('pic', None)
        if site is None:
            raise AppError(error_code=errors.site_id_noexistent)
        self._set_site(site, **kwargs)
        self.save(site)

        if new_site_pic and new_site_pic != original_site_pic:
            def do_thumbnail_site_pic():
                tasks.thumbnail_image.apply_async(('Site', site.id, 'pic', new_site_pic, '600x400!'))

            after_commit(do_thumbnail_site_pic)

        return site

    def delete_site(self, site_id):
        site = self.get(site_id)
        if site is None:
            raise AppError(error_code=errors.site_id_noexistent)
        self.delete(site)

    def set_site_status(self, site_id, status):
        site = self.get(site_id)
        if site is None:
            raise AppError(error_code=errors.site_id_noexistent)
        site.status = status
        return self.save(site)

    def paginate_site_by_publisher(self, publisher_id, offset=0, limit=10):
        filters = [Site.publisher_id == publisher_id]
        return self.paginate_by(filters=filters, orders=[Site.date_published.desc()], offset=offset, limit=limit)

    def _set_site(self, site, **kwargs):
        site.name = kwargs.get('name')
        site.address = kwargs.get('address')
        site.tel = kwargs.get('tel')
        site.price = kwargs.get('price')
        site.intro = kwargs.get('intro')
        site.pic = kwargs.get('pic')
        site.loc_state = kwargs.get('loc_state')
        site.loc_city = kwargs.get('loc_city')
        site.loc_county = kwargs.get('loc_county')
        site.loc_address = kwargs.get('loc_address')
        site.features = kwargs.get('features')
        site.status = 0
        site.athletic_item_id = kwargs.get('athletic_item_id')
        return site

    def paginate_site(self, offset=0, limit=10, **kwargs):
        filters = []
        if 'name' in kwargs and kwargs['name']:
            filters.append(Site.name.startswith(kwargs['name']))
        if 'athletic_item_id' in kwargs and kwargs['athletic_item_id']:
            filters.append(Site.athletic_item_id == kwargs['athletic_item_id'])
        if 'status' in kwargs and kwargs['status'] is not None:
            filters.append(Site.status == kwargs['status'])
        else:
            filters.append(Site.status != -1)
        if 'loc_state' in kwargs and kwargs['loc_state']:
            filters.append(Site.loc_state == kwargs['loc_state'])
        if 'loc_city' in kwargs and kwargs['loc_city']:
            filters.append(Site.loc_city == kwargs['loc_city'])
        if 'loc_county' in kwargs and kwargs['loc_county']:
            filters.append(Site.loc_county == kwargs['loc_county'])
        if 'price_orderby' in kwargs and kwargs['price_orderby'] == -1:
            price_orderby = Site.price.desc()
        else:
            price_orderby = Site.price.asc()

        return self.paginate_by(filters=filters, orders=[price_orderby], offset=offset, limit=limit)
