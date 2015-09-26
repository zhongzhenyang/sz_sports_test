# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import team_service
from ...helpers.flask_helper import json_response
from ... import models

bp = Blueprint('admin_teams', __name__, url_prefix='/admin/teams')


@bp.route('/', methods=['GET'])
@roles_required('admin')
def home_page():
    athletic_items = models.AthleticItem.from_cache_by_all()
    return render_template('backend/teamsMgr.html', athletic_items=athletic_items)


@bp.route('/list', methods=['GET'])
@roles_required('admin')
def list_team():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    athletic_item_id = int(request.args.get('athletic_item_id')) if request.args.get('athletic_item_id') else None
    team_name = request.args.get('team_name') if request.args.get('team_name') else None

    count, teams = team_service.paginate_team(offset, limit, athletic_item_id=athletic_item_id, team_name=team_name)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count,
                         aaData=[team.__json__(include_keys=['athletic_item']) for team in teams])


@bp.route('/<int:team_id>/delete', methods=['POST'])
@roles_required('admin')
def delete_team(team_id):
    team_service.delete_team(team_id)
    return json_response(success=True)
