# coding: utf-8
import os

from flasgger import swag_from
from flask import send_from_directory, current_app
from flask_restplus import Resource, reqparse

from agile.commons import s3file
from agile.commons.api_doc_helper import get_request_parser_doc_dist
from agile.commons.api_response import ResposeStatus, ApiResponse
from agile.extensions import cache


def get_args(return_parse_args=True):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", location="args", type=str, required=True, help="file name"
    )
    return parser.parse_args() if return_parse_args else parser


class FileList(Resource):
    @swag_from(
        get_request_parser_doc_dist(
            "download file",
            ["File"],
            get_args(False),
            "file",
        )
    )
    def get(self):
        args = get_args()
        filename = current_app.config['UPLOAD_FOLDER'] + '/' + args.name
        upload_dir, filename = filename.rsplit('/', 1)
        # if relative path is used, found in current_app.root_path by default, which is agile folder
        upload_dir = os.path.abspath(upload_dir)
        return send_from_directory(upload_dir, filename)


class S3Url(Resource):
    @cache.cached(query_string=True)
    def get(self):
        args = get_args()
        object_name = args.object_name
        object_url = s3file.DEFAULT_BUCKET.generate_presigned_url(object_name)
        return ApiResponse(object_url, ResposeStatus.Success)
