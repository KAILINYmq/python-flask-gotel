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
    #
    idea_id = db.Column(db.String(255))
    #
    image = db.Column(db.String(255))
    #
    video = db.Column(db.String(255))
    # 创建时间
    create_time = db.Column(db.DateTime)
    # 更新时间
    update_time = db.Column(db.DateTime)
    #
    active_id = db.Column(db.Integer)
    # 用户id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))