from datetime import datetime

from flask import request
from flask_restplus import Resource

from agile.api.resources.tag import timeConvert
from agile.commons.api_response import ApiResponse, ResposeStatus
from agile.extensions import db
from agile.models import Activities


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
