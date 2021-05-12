import os.path

from flask import Blueprint, render_template, request, session, abort

from ..configs.macros import *
from ..database import *
from ..models import *
from ..scrapper import *

a_user = Blueprint("abstract_user", __name__)


@a_user.route("/")
def index():
    """
    This function is used to show the main page of our system with recommend boards and hot news
    :return: index.html, which is our main page
    """
    hot_articles = OT_spider.get_hot_news(num=RECOMMEND_NUM_NEWS, freq=NEWS_UPDATE_FREQUENCY)
    hot_news = [{"title": a["title"], "abstract": a["description"], "link": f"/redirect?link={a['url']}",
                 "img_src": a["urlToImage"]} for a in hot_articles]
    boards = my_db.query(Board, and_(Board.status == 0), order=Board.hot.desc())[:RECOMMEND_NUM_BOARD]
    recommend_boards = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount} for b in boards]
    data = {"boards": recommend_boards, "news": hot_news}
    return render_template("index.html", data=data)


@a_user.route("/board/<int:Bid>")
def get_posts_in_board(Bid):
    """
    This function is used to show the corresponding board page according to Bid with several posts in it.
    :param Bid: the id of a Board
    :return: board.html, a board with corresponding Bid
    """
    b = my_db.query(Board, and_(Board.Bid == Bid, Board.status == 0), first=True)
    if not b:
        abort(404)

    b.viewCount += 1  # when page is accessed, increment view count
    subs = my_db.query(Subscription, and_(Subscription.Uid == (Uid := session.get("Uid")),
                                          Subscription.Bid == Bid), first=True)

    board_info = {"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount, "subs_count": b.subscribeCount,
                  "time": b.timestamp, "view_count": b.viewCount, "cover": b.cover, "description": b.description,
                  "subs_by_user": subs.subscribed if subs else 0}

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

    posts_match_result = my_db.query(Post, and_(Post.Bid == Bid, Post.status == 0), order)
    num_match = len(posts_match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    posts = []
    for p in posts_match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
        post_info = {"Pid": (Pid := p.Pid), "Uid": p.Uid, "title": p.title, "summary": p.text,
                     "publish_time": p.timestamp, "comment_count": p.commentCount, "like_count": p.likeCount,
                     "dislike_count": p.dislikeCount, "max_floor": p.available_floor,
                     "preview_type": None, "preview_src": None}
        if p.medias:
            preview_media = p.medias[0].split("/")
            post_info.update({"preview_type": preview_media[0], "preview_src": preview_media[1]})
        posts.append(post_info)

        if not session.get("Uid"):
            post_info.update({"liked_by_user": 0, "disliked_by_user": 0})
        else:
            Uid = session["Uid"]
            match_status = my_db.query(PostStatus, and_(PostStatus.Uid == Uid, PostStatus.Pid == Pid), first=True)
            if not match_status:
                post_info.update({"liked_by_user": 0, "disliked_by_user": 0})
            else:
                post_info.update({"liked_by_user": match_status.liked, "disliked_by_user": match_status.disliked})

    data = {"num_match": num_match, "num_page": num_page, "page": page, "posts": posts, "board_info": board_info}

    return render_template("board.html", data=data)


@a_user.route("/post/<int:Pid>")
def get_comments_in_post(Pid):
    """
    This function is used to show the corresponding post page according to Pid with several comments in it
    :param Pid: the id of a Post
    :return: post.html, a post with corresponding Pid
    """
    p = my_db.query(Post, and_(Post.Pid == Pid, Post.status == 0), first=True)
    if not p:
        abort(404)

    p.viewCount += 1  # when page is accessed, increment view count
    post_info = {"Pid": p.Pid, "Bid": p.Bid, "Uid": p.Uid, "title": p.title, "content": p.content,
                 "publish_time": p.timestamp, "comment_count": p.commentCount, "like_count": p.likeCount,
                 "dislike_count": p.dislikeCount, "owner": (o := p.owner).nickname, "avatar": o.avatar}
    board_info = {"cover": (b := p.under).cover, "bname": b.name}
    if not session.get("Uid"):
        post_info.update({"liked_by_user": 0, "disliked_by_user": 0})
    else:
        Uid = session["Uid"]
        match_status = my_db.query(PostStatus, and_(PostStatus.Uid == Uid, PostStatus.Pid == Pid), first=True)
        if not match_status:
            post_info.update({"liked_by_user": 0, "disliked_by_user": 0})
        else:
            post_info.update({"liked_by_user": match_status.liked, "disliked_by_user": match_status.disliked})

        match_history = my_db.query(History, and_(History.Uid == Uid, History.Pid == Pid), first=True)
        if not match_history:
            new_history = History(Uid, Pid)
            my_db.add(new_history)
        else:
            match_history.lastVisitTime = datetime.datetime.utcnow()

    order = request.args.get("order")
    page = request.args.get("page", "1")

    if order == "desc":
        order = Comment.timestamp.desc()
    elif order == "like_count":
        order = Comment.likeCount.desc()
    else:  # if order is None or invalid parameters
        order = Comment.timestamp  # default order is asc()

    comment_match_result = my_db.query(Comment, and_(Comment.Pid == Pid, Comment.status == 0), order)
    num_match = len(comment_match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page

    Comments = []
    for c in comment_match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
        base_info = {"Cid": c.Cid, "Uid": c.Uid, "content": c.content, "publish_time": c.timestamp,
                     "like_count": c.likeCount, "dislike_count": c.dislikeCount, "publish_user": c.comment_by.nickname,
                     "user_avatar": c.comment_by.avatar, "floor": c.floor}
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

    data = {"num_match": num_match, "num_page": num_page, "page": page, "comments": Comments, "post_info": post_info,
            "board_info": board_info}  # board here means the board that the post is under
    return render_template("post.html", data=data)


@a_user.route("/search_board")
def search_board():
    """
    This function is used to search for relating board based on the key words users give.
    :return: search_result.html, which shows all corresponding boards satisfying the demand
    """
    keyword = request.args.get("kw")
    if not keyword:
        return render_template("search_result.html", error="Please enter a keyword!")
    order = request.args.get("order", "popular")
    page = request.args.get("page", "1")
    order = Board.timestamp.desc() if order == "popular" else Board.hot.desc()
    match_result = my_db.query(Board, and_(Board.name.like("%" + keyword + "%"), Board.status == 0), order)
    num_match = len(match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    boards = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount}
              for b in match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
    data = {"num_match": num_match, "num_page": num_page, "page": page, "boards": boards}
    return render_template("search_result.html", data=data)


@a_user.route("/profile/<int:Uid>")
def get_personal_profile(Uid):
    """
    This function is used to show the corresponding profile page according to Uid
    :param Uid:
    :return: profile.html, which contains many information of corresponding user
    """
    u = my_db.query(User, User.Uid == Uid, first=True)
    if not u:
        abort(404)

    post_count = my_db.count(Post, and_(Post.Uid == Uid, Post.status == 0))
    comment_count = my_db.count(Comment, and_(Comment.Uid == Uid, Comment.status == 0))
    subs_count = my_db.query_join(Subscription.Uid, Board, and_(Subscription.Uid == Uid, Subscription.subscribed == 1,
                                                                Board.status == 0), count=True)
    history_count = my_db.count(History, History.Uid == Uid)

    user_info = {
        "nickname": u.nickname, "avatar": u.avatar, "timestamp": u.timestamp, "gender": u.gender,
        "phoneNumber": u.phoneNumber, "email": u.email, "address": u.address, "dateOfBirth": u.dateOfBirth,
        "banned": u.banned, "banDuration": str(u.banDuration), "isCurrent": int(Uid == session.get("Uid", -1)),
        "post_count": post_count, "subs_count": subs_count, "history_count": history_count, "Uid": Uid,
        "comment_count": comment_count
    }
    return render_template("profile.html", data=user_info)


@a_user.route("/photos")
def photo_gallery():
    """
    This function is used to view the images in the board and post.
    :return: photos.html, which contains all photos related to this board or post, and
    the initial position of photo in the slides (not photo list)
    """
    # if only "Pid" param, show all images in post content, else if valid "src" param,
    # show all images in both post and comment content, else show nothing
    Pid = request.args.get("Pid")
    src = request.args.get("src")
    if not Pid:
        abort(404)
    match_post = my_db.query(Post, Post.Pid == Pid, first=True)
    if not match_post:
        abort(404)

    photos = []
    position = None
    # get photos in post
    medias = match_post.medias
    base_len = 0
    for i, m in enumerate(medias):
        if m.startswith(PHOTO_PATH):
            base_len += 1
            cur_src = "/" + CDN_ROOT_PATH + m
            photos.append(cur_src)
            if cur_src == src:
                position = base_len
    # also get photos in comment if "src" specified
    if src:
        comments = my_db.query(Comment, Comment.Pid == Pid)
        for c in comments:
            medias = c.medias
            for i, m in enumerate(medias):
                if m.startswith(PHOTO_PATH):
                    base_len += 1
                    cur_src = "/" + CDN_ROOT_PATH + m
                    photos.append(cur_src)
                    if cur_src == src:
                        position = base_len
        if position is None:  # which means invalid "src"
            abort(404)
    else:
        position = 1 if photos else 0
    data = {"photos": photos, "init_index": position}
    return render_template("photos.html", data=data)


@a_user.route("/redirect")
def redirect_page():
    """
    This function is used to redirect user when user clicks an external link. Valid links begins with "http://",
    "https://" or "ftp://".
    :return: redirect.html, which contains the link of the outside news
    """
    link: str = request.args.get("link")
    if not link or not (link.startswith("http://") or link.startswith("https://") or link.startswith("ftp://")):
        data = {"status": 0}
    else:
        data = {"link": link, "status": 1}
    return render_template("redirect.html", data=data)


# mainly for pasring url, can also do in "dplayer_embed.html" by pure javascript
@a_user.route("/play")
def render_dplayer():
    """
    This function is used to help the users to view videos
    :return: dplayer_embed.html, which can allow the users to view videos
    """
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
