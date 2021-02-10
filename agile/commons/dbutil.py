import pandas as pd
from contextlib import contextmanager
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime as cdatetime  # 有时候会返回datatime类型
from datetime import date, time
from flask_sqlalchemy import Model
from sqlalchemy.orm.query import Query
from sqlalchemy import DateTime, Numeric, Date, Time  # 有时又是DateTime
from agile.extensions import db


def safe_tsquery(text):
    def safestr(text):
        for c in reserve_chars:
            text = text.replace(c, '')
        return text

    reserve_chars = ':<()!& '
    if isinstance(text, str):
        return safestr(text)
    elif isinstance(text, list):
        return list(map(safestr, text))


def queryToDict(models):
    if (isinstance(models, list)):
        if (isinstance(models[0], Model)):
            lst = []
            for model in models:
                gen = model_to_dict(model)
                dit = dict((g[0], g[1]) for g in gen)
                lst.append(dit)
            return lst
        else:
            res = result_to_dict(models)
            return res
    else:
        if (isinstance(models, Model)):
            gen = model_to_dict(models)
            dit = dict((g[0], g[1]) for g in gen)
            return dit
        else:
            res = dict(zip(models.keys(), models))
            find_datetime(res)
            return res


# 当结果为result对象列表时，result有key()方法
def result_to_dict(results):
    res = [dict(zip(r.keys(), r)) for r in results]
    # 这里r为一个字典，对象传递直接改变字典属性
    for r in res:
        find_datetime(r)
    return res


def model_to_dict(model):  # 这段来自于参考资源
    for col in model.__table__.columns:
        if isinstance(col.type, DateTime):
            value = convert_datetime(getattr(model, col.name))
        elif isinstance(col.type, Numeric):
            value = float(getattr(model, col.name))
        else:
            value = getattr(model, col.name)
        yield (col.name, value)


def find_datetime(value):
    for v in value:
        if (isinstance(value[v], cdatetime)):
            value[v] = convert_datetime(value[v])  # 这里原理类似，修改的字典对象，不用返回即可修改


def convert_datetime(value):
    if value:
        if (isinstance(value, (cdatetime, DateTime))):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif (isinstance(value, (date, Date))):
            return value.strftime("%Y-%m-%d")
        elif (isinstance(value, (Time, time))):
            return value.strftime("%H:%M:%S")
    else:
        return ""


class DbUtil:

    def get_session(self, bind=None, engine=None):
        if engine is None:
            engine = db.get_engine(app=db.get_app(), bind=bind)
        Session = scoped_session(sessionmaker(bind=engine))
        return Session()

    @contextmanager
    def auto_commit(self, bind=None, engine=None):

        try:
            self.session = self.get_session(bind, engine)
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()

    """
       用于执行一次查询的数据库查询操作封装
    """

    def execute(self, sql='', params={}):
        session = self.session
        if sql:
            stmt = text(sql)
            try:
                if params:
                    return session.execute(stmt, params)
                else:
                    return session.execute(stmt)
            except:
                session = self.get_session()
                if params:
                    return session.execute(stmt, params)
                else:
                    return session.execute(stmt)

        else:
            print("SQL为空!")

    def select(self, sql='', params={}, return_frame=False, flat_list=False):
        resList = []
        session = self.session
        if sql:
            stmt = text(sql)
            rowDict = None
            if params:
                for record in session.execute(stmt, params):
                    rowDict = dict((zip(record.keys(), record)))
                    resList.append(rowDict)
            else:
                for record in session.execute(stmt):
                    rowDict = dict((zip(record.keys(), record)))
                    resList.append(rowDict)
            if return_frame and rowDict:
                return pd.DataFrame(resList)
            elif flat_list and rowDict:
                return [list(each.values())[0] for each in resList]
            else:
                return resList
        else:
            print("SQL为空!")

    def __del__(self):
        self.session.close()
