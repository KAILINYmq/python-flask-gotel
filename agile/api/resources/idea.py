import json
import time

from flask import request
from flask_restplus import Resource
from flask_jwt_extended import current_user
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.extensions import db
from agile.models import Idea, Idea_lab ,Tag,Praise,Learn,Activities,Learn_lab
from flask_jwt_extended import jwt_required

from sqlalchemy import func
from sqlalchemy import distinct
# 新增学习
class AddMyIdea(Resource):
    def post(self):
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        student = session.query(Idea).filter(Idea.name == data["name"]).first()
        if student:
            return ApiResponse("", ResposeStatus.Fail, "该名字已经存在")
        new_user = Idea(name=data["name"], description=data["description"],creat_time=now, update_time=now)
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
        size = int(request.args.get("size"))
        page = int(request.args.get("page"))
        session = db.session
        student = session.query(Idea).limit(size).offset((page-1)*size).all()
        data = []
        for value in student:
            parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                             Praise.type == "idea",
                                                                             Praise.is_give == 1).scalar()
            dict = {}
            dict["paraseNum"] = parasnum
            dict["id"] = value.id
            dict["name"] = value.name
            dict["description"] = value.description
            dict["time"] = value.update_time
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
            dict["barnd"] = brandName
            dict["category"] = categoryName
            data.append(dict)
        return ApiResponse(data, ResposeStatus.Success)


# 根据tag,brand，category进行查询
class SortSearchIdea(Resource):

    def post(self):
        data = json.loads(request.get_data(as_text=True))
        tag = data["tag"]
        brand = data["brand"]
        category = data["category"]
        sortTime = data["sort"]
        page = int(data["page"])
        size = int(data["size"])
        if tag == 0 and brand == 0 and category == 0:
            session = db.session
            if sortTime is None:
                student = session.query(Idea).limit(size).offset((page-1)*size).all()
            else:
                student = session.query(Idea).limit(size).offset((page-1)*size).order_by(Idea.update_time.asc()).all()

            data = []
            countTotle = session.query(func.count(distinct(Idea.id))).scalar()
            dicts = {}
            if countTotle % size == 0:
                dicts["TotleNum"] = int(countTotle / size)
            else:
                dicts["TotleNum"] = int(countTotle / size) + 1
            for value in student:
                parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                                 Praise.type == "idea",
                                                                                 Praise.is_give == 1).scalar()
                dict = {}
                dict["paraseNum"] = parasnum
                dict["id"] = value.id
                dict["name"] = value.name
                dict["description"] = value.description
                dict["time"] = value.update_time
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
                dict["barnd"] = brandName
                dict["category"] = categoryName
                data.append(dict)
            dicts["data"] = data
            session.commit()
            return ApiResponse(dicts, ResposeStatus.Success)
        else:
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

            countTotle = session.query(func.count(distinct(Idea.id))).filter(Idea.id.in_(tagnum)).scalar()
            dicts = {}
            if countTotle % size == 0:
                dicts["TotleNum"] = int(countTotle / size)
            else:
                dicts["TotleNum"] = int(countTotle / size) + 1
            if sortTime is None:
                result_six = session.query(Idea).filter(Idea.id.in_(tagnum))
            else:
                result_six = session.query(Idea).filter(Idea.id.in_(tagnum)).order_by(Idea.update_time.asc())
            data = []
            for val in result_six:
                parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == val.id,
                                                                                 Praise.type == "idea",
                                                                                 Praise.is_give == 1).scalar()
                dict = {}
                dict["paraseNum"] = parasnum
                dict["id"] = val.id
                dict["name"] = val.name
                dict["description"] = val.description
                dict["time"] = val.creat_time
                dict["image"] = val.image
                dict["video"] = val.video
                labId = session.query(Idea_lab).filter(Idea_lab.idea_id == val.id).all()
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
            dicts["data"]=data
            session.commit()
            return ApiResponse(dicts, ResposeStatus.Success)


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
class PraisesIdea(Resource):

    method_decorators = [jwt_required]
    def post(self):
        #作品id
        data = json.loads(request.get_data(as_text=True))
        session = db.session
        #点赞人id
        id = current_user.id
        # id=1
        #learn
        learn = session.query(Praise).filter(Praise.user_id == id, Praise.work_id == data["id"] ,Praise.type == "idea").first()
        if learn is None:
            now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            new_parise = Praise(user_id=id, type="idea", work_id=data["id"], is_give=1,time=now)
            session.add(new_parise)
            session.commit()
        else:
            if learn.is_give == 1:
                learn.is_give = 0
            else:
                learn.is_give = 1
            session.commit()
        return ApiResponse("sucess",ResposeStatus.Success)

class SeachOneIdea(Resource):
    def get(self):
        # SaveActiveAndIdea(2,"1")
        id = request.args.get("id")
        session = db.session
        value = session.query(Idea).filter(Idea.id == id).first()
        parasnum = session.query(func.count(distinct(Praise.id))).filter(Praise.work_id == value.id,
                                                                         Praise.type == "idea",
                                                                         Praise.is_give == 1).scalar()
        dict = {}
        dict["paraseNum"] = parasnum
        dict["id"] = value.id
        dict["name"] = value.name
        dict["description"] = value.description
        dict["time"] = value.update_time
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
        dict["barnd"] = brandName
        dict["category"] = categoryName
        learn = session.query(Learn).filter(Learn.id == value.learning_id).first()
        learndict ={}
        learndict["id"] = learn.id
        learndict["name"] = learn.name
        learndict["description"] = learn.description
        learndict["image"] = learn.image
        learndict["video"] = learn.video
        learndict["time"] = learn.update_time
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


def SaveActiveAndIdea(activeIds,datas):

        # shuju = '''{
	    #     "learnings": [{
		#     "name": "你dawd34向ddeqewewewewewe我",
		#     "description": "分割开始，走电工的阿萨",
		#     "tags": [1,2],
		#     "brands": [1,2],
		#     "category": [1,2],
        #     "imageUrls": ["dddd","dddddawd"],
        #     "videoUrls": ["wdawdad","Dawdawdad"],
        #     "ideas": [{
        #             "name": "344wweqewedddeqwewd我",
        #             "description": "你说队列",
        #             "tags": [1,2],
        #             "brands": [1,2],
        #             "category": [1,2],
        #             "imageUrls": ["安徽嗲文化","dawdawd"],
        #             "videoUrls": ["dawdadad","dawdad"]
        #         },
        #         {
		# 		"name": "非deqwdddewweqeqeeaeeqw想你",
		# 		"description": "zouzai1dhawdj1",
		# 		"tags": [1,2],
		# 		"brands": [1,2],
		# 		"category": [1,2],
		# 		"imageUrls": ["whdauwdj","dawdjawdil"],
		# 		"videoUrls": ["dawidjawdi","dadawd"]
		# 	        }
		#         ]
	    #         }]
        #         }'''

        # aa =json.loads(shuju)
        #
        # datas = aa
        for lern in datas["learnings"]:
            idealist = []
            now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            # data = json.loads(request.get_data(as_text=True))
            session = db.session
            # student = session.query(Learn).filter(Learn.name == lern["name"]).first()
            # if student:
            #     return ApiResponse("", ResposeStatus.Fail, "该名字已经存在")
            # user =Learn.session.filter(func.lower(User.email) == func.lower(email))
            print(lern["imageUrls"],)
            new_user = Learn(name=lern["name"], description=lern["description"],active_id = activeIds,
                             image=str(lern["imageUrls"]),video=str(lern["videoUrls"]),creat_time=now, update_time=now)
            session.add(new_user)
            session.commit()
            # for id in data["ideaIdList"]:
            #     ideadata = session.query(Idea).filter(Idea.id == id).first()
            #     ideadata.learning_id = new_user.id
            # session.commit()

            tag = lern["tags"]
            learning = session.query(Learn).filter(Learn.name == lern["name"]).first()
            now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            for value in tag:
                new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now,
                                            is_delete=0)
                session.add(new_learn_lable)

            for value in lern["brands"]:
                new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=value, creat_time=now, update_time=now,
                                            is_delete=0)
                session.add(new_learn_lable)

            # for value in lern["category"]:
            new_learn_lable = Learn_lab(idea_id=learning.id, tag_id=lern["category"], creat_time=now, update_time=now,
                                            is_delete=0)
            session.add(new_learn_lable)
            session.commit()
            for idea in lern["ideas"]:
                # now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                # data = json.loads(request.get_data(as_text=True))
                session = db.session
                # student = session.query(Idea).filter(Idea.name == idea["name"]).first()
                # if student:
                #     return ApiResponse("", ResposeStatus.Fail, "该名字已经存在")
                new_users = Idea(name=idea["name"], description=idea["description"],image=str(idea["imageUrls"]),video=str(idea["videoUrls"]),learning_id=new_user.id,creat_time=now, update_time=now)
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
            learninfo.idea_id = idealist
            session.commit()

        return 1








def intersect(nums1, nums2):
    import collections
    a, b = map(collections.Counter, (nums1, nums2))
    return list((a & b).elements())
