# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Idea_type(db.Model):
    """
    Idea_name
    """
    __tablename__ = 'idea_type'
    id = db.Column(db.Integer, primary_key=True)
    # 想法ID
    idea_id = db.Column(db.Integer, db.ForeignKey('idea.id'))
    # 类型ID
    type_id = db.Column(db.Integer, db.ForeignKey('type_table.id'))
    # 创建时间
    creat_time = db.Column(db.DateTime)
    # 更新时间
    update_time = db.Column(db.DateTime)
    # 是否删除
    is_delete = db.Column(db.Integer)