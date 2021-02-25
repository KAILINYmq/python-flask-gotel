from flask import request, json
from flask_restplus import Resource

from agile.commons.api_response import ApiResponse, ResposeStatus
from agile.models import Tag, Guestbook, Type_table, Details_table, User
from agile.extensions import db
from datetime import date, datetime
from flask_jwt_extended import current_user
import time
from flask_jwt_extended import jwt_required

# 把type信息封装到一个dict里
typeDict = {
    "0": [Type_table, "ActivityType"],
    "1": [Details_table, "ActivityDetails"],
    "2": [Tag, "Learnings"],
    "3": [Tag, "Idea"],
    "4": [Tag, "Brand"],
    "5": [Tag, "Category"]
}


class TagList(Resource):
    """Get the type list"""

    def get(self):
        try:
            type = request.args.get("type")
            result = getTagList(typeDict[type])
            return ApiResponse(result, ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)


class AllTagList(Resource):
    """
    Get all ActivityType
    new: 1 —— 新 , 0 —— 旧
    """

    def get(self):
        try:
            result = {"activityType": getTagList(typeDict["0"]), "activityDetails": getTagList(typeDict["1"]),
                      "learningsTags": getTagList(typeDict["2"]), "ideaTags": getTagList(typeDict["3"]),
                      "brand": getTagList(typeDict["4"]), "category": getTagList(typeDict["5"])}
            return ApiResponse(result, ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)


class InsertTag(Resource):
    """
    添加元素
    tagType:ActivityDetails,ActivityType,Learnings,Idea,Brand,Category
    activityType:当选择Activity Type的时候，要选择一个details
    durationHours:持续时间（以小时为单位）
    name:标签值
    """

    def post(self):
        try:
            # 获取当前的时间
            localtime = time.strftime("%Y-%m-%d", time.localtime())
            data = json.loads(request.get_data(as_text=True))
            print(data)
            if data["tagType"] == typeDict["0"][1]:
                typeTab = Type_table()
                typeTab.name = data["name"]
                typeTab.creat_time = localtime
                typeTab.duration_hours = int(data["durationHours"])
                db.session.add(typeTab)
                db.session.commit()
            elif data["tagType"] == typeDict["1"][1]:
                detailsTab = Details_table()
                detailsTab.name = data["name"]
                type = db.session.query(Type_table).filter_by(name=data["activityType"]).first_or_404()
                detailsTab.type_id = int(type.id)
                detailsTab.creat_time = localtime
                db.session.add(detailsTab)
                db.session.commit()
            else:
                tagTab = Tag()
                tagTab.label = data["name"]
                tagTab.label_type = data["tagType"]
                tagTab.create_time = localtime
                db.session.add(tagTab)
                db.session.commit()

            return ApiResponse("Already insert tag", ResposeStatus.Success)
        except RuntimeError:
            db.session.rollback()
            return ApiResponse("Insert failed! Please try again.", ResposeStatus.Fail)


class Feedback(Resource):
    """
    通过判断status返回反馈信息
    status: 0: 通过， 1: get 未通过， 2: get 未审批， 3: get all
    startTime:Year-month-day
    endTime:Year-month-day
    page: 第几页
    size: 每页几条数据
    """
    method_decorators = [jwt_required]

    def get(self):

        try:
            # 1. 获取参数，参数init
            status = request.args.get("status", default="3", type=str)
            startTime = request.args.get("startTime", default="2020-1-1", type=str)
            endTime = request.args.get("endTime", default=time.strftime("%Y-%m-%d", time.localtime()), type=str)
            userId = request.args.get("userId", default=-1, type=int)
            page = request.args.get("page", default=-1, type=int)
            size = request.args.get("size", default=-1, type=int)

            # print("status:" + str(status))
            # print("startTime:" + str(startTime))
            # print("endTime:" + str(endTime))
            # print("userId:" + str(userId))
            # print("page:" + str(page))
            # print("size:" + str(size))

            if status == "":
                status = "3"
            if startTime == "":
                startTime = "2020-1-1"
            if endTime == "":
                endTime = time.strftime("%Y-%m-%d", time.localtime())
            if page <= 0 or size <= 0:
                return ApiResponse("page or size parm have mistake.", ResposeStatus.Fail)
            if userId <= 0:
                return ApiResponse("user is not found!", ResposeStatus.Fail)

            # 通过参数来查询数据并返回
            result = {}
            feedbackData = []

            superStatus = db.session.query(User).filter_by(id=current_user.id).first_or_404().is_supervisor

            if superStatus:
                if status == "3":
                    data = db.session.query(Guestbook).filter(
                                Guestbook.time.between(startTime, endTime)).all()
                else:
                    data = db.session.query(Guestbook).filter_by(state=status).filter(
                        Guestbook.time.between(startTime, endTime)).all()
            else:
                if status == "3":
                    data = db.session.query(Guestbook).filter(
                                Guestbook.time.between(startTime, endTime)).filter_by(user_id=userId).all()
                else:
                    data = db.session.query(Guestbook).filter_by(state=status).filter(
                        Guestbook.time.between(startTime, endTime)).filter_by(user_id=userId).all()

            # 对数据进行处理，只保留分页需要的数据
            count = 0
            countPage = 1
            for i in data:
                if countPage == page:
                    temp = {"id": i.id, "type": i.type, "description": i.description, "time": str(i.time).split(" ")[0],
                            "state": i.state,
                            "userId": i.user_id}
                    feedbackData.append(temp)

                count += 1
                if count % size == 0:
                    countPage += 1

            result["feedbackData"] = feedbackData

            if len(data) % size == 0:
                result["total"] = len(data) // size
            else:
                result["total"] = len(data) // size + 1

            return ApiResponse(result, ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)

    def put(self):
        """
        update user feedback status
        id: The user id status will be update,
        status: 0: 未审批, 1: 通过, 2: 拒绝
        """
        try:
            id = request.args.get("id")
            status = request.args.get("status")
            data = db.session.query(Guestbook).filter_by(id=id).first_or_404()
            data.state = status
            db.session.commit()
            return ApiResponse("Already update state to " + status, ResposeStatus.Success)
        except RuntimeError:
            db.session.rollback()
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)

    def post(self):
        """
        用户提交反馈信息到guestbook表
        """
        try:
            data = json.loads(request.get_data(as_text=True))
            type = data["type"]
            description = data["description"]
            userId = data["userId"]

            guestbookTab = Guestbook()
            guestbookTab.type = type
            guestbookTab.description = description
            guestbookTab.user_id = userId
            guestbookTab.state = "0"
            guestbookTab.time = time.strftime("%Y-%m-%d", time.localtime())
            db.session.add(guestbookTab)
            db.session.commit()
            return ApiResponse("Already submit feedbook.", ResposeStatus.Success)
        except RuntimeError:
            db.session.rollback()
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)


def timeConvert(startTime, endTime):
    """转换时间"""
    startTime = startTime.split("-")
    endTime = endTime.split("-")
    start = datetime(year=int(startTime[0]), month=int(startTime[1]), day=int(startTime[2]))
    end = datetime(year=int(endTime[0]), month=int(endTime[1]), day=int(endTime[2]))
    result = [start, end]
    return result


def getNewState(startTime):
    """传进来标签时间，返回1或0，为标签状态"""
    if startTime is None:
        return "0"

    endTime = time.strftime("%Y-%m-%d", time.localtime())
    endTime = datetime.strptime(endTime, "%Y-%m-%d")
    startTime = datetime.strptime(str(startTime), "%Y-%m-%d %H:%M:%S")
    startTime = datetime(year=startTime.year, month=startTime.month, day=startTime.day)

    if (startTime.__rsub__(endTime)).days >= 7:
        return "0"

    return "1"


def getTagList(tableData):
    """
    tableData:封装的信息，如果是前两个，只有表信息就够了，后四个需要给一个brand名字，所以是一个list
        typeDict = {
        "0": [Type_table,"ActivityType"],
        "1": [Details_table,ActivityDetails],
        "2": [Tag,"LearningsTags"],
        "3": [Tag,"IdeaTags"],
        "4": [Tag,"Brand"],
        "5": [Tag,"Category"],
    }
    """

    if tableData[1] == "ActivityType" or tableData[1] == "ActivityDetails":
        allName = db.session.query(tableData[0]).all()
        result = [{"id": name.id, "tag": name.name, "new": getNewState(name.creat_time)} for name in allName]
    else:
        allName = db.session.query(tableData[0]).filter_by(label_type=tableData[1]).all()
        result = [{"id": name.id, "tag": name.label, "new": getNewState(name.create_time)} for name in allName]

    return result
