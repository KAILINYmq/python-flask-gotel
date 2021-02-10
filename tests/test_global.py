import factory
import logging
from agile.extensions import db
from pytest_factoryboy import register

from agile.models import User, Department, Category
from .test_user import UserFactory

logger = logging.getLogger("test_global")


@register
class DeaprtmentFactory(factory.Factory):
    name = factory.Sequence(lambda n: "ORG%d" % n)
    pred_idea_quota = 100
    bases_test_quota = 100

    class Meta:
        model = Department


def test_list_depart(client, db, admin_headers):
    rep = client.get(f"/api/v1/department", headers=admin_headers)
    assert rep.status_code == 200, rep.json


def test_list_category(client, db, admin_headers):
    rep = client.get(f"/api/v1/category", headers=admin_headers)
    assert rep.status_code == 200, rep.json
    logger.info(rep.json)


def test_update_department(client, db, admin_headers):
    """test `chagne quota and users`"""
    dept = DeaprtmentFactory.create()
    dept.categories.append(Category.find(1))
    dept.save()
    db.session.commit()
    rep = client.put(
        f"/api/v1/department/{dept.id}",
        json={"bases_test_quota": 99, "categories": [2]},
        headers=admin_headers,
    )
    assert rep.status_code == 200, rep.json
    dept = Department.find(dept.id)
    assert dept.bases_test_quota == 99
    assert rep.json["data"]["categories"] == [2]


def test_create_department(client, db, admin_headers):
    """test `chagne quota and users`"""
    rep = client.post(
        f"/api/v1/department",
        json={"name": "ORG1", "bases_test_quota": 99, "categories": [2]},
        headers=admin_headers,
    )
    assert rep.status_code == 200, rep.json
    assert rep.json["data"]["categories"] == [2]
