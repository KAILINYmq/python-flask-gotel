# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Idea(db.Model):
    """
    创意
    """
    __tablename__ = 'idea'
    id = db.Column(db.Integer, primary_key=True)
    # 姓名
    name = db.Column(db.String(64))
    # 描述
    description = db.Column(db.String(64))