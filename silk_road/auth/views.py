from flask import jsonify, request, redirect
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from silk_road.auth import bp
from silk_road.models import *
from silk_road import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from silk_road.serializers import user_schema


@bp.route('/refresh')
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user_schema.dump(user))


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()
    if user:
        if check_password_hash(user.password_hash, data.get('password')):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify(access_token=access_token, refresh_token=refresh_token)
    return jsonify({"msg":"Bad email or password"})


@bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklisted_token = BlacklistToken(
        user_id = get_jwt_identity(),
        token = jti,
        blacklisted_on = datetime.now()
        )
    db.session.add(blacklisted_token)
    db.session.commit()
    return jsonify({"msg": "Successfully logged out"}), 200