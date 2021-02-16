import json
import time

from flask import request
from flask_restplus import Resource

from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.extensions import db
from agile.models import Idea, Idea_lab


# 新增学习
class AddMyIdea(Resource):
    def post(self):
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        student = session.query(Idea).filter(Idea.name == data["name"]).first()
        if student:
            return ApiResponse("", ResposeStatus.Fail, "该名字已经存在")
        new_user = Idea(name=data["name"], description=data["description"])
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
        return ApiResponse({"id": learning.id}, ResposeStatus.Success, "OK")


# 查询学习的所有数据
class GetAllIdea(Resource):
    def get(self):
        session = db.session
        student = session.query(Idea).all()
        data = []
        for value in student:
            dict = {}
            dict["id"] = value.id
            dict["name"] = value.name
            dict["description"] = value.description
            data.append(dict)
        return ApiResponse(data, ResposeStatus.Success)


# 根据tag,brand，category进行查询
class SortSearchIdea(Resource):

    def get(self):
        tag = request.args.get("tag")
        brand = request.args.get("brand")
        category = request.args.get("category")
        sortTime = request.args.get("sort")
        session = db.session
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

        # listNums = []
        # if len(tagnum) and len(brandnum) and len(categorynum):
        #     listNums = intersect(tagnum, brandnum)
        #     listNums = intersect(listNums, categorynum)
        # elif len(tagnum) & len(categorynum):
        #     listNums = intersect(tagnum, categorynum)
        # elif len(categorynum) & len(brandnum):
        #     listNums = intersect(brandnum, categorynum)
        # elif len(tagnum) & len(brandnum):
        #     listNums = intersect(tagnum, brandnum)
        # elif len(tagnum):
        #     listNums = tagnum
        # elif len(brandnum):
        #     listNums = brandnum
        # elif len(categorynum):
        #     listNums = categorynum
        # listNums = intersect(listNums,categorynum)
        # # .order_by(User.create_time.desc())
        if sortTime is None:
            result_six = session.query(Idea).filter(Idea.id.in_(tagnum))
        else:
            result_six = session.query(Idea).filter(Idea.id.in_(tagnum)).order_by(Idea.update_time.asc())
        data = []
        for val in result_six:
            dict = {}
            dict["id"] = val.id
            dict["name"] = val.name
            dict["description"] = val.description
            data.append(dict)
        return ApiResponse(data, ResposeStatus.Success)


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


def intersect(nums1, nums2):
    import collections
    a, b = map(collections.Counter, (nums1, nums2))
    return list((a & b).elements())
