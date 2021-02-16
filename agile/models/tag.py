# coding: utf-8
from agile.extensions import db
from agile.database import BaseModel

class Tag(BaseModel):
    """
    标签
    """
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    # 标签名称
    label = db.Column(db.String(64))
    # 所属标签名字
    label_type = db.Column(db.String(64))
    # 描述
    description = db.Column(db.String(164))
    # 创建时间
    create_time = db.Column(db.DateTime)
    # 修改时间
    update_time = db.Column(db.DateTime)
