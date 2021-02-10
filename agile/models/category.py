from .permission import Permission
from agile.extensions import db
from agile.database import AuditModel

ALL_CATEGORY = [
    ('Fabric Solution', 'Home Care', 'HCL'),
    ('Fabric Sensation', 'Home Care', 'HCS'),
    ('Shampoo', 'Beauty & Personal Care', 'PCS'),
    ('Postwash', 'Beauty & Personal Care', 'PCP'),
    ('Personal Wash', 'Beauty & Personal Care', 'PWS'),
    ('Skin Care', 'Beauty & Personal Care', 'BSC'),
    ('Oral', 'Personal Care', 'PCO'),
    ('Icecream', 'Refreshment', 'REI'),
]

ALL_CATEGORY_CODE = [item[2] for item in ALL_CATEGORY]


class Category(AuditModel):
    """
    用户角色
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    group = db.Column(db.String(50))
    code = db.Column(db.String(3))

    __mapper_args__ = {
        "order_by": id
    }

    def __init__(self, **kwargs):
        if 'code' in kwargs:
            kwargs['code'] = kwargs['code'].upper()
        super(Category, self).__init__(**kwargs)

    @staticmethod
    def init_categories():
        """
        创建品类
        """
        for cat_name, group_, code_ in ALL_CATEGORY:
            cat = Category.query.filter_by(name=cat_name).first()
            if cat is None:
                # 如果用户角色没有创建: 创建用户角色
                cat = Category(name=cat_name, group=group_, code=code_)
            cat.code = code_
            cat.group = group_
            cat.save()
        db.session.commit()
