# Agile Innovation Backend

## Install Requirement

## Software enviroment
 - Linux
 - Python 3.7.7
 - Nodejs 10+

## prepare enviroment
 ```
    pip install -r requirements/prod.txt
    pip install -r requirements/dev.txt

    cnpm i
 ```

## Flask commands
### create database
```
    flask db migrate
```

### Create sqlalchemy migration script
```
    flask db upgrade
```

## startup backend
```
    flask run
```
## startup frontend
```
    yarn serve
```

### backend unit test
```
    pytest tests\
```

### generate tokey
token永久有效，需要妥善保管
```bash
flask token -u agile -p jollybean
```

## Document Guide
[sqlAlchemy](https://docs.sqlalchemy.org/en/13/orm/join_conditions.html#handling-multiple-join-paths)
[sqlAlchemy-mixin](https://github.com/absent1706/sqlalchemy-mixins#beauty-__repr__)
[facker](https://www.jianshu.com/p/6bd6869631d9)
[flask-restplus](https://flask-restplus.readthedocs.io/en/stable/errors.html)
[marshmallow](https://marshmallow.readthedocs.io/en/stable/index.html)
[marshmallow自定义字段](https://cloud.tencent.com/developer/article/1435948)
[flask-marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/)
[marshmallow-sqlalchemy](https://marshmallow-sqlalchemy.readthedocs.io/en/latest/api_reference.html)
[marshmallow轻量自动化验证和序列化][https://www.jianshu.com/p/6e91863008b3]
[ SQLAlchemy-Searchable](https://sqlalchemy-searchable.readthedocs.io/en/latest/installation.html)
[Office 365 API](https://pypi.org/project/O365/)
[pg_trgm](https://www.cnblogs.com/zhangfx01/p/postgresql_like_zhparser_pg_trgm.html)
