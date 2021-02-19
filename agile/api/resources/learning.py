from flask_restplus import Resource, reqparse
from agile.commons.api_response import ResposeStatus, ApiResponse
from flask import request
from agile.extensions import db
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
import json
import time
from agile.models import Learn,Learn_lab, Learn_name,Learn_type,Tag,Praise

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
        new_user = Learn(name=data["name"],description=data["description"],creat_time=now, update_time=now)
        session.add(new_user)
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
        session = db.session
        student = session.query(Learn).all()
        data =[]
        for value in student:
            dict ={}
            dict["id"]=value.id
            dict["name"]=value.name
            dict["description"]=value.description
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
            data.append(dict)
        return ApiResponse(data, ResposeStatus.Success)



# 根据tag,brand，category进行查询
class SortSearch(Resource):

    def get(self):
        tag = request.args.get("tag")
        brand = request.args.get("brand")
        category = request.args.get("category")
        sortTime = request.args.get("sort")
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

        if sortTime  is None:
            result_six = session.query(Learn).filter(Learn.id.in_(tagnum))
        else:
            result_six = session.query(Learn).filter(Learn.id.in_(tagnum)).order_by(Learn.update_time.asc())

        data = []
        for val in result_six:
            dict ={}
            dict["id"]=val.id
            dict["name"]=val.name
            dict["description"]=val.description
            labId = session.query(Learn_lab).filter(Learn_lab.idea_id == val.id).all()
            tagName = []
            brandName = []
            categoryName = []
            for id in labId:
                # print(id,"=================")
                labIds = session.query(Tag).filter(Tag.id == id.tag_id).all()
                for lab in labIds:
                    print(lab, "=================")
                    if lab.label_type == "Brand":
                        brandName.append(lab.label)
                    elif lab.label_type == "Category":
                        categoryName.append(lab.label)
                    else:
                        tagName.append(lab.label)
            # dict["tag"] = tagName
            dict["barnd"] = brandName
            dict["category"] = categoryName
            data.append(dict)
        print(data)
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


def intersect(nums1, nums2):
  import collections
  a, b = map(collections.Counter, (nums1, nums2))
  return list((a & b).elements())
