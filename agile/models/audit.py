import datetime
import uuid
from agile.extensions import db
from sqlalchemy_mixins import AllFeaturesMixin
from agile.database import JSONstore


def gen_id():
    return uuid.uuid4().hex


class AuditLog(db.Model, AllFeaturesMixin):
    __tablename__ = 'audit_log'

    id = db.Column(db.String(32), default=gen_id, primary_key=True)
    ts = db.Column(db.DateTime())
    ## This makes life more pleasant
    event = db.Column(db.String(20), index=True)
    category = db.Column(db.String(50))
    message = db.Column(db.String(200))
    extra = db.Column(JSONstore)
    ip = db.Column(db.String(16))
    ## More direct
    user_id = db.Column(db.Integer, index=True)
