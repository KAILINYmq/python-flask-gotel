from .permission import Permission
from agile.extensions import db
from agile.database import AuditModel
from .category import Category

department_category = db.Table(
    "department_category",
    db.Column(
        "department_id", db.Integer, db.ForeignKey("department.id"), primary_key=True
    ),
    db.Column(
        "category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True
    ),
)


class Department(AuditModel):
    """
    用户角色
    """

    id = db.Column(db.Integer, primary_key=True)
    # 该部门名称
    name = db.Column(db.String(164))
    # 该部门是否为默认
    default = db.Column(db.Boolean, default=False, index=True)

    categories = db.relationship(
        "Category", secondary=department_category, backref="departments"
    )
    bases_test_quota = db.Column(db.Integer, default=0)
    pred_idea_quota = db.Column(db.Integer, default=0)

    __mapper_args__ = {"order_by": id}

    @staticmethod
    def init_departments():
        """
        创建部门
        """
        departments = {
            # 定义了两个用户角色(User, Admin)
            ("CMI", True, None),
            ("Fabric Solution", False, ("Fabric Solution",)),
            ("Fabric Sensation", False, ("Fabric Sensation",)),
            ("Personal Wash", False, ("Personal Wash",)),
            ("Hair Care", False, ("Shampoo", "Postwash")),
            ("Skin Care", False, ("Skin Care")),
            ("Oral", False, ("Oral",)),
            ("Icecream", False, ("Icecream",)),
            ("Excubator", False, ("Postwash",)),
        }
        for dpt_name, default_, categories in departments:
            dpt = Department.query.filter_by(name=dpt_name).first()
            if dpt is None:
                # 如果用户角色没有创建: 创建用户角色
                dpt = Department(name=dpt_name)

            dpt.default = default_
            if dpt_name == "CMI":
                dpt.categories = Category.all()
            else:
                for cate in categories:
                    dpt.categories.append(Category.where(name=cate).first())
        db.session.commit()
