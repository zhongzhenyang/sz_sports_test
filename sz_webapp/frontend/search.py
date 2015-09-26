# coding:utf-8

from flask import Blueprint, request, render_template
from ..helpers.flask_helper import json_response
from .. import models
from ..services import team_service, account_athletic_item_service

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('/', methods=['GET'])
def search_page():
    return render_template('frontend/search.html')


@bp.route('/do', methods=['GET'])
def do_search():
    offset = int(request.args.get('offset', '0'))
    limit = int(request.args.get('limit', '10'))
    category = request.args.get('category', 'person')
    name = request.args.get('name', None)
    athletic_item_id = int(request.args.get('athletic_item_id')) if request.args.get('athletic_item_id') else None
    loc_state = request.args.get('loc_state', None)
    loc_city = request.args.get('loc_city', None)
    loc_county = request.args.get('loc_county', None)

    if category == 'person':
        count, accounts = account_athletic_item_service.paginate_athlete(offset, limit,
                                                                         name=name, athletic_item_id=athletic_item_id,
                                                                         loc_state=loc_state, loc_city=loc_city,
                                                                         loc_county=loc_county)
        data = [account.__json__(include_keys=['user']) for account in accounts]
    else:
        count, teams = team_service.paginate_team(offset, limit, team_name=name, athletic_item_id=athletic_item_id,
                                                  loc_state=loc_state, loc_city=loc_city,
                                                  loc_county=loc_county)
        data = [team.__json__(include_keys=['athletic_item']) for team in teams]
    return json_response(count=count, results=data)


@bp.route('/person', methods=['GET'])
def search_person():
    name = request.args.get('name')
    accounts = models.Account.query.filter(models.Account.fullname.startswith(name)).order_by(models.Account.id.asc()).limit(10).all()
    return json_response(results=accounts)
