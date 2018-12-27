# 新闻详情模块蓝图

from flask import Blueprint

news_blu = Blueprint("news",__name__,url_prefix="/news")
# url_prefix="/passport"
from . import views