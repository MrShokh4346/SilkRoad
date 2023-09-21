from flask import jsonify, request, redirect
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from silk_road.api import bp 
from silk_road.models import *
from silk_road import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from silk_road.serializers import user_schema


@bp.route('/add-to-card/<int:product_id>')
@jwt_required()
def add_to_card():
    id = get_jwt_identity()
