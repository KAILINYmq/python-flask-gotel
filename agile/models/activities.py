# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Activities(db.Model):
    """
    活动
    """
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    # 活动名称
    active = db.Column(db.String(64))
    # 活动类型
    active_type = db.Column(db.String(64))
    # 活动持续时间
    active_time = db.Column(db.Integer)
    # 活动对象
    active_object = db.Column(db.String(164))
    # 描述
    description = db.Column(db.String(164))
    # 图片
    image = db.Column(db.String(164))
    # 视频
    video = db.Column(db.String(164))
    # 创意id
    idea_id = db.Column(db.Integer, db.ForeignKey('idea.id'))
    # 学习id
    learn_id = db.Column(db.Integer, db.ForeignKey('learn.id'))
    # 创建时间
    create_time = db.Column(db.DateTime)
    # 修改时间
    update_time = db.Column(db.DateTime)
    # is_del
    is_delete = db.Column(db.Integer)
