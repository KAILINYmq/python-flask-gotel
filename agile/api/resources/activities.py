from flask import request
from flask_restplus import Resource, reqparse
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.models import Activities, Type_table, Name_table
from agile.extensions import ma, db
from sqlalchemy import and_
from sqlalchemy import or_
import json
from datetime import datetime

# 返回单个数据格式
class ActivitiesSchema(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "active", "active_type", "active_time", "active_object", "description", "status")
        model = Activities
        sqla_session = db.session

# 查询返回数据格式
class ActivitiesSchemas(ma.ModelSchema):
    class Meta:
        include_fk = False
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
            learn = request.args.get('learn')
            idea = request.args.get('idea')
            page = int(request.args.get('page') or 1)
            size = int(request.args.get('size') or 5)
            blurry = request.args.get('blurry')
        except Exception:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误!")

        # 2. 查询参数
        schema = ActivitiesSchemas()
        filterList = []
        filterList.append(Activities.is_delete != 1)
        try:
            if blurry is not None:
                object = Activities.query.filter(or_(Activities.active.like('%' + blurry + '%'),
                                                     Activities.active_type.like('%' + blurry + '%'),
                                                     Activities.description.like('%' + blurry + '%'),
                                                     Activities.idea_name.like('%' + blurry + '%'),
                                                     Activities.learn_name.like('%' + blurry + '%')
                                                     )).offset((page - 1) * size).limit(size)
                # 3.返回数据
                return ApiResponse(obj=schema.dump(object, many=True), status=ResposeStatus.Success, msg="OK")
            else:
                if name is not None:
                    filterList.append(Activities.active == name)
                if type is not None:
                    filterList.append(Activities.active_type == type)
                if startTime and endTime is not None:
                    filterList.append(Activities.create_time >= datetime.strptime(startTime, '%Y-%m-%d  %H:%M:%S'))
                    filterList.append(Activities.create_time <= datetime.strptime(endTime, '%Y-%m-%d  %H:%M:%S'))
                if learn is not None:
                    filterList.append(Activities.idea_name.like('%'+learn+'%'))
                if idea is not None:
                    filterList.append(Activities.learn_name.like('%'+idea+'%'))
                object = Activities.query.filter(and_(*filterList)).offset((page-1) * size).limit(size)
                return ApiResponse(obj=schema.dump(object, many=True), status=ResposeStatus.Success, msg="OK")
        except Exception:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误!")


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
