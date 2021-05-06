import os.path

from flask import Blueprint, render_template, request, session, abort

from ..configs.macros import *
from ..database import *
from ..models import *
from ..scrapper import *

a_user = Blueprint("abstract_user", __name__)


@a_user.route("/")
def index():
    my_db.update(Post, Post.Pid == 20, values={"medias": ["photo/-3701751787780283978.jpeg"]})
    hot_articles = OT_spider.get_hot_news(num=RECOMMEND_NUM_NEWS, freq=NEWS_UPDATE_FREQUENCY)
    hot_news = [{"title": a["title"], "abstract": a["description"], "link": f"/redirect?link={a['url']}",
                 "img_src": a["urlToImage"]} for a in hot_articles]
    boards = my_db.query(Board, order=Board.hot.desc())[:RECOMMEND_NUM_BOARD]
    recommend_boards = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount} for b in boards]
    data = {"boards": recommend_boards, "news": hot_news}
    return render_template("index.html", data=data)


@a_user.route("/board/<int:Bid>")
def get_posts_in_board(Bid):
    b = my_db.query(Board, Board.Bid == Bid, first=True)
    if not b:
        return "Not Found!", 404
    b.viewCount += 1  # when page is accessed, increment view count
    board_info = {"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount,
                  "time": b.timestamp, "view_count": b.viewCount}

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

    posts_match_result = my_db.query(Post, Post.Bid == Bid, order)
    num_match = len(posts_match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    posts = []
    for p in posts_match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
        post_info = {"Pid": p.Pid, "Uid": p.Uid, "title": p.title, "summary": p.text[:100] + '...',
                     "publish_time": p.timestamp, "comment_count": p.commentCount, "like_count": p.likeCount,
                     "dislike_count": p.dislikeCount, "preview_type": None, "preview_src": None}
        if p.medias:
            preview_media = p.medias[0].split("/")
            print(p.medias, type(p.medias))
            post_info.update({"preview_type": preview_media[0], "preview_src": preview_media[1]})
        posts.append(post_info)

    data = {"num_match": num_match, "num_page": num_page, "page": page, "posts": posts, "board_info": board_info}

    return render_template("board.html", data=data)


@a_user.route("/post/<int:Pid>")
def get_comments_in_post(Pid):
    p = my_db.query(Post, Post.Pid == Pid, first=True)
    if not p:
        return "Not Found", 404
    p.viewCount += 1  # when page is accessed, increment view count
    post_info = {"Pid": p.Pid, "Bid": p.Bid, "Uid": p.Uid, "title": p.title, "content": p.content,
                 "publish_time": p.timestamp, "comment_count": p.commentCount, "like_count": p.likeCount,
                 "dislike_count": p.dislikeCount, "owner": p.owner.nickname, "avatar": p.owner.avatar}
    if not session.get("Uid"):
        post_info.update({"liked_by_user": 0, "disliked_by_user": 0})
    else:
        Uid = session["Uid"]
        match_status = my_db.query(PostStatus, and_(PostStatus.Uid == Uid, PostStatus.Pid == Pid), first=True)
        if not match_status:
            post_info.update({"liked_by_user": 0, "disliked_by_user": 0})
        else:
            post_info.update({"liked_by_user": match_status.liked, "disliked_by_user": match_status.disliked})

    order = request.args.get("order")
    page = request.args.get("page", "1")

    if order == "desc":
        order = Comment.timestamp.desc()
    elif order == "like_count":
        order = Comment.likeCount.desc()
    else:  # if order is None or invalid parameters
        order = Comment.timestamp  # default order is asc()

    comment_match_result = my_db.query(Comment, Comment.Pid == Pid, order)
    num_match = len(comment_match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page

    Comments = []
    for c in comment_match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
        base_info = {"Cid": c.Cid, "Uid": c.Uid, "content": c.content, "publish_time": c.timestamp,
                     "like_count": c.likeCount, "dislike_count": c.dislikeCount, "publish_user": c.comment_by.nickname,
                     "user_avatar": c.comment_by.avatar}
        if not session.get("Uid"):
            base_info.update({"liked_by_user": 0, "disliked_by_user": 0})
        else:
            Uid = session["Uid"]
            match_status = my_db.query(CommentStatus, and_(CommentStatus.Uid == Uid, CommentStatus.Cid == c.Cid),
                                       first=True)
            if not match_status:
                base_info.update({"liked_by_user": 0, "disliked_by_user": 0})
            else:
                base_info.update({"liked_by_user": match_status.liked, "disliked_by_user": match_status.disliked})
        Comments.append(base_info)

    data = {"num_match": num_match, "num_page": num_page, "page": page, "comments": Comments, "post_info": post_info}
    return render_template("post.html", data=data)


@a_user.route("/search_board")
def search_board():
    keyword = request.args.get("kw")
    if not keyword:
        return render_template("search_result.html", error="Please enter a keyword!")
    order = request.args.get("order", "popular")
    page = request.args.get("page", "1")
    order = Board.timestamp.desc() if order == "popular" else Board.hot.desc()
    match_result = my_db.query(Board, Board.name.like("%" + keyword + "%"), order)
    num_match = len(match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    boards = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount}
              for b in match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
    data = {"num_match": num_match, "num_page": num_page, "page": page, "boards": boards}
    return render_template("search_result.html", data=data)


@a_user.route("/profile/<int:Uid>")
def get_personal_profile(Uid):
    u = my_db.query(User, User.Uid == Uid, first=True)
    if not u:
        return "Not Found", 404
    user_info = {
        "nickname": u.nickname, "avatar": u.avatar, "timestamp": u.timestamp, "gender": u.gender,
        "phoneNumber": u.phoneNumber, "email": u.email, "address": u.address, "dateOfBirth": u.dateOfBirth,
        "banned": u.banned, "banDuration": u.banDuration, "isCurrent": int(Uid == session.get("Uid", -1))
    }
    return render_template("profile.html", data=user_info)


@a_user.route("/photos")
def photo_gallery():
    # if only "pid" param, show all images in post content, else if valid "src" param,
    # show all images in both post and comment content, else show nothing
    return render_template("photos.html")


@a_user.route("/redirect")
def redirect_page():
    link = request.args.get("link")
    if not link or not link.startswith("http") or not link.startswith("https"):
        data = {"error": {"msg": "Invalid link!"}, "status": 0}
    else:
        data = {"link": link, "status": 1}
    return render_template("redirect.html", data=data)


# mainly for pasring url, can also do in "dplayer_embed.html" by pure javascript
@a_user.route("/play")
def render_dplayer():
    src = request.args.get("src")
    if not src:
        abort(404)
    if not src.startswith("http"):  # inner src link
        src = os.path.join(CDN_ROOT_PATH, src)
    autoplay = request.args.get("autoplay")
    if not autoplay or not autoplay.isnumeric():
        autoplay = 0  # default is no autoplay
    loop = request.args.get("loop")
    if not loop or not loop.isnumeric():
        loop = 0  # default is no loop
    data = {"src": src, "autoplay": autoplay, "loop": loop}
    return render_template("dplayer_embed.html", data=data)
