from flask import request
from flask_restplus import Resource, reqparse
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from agile.commons.api_doc_helper import get_request_parser_doc_dist
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.models import User, AuditLog
from agile.commons.audit import download_audit_trail, auth_audit_trail
from agile.decorators import supervisor_required
from flask_jwt_extended import current_user
from flask import current_app as app
from agile.commons import dbutil
from agile.extensions import db
import sqlalchemy as sa
from sqlalchemy import func, distinct
from sqlalchemy.sql.expression import case
from datetime import datetime, timedelta


class UsageReportList(Resource):
    method_decorators = [supervisor_required]

    @swag_from(get_request_parser_doc_dist("system usage statistics", ["Audit"]))
    def get(self):
        #  use sql for postgres
        if app.config['ENV'] == 'production':
            #  user counts by day        
            daily_users = db.session.query(func.to_char(AuditLog.ts, "YYYY-MM-DD").label('date'),
                                           func.count(distinct(AuditLog.user_id)).label('num_of_user')
                                           ).filter(AuditLog.ts >= datetime.now() + timedelta(days=-7)).group_by(
                func.to_char(AuditLog.ts, "YYYY-MM-DD")).all()
            # events count
            loginCase = case([(AuditLog.event.endswith('auth-login'), 1)], else_=0)
            downloadCase = case([(AuditLog.category == 'download', 1)], else_=0)
            user_events = db.session.query(User.username, func.sum(loginCase).label('login_times'),
                                           func.sum(downloadCase).label('download_times')
                                           ).join(User, User.id == AuditLog.user_id).filter(
                AuditLog.ts >= datetime.now() + timedelta(days=-7)
                ).group_by(User.username).all()
            # detailed events
            event_details = db.session.query(User.username, func.to_char(AuditLog.ts, "YYYY-MM-DD").label('date'),
                                             func.sum(loginCase).label('login_times'),
                                             func.sum(downloadCase).label('download_times')
                                             ).join(User, User.id == AuditLog.user_id).filter(
                AuditLog.ts >= datetime.now() + timedelta(days=-7)
                ).group_by(User.username, func.to_char(AuditLog.ts, "YYYY-MM-DD")).all()
        else:
            #  user counts by day        
            daily_users = db.session.query(func.strftime("%Y-%m-%d", AuditLog.ts).label('date'),
                                           func.count(distinct(AuditLog.user_id)).label('num_of_user')
                                           ).filter(AuditLog.ts >= datetime.now() + timedelta(days=-7)).group_by(
                func.strftime("%Y-%m-%d", AuditLog.ts)).all()
            # events count
            loginCase = case([(AuditLog.event.endswith('auth-login'), 1)], else_=0)
            downloadCase = case([(AuditLog.category == 'download', 1)], else_=0)
            user_events = db.session.query(User.username, func.sum(loginCase).label('login_times'),
                                           func.sum(downloadCase).label('download_times')
                                           ).join(User, User.id == AuditLog.user_id).filter(
                AuditLog.ts >= datetime.now() + timedelta(days=-7)
                ).group_by(User.username).all()
            # detailed events
            event_details = db.session.query(User.username, func.strftime("%Y-%m-%d", AuditLog.ts).label('date'),
                                             func.sum(loginCase).label('login_times'),
                                             func.sum(downloadCase).label('download_times')
                                             ).join(User, User.id == AuditLog.user_id).filter(
                AuditLog.ts >= datetime.now() + timedelta(days=-7)
                ).group_by(User.username, func.strftime("%Y-%m-%d", AuditLog.ts)).all()
        return ApiResponse({
            'userEvents': dbutil.queryToDict(user_events),
            'eventDetails': dbutil.queryToDict(event_details),
            'dailyUsers': dbutil.queryToDict(daily_users)
        })


def get_auditlog_args(return_parse_args=True):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "category", location="json", type=str, required=True, help="category of audit log"
    )
    parser.add_argument(
        "event", location="json", type=str, required=True, help="event of audit log"
    )
    parser.add_argument(
        "message", location="json", type=str, required=True, help="message of audit log"
    )
    parser.add_argument(
        "extra", location="json", type=str, required=False, help="extra of audit log"
    )
    return parser.parse_args() if return_parse_args else parser


class AuditLogDetail(Resource):
    @jwt_required
    @swag_from(get_request_parser_doc_dist("create new audit log", ["Audit"]))
    def post(self):
        args = get_auditlog_args()
        if args.category == 'auth':
            auth_audit_trail.send(app._get_current_object(), event=args.event, message=args.message, result='ok',
                                  user=current_user, request=request)
        elif args.category == 'download':
            download_audit_trail.send(app._get_current_object(), event=args.event, message=args.message, result='ok',
                                      user=current_user, request=request)
        return ApiResponse(None, ResposeStatus.Success)
