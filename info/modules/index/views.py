from flask import render_template, current_app, session, request, jsonify

from info import redis_store, constants
from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blu

@index_blu.route('/news_list')
def news_list():
    """获取新闻首页信息"""
    # 1.获取参数
    # 新闻的分类id
    cid = request.args.get("cid","1")
    page = request.args.get("page","1")
    per_page = request.args.get("per_page","10")

    # 2.效验参数
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    filters = [News.status == 0]
    if cid !=1: #查询的不是最新的数据
        # 需要添加条件
        filters.append(News.category_id == cid)

    #3.查询数据
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as  e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据查询错误")

    #取到当前页数据
    news_model_list = paginate.items #模型对象列表
    total_page = paginate.pages
    current_page = paginate.page

    #将模型对象列表转换成字典列表
    news_dict_li = []
    for news in news_model_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "total_page":total_page,
        "current_page":current_page,
        "news_dict_li":news_dict_li
    }

    return jsonify(errno = RET.OK , errmsg="OK",data=data)





@index_blu.route('/')
def index():
    # redis_store.set("name","hahaha")
    # return "index333"
    # 取到用户id
    user_id = session.get("user_id",None)
    user = None
    if user_id:
        # 尝试查询用户的模型
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    #右侧新闻排行逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e :
        current_app.logger.error(e)

    #定义一个空列表,里面装的就是字典
    news_dict_li = []
    #遍历对象列表，将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 查询分类数据，通过模板的形式渲染出来
    categories = Category.query.all()

    category_li = []
    for category in categories:
        category_li.append(category.to_dict())



    data = {
        "user" : user.to_dict() if user else None,
        "news_dict_li":news_dict_li,
        "category_li":category_li
    }


    return render_template('news/index.html',data =data)

@index_blu.route('/favicon.ico')
def favicon():
    #send_static_file 发送静态文件 找到项目的静态文件夹中的某个静态文件，并且返回
    return current_app.send_static_file('news/favicon.ico')