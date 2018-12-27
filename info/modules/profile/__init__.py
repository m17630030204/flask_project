# 个人中心模块蓝图

from flask import Blueprint

profile_blu = Blueprint("profile",__name__,url_prefix="/user")


from . import views