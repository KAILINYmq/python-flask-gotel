from flask import request
from flask_restplus import Resource, reqparse
from flask_jwt_extended import jwt_required
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.models import User, Department, Category, Role
from agile.extensions import ma, db
from agile.commons.pagination import paginate
from marshmallow import fields, ValidationError
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
from agile.decorators import supervisor_or_me_required, admin_required
from flask_jwt_extended import get_jwt_claims, current_user
from flasgger import swag_from
from agile.commons.api_doc_helper import get_request_parser_doc_dist


class CategorySchema(ma.ModelSchema):
    name = fields.String(validate=Length(max=50))
    code = fields.String(validate=Length(max=50))

    class Meta:
        fields = ("id", "name", "code", "group")
        dump_only = ("id",)
        model = Category
        sqla_session = db.session


class RoleSchema(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "name")
        model = Role
        sqla_session = db.session


class DepartmentSchema(ma.ModelSchema):
    name = fields.String(validate=Length(max=50))
    bases_test_quota = fields.Integer(validate=Range(0, 9999))
    pred_idea_quota = fields.Integer(validate=Range(0, 9999))

    class Meta:
        include_fk = False
        model = Department
        sqla_session = db.session


class RoleList(Resource):
    @jwt_required
    @swag_from(get_request_parser_doc_dist("list roles", ["Global"], None, RoleSchema))
    def get(self):
        schema = RoleSchema()
        objects = Role.all()
        return ApiResponse(schema.dump(objects, many=True), ResposeStatus.Success)


class DepartmentList(Resource):
    """Single object resource
    """

    @jwt_required
    @swag_from(
        get_request_parser_doc_dist(
            "list departments", ["Global"], None, DepartmentSchema
        )
    )
    def get(self):
        schema = DepartmentSchema()
        objects = Department.all()
        return ApiResponse(schema.dump(objects, many=True), ResposeStatus.Success)

    @admin_required
    @swag_from(get_request_parser_doc_dist("create new department", ["Global"]))
    def post(self):
        schema = DepartmentSchema()
        try:
            obj = schema.load(request.json)
        except ValidationError as ex:
            return ApiResponse(None, ResposeStatus.ParamFail, ex.messages)
        if Department.where(name=obj.name).first():
            return ApiResponse(
                None,
                ResposeStatus.ParamFail,
                f"Department name[{obj.name}] already exists",
            )
        obj.save()
        db.session.commit()
        return ApiResponse(schema.dump(obj), ResposeStatus.Success)


class DepartmentDetail(Resource):
    """Single object resource
    """

    @admin_required
    @swag_from(
        get_request_parser_doc_dist(
            "delete department by id", ["Global"], None, DepartmentSchema
        )
    )
    def delete(self, dept_id):
        obj = Department.query.get_or_404(dept_id)
        if obj.users.query.count() > 0:
            return ApiResponse(
                None, ResposeStatus.ParamFail, "cannot delete department that has users"
            )
        db.session.remove(obj)
        return ApiResponse(None, ResposeStatus.Success)

    @admin_required
    @swag_from(get_request_parser_doc_dist("create new department", ["Global"]))
    def put(self, dept_id):
        schema = DepartmentSchema(partial=True)
        obj = Department.query.get_or_404(dept_id)
        try:
            obj = schema.load(request.json, instance=obj)
            obj.save()
            db.session.commit()
        except ValidationError as ex:
            db.session.rollback()
            return ApiResponse(None, ResposeStatus.ParamFail, ex.messages)

        return ApiResponse(schema.dump(obj), ResposeStatus.Success)


class CategoryList(Resource):
    """Single object resource
    """

    @jwt_required
    @swag_from(
        get_request_parser_doc_dist("list categories", ["Global"], None, CategorySchema)
    )
    def get(self):
        schema = CategorySchema()
        objects = Category.all()
        return ApiResponse(schema.dump(objects, many=True), ResposeStatus.Success)

    @admin_required
    @swag_from(get_request_parser_doc_dist("create new category", ["Global"]))
    def post(self):
        schema = CategorySchema()
        try:
            obj = schema.load(request.json)
        except ValidationError as ex:
            return ApiResponse(None, ResposeStatus.ParamFail, ex.messages)
        if Category.where(code=obj.code).first():
            return ApiResponse(
                None,
                ResposeStatus.ParamFail,
                f"Category code[{obj.name}] already exists",
            )
        obj.save()
        db.session.commit()
        return ApiResponse(schema.dump(obj), ResposeStatus.Success)
