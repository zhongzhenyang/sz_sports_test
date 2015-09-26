# coding:utf-8

import sqlalchemy as sa
import datetime
from flask import current_app
from ..core import db, BaseService, AppError, after_commit
from ..models import Account, User, UserRelation
from .. import errors
from .. import tasks
from .. import settings


class AccountService(BaseService):
    __model__ = Account

    def create_account(self, role='user', **kwargs):
        account = Account()
        account.email = kwargs.get('email')
        account.password = current_app.user_manager.hash_password(kwargs.get('password'))
        account.role = role
        self.save(account)
        return account

    def update_password(self, account_id, password, new_password):
        account = self.get(account_id)
        if not account:
            raise AppError(error_code=errors.account_id_noexistent)
        if not current_app.user_manager.verify_password(password, account):
            raise AppError(error_code=errors.account_password_not_match)
        account.password = current_app.user_manager.hash_password(new_password)
        self.save(account)

    def delete_account(self, account_id):
        account = self.get(account_id)
        if not account:
            raise AppError(error_code=errors.account_id_noexistent)
        self.delete(account)

    def toggle_active(self, account_id):
        account = self.get(account_id)
        if not account:
            raise AppError(error_code=errors.account_id_noexistent)
        account.active = not account.active
        return self.save(account)

    def paginate_account(self, fullname_or_email=None, offset=0, limit=0):
        filters = []
        if fullname_or_email:
            filters.append(
                sa.or_(Account.fullname.startswith(fullname_or_email), Account.email.startswith(fullname_or_email)))
        return self.paginate_by(filters=filters, orders=[Account.id.asc()], offset=offset, limit=limit)


class UserService(BaseService):
    __model__ = User

    def create_or_update_user(self, account_id, **kwargs):
        user = User.query.get(account_id)
        original_profile = None
        if user is None:
            user = User(id=account_id)
        else:
            original_profile = user.profile

        new_profile = kwargs.get('profile', None)
        if new_profile and new_profile == settings.account_default_profile:
            new_profile = None

        user.birthday = datetime.datetime.strptime(kwargs.get('birthday'), '%Y-%m-%d') if kwargs.get(
            'birthday') else None
        user.genre = kwargs.get('genre', 'M')
        user.loc_state = kwargs.get('loc_state')
        user.loc_city = kwargs.get('loc_city')
        user.loc_county = kwargs.get('loc_county')
        user.loc_address = kwargs.get('loc_address')
        user.profile = new_profile
        user.intro = kwargs.get('intro')
        user.contact_me = kwargs.get('contact_me')
        self.save(user)

        if new_profile and original_profile != new_profile:
            def do_after_commit():
                tasks.thumbnail_image.apply_async(('User', account_id, 'profile', new_profile, '200x200!'))

            after_commit(do_after_commit)

        return user


class UserRelationService(BaseService):
    __model__ = UserRelation

    def add_user_relation(self, account_id, oppo_uid):
        oppo_account = Account.query.get(oppo_uid)
        if oppo_account is None:
            raise AppError(error_code=errors.account_id_noexistent)
        user_relation = UserRelation.query.filter(UserRelation.uid == account_id,
                                                  UserRelation.oppo_uid == oppo_uid).first()
        if user_relation:
            raise AppError(error_code=errors.user_relation_duplicate)

        user_relation = UserRelation(uid=account_id, oppo_uid=oppo_uid)
        self.save(user_relation)

    def delete_user_relation(self, account_id, oppo_uid):
        user_relation = UserRelation.query.filter(UserRelation.uid == account_id,
                                                  UserRelation.oppo_uid == oppo_uid).first()
        if user_relation is None:
            raise AppError(error_code=errors.user_relation_noexistent)
        self.delete(user_relation)

    def get_user_relation_status(self, account_id, oppo_uid):
        user_relation = UserRelation.query.filter(UserRelation.uid == account_id,
                                                  UserRelation.oppo_uid == oppo_uid).first()
        if user_relation:
            status = 'yes'
        else:
            status = 'no'
        return status
