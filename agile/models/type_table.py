# coding: utf-8
from agile.extensions import db


class Type_table(db.Model):
    """
    类型
    """
    __tablename__ = 'type_table'
    id = db.Column(db.Integer, primary_key=True)
    # 类型名称
    name = db.Column(db.String(64))
    # 所属名称类型
    name_type = db.Column(db.String(64))
    # 描述
    description = db.Column(db.String(64))
    # 创建时间
    creat_time = db.Column(db.DateTime)
    # 更新时间
    update_time = db.Column(db.DateTime)
    # 名称id
    name_id = db.Column(db.Integer)
