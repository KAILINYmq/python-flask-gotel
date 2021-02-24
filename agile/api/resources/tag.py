from flask import request, json
from flask_restplus import Resource

from agile.commons.api_response import ApiResponse, ResposeStatus
from agile.models import Tag, Guestbook, Type_table, Details_table
from agile.extensions import db
from datetime import date, datetime
import time


class TagList(Resource):
    """Get the type list"""

    def get(self):
        try:
            type = request.args.get("type")

            if type == "0":
                allName = db.session.query(Type_table).all()
                return ApiResponse(
                    [{"id": name.id, "tag": name.name, "new": getNewState(name.creat_time)} for name in allName],
                    ResposeStatus.Success)
            elif type == "1":
                allName = db.session.query(Details_table).all()
                return ApiResponse(
                    [{"id": name.id, "tag": name.name, "new": getNewState(name.creat_time)} for name in allName],
                    ResposeStatus.Success)
            elif type == "2":
                allName = db.session.query(Tag).filter_by(label_type="LearningsTags").all()
                return ApiResponse(
                    [{"id": name.id, "tag": name.label, "new": getNewState(name.create_time)} for name in allName],
                    ResposeStatus.Success)
            elif type == "3":
                allName = db.session.query(Tag).filter_by(label_type="IdeaTags").all()
                return ApiResponse(
                    [{"id": name.id, "tag": name.label, "new": getNewState(name.create_time)} for name in allName],
                    ResposeStatus.Success)
            elif type == "4":
                allName = db.session.query(Tag).filter_by(label_type="Brand").all()
                return ApiResponse(
                    [{"id": name.id, "tag": name.label, "new": getNewState(name.create_time)} for name in allName],
                    ResposeStatus.Success)
            elif type == "5":
                allName = db.session.query(Tag).filter_by(label_type="Category").all()
                return ApiResponse(
                    [{"id": name.id, "tag": name.label, "new": getNewState(name.create_time)} for name in allName],
                    ResposeStatus.Success)

        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)


class AllTagList(Resource):
    """
    Get all ActivityType
    new: 1 —— 新 , 0 —— 旧
    """

    def get(self):
        try:
            result = {}
            allName = db.session.query(Type_table).all()
            result["activityType"] = [{"id": name.id, "tag": name.name, "new": getNewState(name.creat_time)} for name in
                                      allName]

            allName = db.session.query(Details_table).all()
            result["activityDetails"] = [{"id": name.id, "tag": name.name, "new": getNewState(name.creat_time)} for name
                                         in allName]

            allName = db.session.query(Tag).filter_by(label_type="Learnings").all()
            result["learningsTags"] = [{"id": name.id, "tag": name.label, "new": getNewState(name.create_time)} for name
                                       in allName]

            allName = db.session.query(Tag).filter_by(label_type="Idea").all()
            result["ideaTags"] = [{"id": name.id, "tag": name.label, "new": getNewState(name.create_time)} for name in
                                  allName]

            allName = db.session.query(Tag).filter_by(label_type="Brand").all()
            result["brand"] = [{"id": name.id, "tag": name.label, "new": getNewState(name.create_time)} for name in
                               allName]

            allName = db.session.query(Tag).filter_by(label_type="Category").all()
            result["category"] = [{"id": name.id, "tag": name.label, "new": getNewState(name.create_time)} for name in
                                  allName]

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
            if data["tagType"] == "ActivityDetails":
                detailsTab = Details_table()
                detailsTab.name = data["name"]
                type = db.session.query(Type_table).filter_by(name=data["activityType"]).first_or_404()
                detailsTab.type_id = int(type.id)
                detailsTab.creat_time = localtime
                db.session.add(detailsTab)
                db.session.commit()
            elif data["tagType"] == "ActivityType":
                typeTab = Type_table()
                typeTab.name = data["name"]
                typeTab.creat_time = localtime
                typeTab.duration_hours = int(data["durationHours"])
                db.session.add(typeTab)
                db.session.commit()
            else:
                tagTab = Tag()
                tagTab.label = data["name"]
                if data["tagType"] == "Learnings":
                    tagTab.label_type = "Learnings"
                elif data["tagType"] == "Brand":
                    tagTab.label_type = "Brand"
                elif data["tagType"] == "Idea":
                    tagTab.label_type = "Idea"
                elif data["tagType"] == "Category":
                    tagTab.label_type = "Category"
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
    """

    def get(self):
        try:
            # 1. 获取参数，参数init
            status = request.args.get("status")
            startTime = request.args.get("startTime")
            endTime = request.args.get("endTime")
            userId = request.args.get("userId")
            if status is None:
                status = "3"

            if startTime is None:
                startTime = "2020-1-1"

            if endTime is None:
                endTime = time.strftime("%Y-%m-%d", time.localtime())

            # 2. 通过参数来查询数据并返回
            timeList = timeConvert(startTime, endTime)
            result = {}
            feedbackData = []

            if userId is None:
                if status == "3":
                    data = db.session.query(Guestbook).filter(Guestbook.time.between(timeList[0], timeList[1])).all()
                else:
                    data = db.session.query(Guestbook).filter_by(state=status).filter(
                        Guestbook.time.between(timeList[0], timeList[1])).all()
            else:
                if status == "3":
                    data = db.session.query(Guestbook).filter(
                        Guestbook.time.between(timeList[0], timeList[1])).filter_by(user_id=userId).all()
                else:
                    data = db.session.query(Guestbook).filter_by(state=status).filter(
                        Guestbook.time.between(timeList[0], timeList[1])).filter_by(user_id=userId).all()

            for i in data:
                temp = {"id": i.id, "type": i.type, "description": i.description, "time": str(i.time).split(" ")[0],
                        "state": i.state,
                        "userId": i.user_id}
                feedbackData.append(temp)

            result["feedbackData"] = feedbackData
            result["total"] = len(data)
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
