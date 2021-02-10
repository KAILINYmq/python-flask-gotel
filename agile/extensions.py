# coding: utf-8
"""Extensions registry

All extensions here are used as singletons and
initialized in application factory
"""
from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_caching import Cache
from celery import Celery
from agile.commons.apispec import APISpecExt

apispec = APISpecExt()

# 不自动提交SQL, session.flush()确认
db = SQLAlchemy(session_options={'autoflush': False})
cache = Cache()
jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate()
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
celery = Celery()
