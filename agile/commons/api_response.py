#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import make_response
import json
from .format import CustomJSONEncoder


class ApiResult(object):
    def __init__(self, status, message, code):
        self.status_code = code
        self.message = message
        self.restful_status = status


class ResposeStatus(object):
    Success = ApiResult('Success', 'success', 200)
    Fail = ApiResult('Error', 'operation failed', 400)
    ParamFail = ApiResult("Param fail", "params not invaild", 422)
    AuthenticationFailed = ApiResult("authentication fail", "invalid user or password", 401)
    Powerless = ApiResult("Power failed", "permission required", 403)


def ApiResponse(obj=None, status=ResposeStatus.Success, msg=None):
    return make_response(json.dumps({
        "data": obj,
        "message": msg or status.message,
        "status": status.restful_status
    }, cls=CustomJSONEncoder), status.status_code)
