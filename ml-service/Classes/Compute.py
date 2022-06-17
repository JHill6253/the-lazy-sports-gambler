from mongo_interactor import post_predictions_db, get_games_today
from datetime import date
from threading import Thread
from nba_ml import game_res


class Compute(Thread):
    def __init__(self, request):
        Thread.__init__(self)
        self.request = request

    def run(self):
        today = date.today()
        games = get_games_today()
        predictionResults = []
        for i in range(len(games)):
            home = games[i]["home"]["teamAbrev"]
            away = games[i]["away"]["teamAbrev"]
            res = game_res(home, away)

            # res = run_game_ml(games[i])
            predictionResults.append(res)
        res = post_predictions_db({"games": predictionResults,
                                   "date": today.strftime("%m/%d/%y")})
        print(res["Status"])
