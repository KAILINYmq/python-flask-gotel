# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Guestbook(db.Model):
    """
    留言
    """
    __tablename__ = 'guestbook'
    id = db.Column(db.Integer, primary_key=True)
    # 类型名称
    type = db.Column(db.String(32))
    # 描述
    description = db.Column(db.String(32))
    # 创建时间
    time = db.Column(db.DateTime)
    # 状态
    state = db.Column(db.String(32))
    # 留言人id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))