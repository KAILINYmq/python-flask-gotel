from flask import request, abort
from flask_restplus import Resource, reqparse
from flask_jwt_extended import jwt_required
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.models import (
    User,
    Role,
    Department,
    Category,
)
from agile.extensions import ma, db
from agile.commons.pagination import paginate
from sqlalchemy_mixins import SmartQueryMixin, ReprMixin, JOINED, smart_query
from marshmallow import fields
from marshmallow import INCLUDE, Schema, ValidationError
from marshmallow.validate import (
    URL,
    Email,
    Range,
    Length,
    Equal,
    Regexp,
    Predicate,
    NoneOf,
    OneOf,
    ContainsOnly,
)
from agile.decorators import supervisor_or_me_required, supervisor_required
from flask_jwt_extended import get_jwt_claims, current_user
from flasgger import swag_from
from agile.commons.api_doc_helper import get_request_parser_doc_dist


class CategorySchema(ma.ModelSchema):
    name = fields.String(validate=Length(max=50))
    code = fields.String(validate=Length(max=50))
    group = fields.String(validate=Length(max=50))


class DepartmentSchema(ma.ModelSchema):
    id = fields.Integer()
    name = fields.String(validate=Length(max=50))
    bases_test_quota = fields.Integer(validate=Range(0, 9999))
    pred_idea_quota = fields.Integer(validate=Range(0, 9999))
    categories = fields.Nested(CategorySchema, many=True, only=["name", "code", "group"])


class UserSchema(ma.ModelSchema):
    password = ma.String(load_only=True)
    department = ma.Function(lambda obj: obj.department.name)
    department_id = fields.Integer()
    role = ma.Function(lambda obj: obj.role.name)
    role_id = fields.Integer()
    permissions = ma.Method('dump_permissions')
    created_by = ma.Function(
        lambda obj: obj.created_by.username if obj.created_by else "", dump_only=True
    )
    updated_by = ma.Function(
        lambda obj: obj.updated_by.username if obj.updated_by else "", dump_only=True
    )

    def dump_permissions(self, obj):
        p = obj.role.authorized_permissions()
        if obj.is_supervisor:
            p.append("SUPERVISOR")
        return p

    class Meta:
        # exclude = ("approved_workflows", "finalized_workflows", "password_")
        exclude = ("password_", "is_delete")
        datetimeformat = "%Y-%m-%d"
        model = User
        sqla_session = db.session


class MeSchema(ma.ModelSchema):
    password = ma.String(load_only=True, required=True, default="123456")
    department = fields.Nested(DepartmentSchema, dump_only=True)
    role = ma.Function(lambda obj: obj.role.name)
    permissions = ma.Function(lambda obj: obj.role.authorized_permissions())
    statistics = ma.Method("dump_statistics")
    created_by = ma.Function(
        lambda obj: obj.created_by.username if obj.created_by else "", dump_only=True
    )
    updated_by = ma.Function(
        lambda obj: obj.updated_by.username if obj.updated_by else "", dump_only=True
    )

    class Meta:
        # exclude = ("approved_workflows", "finalized_workflows", "password_")
        exclude = ("password_", "is_delete")
        datetimeformat = "%Y-%m-%d"
        model = User
        sqla_session = db.session


class UserResource(Resource):
    """Single object resource
    """

    method_decorators = [supervisor_or_me_required]

    @swag_from(
        get_request_parser_doc_dist(
            "login with username/password and return access token",
            ["User"],
            None,
            UserSchema,
        )
    )
    def get(self, user_id):
        schema = UserSchema()
        user = User.query.filter(User.is_delete == 0 and User.id == user_id).first()
        if user is None:
            abort(404)
        return ApiResponse(schema.dump(user), ResposeStatus.Success)

    @swag_from(
        get_request_parser_doc_dist("update user profile and permission", ["User"])
    )
    def put(self, user_id):
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_id)
        try:
            user = schema.load(request.json, instance=user)
            user.save()
            db.session.commit()
        except ValidationError as ex:
            return ApiResponse(None, ResposeStatus.ParamFail, ex.messages)

        return ApiResponse(schema.dump(user), ResposeStatus.Success)

    @swag_from(get_request_parser_doc_dist("delete a user", ["User"]))
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        user.is_delete = 1
        user.save()
        # db.session.delete(user)
        db.session.commit()

        return ApiResponse(None, ResposeStatus.Success)


class MyProfileResource(Resource):
    parameters = []
    responses = {
        200: {
            "description": "A list of colors (may be filtered by palette)",
            "schema": MeSchema,
        }
    }

    method_decorators = [jwt_required]

    @swag_from(
        get_request_parser_doc_dist(
            "get my profile",
            ["User"],
            None,
            "return user profile and authorizations",
            MeSchema,
        )
    )
    def get(self):
        schema = MeSchema()
        return ApiResponse(schema.dump(current_user), ResposeStatus.Success)


def get_args(return_parse_args=True):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "sort", default="username", location="args", type=str, help="sort by fields"
    )
    parser.add_argument(
        "filters", default="", location="args", type=str, help="filter by conditions"
    )
    return parser.parse_args() if return_parse_args else parser


class UserList(Resource):
    """Creation and get_all
    """

    method_decorators = [supervisor_required]

    def get(self):
        args = get_args()
        filters = {}
        if args.filters:
            for each in args.filters.split(","):
                items = each.split(":")
                if len(items) == 2 and items[1]:
                    filters[items[0] + "__ilike"] = "%{0}%".format(items[1])
        query = User.smart_query(
            sort_attrs=args.sort.split(","),
            filters=filters,
            schema={"department": JOINED},
        )
        # query = query.with_joined('department', 'department.categories')
        # dump
        schema = UserSchema(many=True)
        return paginate(query, schema)

    def post(self):
        schema = UserSchema()
        errors = schema.validate(request.json)
        if errors:
            return ApiResponse(None, ResposeStatus.ParamFail, errors)
        user = schema.load(request.json)
        if not user.password:
            return ApiResponse(None, ResposeStatus.ParamFail, "Must have a password")
        if User.where(username=user.username).first():
            return ApiResponse(None, ResposeStatus.ParamFail, "User name already in use")
        if User.where(email=user.email).first():
            return ApiResponse(None, ResposeStatus.ParamFail, "Email already in use")
        if user.is_adal is None:
            user.is_adal = user.email.lower().endswith('@unilever.com')
        user.is_delete = 0
        db.session.add(user)
        db.session.commit()

        return ApiResponse(schema.dump(user), ResposeStatus.Success)
