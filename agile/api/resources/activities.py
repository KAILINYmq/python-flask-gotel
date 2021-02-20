from flask import make_response, send_from_directory
from flask_restplus import Resource, reqparse
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.models import Activities, Type_table, Details_table
from agile.extensions import ma, db
from agile import PROJECT_ROOT
from sqlalchemy import and_
import os, zipfile, re
from datetime import datetime
import json, shutil
import xlsxwriter
import requests

# 返回单个数据格式
class ActivitiesSchema(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "active", "active_type", "active_time", "active_object", "idea_name", "learn_name", "description", "image", "video", "status")
        model = Activities
        sqla_session = db.session

# 查询返回数据格式
class ActivitiesSchemas(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "active", "description", "image", "video", "learn_name", "idea_name", "active_type", "create_time")
        model = Activities
        sqla_session = db.session

# 查询返回types 和 details
class ActivitiesSchemaTypes(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "name", "duration_hours", "creat_time")
        model = Type_table
        sqla_session = db.session

class ActivitiesList(Resource):
    # /api/v1/activities/list
    def post(self):
        # 查询活动数据
        # 1.获取参数
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('name')
            parser.add_argument('type')
            parser.add_argument('startTime')
            parser.add_argument('endTime')
            parser.add_argument('learn')
            parser.add_argument('idea')
            parser.add_argument('page', type=int, required=True)
            parser.add_argument('size', type=int, required=True)
            args = parser.parse_args()
            # name = request.args.get('name')
            # type = request.args.get('type')
            # startTime = request.args.get('startTime')
            # endTime = request.args.get('endTime')
            # learn = request.args.get('learn')
            # idea = request.args.get('idea')
            # page = int(request.args.get('page') or 1)
            # size = int(request.args.get('size') or 10)
            # blurry = request.args.get('blurry')
        except Exception as e:
            print(e)
            return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误!")

        # 2. 查询参数
        # schema = ActivitiesSchemas()
        filterList = []
        filterList.append(Activities.is_delete != 1)
        filterList.append(Activities.status == 0)
        try:
            # if blurry is not None:
            #     object = Activities.query.filter(and_(*filterList, or_(Activities.active.like('%' + blurry + '%'),
            #                                          Activities.active_type.like('%' + blurry + '%'),
            #                                          Activities.description.like('%' + blurry + '%'),
            #                                          Activities.idea_name.like('%' + blurry + '%'),
            #                                          Activities.learn_name.like('%' + blurry + '%')
            #                                          ))).offset((page - 1) * size).limit(size)
            #     # 3.返回数据
            #     # data = schema.dump(object, many=True)
            #     paginate = Activities.query.filter(and_(*filterList, or_(Activities.active.like('%' + blurry + '%'),
            #                                          Activities.active_type.like('%' + blurry + '%'),
            #                                          Activities.description.like('%' + blurry + '%'),
            #                                          Activities.idea_name.like('%' + blurry + '%'),
            #                                          Activities.learn_name.like('%' + blurry + '%')
            #                                          ))).paginate(page, size)
            #     return ApiResponse(obj={"activitiesDataData": data, "pages":paginate.pages},
            #                        status=ResposeStatus.Success, msg="OK")
            # else:
            if args["name"] is not None:
                filterList.append(Activities.active == args["name"])
            if args["type"] is not None:
                filterList.append(Activities.active_type == args["type"])
            if args["startTime"] and args["endTime"] is not None:
                filterList.append(Activities.create_time >= datetime.strptime(args["startTime"], '%Y-%m-%d  %H:%M:%S'))
                filterList.append(Activities.create_time <= datetime.strptime(args["endTime"], '%Y-%m-%d  %H:%M:%S'))
            if args["learn"] is not None:
                filterList.append(Activities.idea_name.like('%'+args["learn"]+'%'))
            if args["idea"] is not None:
                filterList.append(Activities.learn_name.like('%'+args["idea"]+'%'))
            object = Activities.query.filter(and_(*filterList)).offset((args["page"]-1) * args["size"]).limit(args["size"])
            # data = schema.dump(object, many=True)
            datas = []
            for k in object:
                data = {}
                data["id"] = k.id
                data["activeName"] = k.active
                data["activeType"] = k.active_type
                data["image"] = k.image
                data["video"] = k.video
                data["description"] = k.description
                data["ideaTags"] = k.idea_name
                data["learnTags"] = k.learn_name
                data["createTime"] = k.create_time
                datas.append(data)
            paginate = Activities.query.filter(and_(*filterList)).paginate(args["page"], args["size"])
            return ApiResponse(obj={"activitiesData": datas, "total":paginate.pages},
                               status=ResposeStatus.Success, msg="OK")
        except Exception as e:
            print(e)
            print(11111)
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
            parser.add_argument('learnId', required=True, help="learnId cannot be blank!")
            args = parser.parse_args()

            # 2. 存储数据
            try:
                active = Activities.query.filter_by(id=args['id']).first()
                active.idea_name = args['idea_name']
                active.learn_name = args['learn_name']
                active.learn_id = args['learnId']
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
    # /activities/<int:activities_id>
    def get(self, activities_id):
        # 查询单个活动数据
        # schema = ActivitiesSchema()
        # object = schema.dump(Activities.query.filter(and_(Activities.id == activities_id, Activities.is_delete != 1)).first())
        object = Activities.query.filter(and_(Activities.id == activities_id, Activities.is_delete != 1)).first()
        data = {}
        data["name"] = object.active
        data["type"] = object.active_type
        data["activeTime"] = object.active_time
        data["activeObject"] = object.active_object
        data["description"] = object.description
        data["ideaName"] = object.idea_name
        data["learnName"] = object.learn_name
        data["video"] = object.video
        data["image"] = object.image
        return ApiResponse(obj=data, status=ResposeStatus.Success, msg="OK")

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
    # /api/v1/activities/activity
    def get(self):
        datas = []
        schema = ActivitiesSchemaTypes()
        object = schema.dump(Type_table.query.all(), many=True)
        for i in range(len(object)):
            data = {}
            data["activityTypes"] = object[i]["name"]
            data["durationHours"] = object[i]["duration_hours"]
            obj = Details_table.query.filter(Details_table.type_id == int(object[i]["id"])).all()
            data["activityDetails"] = []
            for k in obj:
                data["activityDetails"].append(k.name)
            creatTime = datetime.strptime(object[i]["creat_time"][0:10], "%Y-%m-%d")
            nowTime = datetime.strptime(str(datetime.now())[0:10], "%Y-%m-%d")
            data["isNew"] = 1 if (nowTime-creatTime).days < 7 else 0
            datas.append(data)
        return ApiResponse(obj=datas, status=ResposeStatus.Success, msg="OK")

class Download(Resource):
    def get(self, activities_id):
        # 1.创建文件
        path = PROJECT_ROOT+"/static/"
        fileDownloadPath = path.replace('\\', '/')
        filePath = fileDownloadPath+ str(activities_id)+"/"
        if os.path.exists(filePath):
            shutil.rmtree(filePath)
        os.makedirs(filePath)
        #  2.存储excel
        object = Activities.query.filter(and_(Activities.id == activities_id, Activities.is_delete != 1)).first()
        create_workbook(object, filePath+"Active.xlsx")
        # 3. 存储图片 存储视频
        if object.image is not None:
            imageUrl = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(object.image))
            if imageUrl is not None:
                for data in imageUrl:
                    getFile(filePath, data, "Image"+str(imageUrl.index(data)))
        if object.video is not None:
            videoUrl = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(object.video))
            if videoUrl is not None:
                for data in videoUrl:
                    getFile(filePath, data, "Video" + str(videoUrl.index(data)))
        # 4. 打包zip
        make_zip(filePath, fileDownloadPath+str(activities_id)+".zip")
        # 5. 返回zip
        response = make_response(
            send_from_directory(fileDownloadPath, str(activities_id)+".zip", as_attachment=True))
        return response

def create_workbook(object, filePath):
    # 创建Excel文件,不保存,直接输出
    workbook = xlsxwriter.Workbook(filePath)
    worksheet = workbook.add_worksheet("sheet")
    title = ["Activity Types", "Activity Details", "Duration Hours", "With Whom",  "Description", "Learnings", "Ideas"]
    worksheet.write_row('A1', title)
    worksheet.write_row('A2', [str(object.active),
                               str(object.active_type),
                               str(object.active_time),
                               # TODO 解析object
                               str(object.active_object),
                               str(object.description),
                               # TODO 解析Learn
                               str(object.learn_name),
                               #  TODO 解析Idea
                               str(object.idea_name)
                               ])
    workbook.close()

def getFile(filePath, url, fileName):
    response = requests.get(url).content
    with open(filePath+fileName+url[-4:], 'wb') as f:
        f.write(response)
    print ("Sucessful to download "+fileName)

def make_zip(filePath, source_dir):
  zipf = zipfile.ZipFile(source_dir, 'w')
  pre_len = len(os.path.dirname(filePath))
  for parent, dirnames, filenames in os.walk(filePath):
    for filename in filenames:
      pathfile = os.path.join(parent, filename)
      arcname = pathfile[pre_len:].strip(os.path.sep)
      zipf.write(pathfile, arcname)
  zipf.close()