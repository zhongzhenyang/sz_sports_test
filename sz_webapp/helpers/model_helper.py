from .. import models


def get_accounts(account_ids=[], fetch_user=False):
    datas = []
    for account_id in account_ids:
        account = models.Account.from_cache_by_id(account_id)
        if account:
            data = {}
            data['account'] = account
            if fetch_user:
                user = account.user
                data['user'] = user

            datas.append(data)
    return datas

