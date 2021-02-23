from flask import request, make_response, send_from_directory
from flask_restplus import Resource, reqparse
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.models import Activities, Type_table, Details_table, Learn, Idea
from agile.extensions import ma, db
from agile import PROJECT_ROOT
from sqlalchemy import and_
import os, zipfile, re, xlsxwriter, requests
from datetime import datetime, timedelta
import json, shutil

from .idea import SaveActiveAndIdea
from .learning import SecetLearnInfo
from agile.commons import s3file
from flask_jwt_extended import current_user, jwt_required


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
        except Exception as e:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误!")

        # 2. 查询参数
        filterList = []
        filterList.append(Activities.is_delete != 1)
        try:
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
            datas = []
            for k in object:
                data = {}
                data["image"] = []
                data["video"] = []
                data["id"] = k.id
                data["activeName"] = k.active
                data["activeType"] = k.active_type
                data["description"] = k.description
                image, video, data["ideaTags"], data["learnTags"] = SelectLearnIdea(k.id)
                img = re.findall('GOTFL[^\"]*', str(image))
                vid = re.findall('GOTFL[^\"]*', str(video))
                if img is not None:
                    for i in img:
                        data["image"].append(s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=i))
                if vid is not None:
                    for v in vid:
                        data["video"].append(s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=v))
                data["createTime"] = datetime.date(k.create_time + timedelta(days=1))
                datas.append(data)
            paginate = Activities.query.filter(and_(*filterList)).paginate(args["page"], args["size"])
            return ApiResponse(obj={"activitiesData": datas, "total":paginate.pages},
                               status=ResposeStatus.Success, msg="OK")
        except Exception as e:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误!")

def SelectLearnIdea(id):
    Image = []
    Video = []
    IdeaTag = []
    LearnTags = []
    LearnData = Learn.query.filter(and_(Learn.active_id == id)).all()
    for l in LearnData:
        IdeaData = Idea.query.filter(and_(Idea.learning_id == l.id)).all()
        for i in IdeaData:
            IdeaTag.append(i.name)
            Image.append(i.image)
            Video.append(i.video)
        Image.append(l.image)
        Video.append(l.video)
        LearnTags.append(l.name)
    return set(filter(None, Image)), set(filter(None, Video)), set(filter(None, IdeaTag)), set(filter(None, LearnTags))



class ActivitiesAdd(Resource):
    method_decorators = [jwt_required]

    def post(self):
        # 新增活动
        # 验证登录
        try:
            if current_user.id is None:
                return ApiResponse(status=ResposeStatus.AuthenticationFailed, msg="Please log in and try again！")
        except Exception:
            return ApiResponse(status=ResposeStatus.AuthenticationFailed, msg="Please log in and try again！")

        args = json.loads(request.get_data(as_text=True))
        if args["id"] is not None and args["id"] > 0:
            # 修改
            try:
                active = Activities.query.filter_by(id=args['id']).first()
                active.active = args['activityTypes']
                active.active_type = args['activityDetails']
                active.active_time = args['durationHours']
                active.active_object = args['activityObject']
                active.description = args['activityDescription']
                active.is_delete = 0
                db.session.commit()
                if SaveActiveAndIdea(current_user.id, active.id, args) == 1:
                    return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
                else:
                    db.session.rollback()
                    return ApiResponse(status=ResposeStatus.ParamFail, msg="Change failed！")
            except Exception as e:
                db.session.rollback()
                return ApiResponse(status=ResposeStatus.ParamFail, msg="Change failed！")
        else:
            # 新增
            try:
                activities = Activities( active = args['activityTypes'], active_type = args['activityDetails'],
                                        active_time=args['durationHours'], active_object=args['activityObject'],
                                        description=args['activityDescription'], user_id = current_user.id, is_delete = 0)
                db.session.add(activities)
                db.session.commit()
                if SaveActiveAndIdea(current_user.id, activities.id, args) == 1:
                    return ApiResponse(obj=json.dumps({"id": activities.id}), status=ResposeStatus.Success, msg="OK")
                else:
                    db.session.rollback()
                    return ApiResponse(status=ResposeStatus.ParamFail, msg="Add failed！")
            except Exception as e:
                db.session.rollback()
                return ApiResponse(status=ResposeStatus.ParamFail, msg="Add failed！")
    # def put(self):
    #     # 修改活动
    #     parser = reqparse.RequestParser()
    #     parser.add_argument('id', type=int, required=True, help="id cannot be blank!")
    #     parser.add_argument('status', type=int, required=True, help="status cannot be blank!")
    #     args = parser.parse_args()
    #     if args['status'] == 1:
    #         parser.add_argument('active', required=True, help="active cannot be blank!")
    #         parser.add_argument('active_type', required=True, help="active_type cannot be blank!")
    #         parser.add_argument('active_time', type=int, required=True, help="active_time cannot be blank!")
    #         parser.add_argument('active_object', required=True, help="active_object cannot be blank!")
    #         parser.add_argument('description', required=True, help="description cannot be blank!")
    #         args = parser.parse_args()
    #
    #         # 2. 存储数据
    #         try:
    #             active = Activities.query.filter_by(id=args['id']).first()
    #             active.active = args['active']
    #             active.active_type = args['active_type']
    #             active.active_time = args['active_time']
    #             active.active_object = args['active_object']
    #             active.description = args['description']
    #             active.status = 0
    #             db.session.commit()
    #             return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
    #         except Exception:
    #             return ApiResponse(status=ResposeStatus.ParamFail, msg="Add failed！")
    #     if args['status'] == 2:
    #         parser.add_argument('idea_name', required=True, help="idea_name cannot be blank!")
    #         parser.add_argument('learn_name', required=True, help="learn_name cannot be blank!")
    #         args = parser.parse_args()
    #
    #         # 2. 存储数据
    #         try:
    #             active = Activities.query.filter_by(id=args['id']).first()
    #             active.idea_name = args['idea_name']
    #             active.learn_name = args['learn_name']
    #             active.status = 0
    #             db.session.commit()
    #             return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
    #         except Exception:
    #             return ApiResponse(status=ResposeStatus.ParamFail, msg="Add failed！")
    #     if args['status'] == 3:
    #         parser.add_argument('image', required=True, help="image cannot be blank!")
    #         parser.add_argument('video', required=True, help="video cannot be blank!")
    #         args = parser.parse_args()
    #
    #         # 2. 存储数据
    #         try:
    #             active = Activities.query.filter_by(id=args['id']).first()
    #             active.image = args['image']
    #             active.video = args['video']
    #             active.status = 0
    #             db.session.commit()
    #             return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
    #         except Exception:
    #             return ApiResponse(status=ResposeStatus.ParamFail, msg="Add failed！")
    #     return ApiResponse(status=ResposeStatus.ParamFail, msg="参数错误！")

class SingleActivities(Resource):
    def get(self, activities_id):
        # 查询单个活动数据
        object = Activities.query.filter(and_(Activities.id == activities_id, Activities.is_delete != 1)).first()
        if object is None:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="No data for this activity！")
        data = {}
        data["name"] = object.active
        data["type"] = object.active_type
        data["activeTime"] = object.active_time
        data["activeObject"] = object.active_object
        data["description"] = object.description
        data["learnings"] = []
        LearnData = Learn.query.filter(and_(Learn.active_id == activities_id)).all()
        for l in LearnData:
            try:
                learn = SecetLearnInfo(l.id)
                data["learnings"].append(learn)
            except Exception:
                pass
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
        # 1.创建文件夹
        path = PROJECT_ROOT+"/static/"
        fileDownloadPath = path.replace('\\', '/')
        filePath = fileDownloadPath+ str(activities_id)+"/"
        if os.path.exists(filePath):
            shutil.rmtree(filePath)
        os.makedirs(filePath)
        #  2.存储excel
        object = Activities.query.filter(and_(Activities.id == activities_id, Activities.is_delete != 1)).first()
        if object is None:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="No data for this activity！")
        image, video, idea, learn = SelectLearnIdea(object.id)
        create_workbook(object, filePath+"Active.xlsx", idea, learn)
        img = re.findall('GOTFL[^\"]*', str(image))
        vid = re.findall('GOTFL[^\"]*', str(video))
        # 3. 存储图片 存储视频
        if img is not None:
            for i in img:
                getFile(filePath, s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=i), "Image-" + str(i.index(i))+i[-4:])
        if vid is not None:
            for v in vid:
                getFile(filePath, s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=v), "Video-" + str(v.index(v))+v[-4:])
        # 4. 打包zip
        make_zip(filePath, fileDownloadPath+str(activities_id)+".zip")
        # 5. 返回zip
        response = make_response(
            send_from_directory(fileDownloadPath, str(activities_id)+".zip", as_attachment=True))
        return response

def create_workbook(object, filePath, idea, learn):
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
                               str(idea),
                               str(learn)
                               ])
    workbook.close()

def getFile(filePath, url, fileName):
    response = requests.get(url).content
    with open(filePath+fileName, 'wb') as f:
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