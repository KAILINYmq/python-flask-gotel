# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Type_table(db.Model):
    """
    名称
    """
    __tablename__ = 'type_table'
    id = db.Column(db.Integer, primary_key=True)
    # 类型名称
    name = db.Column(db.String(64))
    # 描述
    description = db.Column(db.String(64))
    #持续了多长时间，单位（小时）
    duration_hours = db.Column(db.Integer)
    # 创建时间
    creat_time = db.Column(db.DateTime)
    # 更新时间
    update_time = db.Column(db.DateTime)