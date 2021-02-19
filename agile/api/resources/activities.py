from flask import request, make_response
from flask_restplus import Resource, reqparse
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.models import Activities, Type_table,Details_table
from agile.extensions import ma, db
from marshmallow import fields
from sqlalchemy import and_
from sqlalchemy import or_
from datetime import datetime
import json
from io import BytesIO
import xlsxwriter

# 返回单个数据格式
class ActivitiesSchema(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "active", "active_type", "active_time", "active_object", "idea_name", "learn_name", "description", "image", "video", "status")
        model = Activities
        sqla_session = db.session

# 下载
class ActivitiesSchemaDownload(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("active", "active_type", "active_object", "idea_name", "learn_name", "description", "active_time")
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
        model = Details_table
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
        filterList.append(Activities.status == 0)
        try:
            if blurry is not None:
                object = Activities.query.filter(and_(*filterList, or_(Activities.active.like('%' + blurry + '%'),
                                                     Activities.active_type.like('%' + blurry + '%'),
                                                     Activities.description.like('%' + blurry + '%'),
                                                     Activities.idea_name.like('%' + blurry + '%'),
                                                     Activities.learn_name.like('%' + blurry + '%')
                                                     ))).offset((page - 1) * size).limit(size)
                # 3.返回数据
                data = schema.dump(object, many=True)
                paginate = Activities.query.filter(and_(*filterList, or_(Activities.active.like('%' + blurry + '%'),
                                                     Activities.active_type.like('%' + blurry + '%'),
                                                     Activities.description.like('%' + blurry + '%'),
                                                     Activities.idea_name.like('%' + blurry + '%'),
                                                     Activities.learn_name.like('%' + blurry + '%')
                                                     ))).paginate(page, size)
                return ApiResponse(obj={"activitiesDataData": data, "pages":paginate.pages},
                                   status=ResposeStatus.Success, msg="OK")
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
                data = schema.dump(object, many=True)
                paginate = Activities.query.filter(and_(*filterList)).paginate(page, size)
                return ApiResponse(obj={"activitiesDataData": data, "pages":paginate.pages},
                                   status=ResposeStatus.Success, msg="OK")
        except Exception:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误!")

class ActivitiesAdd(Resource):
    def post(self):
        # 新增活动
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=int, required=True, help="status cannot be blank!")
        args = parser.parse_args()
        if args['status'] == 1:
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
                                        description=args['description'], status=args['status'])
                db.session.add(activities)
                db.session.commit()
                return ApiResponse(obj=json.dumps({"id": activities.id}), status=ResposeStatus.Success, msg="OK")
            except Exception:
                return ApiResponse(status=ResposeStatus.ParamFail, msg="添加失败！")
        if args['status'] == 2:
            parser.add_argument('id', type=int, required=True, help="id cannot be blank!")
            parser.add_argument('idea_name', required=True, help="idea_name cannot be blank!")
            parser.add_argument('learn_name', required=True, help="learn_name cannot be blank!")
            args = parser.parse_args()

            # 2. 存储数据
            try:
                active = Activities.query.filter_by(id=args['id']).first()
                active.idea_name = args['idea_name']
                active.learn_name = args['learn_name']
                active.status = args['status']
                db.session.commit()
                return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
            except Exception:
                return ApiResponse(status=ResposeStatus.ParamFail, msg="添加失败！")
        if args['status'] == 3:
            parser.add_argument('id', type=int, required=True, help="id cannot be blank!")
            parser.add_argument('image', required=True, help="image cannot be blank!")
            parser.add_argument('video', required=True, help="video cannot be blank!")
            args = parser.parse_args()

            # 2. 存储数据
            try:
                active = Activities.query.filter_by(id=args['id']).first()
                active.image = args['image']
                active.video = args['video']
                active.status = 0
                db.session.commit()
                return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
            except Exception:
                return ApiResponse(status=ResposeStatus.ParamFail, msg="添加失败！")
        return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误！")

    def put(self):
        # 修改活动
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help="id cannot be blank!")
        parser.add_argument('status', type=int, required=True, help="status cannot be blank!")
        args = parser.parse_args()
        if args['status'] == 1:
            parser.add_argument('active', required=True, help="active cannot be blank!")
            parser.add_argument('active_type', required=True, help="active_type cannot be blank!")
            parser.add_argument('active_time', type=int, required=True, help="active_time cannot be blank!")
            parser.add_argument('active_object', required=True, help="active_object cannot be blank!")
            parser.add_argument('description', required=True, help="description cannot be blank!")
            args = parser.parse_args()

            # 2. 存储数据
            try:
                active = Activities.query.filter_by(id=args['id']).first()
                active.active = args['active']
                active.active_type = args['active_type']
                active.active_time = args['active_time']
                active.active_object = args['active_object']
                active.description = args['description']
                active.status = 0
                db.session.commit()
                return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
            except Exception:
                return ApiResponse(status=ResposeStatus.ParamFail, msg="添加失败！")
        if args['status'] == 2:
            parser.add_argument('idea_name', required=True, help="idea_name cannot be blank!")
            parser.add_argument('learn_name', required=True, help="learn_name cannot be blank!")
            args = parser.parse_args()

            # 2. 存储数据
            try:
                active = Activities.query.filter_by(id=args['id']).first()
                active.idea_name = args['idea_name']
                active.learn_name = args['learn_name']
                active.status = 0
                db.session.commit()
                return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
            except Exception:
                return ApiResponse(status=ResposeStatus.ParamFail, msg="添加失败！")
        if args['status'] == 3:
            parser.add_argument('image', required=True, help="image cannot be blank!")
            parser.add_argument('video', required=True, help="video cannot be blank!")
            args = parser.parse_args()

            # 2. 存储数据
            try:
                active = Activities.query.filter_by(id=args['id']).first()
                active.image = args['image']
                active.video = args['video']
                active.status = 0
                db.session.commit()
                return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
            except Exception:
                return ApiResponse(status=ResposeStatus.ParamFail, msg="添加失败！")
        return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误！")


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

class Activity(Resource):
    def get(self):
        # TODO
        schema = ActivitiesSchemaName()
        print(Name_table.query.all())
        print(type(Name_table.query.all()))
        object = schema.dump(Name_table.query.all(), many=True)
        return ApiResponse(obj=object, status=ResposeStatus.Success, msg="OK")

class Download(Resource):
    def get(self, activities_id):
        schema = ActivitiesSchemaDownload()
        object = schema.dump(Activities.query.filter(and_(Activities.id == activities_id, Activities.is_delete != 1)).first())
        print(type(object))
        print(object)
        response = create_workbook(activities_id, object)
        response.headers['Content-Type'] = "utf-8"
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Content-Disposition"] = "attachment; filename=download.xlsx"
        return response

def create_workbook(activities_id, object):
    output = BytesIO()
    # 创建Excel文件,不保存,直接输出
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    # 设置Sheet的名字为download
    worksheet = workbook.add_worksheet('download'+str(activities_id))

    # 列首
    title = ["active", "active_type", "active_object", "idea_name", "learn_name", "description", "active_time"]
    worksheet.write_row('A1', object)
    dictList = [{"a":"a1","b":"b1","c":"c1"}, {"a":"a2","b":"b2","c":"c2"}, {"a":"a3","b":"b3","c":"c3"}]
    for key in object:
        # print(key + ':' + object[key])
        # row = [dictList[i]["a"],dictList[i]["b"], dictList[i]["c"]]
        print(object[key])
        worksheet.write_row('A2',  str(object[key]))
    workbook.close()
    response = make_response(output.getvalue())
    output.close()
    return response