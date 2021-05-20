import os.path

from flask import Blueprint, render_template, request, session, abort

from ..configs.macros import *
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
    recommend_boards = Board.get_recommend(RECOMMEND_NUM_BOARD)
    data = {"boards": recommend_boards, "news": hot_news}
    return render_template("index.html", data=data)


@a_user.route("/board/<int:Bid>")
def get_posts_in_board(Bid):
    """
    This function is used to show the corresponding board page according to Bid with several posts in it.
    :param Bid: the id of a Board
    :return: board.html, a board with corresponding Bid
    """
    board_info = Board.get_info(Bid, increment_view=True)
    if not board_info:
        abort(404)

    board_info.update({"subs_by_user": Subscription.subs_by_user(session.get("Uid"), Bid)})

    order = request.args.get("order", "latest_comment")
    board_info.update({"order": order})
    page = request.args.get("page", "1")
    if order == "latest_comment":
        order = Post.latestCommentTime.desc()
    elif order == "newest":
        order = Post.timestamp.desc()
    elif order == "like_count":
        order = Post.likeCount.desc()
    else:
        order = Post.commentCount.desc()

    num_match = board_info["post_count"]
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    posts = Post.get_info_list_by_page(page, PAGE_SIZE, Bid, order, preview=True)
    for post_info in posts:
        if not (Uid := session.get("Uid")):
            post_info.update({"liked_by_user": 0, "disliked_by_user": 0})
        else:
            status = PostStatus.status_by_user(Uid, post_info["Pid"])
            post_info.update({"liked_by_user": status[0], "disliked_by_user": status[1]})

    data = {"num_match": num_match, "num_page": num_page, "page": page, "posts": posts, "board_info": board_info}

    return render_template("board.html", data=data)


@a_user.route("/post/<int:Pid>")
def get_comments_in_post(Pid):
    """
    This function is used to show the corresponding post page according to Pid with several comments in it
    :param Pid: the id of a Post
    :return: post.html, a post with corresponding Pid
    """
    post_info, board_info = Post.get_info_and_board_info(Pid, increment_view=True)
    if not post_info:
        abort(404)

    status = PostStatus.status_by_user((Uid := session.get("Uid")), Pid)
    post_info.update({"liked_by_user": status[0], "disliked_by_user": status[1]})

    if Uid:
        History.merge(Uid, Pid, datetime.datetime.utcnow())

    order = request.args.get("order", "asc")
    post_info.update({"order": order})
    page = request.args.get("page", "1")

    if order == "desc":
        order = Comment.timestamp.desc()
    elif order == "like_count":
        order = Comment.likeCount.desc()
    else:  # if order is None or invalid parameters
        order = Comment.timestamp  # default order is asc()

    num_match = post_info["comment_count"]
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page

    comment_info_list = Comment.get_info_list_by_page(page, PAGE_SIZE, Pid, order)
    for c in comment_info_list:
        status = CommentStatus.status_by_user(Uid, c["Cid"])
        c.update({"liked_by_user": status[0], "disliked_by_user": status[1]})

    data = {"num_match": num_match, "num_page": num_page, "page": page, "comments": comment_info_list,
            "post_info": post_info, "board_info": board_info}  # board here means the board that the post is under
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

    num_match = Board.get_search_count(keyword)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    boards = Board.get_search_list_by_page(page, PAGE_SIZE, keyword, order)
    data = {"num_match": num_match, "num_page": num_page, "page": page, "boards": boards}
    return render_template("search_result.html", data=data)


@a_user.route("/profile/<int:Uid>")
def get_personal_profile(Uid):
    """
    This function is used to show the corresponding profile page according to Uid
    :param Uid:
    :return: profile.html, which contains many information of corresponding user
    """
    user_info = User.get_info(Uid)
    if not user_info:
        abort(404)

    post_count = Post.count(Post.Uid == Uid)
    comment_count = Comment.count(Comment.Uid == Uid)
    subs_count = Subscription.user_subs_count(Uid)
    history_count = History.count(History.Uid == Uid)

    user_info.update({"isCurrent": int(Uid == session.get("Uid", -1)), "post_count": post_count,
                      "subs_count": subs_count, "history_count": history_count, "Uid": Uid,
                      "comment_count": comment_count})
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
    medias = Post.get_medias(Pid)
    if medias is None:
        abort(404)

    photos = []
    position = None
    # get photos in post
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
        comment_medias = Post.get_comment_medias(Pid)
        for i, m in enumerate(comment_medias):
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
