from flask import render_template, current_app, session, g, abort, jsonify, request

from info import constants, db
from info.models import News, User, Comment, CommentLike
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@news_blu.route('/followed_user',methods = ['POST'])
@user_login_data
def followed_user():
    """关注或者取消关注"""

    #0.取到自己的登录信息
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="未登录")

    #1.取参数
    user_id = request.json.get("user_id")
    action = request.json.get("action")

    #2.判断参数
    if not all([user_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    if action not in ("follow","unfollow"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3. 取到要被关注的用户
    try:
        other = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not other:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    # 4. 根据要执行的操作去修改对应的数据
    if action == "follow":
        if other not in user.followed:
            #当前用户关注列表添加一个值
            user.followed.append(other)
        else:
            return jsonify(errno=RET.DATAEXIST, errmsg="当前用户已被关注")

    else:
        #取消关注
        if other in user.followed:
            user.followed.remove(other)
        else:
            return jsonify(errno=RET.DATAEXIST, errmsg="当前用户未被关注")

    return jsonify(errno=RET.OK,errmsg="OK")





@news_blu.route('/comment_like',methods = ['POST'])
@user_login_data
def comment_like():

    """点赞"""
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

     # 1.取到请求参数
    news_id = request.json.get("news_id")
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")
    # 2.判断参数
    if not all([news_id, comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")


    if action not in ["add" , "remove"]:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    try:
        comment_id = int(comment_id)
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment =Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno=RET.DBERR,errmsg="数据查询错误")

    if not comment:
        return jsonify(errno=RET.NODATA,errmsg="评论不存在")

    if action == "add":
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,CommentLike.comment_id ==comment.id).first()

        if not comment_like_model:
            #点赞评论
            comment_like_model = CommentLike()
            comment_like_model.user_id = user.id
            comment_like_model.comment_id = comment.id
            db.session.add(comment_like_model)
            comment.like_count += 1

    else:
        #取消点赞评论
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,CommentLike.comment_id == comment.id).first()

        if comment_like_model:
            db.session.delete(comment_like_model)
            comment.like_count -=1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库操作失败")

    return jsonify(errno=RET.OK,errmsg="OK")





@news_blu.route('/news_comment',methods = ['POST'])
@user_login_data
def comment_news():
    """评论新闻"""
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")

    #1.取到请求参数
    news_id = request.json.get("news_id")
    comment_content = request.json.get("comment")
    parent_id= request.json.get("parent_id")

    #2.判断参数
    if not all([news_id,comment_content]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    # 查询新闻，并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    #3. 初始化一个评论模型，并且赋值
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    # 添加到数据库
    # 为啥要自己去commit()? 因为在return的时候需要用的comment 的 id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK,errmsg="OK",data = comment.to_dict())



@news_blu.route('/news_collect',methods = ['POST'])
@user_login_data
def collect_news():
    """收藏新闻"""

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")

    #1.接受参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    #2.判断参数
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg= "参数错误")

    if action not in ["collect" , "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as  e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    #3.查询新闻，并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.NODATA,errmsg="未查询到新闻数据")

    # 4. 收藏以及取消收藏

    if action == "cancel_collect":
        # 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)

    else:
        #收藏
        if news not in user.collection_news:
            user.collection_news.append(news)

    return jsonify(errno=RET.OK,errmsg="操作成功")







@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :param news_id:
    :return:

    """
    # 用户登录信息
    # 取到用户id
    user =g.user
    # 右侧新闻排行逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 定义一个空列表,里面装的就是字典
    news_dict_li = []
    # 遍历对象列表，将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 查询新闻数据

    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        abort(404)
    #更新新闻点击次数
    news.clicks += 1
    #是否收藏 默认不收藏
    is_collected = False
    #判断用户是否登录
    if user:
        #判断用户是否收藏当前新闻
        # user.collection_news 用户收藏列表
        #collection_news 后面可以不加all(),因为 sqlalcheny 会在使用的时候去自动加载
        if news in user.collection_news:
            is_collected = True
    # 查询评论数据
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as  e:
        current_app.logger.error(e)


    comment_like_ids =[]
    if g.user:
        try:
            #需求：查询当前用户在当前新闻里面点赞了哪些评论
            #1.查询出当前新闻的所有评论（[COMMENT]）取到所有的评论id [1,2,3,4,5]
            comment_ids = [comment.id for  comment in comments]
            #2. 在查询当前评论中哪些评论被当前用户所点赞（【CommentLike】）
            # 查询comment_id 在第一步的评论id列表内所有数据 & CommentList.user_id = g.user.id
            comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),CommentLike.user_id==g.user.id).all()
            # 3. 取到所有被点赞的评论id 第二步查询出来是一个【CommentLike】 [3,5]
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)

    comment_dict_li = []

    for  comment in comments:

        comment_dict = comment.to_dict()
        # comment_dict_li.append(comment_dict)
        #代表没有点赞
        comment_dict["is_like"] = False
        #判断当前遍历到评论是否被当前用户所点赞
        if comment.id in comment_like_ids:
            comment_dict["is_like"] = True
        comment_dict_li.append(comment_dict)

    is_followed = False
    # if 当前新闻有作者 并且 当前登录用户以关注过这个用户
    if  news.user and user:
        #if user 是否关注过 news.user
        if news.user in user.followed:
            is_followed =True



    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li,
        "news":news.to_dict(),
        "is_collected":is_collected,
        "is_followed":is_followed,
        "comments":comment_dict_li

    }
    return render_template("news/detail.html" ,data=data)
