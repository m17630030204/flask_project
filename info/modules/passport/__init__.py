# 登录注册的相关逻辑都放在这个模块中

from flask import Blueprint

passport_blu = Blueprint("passport",__name__,url_prefix="/passport")
# url_prefix="/passport"
from . import views