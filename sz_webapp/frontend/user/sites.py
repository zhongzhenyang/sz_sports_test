# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import login_required, current_user
from ...core import AppError
from ...services import site_service
from ...helpers.flask_helper import json_response
from ... import models
from ... import errors

bp = Blueprint('user_sites', __name__, url_prefix='/user/sites')


@bp.route('/', methods=['GET'])
def site_list_page():
    """
        球场列表展示页
    """
    return render_template('frontend/venues.html')


@bp.route('/list', methods=['GET'])
def list_site():
    """
        搜索比赛场地
    """
    offset = int(request.args.get("offset", "0"))
    limit = int(request.args.get("limit", "10"))
    athletic_item_id = int(request.args.get('athletic_item_id')) if request.args.get('athletic_item_id') else None
    name = request.args.get('name') if request.args.get('name') else None
    loc_state = request.args.get('loc_state') if request.args.get('loc_state') else None
    loc_city = request.args.get('loc_city') if request.args.get('loc_city') else None
    loc_county = request.args.get('loc_county') if request.args.get('loc_county') else None
    price_orderby = int(request.args.get('price_orderby')) if request.args.get('price_orderby') else 1
    count, sites = site_service.paginate_site(offset=offset, limit=limit, athletic_item_id=athletic_item_id, name=name,
                                              status=1, loc_state=loc_state, loc_city=loc_city, loc_county=loc_county,
                                              price_orderby=price_orderby)
    return json_response(success=True, results=[site.__json__(include_keys=['athletic_item']) for site in sites])


@bp.route('/create', methods=['GET'])
@bp.route('/<int:site_id>/update', methods=['GET'])
@login_required
def edit_team_page(site_id=None):
    """
        创建修改球场页
    """
    athletic_items = models.AthleticItem.from_cache_by_all()
    if site_id:
        site = models.Site.from_cache_by_id(site_id)
    else:
        site = {}
    return render_template('frontend/venueUpdate.html', site=site, athletic_items=athletic_items)


@bp.route('/create', methods=['POST'])
@login_required
def create_site():
    """
        添加新球场
    """
    account_id = current_user._get_current_object().id
    site = site_service.create_site(account_id, **request.json)
    return json_response(site=site)


@bp.route('/<int:site_id>', methods=['GET'])
def site_page(site_id):
    site = models.Site.from_cache_by_id(site_id)
    if not site:
        raise AppError(error_code=errors.site_id_noexistent)
    return render_template('frontend/venueDetail.html', site=site)


@bp.route('/<int:site_id>/update', methods=['POST'])
@login_required
def update_site(site_id):
    """
        修改球场信息
    """
    site = site_service.update_site(site_id, **request.json)
    return json_response(site=site)


@bp.route('/<int:site_id>/delete', methods=['POST'])
@login_required
def delete_site(site_id):
    """
        删除球场
    """
    site_service.delete_site(site_id)
    return json_response(success=True)


@bp.route('/published-by-me', methods=['GET'])
@login_required
def site_published_by_me():
    """
        获取由我发布的比赛场地
    """
    limit = int(request.args.get("limit", "10"))
    offset = int(request.args.get("offset", "0"))
    account_id = current_user._get_current_object().id
    count, sites = site_service.paginate_site_by_publisher(account_id, offset=offset, limit=limit)
    return json_response(success=True, count=count,
                         results=[site.__json__(include_keys=['athletic_item']) for site in sites])