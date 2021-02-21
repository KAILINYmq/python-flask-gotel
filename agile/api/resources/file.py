# coding: utf-8
import os
import time

from flasgger import swag_from
from flask import send_from_directory, current_app, request
from flask_restplus import Resource, reqparse
from werkzeug.utils import secure_filename

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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


ALLOWED_EXTENSIONS = {'flv', 'avi', 'mov', 'mp4', 'wmv', 'bmp', 'jpg', 'jpeg', 'png', 'git'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB


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

    def post(self):
        file = request.files['file']
        # 对上传的文件进行判断
        if file and allowed_file(file.filename) and file.content_length <= MAX_CONTENT_LENGTH:
            # 在文件名中加入时间戳防止覆盖
            file_name = "GOTFL/" + str(int(time.time())) + secure_filename(file.filename)
            try:
                s3file.DEFAULT_BUCKET.write(file_name, file.read())
            except Exception as err:
                return ApiResponse(None, ResposeStatus.Fail, err)
            return ApiResponse(file_name)
        else:
            return ApiResponse(None, ResposeStatus.Fail, "只能上传 5 MB 以内的图片或视频")


class S3Url(Resource):
    @cache.cached(query_string=True)
    def get(self):
        args = get_args()
        object_name = args.object_name
        object_url = s3file.DEFAULT_BUCKET.generate_presigned_url(object_name)
        return ApiResponse(object_url, ResposeStatus.Success)
