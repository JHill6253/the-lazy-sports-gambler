import imp
from threading import Thread
from datetime import date
from nba_ml import game_res
from mongo_interactor import post_predictions_db


class Game(Thread):
    def __init__(self, request):
        Thread.__init__(self)
        self.request = request.json

    def run(self):
        print(self.request)
        today = date.today()
        res = game_res(self.request["home"], self.request["away"])
        res = post_predictions_db({"games": res,
                                   "date": today.strftime("%m/%d/%y")})
        print(res["Status"])
