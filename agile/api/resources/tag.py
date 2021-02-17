from flask import request, json
from flask_restplus import Resource
from sqlalchemy import and_, between

from agile.commons.api_response import ApiResponse, ResposeStatus
from agile.models import Name_table, Type_table, Tag, Guestbook
from agile.extensions import db
from datetime import date, datetime


class TagList(Resource):
    """Get all tag list"""

    def get(self):
        try:
            allName = db.session.query(Tag).all()
            return ApiResponse([name.label for name in allName], ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)

class ActivityName(Resource):
    """Get all ActivityName"""

    def get(self):
        try:
            allName = db.session.query(Name_table).all()
            return ApiResponse([name.name for name in allName], ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)

class ActivityType(Resource):
    """Get all ActivityType"""

    def get(self):
        try:
            allName = db.session.query(Type_table).all()
            return ApiResponse([name.name for name in allName], ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)

class AllList(Resource):
    """Get all ActivityType"""

    def get(self):
        try:
            result = {}
            allName = db.session.query(Name_table).all()
            result["ActivityName"] = [name.name for name in allName]

            allName = db.session.query(Type_table).all()
            result["ActivityType"] = [name.name for name in allName]

            allName = db.session.query(Tag).all()
            result["Tag"] = [name.label for name in allName]

            return ApiResponse(result, ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)

class AddTag(Resource):
    """
    添加元素
    tagType:Activity Name,Activity Type,Learnings,Idea,Brand,Category
    type: 当选择Activity name的时候，要选择一个类型的名字
    description:标签值
    """

    def post(self):
        try:
            data = json.loads(request.get_data(as_text=True))
            if data["tagType"] == "Activity Name":
                typeTab = Type_table()
                typeTab.name = data["description"]
                typeTab.name_type = "Activity Type"
                name = db.session.query(Name_table).filter_by(name=data["type"]).first_or_404()
                nameId = name.id
                typeTab.name_id = int(nameId)  # TODO 这里的name_id存不进数据库，等待勐奇学长提pr合并，我再拉一下代码，作迁移，再试试
                db.session.add(typeTab)
                db.session.commit()

            elif data["tagType"] == "Activity Type":
                typeTab = Type_table()
                typeTab.name = data["description"]
                typeTab.name_type = "Activity Type"
                db.session.add(typeTab)
                db.session.commit()

            else:
                tagTab = Tag()
                tagTab.label = data["description"]

                if data["tagType"] == "Learnings":
                    tagTab.label_type = "Learnings"
                elif data["tagType"] == "Brand":
                    tagTab.label_type = "Brand"
                elif data["tagType"] == "Idea":
                    tagTab.label_type = "Idea"
                elif data["tagType"] == "Category":
                    tagTab.label_type = "Category"
                db.session.add(tagTab)
                db.session.commit()
            return ApiResponse("Already insert tag", ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Insert failed! Please try again.", ResposeStatus.Fail)

class ShowFeedback(Resource):
    """
    status: 0: get all， 1: get 通过， 2: get 未通过， 3: get 未审批
    startTime:2021-2-21
    endTime:2021-3-21
    """

    def get(self):
        try:
            status = request.args.get("status")
            time = timeConvert(request.args.get("startTime"),request.args.get("endTime"))
            result = []
            if status == "0":
                data = db.session.query(Guestbook).filter(Guestbook.time.between(time[0],time[1])).all()
            elif status == "1":
                data = db.session.query(Guestbook).filter_by(state="passed").filter(Guestbook.time.between(time[0],time[1])).all()
            elif status == "2":
                data = db.session.query(Guestbook).filter_by(state="rejected").filter(Guestbook.time.between(time[0],time[1])).all()
            elif status == "3":
                data = db.session.query(Guestbook).filter_by(state="not reviewed").filter(Guestbook.time.between(time[0],time[1])).all()
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

def timeConvert(startTime,endTime):
    """转换时间"""
    startTime = startTime.split("-")
    endTime = endTime.split("-")
    start = datetime(year=int(startTime[0]), month=int(startTime[1]), day=int(startTime[2]))
    end = datetime(year=int(endTime[0]), month=int(endTime[1]), day=int(endTime[2]))
    result = [start, end]
    return result
