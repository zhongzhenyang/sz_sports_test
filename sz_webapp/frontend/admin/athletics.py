# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required, current_user
from ...services import athletic_item_service
from ...helpers.flask_helper import json_response
from ...core import AppError
from ... import models
from ... import errors

bp = Blueprint('admin_athletics', __name__, url_prefix='/admin/athletics')


@bp.route('/', methods=["GET"])
@roles_required('admin')
def home_page():
    athletic_items = models.AthleticItem.from_cache_by_all()
    return render_template('backend/sportsMgr.html', athletic_items=athletic_items)


@bp.route('/create', methods=["GET"])
@bp.route('/update/<int:athletic_item_id>', methods=["GET"])
@roles_required('admin')
def athletic_edit_page(athletic_item_id=None):
    if athletic_item_id:
        athletic_item = models.AthleticItem.from_cache_by_id(athletic_item_id)
        if not athletic_item:
            raise AppError(error_code=errors.athletic_item_id_nonexistent)
    else:
        athletic_item = {}
    return render_template('backend/sportsUpdate.html', athletic_item=athletic_item)


@bp.route('/create', methods=["POST"])
@roles_required('admin')
def create_athletic_item():
    athletic_item = athletic_item_service.create_athletic_item(**request.json)
    return json_response(athletic_item=athletic_item)


@bp.route('/<int:athletic_item_id>/update', methods=['POST'])
@roles_required('admin')
def update_athletic_item(athletic_item_id):
    athletic_item = athletic_item_service.update_athletic_item(athletic_item_id, **request.json)
    return json_response(athletic_item)


@bp.route('/<int:athletic_item_id>/delete', methods=['POST'])
@roles_required('admin')
def delete_athletic_item(athletic_item_id):
    athletic_item_service.delete_athletic_item(athletic_item_id)
    return json_response(success=True)
