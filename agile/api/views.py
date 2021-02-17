# coding: utf-8
from flask import Blueprint, jsonify
from flask_restplus import Api
from agile.api.resources import *
from agile.api.resources.global_ import Ping
from agile.api.resources.learning import AddMyLearn,GetAllLearn,SortSearch,UpdataLearn
from agile.api.resources.idea import AddMyIdea,GetAllIdea,SortSearchIdea,UpdataIdea
from agile.api.resources.tag import ShowFeedback

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

# learning
api.add_resource(AddMyLearn, "/addLearn")
api.add_resource(GetAllLearn, "/getAll")
api.add_resource(SortSearch, "/search")
api.add_resource(UpdataLearn, "/updata")

# idea
api.add_resource(AddMyIdea, "/addIdea")
api.add_resource(GetAllIdea, "/getAllIdea")
api.add_resource(SortSearchIdea, "/searchIdea")
api.add_resource(UpdataIdea, "/updataIdea")

# Tag
api.add_resource(ActivityName, "/aName/getAll")
api.add_resource(ActivityType, "/aType/getAll")
api.add_resource(TagList, "/tag/getAll")
api.add_resource(AllList, "/settings")
api.add_resource( AddTag, "/addTag" )
api.add_resource(ShowFeedback, "/showFeedback")
