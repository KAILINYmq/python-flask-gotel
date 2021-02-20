from flask import request, json
from flask_restplus import Resource
from sqlalchemy import and_, between

from agile.commons.api_response import ApiResponse, ResposeStatus
from agile.models import Tag, Guestbook, Type_table,Details_table
from agile.extensions import db
from datetime import date, datetime
import time


class TagList(Resource):
    """Get the type list"""

    def get(self):
        try:
            type = request.args.get("type")
            if type == "ActivityType":
                allName = db.session.query(Type_table).all()
                return ApiResponse([name.name for name in allName], ResposeStatus.Success)
            elif type == "ActivityDetails":
                allName = db.session.query(Details_table).all()
                return ApiResponse([name.name for name in allName], ResposeStatus.Success)
            elif type == "LearningsTags":
                allName = db.session.query(Tag).filter_by(label_type=type).all()
                return ApiResponse([name.label for name in allName], ResposeStatus.Success)
            elif type == "IdeaTags":
                allName = db.session.query(Tag).filter_by(label_type=type).all()
                return ApiResponse([name.label for name in allName], ResposeStatus.Success)
            elif type == "Brand":
                allName = db.session.query(Tag).filter_by(label_type=type).all()
                return ApiResponse([name.label for name in allName], ResposeStatus.Success)
            elif type == "Category":
                allName = db.session.query(Tag).filter_by(label_type=type).all()
                return ApiResponse([name.label for name in allName], ResposeStatus.Success)

        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)

class AllTagList(Resource):
    """Get all ActivityType"""

    def get(self):
        try:
            result = {}
            allName = db.session.query(Type_table).all()
            result["activityType"] = [name.name for name in allName]

            allName = db.session.query(Details_table).all()
            result["activityDetails"] = [name.name for name in allName]

            allName = db.session.query(Tag).all()
            result["tag"] = [name.label for name in allName]

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
            return ApiResponse("Insert failed! Please try again.", ResposeStatus.Fail)

class Feedback(Resource):
    """
    status: 0: get all， 1: get 通过， 2: get 未通过， 3: get 未审批
    startTime:Year-month-day
    endTime:Year-month-day
    """

    def get(self):
        try:
            status = request.args.get("status")
            time = timeConvert(request.args.get("startTime"), request.args.get("endTime"))
            result = []
            if status == "0":
                data = db.session.query(Guestbook).filter(Guestbook.time.between(time[0], time[1])).all()
            elif status == "1":
                data = db.session.query(Guestbook).filter_by(state="passed").filter(
                    Guestbook.time.between(time[0], time[1])).all()
            elif status == "2":
                data = db.session.query(Guestbook).filter_by(state="rejected").filter(
                    Guestbook.time.between(time[0], time[1])).all()
            elif status == "3":
                data = db.session.query(Guestbook).filter_by(state="not reviewed").filter(
                    Guestbook.time.between(time[0], time[1])).all()
            for i in data:
                temp = {}
                temp["id"] = i.id
                temp["type"] = i.type
                temp["description"] = i.description
                temp["time"] = i.time
                temp["state"] = i.state
                temp["userId"] = i.user_id
                result.append(temp)
            return ApiResponse(result, ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)

    def put(self):
        """
        update user feedback status
        id: The user id status will be update,
        status: 0: pass, 1: rejected
        """
        try:
            id = request.args.get("id")
            status = "passed" if request.args.get("status") == "0" else "rejected"
            session = db.session
            data = session.query(Guestbook).filter_by(id=id).first_or_404()
            data.state = status
            session.commit()
            return ApiResponse("Already update state to " + status, ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)


def timeConvert(startTime, endTime):
    """转换时间"""
    startTime = startTime.split("-")
    endTime = endTime.split("-")
    start = datetime(year=int(startTime[0]), month=int(startTime[1]), day=int(startTime[2]))
    end = datetime(year=int(endTime[0]), month=int(endTime[1]), day=int(endTime[2]))
    result = [start, end]
    return result
