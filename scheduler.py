from numpy import append
import schedule
import time
import nba_api
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import (
    playercareerstats,
    leaguegamefinder,
    playerdashboardbyclutch,
    playergamelogs,
    commonplayerinfo,
    teamplayeronoffdetails,
    teamgamelogs,
)
import datetime
from nba_api.live.nba.endpoints import scoreboard
import json
from ML import Game_Res
import requests
from Text_Service.TextService import textCLI

def cleanGames(data):
    games = []
    for game in data:
            games.append(
                {"gameId":game["gameId"], 
                "home":{
                    "teamAbrev" : game['homeTeam']['teamTricode'],
                    "teamId":game['homeTeam']['teamId']
                    },
                "away":{
                    "teamAbrev" : game['awayTeam']['teamTricode'],
                    "teamId":game['awayTeam']['teamId']
                    }
                    })
    games = {"games" :games}
    return games 
def clean_pred_res(data):
    games = []
    for game in data:
        games.append({"home":{
                    "teamAbrev" : game['Home'],
                    "teamScore":game['HomeScore']
                    },
                "away":{
                    "teamAbrev" : game['Away'],
                    "teamScore":game['AwayScore']
                    }
        })
    return { "games" :games}

def get_user_numbers():
    url = "http://localhost:5000/mongodb"
    payload = json.dumps({
    "database": "nba_test",
    "collection": "user"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response


def sendTexts(game):
    users = get_user_numbers()
    responses = []
    for res in users:
        if res["sendText"] == "True":
            cli = textCLI()
            name = res["name"]
            home = game["Home"]
            away = game["Away"]
            homeScore = game["HomeScore"]
            awayScore = game["AwayScore"]
            message = f"\n \n {name}, \n Here are your predictions for {home} vs {away}: \n {home} : { homeScore } { away} : {awayScore}"
            messageRes = cli.sendMessage(str(res["phone"]),str(message))
            responses.append(messageRes)
        
    return (responses)




def update_games_db(gameData):
    if len(gameData) > 0:
        url = "http://0.0.0.0:5000/mongodb"
        json_data = {"database": "nba_test", "collection": "game", "Document":gameData}
        headers = {'Content-type':'application/json', 'Accept':'application/json'}
        response = requests.post(url, json= json_data, headers=headers)
        print(response)

def update_predictions_db(predictions):
    if len(predictions) > 0:
        url = "http://0.0.0.0:5000/mongodb"
        json_data = {"database": "nba_test", "collection": "predictions", "Document":predictions}
        headers = {'Content-type':'application/json', 'Accept':'application/json'}
        response = requests.post(url, json= json_data, headers=headers)
        print(response)



def run_ML():
    board = scoreboard.ScoreBoard()
    print("ScoreBoardDate: " + board.score_board_date)
    games = board.games.get_dict()
    db_format = cleanGames(games)
    update_games_db(db_format)
    ml_format =db_format["games"] 
    textResults = []
    predResults = []
    for i in range(len(ml_format)):
        home = ml_format[i]["home"]["teamAbrev"]
        away = ml_format[i]["away"]["teamAbrev"]
        res = Game_Res(home,away)
        result = sendTexts(res)
        textResults.append(result)
        predResults.append(res)
    print(textResults)
    cleanedPred =  clean_pred_res(predResults)
    print(predResults)
    update_predictions_db({"predictions" : cleanedPred})

# Every day at 12am or 00:00 time bedtime() is called.
schedule.every().day.at("12:48").do(run_ML)
  

while True:
  
    # Checks whether a scheduled task 
    # is pending to run or not
    schedule.run_pending()
    time.sleep(1)