import time
import datetime

from dateutil.relativedelta import relativedelta
from flask import request
from flask_restplus import Resource
from sqlalchemy import or_

from agile.api.resources.tag import timeConvert
from agile.commons.api_response import ApiResponse, ResposeStatus
from agile.extensions import db
from agile.models import Activities, Type_table, Learn, Idea, User, department_category, Category


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
    timeType: 0——Month，1——Week
    userId: 用户id   （可选项，默认给本公司所有的数量）
    dateType
    """

    def get(self):
        result = {}
        activityType = request.args.get("type")
        userId = request.args.get("userId")
        timeType = request.args.get("timeType")
        dateType = request.args.get("dateType")
        learnTab = Learn
        ideaTab = Idea

        if dateType is None or dateType == "0":
            # 存最终数据
            data = []
            # 得到用户的城市
            userCountry = db.session.query(User).filter_by(id=int(userId)).first_or_404().country
            # 得到所有和这个用户一样地区的用户id
            sameCountryData = db.session.query(User).filter_by(country=userCountry).all()
            # 得到learn的数据
            if activityType == "learn":
                # 把每一个用户查询集都保存下来
                for user in sameCountryData:
                    data.append(db.session.query(Learn).filter_by(user_id=user.id))
                # 查公司本地区本年12个月的数据
                result = splitTotalCompany(timeType, data, learnTab)

            elif activityType == "idea":
                data = db.session.query(Idea)
                result = splitTotalCompany(timeType, data, ideaTab)
        elif dateType == "1":
            if activityType == "learn":
                # 查用户本年12个月的数据
                data = db.session.query(Learn).filter_by(user_id=userId)
                result = splitTotal(timeType, data, learnTab)
            elif activityType == "idea":
                data = db.session.query(Idea).filter_by(user_id=userId)
                result = splitTotal(timeType, data, ideaTab)

        return ApiResponse(result, ResposeStatus.Success)


class GetCategory(Resource):
    """
    获取本公司，本用户地区的learning下用户category和idea下用户category数量
    Get
    请求参数：
    userId
    """

    def get(self):
        idResult = {}
        nameResult = {}
        # 1. 获取userId参数
        userId = request.args.get("userId")
        # 2. 通过userId获取到本user的country
        userCountry = db.session.query(User).filter_by(id = userId).first_or_404().country
        # 3. 通过country获取所有和这个用户城市一样的用户
        sameCountryUser = db.session.query(User).filter_by(country=userCountry).all()
        # 4. 获取department_category表的数据（list）
        departmentCategoryList = db.session.query(department_category).all()
        # 5. 把user的department_id取出并去重
        userDepartmentId = set()
        # 6. 循环user的department_id添加进set
        for i in sameCountryUser:
            userDepartmentId.add(i.department_id)
        # 7. 查询存储每一个department_id在department_category表中的数据
        count = 0
        # 8. 遍历关联表，如果department_id在userDepartmentId中，存下对应的键和值
        for i in departmentCategoryList:
            if i[0] in userDepartmentId:
                if str(i[1]) in idResult:
                    idResult[str(i[1])] += 1
                else:
                    idResult[str(i[1])] = 1
            count += 1
        # 9. 把idResult对应的category id转成名字返回
        for k in idResult:
            name = db.session.query(Category).filter_by(id=int(k)).first_or_404().name
            nameResult[name] = idResult[k]

        return ApiResponse("Hello", ResposeStatus.Success)


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


def splitTotalCompany(dateType, data, tab):
    """
    dateType: 0 —— Month .  1 —— Week
    data: 查询集数据
    tab: 各表格模型类引用
    用于对公司的分割查询
    """

    result = {}
    count = 0
    if dateType == "0":
        # 对data数据进行筛选往前倒6周的数据，并且对每一周的数量进行记录
        frontTime = datetime.date.today()
        frontTime = datetime.datetime(year=frontTime.year, month=1, day=1)
        month = relativedelta(months=- 1)
        for i in range(12):
            behindTime = frontTime - month
            # print(str(frontTime) + " - " + str(month) + " = " + str(behindTime))
            # 对数据进行筛选
            for j in data:
                count += j.filter(
                    tab.creat_time.between(frontTime, behindTime)).count()
            result[str(i + 1)] = count
            count = 0
            frontTime = behindTime
    elif dateType == "1":
        # 对data数据进行筛选往前倒6周的数据，并且对每一周的数量进行记录
        frontTime = datetime.datetime.now()
        week = datetime.timedelta(days=7)
        for i in range(6):
            behindTime = frontTime - week
            # print(str(frontTime) + " - " + str(week) + " = " + str(behindTime))
            # 对数据进行筛选
            for j in data:
                count += j.filter(
                    tab.creat_time.between(behindTime, frontTime)).count()
            result[str(i + 1)] = count
            count = 0
            frontTime = behindTime

    return result
