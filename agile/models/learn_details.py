# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Learn_type(db.Model):
    """
    Learn_type
    """
    __tablename__ = 'learn_details'
    id = db.Column(db.Integer, primary_key=True)
    # 想法ID
    idea_id = db.Column(db.Integer, db.ForeignKey('learn.id'))
    # 类型ID
    details_id = db.Column(db.Integer, db.ForeignKey('details_table.id'))
    # 创建时间
    creat_time = db.Column(db.DateTime)
    # 更新时间
    update_time = db.Column(db.DateTime)
    # 是否删除
    is_delete = db.Column(db.Integer)