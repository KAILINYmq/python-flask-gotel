# coding: utf-8
from flask import Blueprint, jsonify
from flask_restplus import Api
from agile.api.resources import *
from agile.api.resources.global_ import Ping
from agile.api.resources.learning import *
from agile.api.resources.idea import *
from agile.api.resources.tag import Feedback, InsertTag

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
api.add_resource(ActivitiesList, "/activities/list")
api.add_resource(ActivitiesAdd, "/activities")
# 查询单个活动、删除活动
api.add_resource(SingleActivities, "/activities/<int:activities_id>")
# Activity
api.add_resource(Activity, "/activities/activity")
# Download
api.add_resource(Download, "/activities/download/<int:activities_id>")

# learning
api.add_resource(Praises, "/learning/praise")
api.add_resource(GetLearning, "/learning/<int:learning_id>")
api.add_resource(SearchLearning, "/learning/list")
api.add_resource(DownloadLearn, "/learning/download/<int:learning_id>")


# idea
api.add_resource(PraiseIdea, "/idea/praise")
api.add_resource(GetIdea, "/idea/<int:idea_id>")
api.add_resource(SearchIdea, "/idea/list")
api.add_resource(DownloadIdea, "/idea/download/<int:idea_id>")


# Tag
api.add_resource(TagList, "/tag/list")
api.add_resource(AllTagList, "/allTag/list")
api.add_resource(InsertTag, "/tag")
api.add_resource(Feedback, "/feedback")

# login
api.add_resource(GetHighLightDate, "/highLightDate/list")
api.add_resource(GetAllTotal, "/allTotal/list")
api.add_resource(GetSplitTotal, "/splitTotal/list")
api.add_resource(GetCategory, "/loginCategory/list")
api.add_resource(GetBrand,"/loginBrand/list")