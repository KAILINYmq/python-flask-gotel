# -*- coding:utf-8 -*-

# Author: Will
# E-mail: pcwjobs@163.com
# DateTime: 2020/11/20 9:42 上午

# Copyright (c) 2015-2020
# All Rights Reserved.

import time
import hashlib
import requests
from flask import request, jsonify, Blueprint, current_app as app
from agile.commons.api_response import ApiResponse, ResposeStatus
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
)
from flask_restplus import reqparse
from agile.models import User
from agile.extensions import pwd_context, jwt
from agile.auth.helpers import revoke_token, is_token_revoked, add_token_to_database
from flasgger import swag_from
from agile.commons.api_doc_helper import get_request_parser_doc_dist
from agile.commons.audit import auth_audit_trail
from sqlalchemy import func
from sqlalchemy import or_, desc

blueprint = Blueprint("auth_v2", __name__, url_prefix="/api/v1/auth")


# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what custom claims
# should be added to the access token.
@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    user = User.query.get_or_404(identity)
    return {
        "department": user.department.name,
        "role": user.role.name,
        "permissions": user.role.authorized_permissions(),
        "categories": [c.code for c in user.department.categories],
    }


def get_args(return_parse_args=True):
    rp = reqparse.RequestParser()
    rp.add_argument("username", type=str, default="")
    rp.add_argument("password", type=str, default="")
    rp.add_argument("adalToken", type=str, default="")
    rp.add_argument("app", type=str, default="")
    rp.add_argument("token", type=str, default="")
    rp.add_argument("cts", type=int, default=0)
    return rp.parse_args() if return_parse_args else rp


@blueprint.route("/login", methods=["POST"])
@swag_from(
    get_request_parser_doc_dist(
        "login with username/password and return access token",
        ["Authentication"],
        get_args(False),
    )
)
def login():
    """Authenticate user and return token
    """
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400
    user = None
    args = get_args()
    if args.adalToken:
        # adal authtication
        response = requests.get(  # Use token to call downstream service
            "https://graph.windows.net/me?api-version=1.6",
            headers={'Authorization': 'BEARER ' + args.adalToken},
        )

        if response.status_code == 200:
            graph_data = response.json()
            email = graph_data['userPrincipalName']
        else:
            return jsonify({"message": "Invalid adal token"}), 400
        user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
    elif args.app == "excubator" and args.token and args.cts:
        # check cts
        current_milli_time = int(round(time.time()))
        if current_milli_time - args.cts >= 5 * 60 * 60:
            return jsonify({"message": "cts expired"}), 400
        # check token correct
        hl1 = hashlib.md5()
        hl2 = hashlib.md5()
        secret = 'excubator'
        hl1.update(secret.encode(encoding='utf-8'))
        key = hl1.hexdigest() + str(args.cts)
        hl2.update(key.encode(encoding='utf-8'))
        tgt_token = hl2.hexdigest()
        if tgt_token == args.token:
            user = User.where(username='excubator').first()
    else:
        # basic authetication
        if not args.username or not args.password:
            return jsonify({"message": "Missing username or password"}), 400
        user = User.query.filter(func.lower(User.username) == func.lower(args.username)).first()

    if user is None:
        return jsonify({"message": "Invalid User"}), 400
    if not user.active:
        return jsonify({"message": "Current status is not active"}), 400
    if user.is_adal:
        if not args.adalToken:
            return jsonify({"message": "AD authentication is required"}), 400
    else:
        if args.password and not pwd_context.verify(args.password, user.password):
            return jsonify({"message": "Bad credentials"}), 400
    # We can now pass this complex object directly to the
    # create_access_token method. This will allow us to access
    # the properties of this object in the user_claims_loader
    # function, and get the identity of this object from the
    # user_identity_loader function.
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    add_token_to_database(refresh_token, app.config["JWT_IDENTITY_CLAIM"])
    auth_audit_trail.send(app._get_current_object(), event='jwt-auth-login', message='user login using JWT Auth',
                          result='ok', user=user, request=request, extra='extra')
    ret = {"access_token": access_token, "refresh_token": refresh_token, "username": user.username, "email": user.email}
    return jsonify(ret), 200


@blueprint.route("checkEmail")
def check_email():
    mailUsername = request.args.get('mailUsername')
    if mailUsername:
        user = User.query.filter(or_(func.lower(User.username) == func.lower(mailUsername),
                                     func.lower(User.email) == func.lower(mailUsername))).first()
        if user:
            return jsonify({'is_adal': user.is_adal, 'email': user.email}), 200
        else:
            return jsonify({'message': 'invalid user'}), 400
    return jsonify({'message': 'email is required'}), 400


@blueprint.route("/refresh", methods=["POST"])
@swag_from(
    get_request_parser_doc_dist(
        "get refresh token with existing token", ["Authentication"], None
    )
)
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    ret = {"access_token": access_token}
    add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    auth_audit_trail.send(app._get_current_object(), event='jwt-auth-refresh', message='user refresh JWT Auth token',
                          result='ok', user=None, request=request)
    return jsonify(ret), 200


@swag_from(get_request_parser_doc_dist("revoke access token", ["Authentication"], None))
@blueprint.route("/revoke_access", methods=["DELETE"])
@jwt_required
def revoke_access_token():
    jti = get_raw_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


@swag_from(
    get_request_parser_doc_dist("revoke refresh token", ["Authentication"], None)
)
@blueprint.route("/revoke_refresh", methods=["DELETE"])
@jwt_refresh_token_required
def revoke_refresh_token():
    jti = get_raw_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.query.get(identity)


@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


# 过期令牌
@jwt.expired_token_loader
def expired_token_callback(expired_token):
    token_type = expired_token["type"]
    return (
        jsonify(
            {"status": 401, "message": "The {} token has expired".format(token_type)}
        ),
        401,
    )


# 无效令牌
@jwt.invalid_token_loader
def invalid_token_callback(
        error
):  # we have to keep the argument here, since it's passed in by the caller internally

    auth_audit_trail.send(app._get_current_object(), event='jwt-auth-login', message='user login using JWT Auth',
                          result='fail', user=None, request=request)
    return (
        jsonify(
            {"status": 401, "message": "token error: {}".format(error)}
        ),
        401,
    )
