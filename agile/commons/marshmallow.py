# coding: utf-8
import functools
from marshmallow_peewee import ModelSchema
from marshmallow.fields import Field
from marshmallow import ValidationError
from marshmallow_peewee import Related
from marshmallow.validate import (
    URL, Email, Range, Length, Equal, Regexp,
    Predicate, NoneOf, OneOf, ContainsOnly
)
from .api_response import ResposeStatus, ApiResponse
from flask import request

"""[marshmallow轻量自动化验证和序列化][https://www.jianshu.com/p/6e91863008b3]
"""


def validate_schema(_model, **schema_kwargs):
    """
    用于检查参数正确性。

    :param _model: 数据库模块，用于绑定字段校验。
    :param schema_kwargs:  根据marshmallow.schema.Schema的
                            参数要求进行要求，下面是详细参数列表:
                            extra=None
                            only=()
                            exclude=()
                            prefix=''
                            strict=None
                            many=False
                            context=None
                            load_only=()
                            dump_only=()
                            partial=False
    :return: 校验正确则执行handler，校验失败则返回错误信息。
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):

            class CommonSchema(ModelSchema):

                class Meta:
                    model = _model

            # 检查验证结果
            try:
                result = (CommonSchema(**schema_kwargs)
                          .load(request.json))
            except ValidationError as ex:
                # 当验证结果存在错误时, 返回错误信息.
                msg = ['{}{}'.format(getattr(_model, k).verbose_name, v[0])
                       for k, v in ex.messages.items()]
                return ApiResponse(None, ResposeStatus.ParamFail, msg=msg)

            # 当验证结果正确时, 执行handler.
            return f(self, *args, **kwargs)

        return wrapper

    return decorator


def serializer_schema(_model, *related, **schema_kwargs):
    """
    用于序列化。
    :param _model: 数据库模块，用于绑定字段校验。
    :param related: 声明那些关联字段是需要一起序列化的，参数格式如下:
                     [
                     # 表示外键
                     (field_name, None),
                     # 表示该字段为不是关联字段，但序列化需要存在的字段.
                     (field_name, callback)
                     ]
    :param schema_kwargs: 根据marshmallow.schema.Schema的
                            参数要求进行要求，下面是详细参数列表:
                            extra=None
                            only=()
                            exclude=()
                            prefix=''
                            strict=None
                            many=False
                            context=None
                            load_only=()
                            dump_only=()
                            partial=False
    :return: 返回经过序列化后的数据集。
    """

    class CommonSchema:
        class Meta:
            model = None

    # 绑定类对象
    CommonSchema.Meta.model = _model
    [setattr(CommonSchema, field, callback())
     if callback else setattr(CommonSchema, field, Related())
     for field, callback in related]

    # 混入
    schema_cls = type(
        str('CommonSchema'), (CommonSchema, ModelSchema), {}
    )

    return schema_cls(**schema_kwargs)
