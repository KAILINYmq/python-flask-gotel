# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
from .compat import basestring
from .extensions import db
import json
from sqlalchemy_mixins import AllFeaturesMixin
from flask import current_app
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from flask_jwt_extended import current_user, get_jwt_claims

# Alias common SQLAlchemy names
Column = db.Column
relationship = db.relationship


class JSONstore(sa.types.TypeDecorator):
    impl = sa.types.Text

    def process_bind_param(self, value, dialect):
        # print "BINDING : %s" % value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        # print "RESULT : %s" % value
        return json.loads(value)


class TimestampsMixin:
    """Mixin that define timestamp columns."""

    __abstract__ = True

    __created_at_name__ = 'created_at'
    __updated_at_name__ = 'updated_at'
    __datetime_callback__ = datetime.utcnow

    created_at = sa.Column(__created_at_name__,
                           sa.DateTime,
                           default=__datetime_callback__,
                           nullable=False)

    updated_at = sa.Column(__updated_at_name__,
                           sa.DateTime,
                           default=__datetime_callback__,
                           nullable=False)
    __mapper_args__ = {
        "order_by": created_at.desc()
    }


class AuditMixin(TimestampsMixin):
    """
        AuditMixin
        Mixin for models, adds 4 columns to stamp,
        time and user on creation and modification
        will create the following columns:
        :created by:
        :changed by:
    """

    @declared_attr
    def created_by_fk(cls):
        return sa.Column(
            sa.Integer, default=cls.get_user_id, nullable=True
        )

    @declared_attr
    def created_by(cls):
        return relationship(
            "User",
            primaryjoin="foreign(%s.created_by_fk) == remote(User.id)" % cls.__name__,
            # create relationship without foreign key
            enable_typechecks=False,
        )

    @declared_attr
    def updated_by_fk(cls):
        return sa.Column(
            sa.Integer,
            default=cls.get_user_id,
            onupdate=cls.get_user_id,
            nullable=True
        )

    @declared_attr
    def updated_by(cls):
        return relationship(
            "User",
            primaryjoin="foreign(%s.updated_by_fk) == remote(User.id)" % cls.__name__,
            # create relationship without foreign key
            enable_typechecks=False,
        )

    @classmethod
    def get_user_id(cls):
        try:
            return current_user.id
        except Exception:
            return 1


@sa.event.listens_for(AuditMixin, 'before_update', propagate=True)
def _receive_before_update(mapper, connection, target):
    """Listen for updates and update `updated_at` column."""
    target.updated_at = target.__datetime_callback__()
    if current_user:
        target.updated_by_fk = current_user.id


class PermissionMixin(object):
    """
        check if has data object access authorization
        数据签权, 同一部门下的员工可以互相访问
    """

    def has_permission(self):
        if hasattr(self, 'create_by'):
            department = self.created_by.department
            return department == current_user.department or current_user.department.name == 'CMI'
        return True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class."""

    __table_args__ = {"extend_existing": True}

    id = Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
                (
                        isinstance(record_id, basestring) and record_id.isdigit(),
                        isinstance(record_id, (int, float)),
                )
        ):
            return cls.query.get(int(record_id))
        return None


def reference_col(
        tablename, nullable=False, pk_name="id", foreign_key_kwargs=None, column_kwargs=None):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return Column(
        db.ForeignKey("{0}.{1}".format(tablename, pk_name), **foreign_key_kwargs),
        nullable=nullable,
        **column_kwargs
    )


class BaseModel(db.Model, SurrogatePK, AllFeaturesMixin, PermissionMixin):
    __abstract__ = True
    pass


class AuditModel(BaseModel, AuditMixin):
    __abstract__ = True
    pass
