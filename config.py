import redis
import logging


class Config(object):
    """从对象中加载配置  笔记1.7.5"""


    SECRET_KEY = 'vYx9jHG413JShCnN91R/9AommmhqUft41n5oCwe5vYKatSHz4Q4BvkPWIDSzYb7a'

    """数据库配置 笔记3.13.5"""
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information9"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 在请求结束时候，如果指定此配置为True，那么SQLAlchemy会自动执行一次db.sessionn.commit()
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    """redis数据库地址"""
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    """Flask_session的配置信息"""
    SESSION_TYPE = 'redis' #指定session 保存到 redis 中
    SESSION_USE_SIGNER = True #让cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒

    LOG_LEVEL = logging.DEBUG

class DevelopmentConfig(Config):
    """生产环境下的配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境下的配置"""
    DEBUG = False
    LOG_LEVEL = logging.WARNING

class TestingConfig(Config):
    DEBUG = True
    TESTING = True

config = {
    "development" : DevelopmentConfig,
    "production" : ProductionConfig,
    "testing" : TestingConfig
}