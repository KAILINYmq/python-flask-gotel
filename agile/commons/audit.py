import json
import uuid
from functools import partial
from datetime import datetime
from typing import Any, List
import blinker
import requests
from agile.models.audit import AuditLog
from agile.extensions import db
from flask import Flask, g

audit_signals = blinker.Namespace()

auth_audit_trail = audit_signals.signal('auth')
download_audit_trail = audit_signals.signal('download')


class AuditTrail:

    def __init__(self, app: Flask = None) -> None:
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        if 'auth' in app.config['AUDIT_TRAIL']:
            auth_audit_trail.connect(self.auth_db_response)

        if 'download' in app.config['AUDIT_TRAIL']:
            download_audit_trail.connect(self.download_db_response)

    def _db_response(self, app: Flask, category: str, event: str, message: str, user: str, request: Any,
                     **extra: Any) -> None:
        obj = AuditLog(category=category,
                       ts=datetime.now(),
                       event=event,
                       message=message,
                       user_id=user.id,
                       ip=request.remote_addr,
                       extra=extra)
        db.session.add(obj)
        db.session.commit()

    def _log_response(self, app, category: str, event: str, message: str, user: str, request: Any,
                      **extra: Any) -> None:
        app.logger.info(self._fmt(app, category, event, message, user, request, **extra))

    def auth_db_response(self, app: Flask, **kwargs):
        self._db_response(app, 'auth', **kwargs)

    def download_db_response(self, app: Flask, **kwargs):
        self._db_response(app, 'download', **kwargs)

    @staticmethod
    def _fmt(app, category: str, event: str, message: str, user: str, request: Any, **extra: Any) -> str:
        return {
            'id': str(uuid.uuid4()),
            'ts': datetime.now(),
            'event': event,
            'category': category,
            'message': message,
            'user_id': user.id if user else -1,
            'ip': request.remote_addr,
            'extra': extra
        }
