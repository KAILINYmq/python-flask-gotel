# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Learn(db.Model):
    """
    学习
    """
    __tablename__ = 'learn'
    id = db.Column(db.Integer, primary_key=True)
    # 姓名
    name = db.Column(db.String(64))
    # 描述
    description = db.Column(db.String(64))
    # 创建时间
    creat_time = db.Column(db.DateTime)
    # 更新时间
    update_time = db.Column(db.DateTime)