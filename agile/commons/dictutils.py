# coding: utf-8
DEF_DELIMITER = '.'


def get_value(_dict, key=None, def_value=None, delimiter=DEF_DELIMITER):
    """
    支持嵌套的方式获取复杂结构的字典中的值，例如：
    _dict = {'key1':{'key1_1':1,'key1_2':2},'key_2':3}

    get_value(_dict, 'key1') => {'key1_1':1,'key1_2':2}
    get_value(_dict, 'key1.key1_1') => 1
    get_value(_dict, 'key1.key1_2') => 2
    get_value(_dict, 'key_2') => 3

    :param _dict: 字典结构，可以是复杂的嵌套结构
    :param key: 希望获取的值对应的键，可以用分隔符连接表示嵌套获取
    :param delimiter: 分隔符，默认为：.
    :param def_value: 默认值
    :return: 字典中对应的值
    """
    if not _dict:
        return def_value
    if not key:
        return _dict
    value = None
    if type(key) is not list:
        value = __do_get_value(_dict, key, delimiter)
    else:
        for key0 in key:
            value = __do_get_value(_dict, key0, delimiter)
            if value is not None:
                return value
    if not value:
        return def_value
    return value


def __do_get_value(_dict, key, delimiter):
    split_keys = key.split(delimiter)
    cur_elem = _dict
    for split_key in split_keys:
        if cur_elem and split_key in cur_elem:
            cur_elem = cur_elem[split_key]
        else:
            return None
    return cur_elem


def find(dict_list: list, *dict_filter_list: []):
    for dict_filter in dict_filter_list:
        result = _do_find(dict_list, dict_filter)
        if result:
            return result
    return None


def find_all(dict_list: list, *dict_filter_list: []):
    for dict_filter in dict_filter_list:
        result = _do_find_all(dict_list, dict_filter)
        if result:
            return result
    return None


def _do_find(dict_list: list, dict_filter: dict):
    if not dict_list:
        return None
    for dict_item in dict_list:
        find_it = True
        for key in dict_filter:
            if not __equals(dict_item[key], dict_filter[key]):
                find_it = False
                break
        if find_it:
            return dict_item
    return None


def _do_find_all(dict_list: list, dict_filter: dict):
    if not dict_list:
        return None
    result = []
    for dict_item in dict_list:
        find_it = True
        for key in dict_filter:
            if not __equals(dict_item[key], dict_filter[key]):
                find_it = False
                break
        if find_it:
            result.append(dict_item)
    return result


def __equals(o1, o2):
    if not o1:
        return not o2
    if not o2:
        return False
    if o1 == o2:
        return True
    if type(o1) == str and type(o2) == str:
        return o1.upper() == o2.upper()
