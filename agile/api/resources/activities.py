from flask import request
from flask_restplus import Resource, reqparse
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.models import Activities, Type_table, Name_table
from agile.extensions import ma, db
from sqlalchemy import and_
import json
from datetime import datetime

# 返回单个数据格式
class ActivitiesSchema(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "active", "active_type", "active_time", "active_object", "description")
        model = Activities
        sqla_session = db.session

# 查询返回数据格式
class ActivitiesSchemas(ma.ModelSchema):
    class Meta:
        include_fk = False
        # TODO learn_id.name
        fields = ("id", "active", "description", "image", "video", "learn_name", "idea_name", "active_type", "create_time")
        model = Activities
        sqla_session = db.session

# 查询返回Name
class ActivitiesSchemaName(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "name")
        model = Name_table
        sqla_session = db.session

# 查询返回type
class ActivitiesSchemaType(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "name")
        model = Type_table
        sqla_session = db.session

class ActivitiesList(Resource):
    def get(self):
        # 查询活动数据
        # 1.获取参数
        try:
            name = request.args.get('name')
            type = request.args.get('type')
            startTime = request.args.get('startTime')
            endTime = request.args.get('endTime')
            learnId = request.args.get('learnId')
            ideaId = request.args.get('ideaId')
        except Exception:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误!")

        # 2. 查询参数
        schema = ActivitiesSchemas()
        try:
            if learnId.strip() and ideaId.strip():
                if startTime.strip() and endTime.strip():
                    return ApiResponse(
                        obj=schema.dump(Activities.query.filter(and_(Activities.active == name, Activities.active_type == type,
                                                                     Activities.learn_id == int(learnId), Activities.idea_id == int(ideaId),
                                                                     Activities.is_delete != 1,
                                                                     Activities.create_time >= datetime.strptime(startTime, '%Y-%m-%d  %H:%M:%S'),
                                                                     Activities.create_time <= datetime.strptime(endTime, '%Y-%m-%d  %H:%M:%S'))), many=True)
                        , status=ResposeStatus.Success, msg="OK")
                return ApiResponse(obj=schema.dump(Activities.query.filter(and_(Activities.active == name, Activities.active_type == type,
                                                                  Activities.learn_id == int(learnId), Activities.idea_id == int(ideaId),
                                                                  Activities.is_delete != 1,)), many=True)
                                   , status=ResposeStatus.Success, msg="OK")
            if learnId.strip():
                if startTime.strip() and endTime.strip():
                    return ApiResponse(
                        obj=schema.dump(Activities.query.filter(and_(Activities.active == name, Activities.active_type == type,
                                                                     Activities.learn_id == int(learnId), Activities.is_delete != 1,
                                                                     Activities.create_time >= datetime.strptime(startTime, '%Y-%m-%d  %H:%M:%S'),
                                                                     Activities.create_time <= datetime.strptime(endTime, '%Y-%m-%d  %H:%M:%S'))), many=True)
                        , status=ResposeStatus.Success, msg="OK")
                return ApiResponse(obj=schema.dump(Activities.query.filter(and_(Activities.active == name, Activities.active_type == type,
                                                                 Activities.learn_id == int(learnId),
                                                                 Activities.is_delete != 1, )), many=True)
                    , status=ResposeStatus.Success, msg="OK")
            if ideaId.strip():
                if startTime.strip() and endTime.strip():
                    return ApiResponse(
                        obj=schema.dump(Activities.query.filter(and_(Activities.active == name, Activities.active_type == type,
                                                                     Activities.idea_id == int(ideaId), Activities.is_delete != 1,
                                                                     Activities.create_time >= datetime.strptime(startTime, '%Y-%m-%d  %H:%M:%S'),
                                                                     Activities.create_time <= datetime.strptime(endTime, '%Y-%m-%d  %H:%M:%S'))), many=True)
                        , status=ResposeStatus.Success, msg="OK")
                return ApiResponse(obj=schema.dump(Activities.query.filter(and_(Activities.active == name, Activities.active_type == type,
                                                                 Activities.idea_id == int(ideaId),
                                                                 Activities.is_delete != 1, )), many=True)
                    , status=ResposeStatus.Success, msg="OK")
            if startTime.strip() and endTime.strip():
                return ApiResponse(
                    obj=schema.dump(
                        Activities.query.filter(and_(Activities.active == name, Activities.active_type == type, Activities.is_delete != 1,
                                                     Activities.create_time >= datetime.strptime(startTime,
                                                                                                 '%Y-%m-%d  %H:%M:%S'),
                                                     Activities.create_time <= datetime.strptime(endTime,
                                                                                                 '%Y-%m-%d  %H:%M:%S'))),
                        many=True)
                    , status=ResposeStatus.Success, msg="OK")
        except Exception as e:
            object = Activities.query.all()
            return ApiResponse(obj=schema.dump(object, many=True), status=ResposeStatus.Success, msg="OK")

    def post(self):
        # 新增活动
        # 1. 获取校验数据
        parser = reqparse.RequestParser()
        parser.add_argument('active', required=True, help="active cannot be blank!")
        parser.add_argument('active_type', required=True, help="active_type cannot be blank!")
        parser.add_argument('active_time', type=int, required=True, help="active_time cannot be blank!")
        parser.add_argument('active_object', required=True, help="active_object cannot be blank!")
        parser.add_argument('description', required=True, help="description cannot be blank!")
        args = parser.parse_args()

        # 2. 存储数据
        try:
            activities = Activities(active=args['active'], active_type=args['active_type'],
                                    active_time=args['active_time'], active_object=args['active_object'],
                                    description=args['description'])
            db.session.add(activities)
            db.session.commit()
        except Exception:
            return ApiResponse(status=ResposeStatus.Success, msg="添加失败！")

        # 3. 返回响应
        return ApiResponse(obj=json.dumps({"id": activities.id}), status=ResposeStatus.Success, msg="OK")

    def put(self):
        # 修改活动
        # 1. 获取校验数据
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help="id cannot be blank!")
        parser.add_argument('active', required=True, help="active cannot be blank!")
        parser.add_argument('active_type', required=True, help="active_type cannot be blank!")
        parser.add_argument('active_time', type=int, required=True, help="active_time cannot be blank!")
        parser.add_argument('active_object', required=True, help="active_object cannot be blank!")
        parser.add_argument('description', required=True, help="description cannot be blank!")
        args = parser.parse_args()

        # 2. 修改数据
        try:
            active = Activities.query.filter_by(id=args['id']).first()
            active.active = args['active']
            active.active_type = args['active_type']
            active.active_time = args['active_time']
            active.active_object = args['active_object']
            active.description = args['description']
            db.session.commit()
        except Exception:
            return ApiResponse(status=ResposeStatus.Success, msg="OK")

        # 3. 返回响应
        return ApiResponse(status=ResposeStatus.Success, msg="OK")


class SingleActivities(Resource):
    def get(self, activities_id):
        # 查询单个活动数据
        schema = ActivitiesSchema()
        object = schema.dump(Activities.query.filter(and_(Activities.id == activities_id, Activities.is_delete != 1)).first())
        return ApiResponse(obj=object, status=ResposeStatus.Success, msg="OK")

    def delete(self, activities_id):
        # 删除活动
        try:
            active = Activities.query.filter_by(id=activities_id).first()
            active.is_delete = 1
            db.session.commit()
        except Exception:
            return ApiResponse(status=ResposeStatus.Success, msg="OK")
        return ApiResponse(status=ResposeStatus.Success, msg="OK")

class ActivitiesName(Resource):
    def get(self):
        schema = ActivitiesSchemaName()
        object = schema.dump(Name_table.query.all(), many=True)
        return ApiResponse(obj=object, status=ResposeStatus.Success, msg="OK")

class ActivitiesTypes(Resource):
    def get(self):
        schema = ActivitiesSchemaType()
        object = schema.dump(Type_table.query.all(), many=True)
        return ApiResponse(obj=object, status=ResposeStatus.Success, msg="OK")
