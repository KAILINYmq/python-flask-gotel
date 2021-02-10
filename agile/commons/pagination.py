# coding: utf-8
"""Simple helper to paginate query
"""
import math
from flask import url_for, request
import flask_restplus as f
from agile.extensions import ma, db
from agile.commons import dbutil
from .api_response import ResposeStatus
from sqlalchemy import text

DEFAULT_PAGE_SIZE = 10
DEFAULT_PAGE_NUMBER = 1


def paginate(query, schema):
    """
    data pagination with sqlalchemy query
    :param query: SqlAlchemy query object
    :param schema: serializer schema using dict spec by default, refer to marshmallow object if marshmallow is true
    """

    page = request.args.get("page", DEFAULT_PAGE_NUMBER, type=int)
    per_page = request.args.get("page_size", DEFAULT_PAGE_SIZE, type=int)
    page_obj = query.paginate(page=page, per_page=per_page)
    next = url_for(
        request.endpoint,
        page=page_obj.next_num if page_obj.has_next else page_obj.page,
        page_size=per_page,
        **request.view_args,
    )
    prev = url_for(
        request.endpoint,
        page=page_obj.prev_num if page_obj.has_prev else page_obj.page,
        per_page=per_page,
        **request.view_args,
    )
    status = ResposeStatus.Success
    # 测试marshmallow序列化方法
    marshmallow = isinstance(schema, ma.ModelSchema)
    return {
        "total": page_obj.total,
        "pages": page_obj.pages,
        "next": next,
        "prev": prev,
        "data": schema.dump(page_obj.items, many=True)
        if marshmallow
        else f.marshal(page_obj.items, schema),
        "message": status.message,
        "status": status.status_code,
    }


def paginate_bysql(sql, params=None, flat_list=False, bind=None):
    """
    data pagination with raw sql
    :param sql: SqlAlchemy query object
    :param flat_list: serializer schema using dict spec by default, refer to marshmallow object if marshmallow is true
    """
    page = request.args.get("page", DEFAULT_PAGE_NUMBER, type=int)
    per_page = request.args.get("page_size", DEFAULT_PAGE_SIZE, type=int)
    stmt1, stmt2 = sql.replace("SELECT", "select").rsplit("select", maxsplit=1)
    # 通过子查询返回总行数
    stmt = f"{stmt1} select count(*) as count from (select {stmt2}) a"

    dbu = dbutil.DbUtil()
    with dbu.auto_commit(bind=bind):
        ret = dbu.select(stmt, params)
        total_size = ret[0]["count"]
        total_pages = math.ceil(total_size / per_page)
        offset_size = per_page * (page - 1)
        if total_size == 0 or offset_size > total_size:
            data = []
        else:
            sql = sql + f" limit {per_page} offset {offset_size}"
            data = dbu.select(sql, params, flat_list=flat_list)

    status = ResposeStatus.Success
    return {
        "total": total_size,
        "pages": total_pages,
        "data": data,
        "message": status.message,
        "status": status.status_code,
    }
