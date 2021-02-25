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
        fields = (
        "id", "active", "active_type", "active_time", "active_object", "description", "image", "video", "status")
        model = Activities
        sqla_session = db.session


# 查询返回数据格式
class ActivitiesSchemas(ma.ModelSchema):
    class Meta:
        include_fk = False
        fields = ("id", "active", "description", "image", "video", "active_type", "create_time")
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
    def has_tag(self, tag_set, tag):
        if not tag:
            return True
        for tag0 in tag_set:
            if tag in tag0:
                return True
        return False

    def SelectLearnIdea(self, learn, idea):
        object = []
        LearnData = Learn.query.filter(Learn.name == learn).all()
        for l in LearnData:
            IdeaData = Idea.query.filter(Idea.name == idea).all()
            object.append(Activities.query.filter(Activities.id == l.active_id).first())
            for i in IdeaData:
                lean = Learn.query.filter(Learn.id == i.learning_id).first()
                object.append(Activities.query.filter(Activities.id == lean.active_id).first())
        return list(filter(None, object))

    def get(self):
        # 查询活动数据
        # 1.获取参数
        args = request.args
        # 2. 查询参数
        filterList = []
        filterList.append(Activities.is_delete == 0)
        try:
            name = args.get("name")
            _type = args.get("type")
            learn = args.get("learn")
            idea = args.get("idea")
            startTime = args.get("startTime")
            endTime = args.get("endTime")
            page = args.get("page")
            size = args.get("size")
            if name == "All":
                name = ""
            if _type == "All":
                _type = ""
            if learn == "All":
                learn = ""
            if idea == "All":
                idea = ""
            if not page:
                page = 1
            if not size:
                size = 10
            page = int(page)
            size = int(size)
            if name:
                filterList.append(Activities.active == name)
            if _type:
                filterList.append(Activities.active_type == _type)
            if startTime and endTime:
                if startTime == endTime:
                    end = startTime.split(" ")[0] + ' 23:59:59'
                    filterList.append(Activities.create_time >= datetime.strptime(startTime, '%Y-%m-%d  %H:%M:%S'))
                    filterList.append(Activities.create_time < datetime.strptime(end, '%Y-%m-%d  %H:%M:%S'))
                else:
                    filterList.append(
                        Activities.create_time >= datetime.strptime(startTime, '%Y-%m-%d  %H:%M:%S'))
                    filterList.append(
                        Activities.create_time <= datetime.strptime(endTime, '%Y-%m-%d  %H:%M:%S'))
            object = Activities.query\
                .filter(and_(*filterList))\
                .order_by(Activities.update_time.desc()) \
                .offset((page - 1) * size) \
                .limit(size)
            paginate = Activities.query.filter(and_(*filterList)).paginate(page, size).pages
            # learn  idea
            if not name and (learn or idea):
                # TODO page
                activitiesObj = self.SelectLearnIdea(learn=learn, idea=idea)
                object = []
                # 对数据进行处理，只保留分页需要的数据
                count = 0
                countPage = 1
                for i in activitiesObj:
                    if countPage == page:
                        object.append(i)

                    count += 1
                    if count % size == 0:
                        countPage += 1
                # object = activitiesObj
                paginate = (len(object)+size-1)//size
            datas = []
            for k in object:
                data = {}
                data["image"] = []
                data["video"] = []
                data["id"] = k.id
                data["activeName"] = k.active
                data["activeType"] = k.active_type
                data["description"] = k.description
                # TODO
                image, video, data["ideaTags"], data["learnTags"] = SelectLearnIdea(k.id)
                img = re.findall('GOTFL[^\"]*', str(image))
                vid = re.findall('GOTFL[^\"]*', str(video))
                if img is not None:
                    for i in img:
                        data["image"].append(s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=i))
                if vid is not None:
                    for v in vid:
                        data["video"].append(s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=v))
                data["createTime"] = str(k.create_time).split(" ")[0]
                datas.append(data)
            return ApiResponse(obj={
                "activitiesData": datas,
                "total": paginate
            },
                status=ResposeStatus.Success, msg="OK")
        except Exception as e:
            print(e)
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
                active.active_object = json.dumps(args['activityObject'])
                active.description = args['activityDescription']
                active.is_delete = 0
                db.session.commit()
                type = SaveActiveAndIdea(current_user.id, active.id, args)
                if type == 1:
                    return ApiResponse(obj=json.dumps({"id": active.id}), status=ResposeStatus.Success, msg="OK")
                elif type == 2:
                    db.session.rollback()
                    return ApiResponse(status=ResposeStatus.ParamFail, msg="Not Have Key!")
                else:
                    db.session.rollback()
                    return ApiResponse(status=ResposeStatus.ParamFail, msg="Change failed！")
            except Exception as e:
                db.session.rollback()
                return ApiResponse(status=ResposeStatus.ParamFail, msg="Change failed！")
        else:
            # 新增
            try:
                activities = Activities(active=args['activityTypes'], active_type=args['activityDetails'],
                                        active_time=args['durationHours'], active_object=json.dumps(args['activityObject']),
                                        description=args['activityDescription'], user_id=current_user.id, is_delete=0)
                db.session.add(activities)
                db.session.commit()
                # if SaveActiveAndIdea(current_user.id, activities.id, args) == 1:
                type = SaveActiveAndIdea(current_user.id, activities.id, args)
                if type == 1:
                    return ApiResponse(obj=json.dumps({"id": activities.id}), status=ResposeStatus.Success, msg="OK")
                elif type == 2:
                    db.session.rollback()
                    return ApiResponse(status=ResposeStatus.ParamFail, msg="Not Have Key!")
                else:
                    db.session.rollback()
                    return ApiResponse(status=ResposeStatus.ParamFail, msg="Add failed！")
            except Exception as e:
                db.session.rollback()
                return ApiResponse(status=ResposeStatus.ParamFail, msg="Add failed！")


class SingleActivities(Resource):
    def get(self, activities_id):
        # 查询单个活动数据
        object = Activities.query.filter(and_(Activities.id == activities_id, Activities.is_delete != 1)).first()
        if object is None:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="No data for this activity！")
        data = {}
        data["activityTypes"] = object.active
        data["activityDetails"] = object.active_type
        data["durationHours"] = object.active_time
        data["activityObject"] = object.active_object
        data["activityDescription"] = object.description
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


class ActivityTypes(Resource):
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
            data["isNew"] = 1 if (nowTime - creatTime).days < 7 else 0
            datas.append(data)
        return ApiResponse(obj=datas, status=ResposeStatus.Success, msg="OK")


class Download(Resource):
    def get(self, activities_id):
        # 1.创建文件夹
        path = PROJECT_ROOT + "/static/"
        fileDownloadPath = path.replace('\\', '/')
        filePath = fileDownloadPath + str(activities_id) + "/"
        if os.path.exists(filePath):
            shutil.rmtree(filePath)
        os.makedirs(filePath)
        #  2.存储excel
        object = Activities.query.filter(and_(Activities.id == activities_id, Activities.is_delete != 1)).first()
        if object is None:
            return ApiResponse(status=ResposeStatus.ParamFail, msg="No data for this activity！")
        image, video, _, _ = SelectLearnIdea(object.id)
        create_workbook(object, filePath + "Activity.xlsx", activities_id)
        img = re.findall('GOTFL[^\"]*', str(image))
        vid = re.findall('GOTFL[^\"]*', str(video))
        # 3. 存储图片 存储视频
        if img is not None:
            for i in img:
                getFile(filePath, s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=i),
                        "Image-" + str(i.index(i)) + i[-4:])
        if vid is not None:
            for v in vid:
                getFile(filePath, s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=v),
                        "Video-" + str(v.index(v)) + v[-4:])
        # 4. 打包zip
        make_zip(filePath, fileDownloadPath + str(activities_id) + ".zip")
        # 5. 返回zip
        response = make_response(
            send_from_directory(fileDownloadPath, str(activities_id) + ".zip", as_attachment=True))
        return response


def create_workbook(object, filePath, activities_id):
    # 创建Excel文件,不保存,直接输出
    workbook = xlsxwriter.Workbook(filePath)
    worksheet = workbook.add_worksheet("sheet")
    title = ["Activity Types", "Activity Details", "Duration Hours",
             "SelectOptions", "Level", "Age", "Gender", "LifeStage", "IncomeLevel", "Occupations",
             "Area", "KidsType", "PetType", "Activity Description",
             "Learning Short Description", "Learning Details", "LearningTags", "Learning Category"]
    worksheet.write_row('A1', title)
    selectOptions = ""
    num = 2
    activities = json.loads(object.active_object.replace("'", "\""))
    for Options in activities["location"]["selectOptions"]:
        selectOptions += Options + ","
    LearnData = Learn.query.filter(and_(Learn.active_id == activities_id)).all()
    for id in LearnData:
        learnDescription = id.name
        learnDetails = id.description
        LearnInfo = SecetLearnInfo(id.id)
        tag = ""
        if LearnInfo['tag'] is not None:
            for Learntag in LearnInfo['tag']:
                tag += Learntag + ","
        worksheet.write_row('O' + str(num), [str(learnDescription), str(learnDetails),
                                             str(tag[0:-1]),
                                             str(LearnInfo['category'])])
        num += 1
    worksheet.write_row('A2', [str(object.active),
                               str(object.active_type),
                               str(object.active_time),
                               str(selectOptions[0:-1]),
                               str(activities["location"]["level"]),
                               str(activities["age"]),
                               str(activities["gender"]),
                               str(activities["lifeStage"]),
                               str(activities["incomeLevel"]),
                               str(activities["occupations"]),
                               str(activities["area"]),
                               str(activities["kidsType"]),
                               str(activities["petType"]),
                               str(object.description)
                               ])
    workbook.close()


def getFile(filePath, url, fileName):
    response = requests.get(url).content
    with open(filePath + fileName, 'wb') as f:
        f.write(response)
    print("Sucessful to download " + fileName)


def make_zip(filePath, source_dir):
    zipf = zipfile.ZipFile(source_dir, 'w')
    pre_len = len(os.path.dirname(filePath))
    for parent, dirnames, filenames in os.walk(filePath):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            zipf.write(pathfile, arcname)
    zipf.close()
