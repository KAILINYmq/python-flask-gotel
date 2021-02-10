# coding: utf-8
from .permission import Permission
from agile.extensions import db
from agile.database import BaseModel


class Role(BaseModel):
    """
    用户角色
    """
    id = db.Column(db.Integer, primary_key=True)
    # 该用户角色名称
    name = db.Column(db.String(164))
    # 该用户角色是否为默认
    default = db.Column(db.Boolean, default=False, index=True)
    # 该用户角色对应的权限
    permissions = db.Column(db.Integer)
    # 该用户角色和用户的关系, 返回该用户角色的所有用户
    users = db.relationship('User', backref='role', lazy='dynamic')

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def authorized_permissions(self):
        permissions = []
        for pname in Permission.__dict__.keys():
            p = getattr(Permission, pname)
            if isinstance(p, int):
                if self.has_permission(p):
                    permissions.append(str(pname))
        return permissions

    @staticmethod
    def init_roles():
        """
        创建用户角色
        """
        roles = {
            # 定义了两个用户角色(User, Admin)
            'TrendUser': (Permission.TREND_VIEWER, True),
            'Admin': (Permission.ADMINISTER, False),
            'IdeaUser': (
            Permission.TREND_VIEWER | Permission.IDEAGEN_CONTRIBUTOR | Permission.IDEATEST_CONTRIBUTOR, False),
            'IdeaTestApprover': (Permission.TREND_VIEWER | Permission.IDEATEST_APPROVER, False),
            'IdeaTestBasesAdmin': (Permission.TREND_VIEWER | Permission.IDEATEST_BASES_MANAGE, False),
            'ClaimAdvisorUser': (Permission.TREND_VIEWER | Permission.CLAIMADVISOR_CONTRIBUTOR, False),
            'ClaimAdvisorAdmin': (Permission.TREND_VIEWER | Permission.CLAIMADVISOR_ADMIN, False),
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # 如果用户角色没有创建: 创建用户角色
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
