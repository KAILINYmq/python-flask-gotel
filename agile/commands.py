# -*- coding: utf-8 -*-
"""Click commands."""
import os
from tqdm import tqdm
from glob import glob
from subprocess import call
import datetime
import click
from flask import current_app
from flask.cli import with_appcontext
from werkzeug.exceptions import MethodNotAllowed, NotFound
from agile.extensions import db
from agile.models import User, Permission, Department, Category, Role
from agile.models.concept_resource import Brand, Packing, Background
import pandas as pd

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """Run the tests."""
    import pytest
    rv = pytest.main([TEST_PATH, '--verbose'])
    exit(rv)


@click.command()
@click.option('-f', '--fix-imports', default=False, is_flag=True,
              help='Fix imports using isort, before linting')
def lint(fix_imports):
    """Lint and check code style with flake8 and isort."""
    skip = ['node_modules', 'requirements']
    root_files = glob('*.py')
    root_directories = [
        name for name in next(os.walk('.'))[1] if not name.startswith('.')]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo('{}: {}'.format(description, ' '.join(command_line)))
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    if fix_imports:
        execute_tool('Fixing import order', 'isort', '-rc')
    execute_tool('Checking code style', 'flake8')


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.

    Borrowed from Flask-Script, converted to use Click.
    """
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dirpath, filename)
                click.echo('Removing {}'.format(full_pathname))
                os.remove(full_pathname)


@click.command()
@click.option('--url', default=None,
              help='Url to test (ex. /static/image.png)')
@click.option('--order', default='rule',
              help='Property on Rule to order by (default: rule)')
@with_appcontext
def urls(url, order):
    """Display all of the url matching routes for the project.

    Borrowed from Flask-Script, converted to use Click.
    """
    rows = []
    column_length = 0
    column_headers = ('Rule', 'Endpoint', 'Arguments')

    if url:
        try:
            rule, arguments = (
                current_app.url_map
                    .bind('localhost')
                    .match(url, return_rule=True))
            rows.append((rule.rule, rule.endpoint, arguments))
            column_length = 3
        except (NotFound, MethodNotAllowed) as e:
            rows.append(('<{}>'.format(e), None, None))
            column_length = 1
    else:
        rules = sorted(
            current_app.url_map.iter_rules(),
            key=lambda rule: getattr(rule, order))
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, None))
        column_length = 2

    str_template = ''
    table_width = 0

    if column_length >= 1:
        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4
        str_template += '{:' + str(max_rule_length) + '}'
        table_width += max_rule_length

    if column_length >= 2:
        max_endpoint_length = max(len(str(r[1])) for r in rows)
        # max_endpoint_length = max(rows, key=len)
        max_endpoint_length = (
            max_endpoint_length if max_endpoint_length > 8 else 8)
        str_template += '  {:' + str(max_endpoint_length) + '}'
        table_width += 2 + max_endpoint_length

    if column_length >= 3:
        max_arguments_length = max(len(str(r[2])) for r in rows)
        max_arguments_length = (
            max_arguments_length if max_arguments_length > 9 else 9)
        str_template += '  {:' + str(max_arguments_length) + '}'
        table_width += 2 + max_arguments_length

    click.echo(str_template.format(*column_headers[:column_length]))
    click.echo('-' * table_width)

    for row in rows:
        click.echo(str_template.format(*row[:column_length]))


@click.command("init")
@with_appcontext
def init():
    """Init application, create database tables
    and create a new user named admin with password admin
    """
    click.echo("create database")
    db.create_all()
    click.echo("create roles")
    Role.init_roles()
    click.echo("create categories")
    Category.init_categories()
    click.echo("create departments")
    Department.init_departments()
    click.echo("create user")
    if not User.where(username='admin').first():
        user = User(
            is_supervisor=True,
            username='admin',
            email='admin@mail.com',
            password='Unilever1234',
            active=True
        )
        db.session.add(user)
        db.session.commit()
    if not User.where(username='excubator').first():
        user = User(
            username='excubator',
            email='excubator@mail.com',
            department=Department.where(name='Excubator').first(),
            is_adal=False,
            password='excubator',
            active=True
        )
        db.session.add(user)
        db.session.commit()
    click.echo("create brand")
    Brand.init_brand()
    click.echo("create packing")
    Packing.init_packing()
    click.echo("create background")
    Background.init_background()
    click.echo("db init finished")


@click.command("load_bases")
@with_appcontext
def load_bases():
    stmt = PredIdea.__table__.delete().where(PredIdea.bases_test != None)
    db.session.execute(stmt)
    db.session.commit()
    PredIdea.init_predideas()


@click.command("token")
@click.option("-u",
              "--username",
              prompt='username',
              help="input username")
@click.option("-p",
              "--password",
              prompt='password',
              help="input password")
@with_appcontext
def generate_token(username, password):
    """ generate permanent token
    """
    from agile.models import User
    from flask_jwt_extended import (
        create_access_token
    )
    from agile.auth.helpers import (
        add_token_to_database
    )
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = password
    else:
        user = User(
            username=username,
            email=username + '@unilever.com',
            password=password,
            active=True
        )
    db.session.add(user)
    db.session.commit()
    # create_access_token
    access_token = create_access_token(identity=user.id, fresh=False, expires_delta=False)
    add_token_to_database(access_token, current_app.config['JWT_IDENTITY_CLAIM'])
    print(access_token)


@click.command()
@with_appcontext
@click.option('-u', '--user_name', prompt='user_name')
@click.option('-r', '--role_name', prompt='role_name')
def add_user_to_role(user_name, role_name):
    user = User.query.filter_by(username=user_name).first()
    if user:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            role.users.append(user)
            db.session.commit()
            print('用户{}添加到角色{}成功'.format(user_name, role_name))
        else:
            print('没有这个角色：{}'.format(role_name))
    else:
        print('没有这个用户：{}'.format(user_name))


@click.command()
@with_appcontext
@click.option('-u', '--user_name', prompt='user_name')
def test_permission(user_name):
    user = User.query.first()  # 目前我数据库只有一个账号
    if user.is_administrator():
        print('用户{}有管理员的权限'.format(user_name))
    permissions = user.role.authorized_permissions()
    print('权限：{}'.format(','.join(permissions)))

