import logging
import time
import datetime

from dateutil.relativedelta import relativedelta
from flask import request
from flask_restplus import Resource
from sqlalchemy import or_

from agile.api.resources.tag import timeConvert
from agile.commons.api_response import ApiResponse, ResposeStatus
from agile.extensions import db
from agile.models import Activities, Type_table, Learn, Idea, User, department_category, Category, Learn_lab, Tag, \
    Idea_lab


class GetHighLightDate(Resource):
    """
    获取当月有活动的日期 HTTP方法：get
    @date {String} year-month
    @result {json} 返回当月几号有活动，list
    """

    def get(self):
        try:
            # 1. 获取数据
            setDay = "参数有误。 "
            date = request.args.get("date")
            date = date.split("-")

            if date is not None and len(date) >= 2:
                # print(date)
                # 存取endTime对12进行特殊处理
                logging.debug(date)
                if date[0] is None or date[1] is None:
                    return ApiResponse("date is faile!", ResposeStatus.Fail)

                if date[1] == "12":
                    end = datetime.datetime(year=int(date[0]) + 1, month=1, day=1)
                else:
                    end = datetime.datetime(year=int(date[0]), month=int(date[1]) + 1, day=1)

                start = datetime.datetime(year=int(date[0]), month=int(date[1]), day=1)
                # 查询在本月有多少条数据
                data = db.session.query(Activities).filter(Activities.create_time >= start,
                                                           Activities.create_time < end).all()
                # print(data)
                setDay = set()

                for i in data:
                    # 从日期中分割出月份并转成int存到set中去重
                    setDay.add(int(str(i.create_time).split("-")[2][0:2]))
                    print(i)

            return ApiResponse(setDay, ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)


class GetAllTotal(Resource):
    """
    获取时间的总数量，用户learning的总数量，用户ideas的总数量    HTTP方法：get
    userId : 需要获取userId
    """

    def get(self):
        try:
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
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)


class GetSplitTotal(Resource):
    """
    获取过去12个月用户上传的数量，获取过去6周用户上传的数量  HTTP方法：GET
    type:learn  or  idea
    timeType: 0——Month，1——Week
    userId: 用户id   （可选项，默认给本公司所有的数量）
    dateType
    """

    def get(self):
        try:
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
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)


class GetCategory(Resource):
    """
    获取本公司，本用户地区的category的数据
    Get
    请求参数：
    userId
    type:learn,idea
    """

    def get(self):
        try:
            result = {}
            # 获取参数
            userId = request.args.get("userId")
            type = request.args.get("type")
            # 通过userId获取到本user的country
            userCountry = db.session.query(User).filter_by(id=userId).first_or_404().country
            # print("用户城市:" + str(userCountry))
            # 获取category列表
            # print("所有的category：" + str(db.session.query(Category).all()))
            for category in db.session.query(Category).all():
                # 获取所有属于本category的同地区的用户id
                tempSameCategoryUserId = getCategoryUserId(category,userCountry)

                # 拿着这个user id去learning表查询所有涉及到这些user id的数据
                count = 0
                if type == "learn":
                    for userId in tempSameCategoryUserId:
                        count += db.session.query(Learn).filter_by(user_id=userId).count()
                        # print("当前count是：" + str(count))
                        # print("当前用户Id是：" + str(userId))
                        # print("属于这个用户id的learn数据是：" + str(db.session.query(Learn).filter_by(user_id=userId).all()))
                elif type == "idea":
                    for userId in tempSameCategoryUserId:
                        count += db.session.query(Idea).filter_by(user_id=userId).count()
                # print("结束：" + category.name)
                result[category.name] = count
            # print(result)
            return ApiResponse(result, ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)


class GetBrand(Resource):
    """
    获取全公司本地区的的品牌信息
    userid
    type: learn or idea
    category: all or 各category分类  Home Care,Beauty & Personal Care,Food & Refreshment


    """

    def get(self):
        try:
            # 获取参数
            userId = request.args.get("userId")
            type = request.args.get("type")
            category = request.args.get("category")
            # 通过userId获取到本user的country
            userCountry = db.session.query(User).filter_by(id=userId).first_or_404().country
            # print("要获取的Type是：" + type)
            # print("用户地区是：" + userCountry)

            if category is None or category == "all":
                category = "all"
                # print("category是：" + category)
                # print("进入函数")
                tempSameCategoryUserId = getCategoryUserId(category,userCountry)
                # print("退出函数")
            else:
                tempCategory = db.session.query(Category).filter_by(name=category).first()
                tempCategoryList = db.session.query(Category).filter_by(name=category).all()

                # print("获取到的category是：" + str(tempCategory))
                # print("获取到的category数量是：" + str(len(tempCategoryList)))
                if len(tempCategoryList) == 0:
                    return ApiResponse("Don't find the category name.",ResposeStatus.Fail)
                else:
                    # print("进入函数")
                    # 获取所有属于本category的同地区的用户id
                    tempSameCategoryUserId = getCategoryUserId(tempCategory, userCountry)
                    # print("退出函数")
            # print("已经获取到user id list：" + str(tempSameCategoryUserId))

            # 拿着这个user id去idea和learn表查询所有涉及到这些user id的数据
            typeList = []
            brandData = {}
            searchData = []
            if type == "learn":
                for userId in tempSameCategoryUserId:
                    # print("当前用户的Id是：" + str(userId))
                    typeList.extend(db.session.query(Learn).filter_by(user_id=userId).all())
                    # 拿着typeList的type id去找关联表中的type id对应的tag id，最后统计
                    # 把所有本type —— tag id的关系筛选出来
                # print("所有的learn数据是：" + str(typeList) + "，数量是：" + str(len(typeList)))

                for tag in typeList:
                    # print("当前的tag_id是：" + str(tag.id))
                    # 获取到关联表中等于idea_id的data
                    searchData.extend(db.session.query(Learn_lab).filter_by(idea_id=tag.id).all())
                # print("筛选后的learn数据是：" + str(searchData) + "，数量是：" + str(len(searchData)))

                for searchTag in searchData:
                    tagType = db.session.query(Tag).filter_by(id=searchTag.tag_id).first_or_404()
                    # print("当前tag_id是：" + str(searchTag.tag_id))
                    # print("当前tag_id的brand是：" + str(tagType.label_type))
                    if tagType.label_type == "Brand":
                        if tagType.label in brandData:
                            brandData[tagType.label] += 1
                        else:
                            brandData[tagType.label] = 1
                # print("品牌数据是：" + str(brandData))

            elif type == "idea":
                for userId in tempSameCategoryUserId:
                    typeList.extend(db.session.query(Idea).filter_by(user_id=userId).all())
                for tag in typeList:
                    # print("当前的tag_id是：" + str(tag.id))
                    # 获取到关联表中等于idea_id的data
                    searchData.extend(db.session.query(Idea_lab).filter_by(idea_id=tag.id).all())
                # print("筛选后的learn数据是：" + str(searchData) + "，数量是：" + str(len(searchData)))

                for searchTag in searchData:
                    tagType = db.session.query(Tag).filter_by(id=searchTag.tag_id).first_or_404()
                    # print("当前tag_id是：" + str(searchTag.tag_id))
                    # print("当前tag_id的brand是：" + str(tagType.label_type))
                    if tagType.label_type == "Brand":
                        if tagType.label in brandData:
                            brandData[tagType.label] += 1
                        else:
                            brandData[tagType.label] = 1
                # print("品牌数据是：" + str(brandData))

            # print("排序中")
            sortResult = sorted(brandData.items(), key=lambda x: x[1], reverse=True)
            # print("排序完毕" + str(sortResult))

            result = {}
            for i in sortResult:
                result[i[0]] = i[1]
            # print("最终结果：" + str(result))
            return ApiResponse(result, ResposeStatus.Success)
        except RuntimeError:
            return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)

def splitTotal(dateType, data, tab):
    """
    dateType: 0 —— Month .  1 —— Week
    data: 查询集数据
    tab: 各表格模型类引用
    """

    result = {}
    monthList = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sept","Oct","Nov","Dec"]
    weekList = ["oneWeek","twoWeek","threeWeek","fourWeek","fiveWeek","sixWeek"]
    if dateType == "0":
        # 对data数据进行筛选往前倒6周的数据，并且对每一周的数量进行记录
        frontTime = datetime.date.today()
        frontTime = datetime.datetime(year=frontTime.year, month=1, day=1)
        month = relativedelta(months=- 1)

        for i in range(12):
            behindTime = frontTime - month
            # print(str(frontTime) + " - " + str(month) + " = " + str(behindTime))
            # 对数据进行筛选
            result[monthList[i]] = data.filter(
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
            result[weekList[i]] = data.filter(
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
    monthList = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]
    weekList = ["oneWeek", "twoWeek", "threeWeek", "fourWeek", "fiveWeek", "sixWeek"]
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
            result[monthList[i]] = count
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
            result[weekList[i]] = count
            count = 0
            frontTime = behindTime

    return result


def getCategoryUserId(category,userCountry):
    """
    获取所有属于category的同地区的人员id list
    category:各category类型，或者all
    """
    try:
        if category == "all":
            # 通过category id在department category中查询出对应的department id
            # print("当前的category名字是:" + category.name)
            # print("当前的categoryId是:" + str(category.id))
            tempDepartmentId = db.session.query(department_category).all()
            # print("查关联表所有与当前category_id关联的数据：" + str(tempDepartmentId))
            # 通过department id来查询涉及到了哪些用户   左边department_id 右边category id
            tempSameCategoryUserId = set()
            for j in tempDepartmentId:
                # print("当前的department id是：" + str(j[0]))
                # 获取到所有department id等于上面department id的user id数据
                temp = db.session.query(User).filter_by(department_id=j[0]).filter_by(country=userCountry).all()
                # print("通过department id查询到的所有本地区的用户是：" + str(temp))
                # 获取到所有的user id
                for user in temp:
                    tempSameCategoryUserId.add(user.id)
                # print("当前所有的用户是：" + str(temp))

            return tempSameCategoryUserId

        else:
            # 通过category id在department category中查询出对应的department id
            # print("当前的category名字是:" + category.name)
            # print("当前的categoryId是:" + str(category.id))
            tempDepartmentId = db.session.query(department_category).filter_by(category_id=category.id).all()
            # print("查关联表所有与当前category_id关联的数据：" + str(tempDepartmentId))
            # 通过department id来查询涉及到了哪些用户   左边department_id 右边category id
            tempSameCategoryUserId = set()
            for j in tempDepartmentId:
                # print("当前的department id是：" + str(j[0]))
                # 获取到所有department id等于上面department id的user id数据
                temp = db.session.query(User).filter_by(department_id=j[0]).filter_by(country=userCountry).all()
                # print("通过department id查询到的所有本地区的用户是：" + str(temp))
                # 获取到所有的user id
                for user in temp:
                    tempSameCategoryUserId.add(user.id)
                # print("当前所有的用户是：" + str(temp))

            return tempSameCategoryUserId

    except RuntimeError:
        return ApiResponse("Search failed! Please try again.", ResposeStatus.Fail)
