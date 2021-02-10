# coding: utf-8
""" demo: https://vickyliin.github.io/config-yaml/demo/demo.html"""
import yaml
import os.path
from argparse import Namespace
from yaml import dump
from yaml import load
from DictObject import DictObject

_tag = '!{.__name__}'
_path, args = None, None


def register(cls):
    yaml.add_representer(cls, cls.representer)
    yaml.add_constructor(_tag.format(cls), cls.constructor)
    return cls


@register
class YamlConfig(Namespace):
    def __repr__(self):
        return yaml.dump(self)

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return iter(self.__dict__.items())

    @classmethod
    def representer(cls, dumper, data):
        assert type(data) == cls
        return dumper.represent_mapping(
            _tag.format(cls),
            data.__dict__,
            flow_style=False
        )

    @classmethod
    def constructor(cls, loader, node):
        result = cls()
        yield result
        mapping = loader.construct_mapping(node)
        result.__dict__ = mapping


def set_path(path):
    global _path, args
    _path = path
    with open(path, 'r') as f:
        args = DictObject(yaml.load(f))


def get_path():
    return _path
