from flask_restplus import Resource, reqparse
from agile.commons.api_response import ResposeStatus, ApiResponse
from flask import request
from agile.extensions import db
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
import json
import time
from agile.models import Learn,Learn_lab, Learn_type,Tag,Praise,Idea,Activities
from sqlalchemy import func
from sqlalchemy import distinct

# 新增学习
class AddMyLearn(Resource):
    def post(self):
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        student = session.query(Learn).filter(Learn.name == data["name"]).first()
        if student:
            return ApiResponse("", ResposeStatus.Fail,"该名字已经存在")
        # user =Learn.session.filter(func.lower(User.email) == func.lower(email))
        new_user = Learn(name=data["name"],description=data["description"],idea_id = str(data["ideaIdList"]), active_id=data["activeId"], creat_time=now, update_time=now)
        session.add(new_user)
        session.commit()
        for id in data["ideaIdList"]:
            ideadata = session.query(Idea).filter(Idea.id == id).first()
            ideadata.learning_id = new_user.id
        session.commit()
        tag = data["tag"]
        learning = session.query(Learn).filter(Learn.name == data["name"]).first()
        now = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        for value in tag:
            new_learn_lable = Learn_lab(idea_id=learning.id,tag_id=value,creat_time=now, update_time =now , is_delete =0)
            session.add(new_learn_lable)

        for value in data["brand"]:
            new_learn_lable = Learn_lab(idea_id=learning.id,tag_id=value,creat_time=now, update_time =now , is_delete =0)
            session.add(new_learn_lable)

        for value in  data["category"]:
            new_learn_lable = Learn_lab(idea_id=learning.id,tag_id=value,creat_time=now, update_time =now , is_delete =0)
            session.add(new_learn_lable)
        session.commit()
        return ApiResponse({"id":learning.id}, ResposeStatus.Success,"OK")


# 查询学习的所有数据
class GetAllLearn(Resource):
    def get(self):
        size = int(request.args.get("size"))
        page = int(request.args.get("page"))
        session = db.session
        student = session.query(Learn).limit(size).offset((page-1)*size).all()
        data =[]
        for value in student:
            parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                             Praise.type == "learning",Praise.is_give == 1).scalar()
            dict ={}
            dict["paraseNum"] = parasnum
            dict["id"]=value.id
            dict["name"]=value.name
            dict["description"]=value.description
            dict["time"] = value.update_time
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
                        ideaDict["time"] = idea.update_time
                        ideaDict["image"] = idea.image
                        ideaDict["video"] = idea.video
                        IdeaData.append(ideaDict)
            dict["idea"] = IdeaData
            data.append(dict)
        print(data)
        return ApiResponse(data, ResposeStatus.Success)



# 根据tag,brand，category进行查询
class SortSearch(Resource):

    def post(self):
        data = json.loads(request.get_data(as_text=True))
        tag = data["tag"]
        brand =data["brand"]
        category =data["category"]
        sortTime =data["sort"]
        page = int(data["page"])
        size = int(data["size"])
        if tag == 0 and brand ==0 and category ==0:
            session = db.session
            if sortTime != 1:
                student = session.query(Learn).limit(size).offset((page-1)*size).all()
            else:
                student = session.query(Learn).limit(size).offset((page-1)*size).order_by(Learn.update_time.asc()).all()
            # student = session.query(Learn).all()
            data = []
            for value in student:
                parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                                 Praise.type == "learning",
                                                                                 Praise.is_give == 1).scalar()
                dict = {}
                dict["paraseNum"] = parasnum
                dict["id"] = value.id
                dict["name"] = value.name
                dict["description"] = value.description
                dict["time"] = value.update_time
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
                            ideaDict["time"] = idea.update_time
                            ideaDict["image"] = idea.image
                            ideaDict["video"] = idea.video
                            IdeaData.append(ideaDict)
                dict["idea"] = IdeaData
                data.append(dict)
            return ApiResponse(data, ResposeStatus.Success)
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

            # listNums = []
            # if len(tagnum)  and len(brandnum) and len(categorynum):
            #     listNums = intersect(tagnum,brandnum)
            #     listNums = intersect(listNums, categorynum)
            # elif len(tagnum)&len(categorynum):
            #     listNums = intersect(tagnum, categorynum)
            # elif len(categorynum) & len(brandnum):
            #     listNums = intersect(brandnum, categorynum)
            # elif len(tagnum) & len(brandnum):
            #     listNums = intersect(tagnum,brandnum)
            # elif len(tagnum):
            #     listNums = tagnum
            # elif len(brandnum):
            #     listNums = brandnum
            # elif len(categorynum):
            #     listNums = categorynum

            if sortTime is None:
                result_six = session.query(Learn).filter(Learn.id.in_(tagnum))
            else:
                result_six = session.query(Learn).filter(Learn.id.in_(tagnum)).order_by(Learn.update_time.asc())

            data = []
            for val in result_six:
                parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == val.id,
                                                                                 Praise.type == "learning",
                                                                                 Praise.is_give == 1).scalar()

                dict ={}
                dict["paraseNum"] = parasnum
                dict["id"]=val.id
                dict["name"]=val.name
                dict["description"]=val.description
                dict["time"] = val.creat_time
                dict["image"] = val.image
                dict["video"] = val.video
                labId = session.query(Learn_lab).filter(Learn_lab.idea_id == val.id).all()
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
                            ideaDict["time"] = idea.update_time
                            ideaDict["image"] = idea.image
                            ideaDict["video"] = idea.video
                            IdeaData.append(ideaDict)
                dict["Idea"] = IdeaData
                data.append(dict)
            return ApiResponse(data, ResposeStatus.Success)

# 修改
class UpdataLearn(Resource):

    def post(self):
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        learn = session.query(Learn).filter(Learn.id == data["id"]).first()
        learn.name=data["name"]
        learn.description = data["description"]
        learn.update_time=now
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
        #作品id
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        #点赞人id
        id = current_user.id
        # id=1

        #learn
        learn = session.query(Praise).filter(Praise.user_id == id, Praise.work_id == data["id"] ,Praise.type == "learning").first()
        if learn is None:
            now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            new_parise = Praise(user_id=id, type="learning", work_id=data["id"], is_give=1,time=now)
            session.add(new_parise)
            session.commit()
        else:
            print(type(learn.is_give))
            if learn.is_give == 1:
                learn.is_give = 0
            else:
                learn.is_give = 1
            session.commit()
        return ApiResponse("sucess", ResposeStatus.Success)

class SeachOneLean(Resource):

    def get(self):
            id = request.args.get("id")
            dict = SecetLearnInfo(id)
            # session = db.session
            # value = session.query(Learn).filter(Learn.id == id).first()
            #
            # parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
            #                                                                  Praise.type == "learning",Praise.is_give == 1).scalar()
            # dict ={}
            # dict["id"]=value.id
            # dict["name"]=value.name
            # dict["description"]=value.description
            # dict["paraseNum"] = parasnum
            # dict["time"] = value.update_time
            # dict["image"] = value.image
            # dict["video"] = value.video
            # labId = session.query(Learn_lab).filter(Learn_lab.idea_id == value.id).all()
            # tagName = []
            # brandName = []
            # categoryName = []
            # for id in labId:
            #     # print(id,"=================")
            #     labIds = session.query(Tag).filter(Tag.id == id.tag_id).all()
            #     for lab in labIds:
            #         if lab.label_type == "Brand":
            #             brandName.append(lab.label)
            #         elif lab.label_type == "Category":
            #             categoryName.append(lab.label)
            #         else:
            #             tagName.append(lab.label)
            # # dict["tag"] = tagName
            # dict["barnd"] = brandName
            # dict["category"] = categoryName
            # # print(type(dict["ideaId"]),type(value.idea_id),"==================")
            # IdeaData = []
            # if value.idea_id is not None:
            #     idealist = json.loads(value.idea_id)
            #     for val in idealist:
            #         ideaDict = {}
            #         idea = session.query(Idea).filter(Idea.id == val).first()
            #         if idea is not None:
            #             ideaDict["id"] = idea.id
            #             ideaDict["name"] = idea.name
            #             ideaDict["description"] = idea.description
            #             ideaDict["time"] = idea.update_time
            #             ideaDict["image"] = idea.image
            #             ideaDict["video"] = idea.video
            #             IdeaData.append(ideaDict)
            # dict["idea"] = IdeaData
            # activedict = {}
            # if value.active_id is not None:
            #     active = session.query(Activities).filter(Activities.id == value.active_id).first()
            #     activedict["name"] = active.active
            #     activedict["activeType"] = active.active_type
            #     activedict["activeTime"] = active.active_time
            #     activedict["description"] = active.description
            #     # activedict["image"] = active.image
            #     # activedict["video"] = active.video
            # dict["active"] = activedict
            # active = session.query(Activities).all()
            # dictactive = {}
            # for val in active:
            #     if id in val.idea_name:
            #         dictactive[""] = val.active
            #         =val.active_type
            #         =val.active_time
            return ApiResponse(dict, ResposeStatus.Success)
def intersect(nums1, nums2):
  import collections
  a, b = map(collections.Counter, (nums1, nums2))
  return list((a & b).elements())


def SecetLearnInfo(id):
    session = db.session
    value = session.query(Learn).filter(Learn.id == id).first()

    parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                     Praise.type == "learning",
                                                                     Praise.is_give == 1).scalar()
    dict = {}
    dict["id"] = value.id
    dict["name"] = value.name
    dict["description"] = value.description
    dict["paraseNum"] = parasnum
    dict["time"] = value.update_time
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
                ideaDict["time"] = idea.update_time
                ideaDict["image"] = idea.image
                ideaDict["video"] = idea.video
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
    return dict