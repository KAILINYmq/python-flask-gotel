# coding: utf-8
from functools import wraps
from flask import abort, current_app, request
from .commons.api_response import ApiResponse, ResposeStatus
from .models import Permission, User
from flask_restplus import reqparse
from flask_jwt_extended import (
    JWTManager, verify_jwt_in_request, create_access_token,
    get_jwt_claims, current_user
)


def permission_required(permission):
    '''定义装饰器
    @permission_required(permission)'''

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            if not current_user.can(permission):
                # 如果当前用户不具有permission则抛出403错误。                  
                return ApiResponse(None, ResposeStatus.Powerless)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    '''定义装饰器
    @admin_required'''
    return permission_required(Permission.ADMINISTER)(f)


def supervisor_or_me_required(f):
    """ wrpaper function with argument user_id"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if 'user_id' not in kwargs:
            return ApiResponse(None, ResposeStatus.ParamFail)
        if len(args) == 1:
            user_id = args[0]
            user = User.query.get_or_404(user_id)
            if not (current_user.is_supervisor or user.id == current_user.id):
                return ApiResponse(None, ResposeStatus.Powerless)
        return f(*args, **kwargs)

    return wrapper


def supervisor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if not current_user.is_supervisor:
            return ApiResponse(None, ResposeStatus.Powerless)
        return f(*args, **kwargs)

    return wrapper


def category_authorization_required(f):
    """ wrpaper function with query arg category, which represent category code"""

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "category" in request.args:
            category_code = request.args["category"]
        else:
            parser = reqparse.RequestParser()
            parser.add_argument(
                "category", location=('values', 'json'), type=str, help="category code"
            )
            args = parser.parse_args()
            category_code = args.category
        if not category_code:
            return ApiResponse(None, ResposeStatus.ParamFail, "Param category not found")
        claims = get_jwt_claims()
        if category_code not in claims['categories']:
            return ApiResponse(None, ResposeStatus.Powerless, "don't have permission to category:%s" % category_code)
        return f(*args, **kwargs)

    return wrapper
