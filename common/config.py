import os
import ConfigParser


root_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
config_path = os.path.join(root_path, "config.ini")
cf = ConfigParser.ConfigParser()
cf.read(config_path)
is_production = cf.getint("DEFAULT", "is_production")
section = "PRODUCTION" if is_production else "DEVELOPMENT"


class BaseConfig(object):
    ROOT_PATH = root_path
    LOG_PATH = cf.get(section, "log_path")
    APP_SLOW_LOG = int(cf.get(section, "app_slow_log"))
    try:
        APP_SLOW_TIME = int(cf.get(section, "app_slow_time"))
    except:
        APP_SLOW_TIME = 5


class DbConfig():
    # MYSQL
    MYSQL_HOST = cf.get(section, "mysql_host")
    MYSQL_PORT = int(cf.getint(section, "mysql_port"))
    MYSQL_USERNAME = cf.get(section, "mysql_user")
    MYSQL_PASSWORD = cf.get(section, "mysql_password")
    MYSQL_DB_NAME = cf.get(section, "mysql_db_name")

    # MONGO
    MONGO_HOST = cf.get(section, "mongo_host")
    MONGO_PORT = int(cf.get(section, "mongo_port"))
    MONGO_USERNAME = cf.get(section, "mongo_user")
    MONGO_PASSWORD = cf.get(section, "mongo_password")
    MONGO_DB_NAME = cf.get(section, "mongo_db_name")

    # REDIS
    REDIS_HOST = cf.get(section, "redis_host")
    REDIS_PORT = int(cf.get(section, "redis_port"))
    REDIS_PASSWORD = cf.get(section, "redis_password")
    REDIS_DB_NAME = cf.get(section, "redis_db_name")