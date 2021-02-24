import json
import os
import requests
import shutil
import time
import xlsxwriter
import zipfile
import datetime
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
from agile.models import Idea, Idea_lab, Tag, Praise, Learn, Activities, Learn_lab


# 新增学习
class AddMyIdea(Resource):
    def post(self):

        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        student = session.query(Idea).filter(Idea.name == data["name"]).first()
        if student:
            return ApiResponse("", ResposeStatus.Fail, "该名字已经存在")
        new_user = Idea(name=data["name"], description=data["description"], creat_time=now, update_time=now)
        session.add(new_user)
        session.commit()
        tag = data["tag"]
        learning = session.query(Idea).filter(Idea.name == data["name"]).first()
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        for value in tag:
            new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)

        for value in data["brand"]:
            new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now,
                                       is_delete=0)
            session.add(new_learn_lable)

        for value in data["category"]:
            new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now,
                                       is_delete=0)
            session.add(new_learn_lable)

        session.commit()
        return ApiResponse({
            "id": learning.id
        }, ResposeStatus.Success, "OK")


# 查询学习的所有数据
class GetAllIdea(Resource):
    def get(self):
        size = int(request.args.get("size"))
        page = int(request.args.get("page"))
        session = db.session
        student = session.query(Idea).limit(size).offset((page - 1) * size).all()
        data = []
        for value in student:
            parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                             Praise.type == "idea",
                                                                             Praise.is_give == 1).scalar()
            dict = {}
            dict["praiseNum"] = parasnum
            dict["id"] = value.id
            dict["name"] = value.name
            dict["description"] = value.description
            dict["time"] = value.update_time.strftime("%Y/%m/%d")
            dict["image"] = value.image
            dict["video"] = value.video
            labId = session.query(Idea_lab).filter(Idea_lab.idea_id == value.id).all()
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
            dict["brand"] = brandName
            dict["category"] = categoryName
            data.append(dict)
        return ApiResponse(data, ResposeStatus.Success)


# 根据tag,brand，category进行查询
class SearchIdea(Resource):
    method_decorators = [jwt_required]

    def get(self):
        session = db.session
        try:
            idd = current_user.id
            # page = int(data["page"])
            # size = int(data["size"])
            tag = int(request.args.get("tag"))
            brand = int(request.args.get("brand"))
            sortTime = int(request.args.get("sort"))
            size = int(request.args.get("size"))
            page = int(request.args.get("page"))
            category = int(request.args.get("category"))
            country = str(request.args.get("country"))
            if tag == 0 and brand == 0 and category == 0 :
                ideaTotle = []
                if int(sortTime) == 0:
                    student = session.query(Idea).limit(size).offset((page - 1) * size).all()
                    for ide in student:
                        if str(country) =="0":
                            ideaTotle.append(ide)
                        else:
                            if country in ide.activityObject:
                                ideaTotle.append(ide)
                else:
                    student = session.query(Idea).order_by(Idea.update_time.asc()).limit(size).offset((page - 1) * size).all()
                    for ide in student:
                        if str(country) =="0":
                            ideaTotle.append(ide)
                        else:
                            if country in ide.activityObject:
                                ideaTotle.append(ide)
                data = []
                dicts = {}
                countSize = session.query(Idea).all()
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
                                                                                     Praise.type == "idea",
                                                                                     Praise.is_give == 1).scalar()
                    dict = {}
                    parise = Praise.query.filter(Praise.work_id == value.id, Praise.type == "idea",
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
                    labId = session.query(Idea_lab).filter(Idea_lab.idea_id == value.id).all()
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
                    data.append(dict)
                dicts["data"] = data
                session.commit()
                return ApiResponse(dicts, ResposeStatus.Success)
            else:

                tagnum = []
                # brandnum = []
                # categorynum = []
                tagList = session.query(Idea_lab).filter(Idea_lab.tag_id == tag).all()
                for val in tagList:
                    tagnum.append(val.idea_id)
                brandList = session.query(Idea_lab).filter(Idea_lab.tag_id == brand).all()
                for val in brandList:
                    tagnum.append(val.idea_id)
                categoryList = session.query(Idea_lab).filter(Idea_lab.tag_id == category).all()
                for val in categoryList:
                    tagnum.append(val.idea_id)

                dicts = {}
                result_six = []
                if int(sortTime) == 0:
                    totleCount = session.query(Idea).filter(Idea.id.in_(tagnum)).limit(size).offset((page - 1) * size)
                    for ide in totleCount:
                        if str(country) =="0":
                            result_six.append(ide)
                        else:
                            if country in ide.activityObject:
                                result_six.append(ide)
                else:
                    totleCount = session.query(Idea).filter(Idea.id.in_(tagnum)).order_by(Idea.update_time.asc()).limit(size).offset((page - 1) * size)
                    for ide in totleCount:
                        if str(country) == "0":
                            result_six.append(ide)
                        else:
                            if country in ide.activityObject:
                                result_six.append(ide)
                countSize = session.query(Idea).filter(Idea.id.in_(tagnum)).all()
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
                                                                                     Praise.type == "idea",
                                                                                     Praise.is_give == 1).scalar()
                    dict = {}
                    parise = Praise.query.filter(Praise.work_id == val.id, Praise.type == "idea",
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
                    labId = session.query(Idea_lab).filter(Idea_lab.idea_id == val.id).all()
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
                    data.append(dict)
                dicts["data"] = data
                session.commit()
                return ApiResponse(dicts, ResposeStatus.Success)
        except:
            db.session.rollback()
        finally:
            db.session.close()


# 修改
class UpdataIdea(Resource):

    def post(self):
        data = json.loads(request.get_data(as_text=True))
        session = db.session

        learn = session.query(Idea).filter(Idea.id == data["id"]).first()
        learn.name = data["name"]
        learn.description = data["description"]
        session.query(Idea_lab).filter(Idea_lab.idea_id == data["id"]).delete()
        # session.query(Idea_type).filter(Idea_type.idea_id == data["id"]).delete()
        # session.query(Idea_name).filter(Idea_name.idea_id == data["id"]).delete()
        session.commit()
        tag = data["tag"]
        learning = session.query(Idea).filter(Idea.name == data["name"]).first()
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        for value in tag:
            new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)

        for value in data["brand"]:
            new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)

        for value in data["category"]:
            new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now, is_delete=0)
            session.add(new_learn_lable)

        session.commit()
        return ApiResponse(data, ResposeStatus.Success)


# 点赞
class PraiseIdea(Resource):
    method_decorators = [jwt_required]

    def post(self):
        # 作品id
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        try:
            # 点赞人id
            id = current_user.id
            # id=1
            # learn
            learn = session.query(Praise).filter(Praise.user_id == id, Praise.work_id == data["id"],
                                                 Praise.type == "idea").first()
            if learn is None:
                now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                new_parise = Praise(user_id=id, type="idea", work_id=data["id"], is_give=1, time=now)
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


class SearchIdea__(Resource):

    def get(self):
        name = request.args.get("name")
        page = request.args.get("page")
        size = request.args.get("size")
        session = db.session
        names = "%%" + name + "%%"
        nums = session.query(Idea).filter(Idea.name.like(names)).all()
        countTotle = len(nums)
        data = []
        student = session.query(Idea).filter(Idea.name.like(names)).limit(int(size)).offset(
            (int(page) - 1) * int(size)).all()
        dicts = {}
        if countTotle % int(size) == 0:
            dicts["TotleNum"] = int(countTotle / int(size))
        else:
            dicts["TotleNum"] = int(countTotle / int(size)) + 1
        for value in student:
            parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                             Praise.type == "idea",
                                                                             Praise.is_give == 1).scalar()
            dict = {}
            dict["praiseNum"] = parasnum
            dict["id"] = value.id
            dict["name"] = value.name
            dict["description"] = value.description
            dict["time"] = value.update_time.strftime("%Y/%m/%d")
            dict["image"] = value.image
            dict["video"] = value.video
            labId = session.query(Idea_lab).filter(Idea_lab.idea_id == value.id).all()
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
            data.append(dict)
        dicts["data"] = data
        session.commit()
        return ApiResponse(dicts, ResposeStatus.Success)


class GetIdea(Resource):
    def get(self, idea_id):
        session = db.session
        try:
            value = session.query(Idea).filter(Idea.id == idea_id).first()
            parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                             Praise.type == "idea",
                                                                             Praise.is_give == 1).scalar()
            dict = {}
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
            img =[]
            vio =[]
            try:
                if dict["image"] is not None and len(dict["image"]) > 0:
                    for i in dict["image"]:
                        img.append(s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=i))
                if dict["video"] is not None and len(dict["video"]) > 0:
                    for i in dict["video"]:
                        vio.append(s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=i))
            except:
                dict["image"] = []
                dict["video"] = []
            dict["image"] = img
            dict["video"] = vio

            labId = session.query(Idea_lab).filter(Idea_lab.idea_id == value.id).all()
            tagName = []
            brandName = []
            categoryName = ""
            for id in labId:
                labIds = session.query(Tag).filter(Tag.id == id.tag_id).all()
                for lab in labIds:
                    if lab.label_type == "Brand":
                        brandName.append(lab.label)
                        tagName.append(lab.label)
                    elif lab.label_type == "Category":
                        categoryName = lab.label
                        tagName.append(lab.label)
                    else:
                        tagName.append(lab.label)
            # dict["tag"] = tagName
            dict["barnd"] = brandName
            dict["category"] = categoryName
            dict["tag"] = tagName
            learn = session.query(Learn).filter(Learn.id == value.learning_id).first()
            learndict = {}
            learndict["id"] = learn.id
            learndict["name"] = learn.name
            learndict["description"] = learn.description
            labId = session.query(Learn_lab).filter(Learn_lab.idea_id == value.id).all()
            tagNamed = []
            brandNamed = []
            categoryNamed = ""
            for id in labId:
                # print(id,"=================")
                labIdss = session.query(Tag).filter(Tag.id == id.tag_id).all()
                for lab in labIdss:
                    if lab.label_type == "Brand":
                        brandNamed.append(lab.label)
                        tagNamed.append(lab.label)
                    elif lab.label_type == "Category":
                        categoryNamed = lab.label
                        tagNamed.append(lab.label)
                    else:
                        tagNamed.append(lab.label)
            learndict["tag"] = tagNamed
            learndict["barnd"] = brandNamed
            learndict["category"] = categoryNamed
            if learn.image is not None and len(learn.image) > 0:
                learndict["image"] = json.loads(value.image)
            else:
                learndict["image"] = []
            if learn.video is not None and len(learn.video) > 0:
                learndict["video"] = json.loads(value.video)
            else:
                learndict["video"] = []
            img = []
            vio = []
            try:
                if learndict["image"] is not None and len(learndict["image"]) > 0:
                    for i in learndict["image"]:
                        img.append(s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=i))
                if learndict["video"] is not None and len(learndict["video"]) > 0:
                    for i in learndict["video"]:
                        vio.append(s3file.DEFAULT_BUCKET.generate_presigned_url(obj_key=i))
            except:
                learndict["image"] = []
                learndict["video"] = []
            learndict["image"] = img
            learndict["video"] = vio

            learndict["time"] = learn.update_time.strftime("%Y/%m/%d")
            dict["learning"] = learndict
            active = session.query(Activities).filter(Activities.id == learn.active_id).first()
            activedict = {}
            activedict["name"] = active.active
            activedict["activeType"] = active.active_type
            activedict["activeTime"] = active.active_time
            activedict["description"] = active.description
            # activedict["image"] = active.image
            # activedict["video"] = active.video
            dict["active"] = activedict
            return ApiResponse(dict, ResposeStatus.Success)
        except:
            db.session.rollback()
        finally:
            db.session.close()


def SaveActiveAndIdea(userId, activeIds, datas):
        # shuju = '''{
        #     "activityObject":"{"location":{"selectOptions":["11","1101","110101","110101001"],"level":"一线"},"age":"21-25","gender":0,"lifeStage":"Single/单身贵族","incomeLevel":"The Mid Class/小康家庭","occupations":"Students/学生","area":"","kidsType":"School Age/学龄","petType":"Cat/猫"}",
        #     "learnings": [{
        #     "name": "learning1 speak",
        #     "description": "learning spea",
        #     "tags": [28,25],
        #     "brands": [25,28],
        #     "category": 25,
        #     "imageUrls": ["dddd","dddddawd"],
        #     "videoUrls": ["wdawdad","Dawdawdad"],
        #     "ideas": [{
        #             "name": "344wwddeqewdeqwewd我",
        #             "description": "你说队列",
        #             "tags": [25],
        #             "brands": [26],
        #             "category": 25,
        #             "imageUrls": ["安徽嗲d文化","dawddawd"],
        #             "videoUrls": ["dawdaddad","dawddad"]
        #         },
        #         {
        #         "name": "非deqwdddedeqeqeeaeeqw想你",
        #         "description": "zouzdai1dhawdj1",
        #         "tags": [25],
        #         "brands": [26],
        #         "category": 27,
        #         "imageUrls": ["whddauwdj","dawddjawdil"],
        #         "videoUrls": ["dawiddjawdi","daddawd"]
        #             }
        #         ]
        #         }]
        #         }'''
        # print(datas, type(datas))
        # aa =json.loads(shuju)

        # datas = aa
        # print(datas,type(datas))
        session = db.session
        try:
            # activityObject
            if len(datas["learnings"])>0:
                for lern in datas["learnings"]:
                    idealist = []
                    now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                    # print(datas["activityObject"], "=11====")
                    im = json.dumps(lern["imageUrls"])
                    vi = json.dumps(lern["videoUrls"])
                    # print(datas["activityObject"],"=====")
                    new_user = Learn(name=lern["name"], description=lern["description"], active_id=activeIds,
                                     image=im, video=vi, user_id=userId,activityObject=datas["activityObject"],creat_time=now,
                                     update_time=now)
                    session.add(new_user)
                    # print(datas["activityObject"], "11=====")
                    session.commit()
                    tag = lern["tags"]
                    learning = session.query(Learn).filter(Learn.id == new_user.id).first()

                    now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                    # print(tag)
                    for value in tag:
                        new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now,
                                                    is_delete=0)
                        session.add(new_learn_lable)
                        session.commit()
                    for value in lern["brands"]:
                        new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now,
                                                    is_delete=0)
                        session.add(new_learn_lable)
                        session.commit()
                    # for value in lern["category"]:
                    new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=lern["category"], creat_time=now, update_time=now,
                                                is_delete=0)
                    session.add(new_learn_lable)
                    session.commit()
                    if len(lern["ideas"]) > 0:
                        for idea in lern["ideas"]:
                            # now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                            # data = json.loads(request.get_data(as_text=True))
                            # student = session.query(Idea).filter(Idea.name == idea["name"]).first()
                            # if student:
                            #     return ApiResponse("", ResposeStatus.Fail, "该名字已经存在")
                            ims = json.dumps(idea["imageUrls"])
                            vis = json.dumps(idea["videoUrls"])
                            new_users = Idea(name=idea["name"], description=idea["description"], user_id=userId,
                                             image=ims, video=vis, learning_id=new_user.id,activityObject=datas["activityObject"],
                                             creat_time=now, update_time=now)
                            session.add(new_users)
                            session.commit()
                            tag = idea["tags"]
                            learning = session.query(Idea).filter(Idea.id == new_users.id).first()
                            now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                            for value in tag:
                                new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now,
                                                           is_delete=0)
                                session.add(new_learn_lable)

                            for value in idea["brands"]:
                                new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now,
                                                           is_delete=0)
                                session.add(new_learn_lable)

                            # for value in idea["category"]:
                            new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=idea["category"], creat_time=now, update_time=now,
                                                       is_delete=0)
                            session.add(new_learn_lable)
                            idealist.append(new_users.id)
                            session.commit()
                    learninfo = session.query(Learn).filter(Learn.id == new_user.id).first()
                    learninfo.idea_id = str(idealist)
                    session.commit()
            return 1
        except:
            db.session.rollback()
            return 0
        finally:
            db.session.close()


class DownloadIdea(Resource):
    def get(self, idea_id):
        # 1.创建文件夹
        path = PROJECT_ROOT + "/static/"
        fileDownloadPath = path.replace('\\', '/')
        filePath = fileDownloadPath + str("idea" + str(idea_id)) + "/"
        if os.path.exists(filePath):
            shutil.rmtree(filePath)
        os.makedirs(filePath)
        #  2.存储excel
        object = Idea.query.filter(and_(Idea.id == idea_id)).first()
        # image, video, idea, learn = SelectLearnIdea(object.id)
        # active ，查询idea
        # print(object.image, "==", type(object.image))
        image = []
        video = []
        learning = Learn.query.filter(and_(Learn.id == object.learning_id)).first()
        active = Activities.query.filter(and_(Activities.id == learning.active_id)).first()
        if learning.image is not None and len(learning.image) > 0:
            for im in json.loads(learning.image):
                image.append(im)
        if learning.video is not None and len(learning.video) > 0:
            for vi in json.loads(learning.video):
                video.append(vi)
        if object.image is not None and len(object.image) > 0:
            for im in json.loads(object.image):
                image.append(im)
        if object.video is not None and len(object.video) > 0:
            for vi in json.loads(object.video):
                video.append(vi)
        create_workbook(object, filePath + "idea.xlsx", active, learning)
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
        # 4. 打包zip
        make_zip(filePath, fileDownloadPath + "idea" + str(idea_id) + ".zip")
        # 5. 返回zip
        response = make_response(
            send_from_directory(fileDownloadPath, "idea" + str(idea_id) + ".zip", as_attachment=True))
        return response


def create_workbook(object, filePath, active, learn):
    # 创建Excel文件,不保存,直接输出
    workbook = xlsxwriter.Workbook(filePath)
    worksheet = workbook.add_worksheet("sheet")
    title = ["Idea Name", "Idea Description", "time", "ActiveName", "ActiveDescription", "LearningName",
             "LearningDescription"]
    worksheet.write_row('A1', title)
    worksheet.write_row('A2', [str(object.name),
                               str(object.description),
                               str(object.creat_time),
                               # TODO 解析object
                               str(active.active),
                               str(active.description),
                               str(learn.name),
                               str(learn.description)
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


def intersect(nums1, nums2):
    import collections
    a, b = map(collections.Counter, (nums1, nums2))
    return list((a & b).elements())
