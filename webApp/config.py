from hashlib import md5

from common.config import BaseConfig, DbConfig


class AppConfig(BaseConfig):
    SECRET_KEY = md5("app_name").hexdigest()
    CSRF_ENABLED = True
    AUTH_HEADER_NAME = "Authentication-Token"
    WTF_CSRF_SECRET_KEY = SECRET_KEY
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024 * 1024  # Max length of upload file, 10G
    SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s:%s/%s?charset=utf8" % (DbConfig.MYSQL_USERNAME, DbConfig.MYSQL_PASSWORD,
                                                                       DbConfig.MYSQL_HOST, DbConfig.MYSQL_PORT,
                                                                       DbConfig.MYSQL_DB_NAME)
    SQLALCHEMY_POOL_SIZE = 5  # default 5
    SQLALCHEMY_POOL_TIMEOUT = 10  # default 10
    # short recycle time to avoid mysql connection exception while touch reload, but it's not a good choice
    SQLALCHEMY_POOL_RECYCLE = 30
    SQLALCHEMY_MAX_OVERFLOW = 1000
    SQLALCHEMY_RECORD_QUERIES = True  # set true to record queries
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_QUERY_TIMEOUT = 0.01
    MONGO_URI = "mongodb://%s:%s@%s:%s/%s" % (DbConfig.MONGO_USERNAME, DbConfig.MONGO_PASSWORD, DbConfig.MONGO_HOST,
                                              DbConfig.MONGO_PORT, DbConfig.MONGO_DB_NAME)
    MONGO_MAX_POOL_SIZE = 100   # Defaults to 100. Cannot be 0.

    REDIS_URL = "redis://:%s@%s:%s/%s" % (DbConfig.REDIS_PASSWORD, DbConfig.REDIS_HOST,
                                          DbConfig.REDIS_PORT, DbConfig.REDIS_DB_NAME)

    CELERY_BROKER_URL = REDIS_URL

