# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import competition_service
from ...helpers.flask_helper import json_response
from ... import models

bp = Blueprint('admin_competitions', __name__, url_prefix='/admin/competitions')


@bp.route('/', methods=['GET'])
@roles_required('admin')
def home_page():
    athletic_items = models.AthleticItem.from_cache_by_all()
    return render_template('backend/competitionsMgr.html', athletic_items=athletic_items)


@bp.route('/list', methods=['GET'])
@roles_required('admin')
def list_competition():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    athletic_item_id = int(request.args.get('athletic_item_id')) if request.args.get('athletic_item_id') else None
    c_name = request.args.get('c_name') if request.args.get('c_name') else None
    only_apply_league = True if request.args.get('only_apply_league', None) == '1' else False
    count, competitions = competition_service.paginate_competition(offset=offset, limit=limit,
        athletic_item_id=athletic_item_id, c_name=c_name, only_apply_league=only_apply_league)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count,
                         aaData=[ competition.__json__(include_keys=['athletic_item', 'stick']) for competition in competitions])


@bp.route('/<int:competition_id>/stick', methods=['POST'])
@roles_required('admin')
def stick_competition(competition_id):
    """
        设置为置顶
    """
    competition_service.stick_competition(competition_id)
    return json_response(success=True)


@bp.route('/<int:competition_id>/unstick', methods=['POST'])
@roles_required('admin')
def unstick_competition(competition_id):
    """
        取消置顶
    """
    competition_service.unstick_competition(competition_id)
    return json_response(success=True)


@bp.route('/audit-league', methods=['GET'])
@roles_required('admin')
def audit_league_page():
    athletic_items = models.AthleticItem.from_cache_by_all()
    return render_template('backend/competitionsToAudit.html', athletic_items=athletic_items)


@bp.route('/<int:competition_id>/audit-league/<int:result>', methods=['POST'])
@roles_required('admin')
def audit_league(competition_id, result):
    """
        处理将活动提升为联赛的申请,result=1 表示同意,其他为不同意
    """
    competition_service.audit_league(competition_id, result)
    return json_response(success=True)


@bp.route('/<int:competition_id>/delete', methods=['POST'])
@roles_required('admin')
def delete_competition(competition_id):
    competition_service.delete_competition(competition_id)
    return json_response(success=True)


@bp.route('/create-league', methods=['POST'])
@roles_required('admin')
def create_league():
    """
        直接创建联赛,该接口暂时不用
    """
    manager_id = request.json.get('manager_id')
    competition = competition_service.create_league(manager_id, **request.json)
    return json_response(competition=competition)
