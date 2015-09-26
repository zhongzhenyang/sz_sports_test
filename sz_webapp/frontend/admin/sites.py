# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import site_service
from ...helpers.flask_helper import json_response
from ... import models

bp = Blueprint('admin_sites', __name__, url_prefix='/admin/sites')


@bp.route('/', methods=['GET'])
@roles_required('admin')
def home_page():
    return render_template('backend/venuesMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('admin')
def list_site():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    name = request.args.get('name') if request.args.get('name') else None
    status = 0 if request.args.get('status') == 'pending' else None
    count, sites = site_service.paginate_site(offset=offset, limit=limit, name=name, status=status)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count,
                         aaData=[site.__json__(include_keys=['athletic_item']) for site in sites])


@bp.route('/set-status', methods=['POST'])
@roles_required('admin')
def set_site_status():
    site_id = int(request.form.get('site_id'))
    status = int(request.form.get('status'))
    site_service.set_site_status(site_id, status)
    return json_response(success=True)
