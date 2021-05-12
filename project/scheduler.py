from flask_apscheduler import APScheduler

from .logger import *
from .models import *

# logger = init_logger()

record = {}

def update_hot():
    """ Not Finished!"""
    global record
    print("updating hot...")
    # logger.logger.info("Start updating hot")
    all_boards = my_db.query(Board, True)  #get all boards
    #Firstly we need to check all Bid and delete non-existing Bid in record
    Bid_list = []
    for j in all_boards:
        Bid_list.append(j.Bid)
    for k in record.keys():
        if k not in Bid_list:
            record.pop(k)
    #Then we start to do the updating:
    for i in all_boards:
        Bid = i.Bid
        old_list = record.get(Bid, None)
        if old_list is None:
            old_list = [0, 0]
            record[Bid] = old_list
        #Algorithm of calculating a board's hot:
        #50% * new_postCount + 50% * new_viewCount
        new_postCount = i.postCount - old_list[0]
        new_viewCount = i.viewCount - old_list[1]
        new_hot = 0.5 * new_postCount + 0.5 * new_viewCount

        #Then update the record dic
        new_list = [i.postCount, i.viewCount]
        record[Bid] = new_list
        my_db.update(Board, Board.Bid == Bid, values={"hot": new_hot})

    print("average hot:", my_db.query(func.avg(Board.hot).label("average")).scalar())
    my_db.commit()


def init_scheduler(app):
    scheduler = APScheduler()
    scheduler.add_job(func=update_hot, id="1", trigger="interval", seconds=86400)  # trigger everyday
    scheduler.init_app(app)
    scheduler.start()
