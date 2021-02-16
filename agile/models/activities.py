# coding: utf-8
from agile.extensions import db
import datetime

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

    # 创意
    idea_name = db.Column(db.String(164))
    # 学习
    learn_name = db.Column(db.String(164))

    # 创建时间
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    # 修改时间
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    # is_del
    is_delete = db.Column(db.Integer, default=0)
