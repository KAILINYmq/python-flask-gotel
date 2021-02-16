# coding: utf-8
from flask import Blueprint, jsonify
from flask_restplus import Api
from agile.api.resources import *
from agile.api.resources.global_ import Ping

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(blueprint)

# user
api.add_resource(MyProfileResource, "/me")
api.add_resource(UserResource, "/users/<int:user_id>")
api.add_resource(UserList, "/users")

# file
api.add_resource(FileList, "/file")

# global
api.add_resource(RoleList, "/role")
api.add_resource(DepartmentList, "/department")
api.add_resource(DepartmentDetail, "/department/<int:dept_id>")
api.add_resource(CategoryList, "/category")

# audit
api.add_resource(AuditLogDetail, "/auditlog")
api.add_resource(UsageReportList, "/usageReport")

# ping
api.add_resource(Ping, "/ping")

# activities
api.add_resource(ActivitiesList, "/activities")
# 查询单个活动、删除活动
api.add_resource(SingleActivities, "/activities/<int:activities_id>")
# activities_name、activities_types
api.add_resource(ActivitiesName, "/activities_name")
api.add_resource(ActivitiesTypes, "/activities_types")