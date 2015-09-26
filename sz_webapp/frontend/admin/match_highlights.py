# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...core import db
from ...services import match_highlight_service
from ...helpers.flask_helper import json_response
from ...models import MatchHighlight

bp = Blueprint('admin_highlights', __name__, url_prefix='/admin/highlights')


@bp.route('/', methods=['GET'])
@roles_required('admin')
def home_page():
    return render_template('backend/momentsMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('admin')
def list_match_highlight():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")

    filters = [MatchHighlight.status == -2] if request.args.get('status') == 'pending' else [MatchHighlight.status.in_([1, -2])]

    subquery = MatchHighlight.query.with_entities(db.func.max(MatchHighlight.id).label('id')).group_by(
        MatchHighlight.uid).subquery()
    count = MatchHighlight.query.with_entities(db.func.count('*')). \
        select_from(MatchHighlight).join(subquery, MatchHighlight.id == subquery.c.id).filter(*filters).scalar()
    if count:
        match_highlights = MatchHighlight.query. \
            select_from(MatchHighlight).join(subquery, MatchHighlight.id == subquery.c.id). \
            filter(*filters).order_by(MatchHighlight.date_recorded.desc()).offset(offset).limit(limit).all()
    else:
        match_highlights = []
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=match_highlights)


@bp.route('/set-status', methods=['POST'])
@roles_required('admin')
def set_highlight_status():
    match_highlight_id = int(request.form.get('match_highlight_id'))
    status = int(request.form.get('status'))
    match_highlight_service.set_match_highlight_status(match_highlight_id, status)
    return json_response(success=True)