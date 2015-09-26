# coding:utf-8

from flask import Blueprint, request, render_template
from ..helpers.flask_helper import json_response
from .. import models

bp = Blueprint('athletics', __name__, url_prefix='/athletics')


@bp.route('/all', methods=['GET'])
def all_athletic_items():
    athletic_items = models.AthleticItem.from_cache_by_all()
    return json_response(results=athletic_items)
