# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import account_service
from ...helpers.flask_helper import json_response
from ...core import AppError
from ... import models
from ... import errors

bp = Blueprint('admin_accounts', __name__, url_prefix='/admin/accounts')


@bp.route('/', methods=["GET"])
@roles_required('admin')
def home_page():
    return render_template('backend/usersMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('admin')
def list_account():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    fullname_or_email = request.args.get('content', None)

    count, accounts = account_service.paginate_account(fullname_or_email, offset, limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=accounts)


@bp.route('/<int:account_id>/toggle-active', methods=['POST'])
@roles_required('admin')
def toggle_account_active(account_id):
    account = account_service.toggle_active(account_id)
    return json_response(success=True, account=account)
