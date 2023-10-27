from flask import jsonify, request, redirect
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from silk_road.auth import bp
from silk_road.models import *
from silk_road import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from silk_road.serializers import user_schema
from .utils import *
from werkzeug.security import generate_password_hash, check_password_hash



@bp.route('/refresh')
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return jsonify(user_schema.dump(user))
    except AssertionError as err:
        return jsonify(msg=f"{err}")


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


@bp.route('/reset-password-code', methods=['POST'])
def reset_password_code():
    email = request.get_json()['email']
    user = User.query.filter_by(email=email).first()
    if user:
        code = code_generator()
        user.code = code
        user.expire_date = datetime.now() + timedelta(minutes = 2)
        db.session.commit()
        send_code(email, code)
        return jsonify({"msg":"Code sent to your email to reset password"})
    else:
        return jsonify({"msg":"No user with this email"})


@bp.route('/check-code', methods=['POST'])
def check_code():
    email = request.get_json()['email']
    code = int(request.get_json()['code'])
    user = User.query.filter_by(email=email).first()
    if user is not None and user.code == code:
        if user.expire_date > datetime.now():
            user.code = None
            db.session.commit()
            return jsonify(msg=True)
        else:
            user.code = None
            db.session.commit()
            return jsonify(msg="Code expired")
    else:
        return jsonify(msg=False)


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.get_json()['email']
    password = request.get_json()['password']
    user = User.query.filter_by(email=email).first()
    user.password = request.get_json()['password']
    db.session.commit()
    return jsonify(msg='Success')


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    id = get_jwt_identity()
    user = db.get_or_404(User, id)
    if check_password_hash(user.password_hash, request.get_json().get('old_password')):
        user.password = request.get_json().get('password')
        db.session.commit()
        return jsonify(msg="Changed")
    else:
        return jsonify(msg="Incorrect password"), 400

