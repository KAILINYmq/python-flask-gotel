# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Praise(db.Model):
    """
    点赞
    """
    __tablename__ = 'praise'
    id = db.Column(db.Integer, primary_key=True)
    # 点赞人id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 点赞作品类型
    type = db.Column(db.String(32))
    # 点赞作品id
    work_id = db.Column(db.Integer)
    # 是否点赞
    is_give = db.Column(db.Integer)
    # 点赞时间
    time = db.Column(db.DateTime)
