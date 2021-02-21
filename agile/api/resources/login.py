import time
import datetime

from dateutil.relativedelta import relativedelta
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
    """

    def get(self):
        userId = request.args.get("userId")
        result = {}
        totalTimeSpent = 0
        # 获取用户总花费时间
        data = db.session.query(Activities).filter_by(user_id=userId).all()
        for i in data:
            totalTimeSpent += i.active_time
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
    dateType: 0——Month，1——Week
    userId: 用户id   （可选项，默认给本公司所有的数量）
    """

    def get(self):
        result = {}
        type = request.args.get("type")
        userId = request.args.get("userId")
        dateType = request.args.get("dateType")
        learnTab = Learn
        ideaTab = Idea

        if userId is None:
            if type == "learn":
                # 查公司本年12个月的数据
                data = db.session.query(Learn)
                result = splitTotal(dateType,data,learnTab)

            elif type == "idea":
                data = db.session.query(Idea)
                result = splitTotal(dateType, data,ideaTab)
        else:
            if type == "learn":
                # 查用户本年12个月的数据
                data = db.session.query(Learn).filter_by(user_id=userId)
                result = splitTotal(dateType, data,learnTab)
            elif type == "idea":
                data = db.session.query(Idea).filter_by(user_id=userId)
                result = splitTotal(dateType, data,ideaTab)

        return ApiResponse(result, ResposeStatus.Success)


def splitTotal(dateType, data, tab):
    """
    dateType: 0 —— Month .  1 —— Week
    data: 查询集数据
    tab: 各表格模型类引用
    """

    result = {}
    if dateType == "0":
        # 对data数据进行筛选往前倒6周的数据，并且对每一周的数量进行记录
        frontTime = datetime.date.today()
        frontTime = datetime.datetime(year=frontTime.year, month=1, day=1)
        month = relativedelta(months=- 1)

        for i in range(12):
            behindTime = frontTime - month
            # print(str(frontTime) + " - " + str(month) + " = " + str(behindTime))
            # 对数据进行筛选
            result[str(i + 1)] = data.filter(
                tab.creat_time.between(frontTime, behindTime)).count()
            frontTime = behindTime
    elif dateType == "1":
        # 对data数据进行筛选往前倒6周的数据，并且对每一周的数量进行记录
        frontTime = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        for i in range(6):
            behindTime = frontTime - week
            # print(str(frontTime) + " - " + str(week) + " = " + str(behindTime))
            # 对数据进行筛选
            result[str(i + 1)] = data.filter(
                        tab.creat_time.between(behindTime, frontTime)).count()
            frontTime = behindTime

    return result