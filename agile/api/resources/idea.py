import json
import os
import shutil
import time
import zipfile

import requests
import xlsxwriter
from flask import request, make_response, send_from_directory
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_restplus import Resource
from sqlalchemy import distinct
from sqlalchemy import exc
from sqlalchemy import func, and_

from agile import PROJECT_ROOT
from agile.commons import s3file
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.extensions import db
from agile.models import Idea, Idea_lab, Tag, Praise, Learn, Activities, Learn_lab, User


# 根据tag,brand，category进行查询
class SearchIdea(Resource):
    method_decorators = [jwt_required]

    def get_idea_ids(self, brand, category, tag):
        if not brand and not category and not tag:
            return None
        brand_results = set()
        category_results = set()
        tag_results = set()
        if brand:
            results = db.session.query(Idea_lab).filter(Learn_lab.tag_id == brand).all()
            for result in results:
                brand_results.add(result.idea_id)

        if category:
            results = db.session.query(Idea_lab).filter(Learn_lab.tag_id == category).all()
            for result in results:
                category_results.add(result.idea_id)

        if tag:
            results = db.session.query(Idea_lab).filter(Learn_lab.tag_id == tag).all()
            for result in results:
                tag_results.add(result.idea_id)

        return brand_results.intersection(category_results).difference(tag_results)

    def get(self):
        session = db.session
        try:
            user_id = current_user.id
            tag = int(request.args.get("tag"))
            brand = int(request.args.get("brand"))
            sort = str(request.args.get("sort"))
            size = int(request.args.get("size"))
            page = int(request.args.get("page"))
            category = int(request.args.get("category"))
            country = str(request.args.get("country"))

            sub_query = session.query(Idea.id, func.sum(Praise.is_give).label("praiseCount")) \
                .filter(Praise.work_id == Idea.id, Praise.type == "idea").group_by(Idea.id).subquery()
            query = session.query(Idea, User, sub_query).filter(Idea.user_id == User.id, Idea.id == sub_query.c.id)
            if country and str(country) != '0':
                query = query.filter(User.country == country)
            idea_ids = self.get_idea_ids(brand, category, tag)
            if idea_ids is not None and len(idea_ids) == 0:
                return ApiResponse({
                    "totalNum": 0,
                    "data"    : []
                }, ResposeStatus.Success)
            if idea_ids:
                query = query.filter(Idea.id.in_(idea_ids))

            order_criteria = Idea.update_time.desc()
            if "praise" == sort:
                order_criteria = sub_query.c.praiseCount.desc()
            results = query.order_by(order_criteria) \
                .offset((page - 1) * size) \
                .limit(size)
            paginate = query.paginate(page, size).pages
            response = {
                "totalNum": paginate
            }
            data = []
            for value, _, _, praiseCount in results:
                # praise_num = session.query(func.count(distinct(Praise.id))) \
                #     .filter(Praise.work_id == value.id, Praise.type == "idea", Praise.is_give == 1).scalar()
                praise = Praise.query.filter(Praise.work_id == value.id, Praise.type == "idea",
                                             Praise.user_id == str(user_id), Praise.is_give == 1).first()
                item = {}
                if praise:
                    item["isPraise"] = 1
                else:
                    item["isPraise"] = 0
                item["praiseNum"] = praiseCount
                item["id"] = value.id
                item["name"] = value.name
                item["description"] = value.description
                item["time"] = value.update_time.strftime("%Y/%m/%d")
                if value.image is not None and len(value.image) > 0:
                    item["image"] = json.loads(value.image)
                else:
                    item["image"] = []
                if value.video is not None and len(value.video) > 0:
                    item["video"] = json.loads(value.video)
                else:
                    item["video"] = []
                query_tags = session.query(Idea_lab, Tag) \
                    .filter(Idea_lab.tag_id == Tag.id) \
                    .filter(Idea_lab.idea_id == value.id) \
                    .all()
                tags = []
                brands = []
                category = ""
                for _, tag in query_tags:
                    if tag.label_type == "Brand":
                        brands.append(tag.label)
                    elif tag.label_type == "Category":
                        category = tag.label
                    else:
                        tags.append(tag.label)
                # item["tag"] = tags
                item["brand"] = brands
                item["category"] = category
                data.append(item)
            response["data"] = data
            return ApiResponse(response, ResposeStatus.Success)
        except Exception as e:
            print(e)
            return ApiResponse(status=ResposeStatus.ParamFail, msg="查询错误!")


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
            return ApiResponse(status=ResposeStatus.ParamFail, msg="点赞错误!")


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
            img = []
            vio = []
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
            labId = session.query(Learn_lab).filter(Learn_lab.learn_id == value.id).all()
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
            return ApiResponse(status=ResposeStatus.ParamFail, msg="获取详情数据错误!")


def SaveActiveAndIdea(userId, activeIds, datas):
    session = db.session
    try:
        if datas["id"] is not None and datas["id"] > 0:
            learning = session.query(Learn).filter(Learn.active_id == datas["id"]).all()
            for learn in learning:
                Learn_lab.query.filter(Learn_lab.learn_id == learn.id).delete()
                ideaData = Idea.query.filter(Idea.learning_id == learn.id).all()
                for idea in ideaData:
                    Idea_lab.query.filter(Idea_lab.idea_id == idea.id).delete()
                Idea.query.filter(Idea.learning_id == learn.id).delete()
            Learn.query.filter(Learn.active_id == datas["id"]).delete()
            session.commit()
        if len(datas["learnings"]) > 0:
            for lern in datas["learnings"]:
                idealist = []
                now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                # print(datas["activityObject"], "=11====")
                im = json.dumps(lern["imageUrls"])
                vi = json.dumps(lern["videoUrls"])
                # print(datas["activityObject"],"=====")
                new_user = Learn(name=lern["name"], description=lern["description"], active_id=activeIds,
                                 image=im, video=vi, user_id=userId, create_time=now, update_time=now)
                session.add(new_user)
                # print(datas["activityObject"], "11=====")
                session.commit()
                tag = lern["tags"]
                learning = session.query(Learn).filter(Learn.id == new_user.id).first()

                now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                # print(tag)
                for value in tag:
                    new_learn_lable = Learn_lab(learn_id=learning.id, tag_id=value, create_time=now, update_time=now,
                                                is_delete=0)
                    session.add(new_learn_lable)
                    session.commit()
                for value in lern["brands"]:
                    new_learn_lable = Learn_lab(learn_id=learning.id, tag_id=value, create_time=now, update_time=now,
                                                is_delete=0)
                    session.add(new_learn_lable)
                    session.commit()
                # for value in lern["category"]:
                new_learn_lable = Learn_lab(learn_id=learning.id, tag_id=lern["category"], create_time=now,
                                            update_time=now,
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
                                         image=ims, video=vis, learning_id=new_user.id,
                                         create_time=now, update_time=now)
                        session.add(new_users)
                        session.commit()
                        tag = idea["tags"]
                        learning = session.query(Idea).filter(Idea.id == new_users.id).first()
                        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                        for value in tag:
                            new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, create_time=now,
                                                       update_time=now,
                                                       is_delete=0)
                            session.add(new_learn_lable)

                        for value in idea["brands"]:
                            new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=value, create_time=now,
                                                       update_time=now,
                                                       is_delete=0)
                            session.add(new_learn_lable)

                        # for value in idea["category"]:
                        new_learn_lable = Idea_lab(idea_id=learning.id, tag_id=idea["category"], create_time=now,
                                                   update_time=now,
                                                   is_delete=0)
                        session.add(new_learn_lable)
                        idealist.append(new_users.id)
                        session.commit()
                learninfo = session.query(Learn).filter(Learn.id == new_user.id).first()
                learninfo.idea_id = str(idealist)
                session.commit()
        return 1
    except exc.IntegrityError:
        db.session.rollback()
        return 2
    except Exception as e:
        db.session.rollback()
        return 0


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
                               str(object.create_time),
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
