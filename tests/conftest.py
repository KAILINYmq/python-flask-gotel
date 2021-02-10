# coding: utf-8
import json
import pytest
import sqlalchemy as sa
from agile.models import User, Role, Department, Category, PredIdea
from agile.app import create_app
from agile.extensions import db as _db
import dotenv
import pandas as pd

dotenv.load_dotenv('.env')


@pytest.fixture(scope="package")
def app():
    app = create_app(testing=True)
    return app


def _create_database(app):
    DB_NAME = 'agile_test'
    template_engine = _db.get_engine(app=app)
    conn = template_engine.connect()
    conn = conn.execution_options(autocommit=False)
    conn.execute("ROLLBACK")

    try:
        conn.execute("DROP DATABASE %s" % DB_NAME)
    except sa.exc.ProgrammingError as err:
        # Could not drop the database, probably does not exist
        conn.execute("ROLLBACK")
    except sa.exc.OperationalError as err:
        # Could not drop database because it's being accessed by other users (psql prompt open?)
        conn.execute("ROLLBACK")

    conn.execute("CREATE DATABASE %s" % DB_NAME)
    conn.close()
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', maxsplit=1)[
                                                0] + f'/{DB_NAME}'
    template_engine.dispose()


@pytest.fixture(scope="package")
def db(app):
    _db.app = app
    with app.app_context():
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            _db.create_all()
            # setup default data
            Role.init_roles()
            Category.init_categories()
            Department.init_departments()
            PredIdea.init_predideas()
            _db.session.commit()
            yield _db
            _db.session.expunge_all()
            _db.session.rollback()
            _db.session.close()
            _db.drop_all()
        else:
            yield _db
        #     _create_database(app)


@pytest.fixture(scope="package")
def admin_user(db):
    user = User(
        username='admin',
        email='admin@admin.com',
        password='admin',
        is_supervisor=True
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_headers(admin_user, client, db):
    admin_user = db.session.merge(admin_user)
    data = {
        'username': admin_user.username,
        'password': 'admin'
    }
    rep = client.post(
        '/api/v1/auth/login',
        data=json.dumps(data),
        headers={'content-type': 'application/json'}
    )
    tokens = json.loads(rep.get_data(as_text=True))
    return {
        'content-type': 'application/json',
        'authorization': 'Bearer %s' % tokens['access_token']
    }


@pytest.fixture
def admin_refresh_headers(admin_user, client, db):
    admin_user = db.session.merge(admin_user)
    data = {
        'username': admin_user.username,
        'password': 'admin'
    }
    rep = client.post(
        '/api/v1/auth/login',
        data=json.dumps(data),
        headers={'content-type': 'application/json'}
    )

    tokens = json.loads(rep.get_data(as_text=True))
    return {
        'content-type': 'application/json',
        'authorization': 'Bearer %s' % tokens['refresh_token']
    }
