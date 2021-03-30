from flask import Blueprint, session, render_template, request

from ..configs.macros import *
from ..database import *
from ..models import *
from ..scrapper import *

a_user = Blueprint("abstract_user", __name__)


@a_user.route("/")
def index():
    hot_articles = get_hot_news(num=RECOMMEND_NUM_NEWS)
    hot_news = [{"title": a["title"], "abstract": a["description"], "link": a["url"],
                 "img_src": a["urlToImage"]} for a in hot_articles]
    boards = my_db.query(Board, order=Board.hot.desc())[:RECOMMEND_NUM_BOARD]
    recommend_boards = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount} for b in boards]
    user_info = {}
    Uid = session.get("Uid")
    if Uid:
        match_user = my_db.query(User, condition=User.Uid == Uid, first=True)
        user_info = {"Uid": Uid, "nickname": match_user.nickname, "avatar": match_user.avatar}
    data = {"boards": recommend_boards, "news": hot_news, "user_info": user_info}
    return render_template("index.html", data=data)


@a_user.route("/board/<int:Bid>")
def get_posts_in_board(Bid):
    b = db_session.query(Board).filter(Board.Bid == Bid).first()
    if not b:
        return "Not Found!", 404
    board_info = {"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount, "time": b.timestamp}

    order = request.args.get("order", "latest_comment")
    page = request.args.get("page", "1")
    if order == "latest_comment":
        order = Post.latestCommentTime.desc()
    elif order == "newest":
        order = Post.timestamp.desc()
    elif order == "like_count":
        order = Post.likeCount.desc()
    else:
        order = Post.commentCount.desc()

    posts_match_result = db_session.query(Post).filter(Post.Bid == Bid).order_by(order).all()
    num_match = len(posts_match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    posts = [{"Pid": p.Pid, "title": p.title, "summary": p.content[:100] + '...', "publish_time": p.timestamp,
              "comment_count": p.commentCount, "like_count": p.likeCount, "dislike_count": p.dislikeCount}
             for p in posts_match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
    data = {"num_match": num_match, "num_page": num_page, "page": page, "posts": posts, "board_info": board_info}

    db_session.commit()
    return render_template("board.html", data=data)


@a_user.route("/post/<int:Pid>")
def get_comments_in_post(Pid):
    p = db_session.query(Post).filter(Post.Pid == Pid).first()
    if not p:
        return "Not Found", 404
    post_info = {"Pid": p.Pid, "title": p.title, "content": p.content, "publish_time": p.timestamp,
                 "comment_count": p.commentCount, "like_count": p.likeCount, "dislike_count": p.dislikeCount,
                 "owner": p.owner.nickname, "avatar": p.owner.avatar}

    order = request.args.get("order", "most_like")
    page = request.args.get("page", "1")

    order = Comment.likeCount.desc() if order == "most_like" else Comment.timestamp.desc()
    comment_match_result = db_session.query(Comment).filter(Comment.Pid == Pid).order_by(order).all()
    num_match = len(comment_match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    Comments = [{"Cid": c.Cid, "content": c.content, "publish_time": c.timestamp, "like_count": c.likeCount,
                 "dislike_count": c.dislikeCount, "publish_user": c.comment_by.nickname,
                 "user_avatar": c.comment_by.avatar}
                for c in comment_match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
    data = {"num_match": num_match, "num_page": num_page, "page": page, "comments": Comments, "post_info": post_info}
    db_session.commit()
    return render_template("post.html", data=data)


@a_user.route("/search_board")
def search_board():
    keyword = request.args.get("kw")
    if not keyword:
        return render_template("search_result.html", error="Please enter a keyword!")
    order = request.args.get("order", "popular")
    page = request.args.get("page", "1")
    order = Board.timestamp.desc() if order == "popular" else Board.hot.desc()
    match_result = db_session.query(Board).filter(Board.name.like("%" + keyword + "%")).order_by(order).all()
    num_match = len(match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    boards = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount}
              for b in match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
    data = {"num_match": num_match, "num_page": num_page, "page": page, "boards": boards}
    db_session.commit()
    return render_template("search_result.html", data=data)