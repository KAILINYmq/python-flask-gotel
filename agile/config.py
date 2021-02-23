"""Default configuration

Use env var to override
"""
import yaml
import os
from dotenv import load_dotenv, find_dotenv
from datetime import timedelta

# important: need to override exising env vars
load_dotenv(find_dotenv(".env"), override=True)
ENV = os.getenv("FLASK_ENV") or "development"
DEBUG = ENV == "development"

load_dotenv(find_dotenv(f".env.{ENV}"), override=True)
FLASK_ADMIN = os.getenv("FLASK_ADMIN")
SECRET_KEY = os.getenv("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

SQLALCHEMY_POOL_SIZE = 50
SQLALCHEMY_POOL_RECYCLE = 8
SQLALCHEMY_POOL_TIMEOUT= 60
print("trend-api-db:", SQLALCHEMY_DATABASE_URI)
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
JWT_VERIFY_EXPIRATION = True
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND_URL")
SQLALCHEMY_BINDS = {
}
# global thread safe
CACHE_TYPE = "filesystem"
CACHE_DIR = "./cache"
CACHE_DEFAULT_TIMEOUT = 3600
UPLOAD_FOLDER = "upload"
CONCEPT_FOLDER = "concept"
CONCEPT_PROGRAMME_FOLDER = "programme"
CONCEPT_IDEA_FOLDER = "idea"
# JWT token expires minites
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
AUDIT_TRAIL = ['auth', 'download']

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_SECRET_KEY_ID = os.getenv("S3_SECRET_KEY_ID")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
S3_REGION = os.getenv("S3_REGION")