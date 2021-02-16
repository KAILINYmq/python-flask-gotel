# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Learn_lab(db.Model):
    """
    Learn_lab
    """
    __tablename__ = 'learn_lab'
    id = db.Column(db.Integer, primary_key=True)
    # 想法ID
    idea_id = db.Column(db.Integer, db.ForeignKey('learn.id'))
    # 标签ID
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    # 创建时间
    creat_time = db.Column(db.DateTime)
    # 更新时间
    update_time = db.Column(db.DateTime)
    # 是否删除
    is_delete = db.Column(db.Integer)