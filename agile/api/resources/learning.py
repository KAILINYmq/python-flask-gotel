import json
import os
import requests
import shutil
import time
import xlsxwriter
import zipfile

from flask import request, make_response, send_from_directory
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_restplus import Resource
from sqlalchemy import distinct
from sqlalchemy import func, and_

from agile import PROJECT_ROOT
from agile.commons import s3file
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.extensions import db
from agile.models import Learn, Learn_lab, Learn_type, Tag, Praise, Idea, Activities, Idea_lab


# 新增学习
class AddMyLearn(Resource):
    def post(self):
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        student = session.query(Learn).filter(Learn.name == data["name"]).first()
        if student:
            return ApiResponse("", ResposeStatus.Fail, "该名字已经存在")
        # user =Learn.session.filter(func.lower(User.email) == func.lower(email))
        new_user = Learn(name=data["name"], description=data["description"], idea_id=str(data["ideaIdList"]),
                         active_id=data["activeId"], creat_time=now, update_time=now)
        session.add(new_user)
        session.commit()
        for id in data["ideaIdList"]:
            ideadata = session.query(Idea).filter(Idea.id == id).first()
            ideadata.learning_id = new_user.id
        session.commit()
        tag = data["tag"]
        learning = session.query(Learn).filter(Learn.name == data["name"]).first()
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        for value in tag:
            new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)

        for value in data["brand"]:
            new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)

        for value in data["category"]:
            new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)
        session.commit()
        return ApiResponse({"id": learning.id}, ResposeStatus.Success, "OK")


# 查询学习的所有数据
class GetAllLearn(Resource):
    def get(self):
        size = int(request.args.get("size"))
        page = int(request.args.get("page"))
        session = db.session
        student = session.query(Learn).limit(size).offset((page - 1) * size).all()
        data = []
        for value in student:
            parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                             Praise.type == "learning",
                                                                             Praise.is_give == 1).scalar()
            dict = {}
            dict["praiseNum"] = parasnum
            dict["id"] = value.id
            dict["name"] = value.name
            dict["description"] = value.description
            dict["time"] = value.update_time.strftime("%Y/%m/%d")
            dict["image"] = value.image
            dict["video"] = value.video
            labId = session.query(Learn_lab).filter(Learn_lab.idea_id == value.id).all()
            tagName = []
            brandName = []
            categoryName = []
            for id in labId:
                # print(id,"=================")
                labIds = session.query(Tag).filter(Tag.id == id.tag_id).all()
                for lab in labIds:
                    if lab.label_type == "Brand":
                        brandName.append(lab.label)
                    elif lab.label_type == "Category":
                        categoryName.append(lab.label)
                    else:
                        tagName.append(lab.label)
            # dict["tag"] = tagName
            dict["barnd"] = brandName
            dict["category"] = categoryName
            # print(type(dict["ideaId"]),type(value.idea_id),"==================")
            IdeaData = []
            if value.idea_id is not None:
                idealist = json.loads(value.idea_id)
                for val in idealist:
                    ideaDict = {}
                    idea = session.query(Idea).filter(Idea.id == val).first()
                    if idea is not None:
                        ideaDict["id"] = idea.id
                        ideaDict["name"] = idea.name
                        ideaDict["description"] = idea.description
                        ideaDict["time"] = idea.update_time.strftime("%Y/%m/%d")
                        ideaDict["image"] = idea.image
                        ideaDict["video"] = idea.video
                        IdeaData.append(ideaDict)
            dict["idea"] = IdeaData
            data.append(dict)
        # print(data)
        return ApiResponse(data, ResposeStatus.Success)


# 根据tag,brand，category进行查询
class SearchLearning(Resource):
    method_decorators = [jwt_required]

    def get(self):
        session = db.session
        try:
            # data = json.loads(request.get_data(as_text=True))
            tag = int(request.args.get("tag"))
            brand = int(request.args.get("brand"))
            sortTime = int(request.args.get("page"))
            size = int(request.args.get("size"))
            page = int(request.args.get("page"))
            category = int(request.args.get("category"))
            country = str(request.args.get("country"))
            # idd = current_user.id
            # tag = data["tag"]
            # brand =data["brand"]
            # category =data["category"]
            # sortTime =data["sort"]
            # page = int(data["page"])
            # size = int(data["size"])
            idd = current_user.id
            if tag == 0 and brand == 0 and category == 0:
                ideaTotle = []
                if int(sortTime) == 0:
                    student = session.query(Learn).limit(size).offset((page - 1) * size).all()
                    for ide in student:
                        if str(country) == "0":
                            ideaTotle.append(ide)
                        else:
                            if country in ide.activityObject:
                                ideaTotle.append(ide)
                else:
                    student = session.query(Learn).limit(size).offset((page - 1) * size).all()
                    for ide in student:
                        if str(country) == "0":
                            ideaTotle.append(ide)
                        else:
                            if country in ide.activityObject:
                                ideaTotle.append(ide)
                data = []
                dicts = {}
                countSize = session.query(Learn).all()
                countCount = []
                for val in countSize:
                    if str(country) == "0":
                        countCount.append(val)
                    else:
                        if country in val.activityObject:
                            countCount.append(val)
                if len(countCount) % size == 0:
                    dicts["totalNum"] = int(len(countCount) / size)
                else:
                    dicts["totalNum"] = int(len(countCount) / size) + 1
                for value in ideaTotle:
                    parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                                     Praise.type == "learning",
                                                                                     Praise.is_give == 1).scalar()
                    dict = {}
                    parise = Praise.query.filter(Praise.work_id == value.id, Praise.type == "learning",
                                                 Praise.user_id == str(idd), Praise.is_give == 1).first()
                    if parise is not None:
                        dict["isPraise"] = 1
                    else:
                        dict["isPraise"] = 0
                    dict["praiseNum"] = parasnum
                    dict["id"] = value.id
                    dict["name"] = value.name
                    dict["description"] = value.description
                    dict["time"] = value.update_time.strftime("%Y/%m/%d")
                    if value.image is not None and len(value.image) > 0:
                        dict["image"] = json.loads(value.image)
                    else:
                        dict["image"] = []
                    if value.video is not None and len(value.video) > 0:
                        dict["video"] = json.loads(value.video)
                    else:
                        dict["video"] = []
                    labId = session.query(Learn_lab).filter(Learn_lab.idea_id == value.id).all()
                    tagName = []
                    brandName = []
                    categoryName = ""
                    for id in labId:
                        # print(id,"=================")
                        labIds = session.query(Tag).filter(Tag.id == id.tag_id).all()
                        for lab in labIds:
                            if lab.label_type == "Brand":
                                brandName.append(lab.label)
                            elif lab.label_type == "Category":
                                categoryName = lab.label
                            else:
                                tagName.append(lab.label)
                    # dict["tag"] = tagName
                    dict["brand"] = brandName
                    dict["category"] = categoryName
                    # print(type(dict["ideaId"]),type(value.idea_id),"==================")
                    IdeaData = []
                    if value.idea_id is not None and len(value.idea_id) > 0:
                        idealist = json.loads(value.idea_id)
                        for val in idealist:
                            ideaDict = {}
                            idea = session.query(Idea).filter(Idea.id == val).first()
                            if idea is not None:
                                ideaDict["id"] = idea.id
                                ideaDict["name"] = idea.name
                                ideaDict["description"] = idea.description
                                ideaDict["time"] = idea.update_time.strftime("%Y/%m/%d")
                                if idea.image is not None and len(idea.image) > 0:
                                    ideaDict["image"] = json.loads(idea.image)
                                else:
                                    ideaDict["image"] = []
                                if idea.video is not None and len(idea.video) > 0:
                                    ideaDict["video"] = json.loads(idea.video)
                                else:
                                    ideaDict["video"] = []
                                IdeaData.append(ideaDict)
                    dict["idea"] = IdeaData
                    data.append(dict)
                dicts["data"] = data
                session.commit()
                return ApiResponse(dicts, ResposeStatus.Success)
            else:
                session = db.session
                tagnum = []
                # brandnum = []
                # categorynum = []
                tagList = session.query(Learn_lab).filter(Learn_lab.tag_id == tag).all()
                for val in tagList:
                    tagnum.append(val.idea_id)
                brandList = session.query(Learn_lab).filter(Learn_lab.tag_id == brand).all()
                for val in brandList:
                    tagnum.append(val.idea_id)
                categoryList = session.query(Learn_type).filter(Learn_lab.tag_id == category).all()
                for val in categoryList:
                    tagnum.append(val.idea_id)

                # countTotle = session.query(func.count(distinct(Learn.id))).filter(Learn.id.in_(tagnum)).scalar()
                dicts = {}
                result_six = []
                if int(sortTime) == 0:
                    totleCount = session.query(Learn).filter(Idea.id.in_(tagnum)).limit(size).offset((page - 1) * size)
                    for ide in totleCount:
                        if str(country) == "0":
                            result_six.append(ide)
                        else:
                            if country in ide.activityObject:
                                result_six.append(ide)
                else:
                    totleCount = session.query(Learn).filter(Learn.id.in_(tagnum)).order_by(Learn.update_time.asc()).limit(
                        size).offset((page - 1) * size)
                    for ide in totleCount:
                        if str(country) == "0":
                            result_six.append(ide)
                        else:
                            if country in ide.activityObject:
                                result_six.append(ide)
                countSize = session.query(Learn).filter(Learn.id.in_(tagnum)).all()
                countCount = []
                for val in countSize:
                    if str(country) == "0":
                        countCount.append(val)
                    else:
                        if country in val.activityObject:
                            countCount.append(val)

                if len(countCount) % size == 0:
                    dicts["totalNum"] = int(len(countCount) / size)
                else:
                    dicts["totalNum"] = int(len(countCount) / size) + 1

                data = []
                for val in result_six:
                    parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == val.id,
                                                                                     Praise.type == "learning",
                                                                                     Praise.is_give == 1).scalar()

                    dict = {}
                    parise = Praise.query.filter(Praise.work_id == val.id, Praise.type == "learning",
                                                 Praise.user_id == str(idd), Praise.is_give == 1).first()
                    if parise is not None:
                        dict["isPraise"] = 1
                    else:
                        dict["isPraise"] = 0
                    dict["praiseNum"] = parasnum
                    dict["id"] = val.id
                    dict["name"] = val.name
                    dict["description"] = val.description
                    dict["time"] = val.update_time.strftime("%Y/%m/%d")
                    if val.image is not None and len(val.image) > 0:
                        dict["image"] = json.loads(val.image)
                    else:
                        dict["image"] = []
                    if val.video is not None and len(val.video) > 0:
                        dict["video"] = json.loads(val.video)
                    else:
                        dict["video"] = []
                    labId = session.query(Learn_lab).filter(Learn_lab.idea_id == val.id).all()
                    tagName = []
                    brandName = []
                    categoryName = ""
                    for id in labId:
                        # print(id,"=================")
                        labIds = session.query(Tag).filter(Tag.id == id.tag_id).all()
                        for lab in labIds:
                            if lab.label_type == "Brand":
                                brandName.append(lab.label)
                            elif lab.label_type == "Category":
                                categoryName = lab.label
                            else:
                                tagName.append(lab.label)
                    # dict["tag"] = tagName
                    dict["brand"] = brandName
                    dict["category"] = categoryName
                    IdeaData = []
                    if val.idea_id is not None:
                        idealist = json.loads(val.idea_id)
                        for value in idealist:
                            ideaDict = {}
                            idea = session.query(Idea).filter(Idea.id == value).first()
                            if idea is not None:
                                ideaDict["id"] = idea.id
                                ideaDict["name"] = idea.name
                                ideaDict["description"] = idea.description
                                ideaDict["time"] = idea.update_time.strftime("%Y/%m/%d")
                                if idea.image is not None and len(idea.image) > 0:
                                    ideaDict["image"] = json.loads(idea.image)
                                else:
                                    ideaDict["image"] = []
                                if idea.video is not None and len(idea.video) > 0:
                                    ideaDict["video"] = json.loads(idea.video)
                                else:
                                    ideaDict["video"] = []
                                IdeaData.append(ideaDict)
                    dict["Idea"] = IdeaData
                    data.append(dict)
                dicts["data"] = data
                session.commit()
                return ApiResponse(dicts, ResposeStatus.Success)
        except:
            db.session.rollback()
        finally:
            db.session.close()


# 修改
class UpdataLearn(Resource):

    def post(self):
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        learn = session.query(Learn).filter(Learn.id == data["id"]).first()
        learn.name = data["name"]
        learn.description = data["description"]
        learn.update_time = now
        session.query(Learn_lab).filter(Learn_lab.idea_id == data["id"]).delete()
        # session.query(Learn_type).filter(Learn_type.idea_id == data["id"]).delete()
        # session.query(Learn_name).filter(Learn_name.idea_id == data["id"]).delete()
        session.commit()
        tag = data["tag"]
        learning = session.query(Learn).filter(Learn.name == data["name"]).first()

        for value in tag:
            new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)

        for value in data["brand"]:
            new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)

        for value in data["category"]:
            new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)

        session.commit()
        return ApiResponse(data, ResposeStatus.Success)


# 点赞
class Praises(Resource):
    method_decorators = [jwt_required]

    def post(self):
        # 作品id
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        try:
            # 点赞人id
            id = current_user.id
            # id=1
            # print(id, "================")
            # learn
            learn = session.query(Praise).filter(Praise.user_id == id, Praise.work_id == data["id"],
                                                 Praise.type == "learning").first()
            if learn is None:
                now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                new_parise = Praise(user_id=id, type="learning", work_id=data["id"], is_give=1, time=now)
                session.add(new_parise)
                session.commit()
                return ApiResponse("1", ResposeStatus.Success)
            else:
                if learn.is_give == 1:
                    learn.is_give = 0
                    session.commit()
                    return ApiResponse("0", ResposeStatus.Success)
                else:
                    learn.is_give = 1
                    session.commit()
                    return ApiResponse("1", ResposeStatus.Success)
        except:
            db.session.rollback()
        finally:
            db.session.close()


class __SearchLearning(Resource):

    def get(self):
        name = request.args.get("name")
        page = request.args.get("page")
        size = request.args.get("size")
        session = db.session
        names = "%%" + name + "%%"
        nums = session.query(Learn).filter(Learn.name.like(names)).all()
        countTotle = len(nums)
        data = []
        student = session.query(Learn).filter(Learn.name.like(names)).limit(int(size)).offset(
            (int(page) - 1) * int(size)).all()
        dicts = {}
        if countTotle % int(size) == 0:
            dicts["totleNum"] = int(countTotle / int(size))
        else:
            dicts["totleNum"] = int(countTotle / int(size)) + 1
        for value in student:
            parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                             Praise.type == "learning",
                                                                             Praise.is_give == 1).scalar()
            dict = {}
            dict["praiseNum"] = parasnum
            dict["id"] = value.id
            dict["name"] = value.name
            dict["description"] = value.description
            dict["time"] = value.update_time.strftime("%Y/%m/%d")
            dict["image"] = value.image
            dict["video"] = value.video
            labId = session.query(Learn_lab).filter(Learn_lab.idea_id == value.id).all()
            tagName = []
            brandName = []
            categoryName = ""
            for id in labId:
                # print(id,"=================")
                labIds = session.query(Tag).filter(Tag.id == id.tag_id).all()
                for lab in labIds:
                    if lab.label_type == "Brand":
                        brandName.append(lab.label)
                    elif lab.label_type == "Category":
                        categoryName = lab.label
                    else:
                        tagName.append(lab.label)
            # dict["tag"] = tagName
            dict["barnd"] = brandName
            dict["category"] = categoryName
            # print(type(dict["ideaId"]),type(value.idea_id),"==================")
            IdeaData = []
            if value.idea_id is not None:
                idealist = json.loads(value.idea_id)
                for val in idealist:
                    ideaDict = {}
                    idea = session.query(Idea).filter(Idea.id == val).first()
                    if idea is not None:
                        ideaDict["id"] = idea.id
                        ideaDict["name"] = idea.name
                        ideaDict["description"] = idea.description
                        ideaDict["time"] = idea.update_time.strftime("%Y/%m/%d")
                        ideaDict["image"] = idea.image
                        ideaDict["video"] = idea.video
                        IdeaData.append(ideaDict)
            dict["idea"] = IdeaData
            data.append(dict)
        dicts["data"] = data
        session.commit()
        return ApiResponse(dicts, ResposeStatus.Success)


class GetLearning(Resource):

    def get(self, learning_id):
        dict = SecetLearnInfo(learning_id)
        return ApiResponse(dict, ResposeStatus.Success)


def intersect(nums1, nums2):
    import collections
    a, b = map(collections.Counter, (nums1, nums2))
    return list((a & b).elements())


class DownloadLearn(Resource):
    def get(self, learning_id):
        # 1.创建文件夹
        # print(type(learning_id))
        path = PROJECT_ROOT + "/static/"
        fileDownloadPath = path.replace('\\', '/')
        filePath = fileDownloadPath + str("learn" + str(learning_id)) + "/"
        if os.path.exists(filePath):
            shutil.rmtree(filePath)
        os.makedirs(filePath)
        #  2.存储excel
        object = Learn.query.filter(and_(Learn.id == learning_id)).first()
        # image, video, idea, learn = SelectLearnIdea(object.id)
        # active ，查询idea
        image = json.loads(object.image)
        video = json.loads(object.video)
        active = Activities.query.filter(and_(Activities.id == object.active_id)).first()
        idea = Idea.query.filter(and_(Idea.learning_id == learning_id)).all()
        ideaName = []
        for ea in idea:
            ideaName.append(ea.name)
            if ea.image is not None and len(ea.image) > 0:
                imaglist = json.loads(ea.image)
                for im in imaglist:
                    image.append(im)
            if ea.video is not None and len(ea.video) > 0:
                videolist = json.loads(ea.video)
                for vi in videolist:
                    video.append(vi)
        create_workbook(object, filePath + "learn.xlsx", active, ideaName)

        # img = re.findall('GOTFL[^\"]*', str(image))
        # vid = re.findall('GOTFL[^\"]*', str(video))
        img = image
        vid = video
        # 3. 存储图片 存储视频
        if img is not None:
            for i in img:
                getFile(filePath, s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=i),
                        "Image-" + str(i.index(i)) + i[-4:])
        if vid is not None:
            for v in vid:
                getFile(filePath, s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=v),
                        "Video-" + str(v.index(v)) + v[-4:])

                # getFile(filePath, data, "Video" + str(videoUrl.index(data)))
        # 4. 打包zip
        make_zip(filePath, fileDownloadPath + "learn" + str(learning_id) + ".zip")
        # 5. 返回zip
        response = make_response(
            send_from_directory(fileDownloadPath, "learn" + str(learning_id) + ".zip", as_attachment=True))
        return response


def create_workbook(object, filePath, active, Idea):
    # 创建Excel文件,不保存,直接输出
    workbook = xlsxwriter.Workbook(filePath)
    worksheet = workbook.add_worksheet("sheet")
    title = ["Learn Name", "Learn Description", "time", "ActiveName", "ActiveDescription", "Idea"]
    worksheet.write_row('A1', title)
    worksheet.write_row('A2', [str(object.name),
                               str(object.description),
                               str(object.creat_time),
                               # TODO 解析object
                               str(active.active),
                               str(active.description),
                               str(Idea)
                               ])
    workbook.close()


def getFile(filePath, url, fileName):
    response = requests.get(url).content
    with open(filePath + fileName, 'wb') as f:
        f.write(response)
    # print("Sucessful to download " + fileName)


def make_zip(filePath, source_dir):
    zipf = zipfile.ZipFile(source_dir, 'w')
    pre_len = len(os.path.dirname(filePath))
    for parent, dirnames, filenames in os.walk(filePath):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            zipf.write(pathfile, arcname)
    zipf.close()


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


def SecetLearnInfo(id):
    session = db.session
    dict = {}
    try:
        value = session.query(Learn).filter(Learn.id == id).first()

        parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                         Praise.type == "learning",
                                                                         Praise.is_give == 1).scalar()
        dict["id"] = value.id
        dict["name"] = value.name
        dict["description"] = value.description
        dict["praiseNum"] = parasnum
        dict["time"] = value.update_time.strftime("%Y/%m/%d")
        if value.image is not None and len(value.image) > 0:
            dict["image"] = json.loads(value.image)
        else:
            dict["image"] = []
        if value.video is not None and len(value.video) > 0:
            dict["video"] = json.loads(value.video)
        else:
            dict["video"] = []
        labId = session.query(Learn_lab).filter(Learn_lab.idea_id == value.id).all()
        tagName = []
        brandName = []
        categoryName = ""
        for id in labId:
            # print(id,"=================")
            labIds = session.query(Tag).filter(Tag.id == id.tag_id).all()
            for lab in labIds:
                if lab.label_type == "Brand":
                    brandName.append(lab.label)
                elif lab.label_type == "Category":
                    categoryName = lab.label
                else:
                    tagName.append(lab.label)
        dict["tag"] = tagName
        dict["brand"] = brandName
        dict["category"] = categoryName
        # print(type(dict["ideaId"]),type(value.idea_id),"==================")
        IdeaData = []
        if value.idea_id is not None:
            idealist = json.loads(value.idea_id)
            for val in idealist:
                ideaDict = {}
                idea = session.query(Idea).filter(Idea.id == val).first()
                if idea is not None:
                    ideaDict["id"] = idea.id
                    ideaDict["name"] = idea.name
                    ideaDict["description"] = idea.description
                    ideaDict["time"] = idea.update_time.strftime("%Y/%m/%d")

                    labId = session.query(Idea_lab).filter(Idea_lab.idea_id == idea.id).all()
                    tagNamed = []
                    brandNamed = []
                    categoryNamed = ""
                    for id in labId:
                        # print(id,"=================")
                        labIds = session.query(Tag).filter(Tag.id == id.tag_id).all()
                        for lab in labIds:
                            if lab.label_type == "Brand":
                                brandNamed.append(lab.label)
                            elif lab.label_type == "Category":
                                categoryNamed = lab.label
                            else:
                                tagNamed.append(lab.label)
                    # dict["tag"] = tagName
                    ideaDict["brand"] = brandNamed
                    ideaDict["category"] = categoryNamed
                    ideaDict["tag"] = tagNamed

                    if idea.image is not None and len(idea.image) > 0:
                        ideaDict["image"] = json.loads(idea.image)
                    else:
                        ideaDict["image"] = []
                    if idea.video is not None and len(idea.video) > 0:
                        ideaDict["video"] = json.loads(idea.video)
                    else:
                        ideaDict["video"] = []
                    IdeaData.append(ideaDict)
        dict["idea"] = IdeaData
        activedict = {}
        if value.active_id is not None:
            active = session.query(Activities).filter(Activities.id == value.active_id).first()
            activedict["name"] = active.active
            activedict["activeType"] = active.active_type
            activedict["activeTime"] = active.active_time
            activedict["description"] = active.description
            # activedict["image"] = active.image
            # activedict["video"] = active.video
        dict["active"] = activedict
        session.commit()
        return dict
    except:
        db.session.rollback()
        return dict
    finally:
        db.session.close()

