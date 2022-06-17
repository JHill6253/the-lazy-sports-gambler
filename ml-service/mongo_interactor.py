
import os
import requests
import json

from datetime import date
from nba_api.live.nba.endpoints import scoreboard
from cleaner import clean_new_games

from dotenv import load_dotenv
# from sports_api_cli import sports_api_cli

load_dotenv()

MONGO_FLASK_ENDPOINT_ROOT = os.getenv("MONGO_FLASK_ENDPOINT_ROOT")
MAIN_MONGO_API = os.getenv("MAIN_MONGO_API")
DATE_MONGO_API = os.getenv("DATE_MONGO_API")


# ---------------------------------------------------GET REQUESTS------------------------------------------------------------

def get_games_today():
    url = MONGO_FLASK_ENDPOINT_ROOT+DATE_MONGO_API
    payload = json.dumps({
        "database": "nba_test",
        "collection": "game"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    try:
        return response[0]["games"]
    except IndexError:
        return "No Games"


# ---------------------------------------------------POST REQUESTS------------------------------------------------------------


def post_games_db():
    board = scoreboard.ScoreBoard()
    print("ScoreBoardDate: " + board.score_board_date)
    games = board.games.get_dict()
    db_format = clean_new_games(games)
    # db_format = sports_api_cli()
    if len(db_format) > 0:
        url = MONGO_FLASK_ENDPOINT_ROOT+MAIN_MONGO_API
        json_data = {"database": "nba_test",
                     "collection": "game", "Document": db_format}
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        response = requests.post(url, json=json_data, headers=headers)
        response_dict = json.loads(response.text)
        return response_dict


def post_predictions_db(predictions):
    if len(predictions) > 0:
        url = MONGO_FLASK_ENDPOINT_ROOT+MAIN_MONGO_API
        json_data = {"database": "nba_test",
                     "collection": "predictions", "Document": predictions}
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        response = requests.post(url, json=json_data, headers=headers)
        response_dict = json.loads(response.text)
        return response_dict
