import time
from datetime import datetime

from flask import request
from flask_restplus import Resource

from agile.api.resources.tag import timeConvert
from agile.commons.api_response import ApiResponse, ResposeStatus
from agile.extensions import db
from agile.models import Activities, Type_table, Learn, Idea


class GetHighLightDate(Resource):
    """
    获取当月有活动的日期 HTTP方法：get
    @date {String} year-month
    @result {json} 返回当月几号有活动，list
    """

    def get(self):
        # 1. 获取数据
        date = request.args.get("date").split("-")
        # 存取endTime对12进行特殊处理
        if date[1] == "12":
            end = datetime(year=int(date[0]) + 1, month=1, day=1)
        else:
            end = datetime(year=int(date[0]), month=int(date[1]) + 1, day=1)

        start = datetime(year=int(date[0]), month=int(date[1]), day=1)
        # 查询在本月有多少条数据
        data = db.session.query(Activities).filter(Activities.create_time >= start, Activities.create_time < end).all()
        setDay = set()

        for i in data:
            # 从日期中分割出月份并转成int存到set中去重
            setDay.add(int(str(i.create_time).split("-")[2][0:2]))

        return ApiResponse(setDay, ResposeStatus.Success)

class GetAllTotal(Resource):
    """
    获取时间的总数量，用户learning的总数量，用户ideas的总数量    HTTP方法：get
    userId : 需要获取userId
    TODO idea表，learn表，类型表都需要加一个user_id字段
    """

    def get(self):
        userId = request.args.get("userId")
        result = {}
        totalTimeSpent = 0
        # 获取用户总花费时间
        data = db.session.query(Type_table).filter_by(user_id=userId).all()
        for i in data:
            totalTimeSpent += i.duration_hours
        result["totalTimeSpent"] = totalTimeSpent
        # 获取用户learning总数
        data = db.session.query(Learn).filter_by(user_id=userId).count()
        result["totalLearnings"] = data
        # 获取用户idea总数
        data = db.session.query(Idea).filter_by(user_id=userId).count()
        result["totalIdeas"] = data

        return ApiResponse(result, ResposeStatus.Success)

class GetSplitTotal(Resource):
    """
    获取过去12个月用户上传的数量，获取过去6周用户上传的数量  HTTP方法：GET
    type:learn  or  idea
    date: 0——Month，1——Week
    userId: 用户id
    """

    def get(self):

        result = {}
        type = request.args.get("type")
        userId = request.args.get("userId")

        if type == "0":
            # 查本年12个月的数据
            data = db.session.query(Learn).filter_by(user_id=userId).count()
            pass
        elif type == "1":
            # 查过去六周的数据
            # endTime = time.strftime("%Y-%m-%d", time.localtime())
            # endTime = datetime.strptime(endTime, "%Y-%m-%d")
            # startTime = datetime.strptime(str(startTime), "%Y-%m-%d %H:%M:%S")
            # startTime = datetime(year=startTime.year, month=startTime.month, day=startTime.day)
            pass

        return ApiResponse(result, ResposeStatus.Success)

