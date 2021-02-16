# coding: utf-8
from agile.extensions import db, pwd_context
from flask import current_app
from agile.database import AuditModel
from agile.database import reference_col, relationship
from agile.config import FLASK_ADMIN
from .role import Role
from .department import Department
from .permission import Permission


class User(AuditModel):
    """
    Basic user model
    """
    id = db.Column(db.Integer, primary_key=True)
    number=db.Column(db.Integer)
    name = db.Column(db.String(32), unique=True, nullable=False)
    # 创建时间
    creat_time = db.Column(db.DateTime)
    # 更新时间
    update_time = db.Column(db.DateTime)
    # is_del
    is_delete = db.Column(db.Integer)
    role_id = reference_col('role')
    department_id = reference_col('department')
    # 该部门和用户的关系, 返回该部门的所有用户
    #department = db.relationship('Department', passive_deletes=True, backref='users', foreign_keys=department_id)
    department = db.relationship('Department', backref='users', foreign_keys=department_id)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_ = db.Column('password', db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    is_supervisor = db.Column(db.Boolean(), default=False, nullable=False)
    is_adal = db.Column(db.Boolean(), default=False, nullable=False)

    def check_password(self, raw_password):
        result = pwd_context.verify(raw_password, self.password)
        return result

    @property
    def password(self):
        return self.password_

    @password.setter
    def password(self, raw_password):
        self.password_ = pwd_context.hash(raw_password)

    def __init__(self, **kwargs):
        is_supervisor = kwargs.get('is_supervisor', False)
        if 'is_supervisor' in kwargs:
            del kwargs['is_supervisor']
        super(User, self).__init__(**kwargs)
        if is_supervisor or self.email == FLASK_ADMIN:
            self.is_supervisor = True
            self.role = Role.query.filter_by(permissions=Permission.ADMINISTER).first()
        elif self.role_id is None:
            self.role = Role.query.filter_by(default=True).first()
        if self.department_id is None and self.department is None:
            self.department = Department.query.filter_by(default=True).first()

    def can(self, permissions):
        '''检查permissions要求的权限角色是否允许'''
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        '''检查是否管理员权限'''
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return "<User %s>" % self.username
