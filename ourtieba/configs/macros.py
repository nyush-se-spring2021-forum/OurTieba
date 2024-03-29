# Macros
PAGE_SIZE = 10
RECOMMEND_NUM_BOARD = 10
RECOMMEND_NUM_NEWS = 3
NEWS_UPDATE_FREQUENCY = 60 * 60  # unit: second

CDN_ROOT_PATH = "cdn/"  # relative to ourtieba working directory (which is .../OurTieba)
AVATAR_PATH = "avatar/"  # relative to CDN root path
PHOTO_PATH = "photo/"  # relative to CDN root path
VIDEO_PATH = "video/"  # relative to CDN root path
COVER_PATH = "cover/"  # relative to CDN root path

ALLOWED_METHODS = ("GET", "POST")

# CSP whitelist (for script)
WHITELIST = ["'self'", "'unsafe-eval'", "https://cdnjs.cloudflare.com/", "https://cdn.jsdelivr.net/"]

# status of database objects
STATUS_NORMAL = 0
STATUS_DELETED = 1
STATUS_BANNED = 2
