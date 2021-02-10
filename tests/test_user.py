import factory
import logging
from agile.extensions import db
from pytest_factoryboy import register

from agile.models import User

logger = logging.getLogger("test_user")


@register
class UserFactory(factory.Factory):
    username = factory.Sequence(lambda n: "user{0:>04d}".format(n))
    email = factory.Sequence(lambda n: "user{0:>04d}@mail.com".format(n))
    password = "mypwd"
    department_id = 1
    role_id = 1

    class Meta:
        model = User


register(UserFactory, "normal_user")


def test_list_role(client, db, admin_headers):
    rep = client.get("/api/v1/role", headers=admin_headers)
    assert rep.status_code == 200, rep.json
    assert len(rep.json["data"]) > 0


def test_get_user_fail_without_header(client, db):
    rep = client.get("/api/v1/users/100000")
    assert rep.status_code == 401


def test_get_user(client, db, user, admin_headers):
    # test 404
    rep = client.get("/api/v1/users/100000", headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(user)
    db.session.commit()

    # test get_user
    rep = client.get("/api/v1/users/%d" % user.id, headers=admin_headers)
    assert rep.status_code == 200

    data = rep.get_json()["data"]
    logger.info(data)
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["active"] == user.active
    assert data["role"] == user.role.name
    assert data["department"] is not None


def test_change_password(client, db, user, admin_headers):
    db.session.add(user)
    db.session.commit()
    data = {"password": "123"}
    # test update user
    rep = client.put("/api/v1/users/%d" % user.id, json=data, headers=admin_headers)
    assert rep.status_code == 200
    user = User.where(id=user.id).first()
    assert user.check_password("123")


def test_put_user(client, db, user, admin_headers):
    # test 404
    rep = client.put("/api/v1/users/100000", headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(user)
    db.session.commit()

    data = {"username": "updated", "role_id": 2, "department_id": 2}

    # test update user
    rep = client.put("/api/v1/users/%d" % user.id, json=data, headers=admin_headers)
    assert rep.status_code == 200, rep.json

    data = rep.get_json()["data"]
    assert data["username"] == "updated"
    assert data["email"] == user.email
    assert data["active"] == user.active


def test_delete_user(client, db, user, admin_headers):
    # test 404
    rep = client.delete("/api/v1/users/100000", headers=admin_headers)
    assert rep.status_code == 404

    db.session.add(user)
    db.session.commit()

    # test get_user
    user_id = user.id
    rep = client.delete("/api/v1/users/%d" % user_id, headers=admin_headers)
    assert rep.status_code == 200
    assert db.session.query(User).filter_by(id=user_id).first() is None


def test_create_user(client, db, user_factory, admin_headers):
    # test bad data
    data = {"username": "created"}
    rep = client.post("/api/v1/users", json=data, headers=admin_headers)
    assert rep.status_code == 422, rep.json

    data["password"] = "admin"
    data["email"] = "create@mail.com"

    rep = client.post("/api/v1/users", json=data, headers=admin_headers)
    assert rep.status_code == 200, rep.json

    data = rep.get_json()
    user = db.session.query(User).filter_by(id=data["data"]["id"]).first()

    assert user.username == "created"
    assert user.email == "create@mail.com"

    user = user_factory.create()
    db.session.commit()
    user = db.session.query(User).filter_by(id=user.id).first()
    assert user.username != ""
    logging.getLogger().info(user.username)


def test_get_all_user(client, db, user_factory, admin_headers):
    users = user_factory.create_batch(30)

    db.session.add_all(users)
    db.session.commit()

    rep = client.get("/api/v1/users?page_size=100", headers=admin_headers)
    assert rep.status_code == 200, rep.json

    results = rep.get_json()
    assert len(results["data"]) >= 30
    for user in users:
        assert any(u["id"] == user.id for u in results["data"]), user.id


def test_filter_users(client, db, user_factory, admin_headers):
    users = user_factory.create_batch(30)
    db.session.add_all(users)
    db.session.commit()
    rep = client.get("/api/v1/users?filters=username:0001", headers=admin_headers)
    assert rep.status_code == 200, rep.json
    results = rep.get_json()
    assert len(results["data"]) == 1


def test_get_my_profile(client, db, admin_headers):
    rep = client.get("/api/v1/me", headers=admin_headers)
    assert rep.status_code == 200, rep.json
    logger.info(rep.json)
