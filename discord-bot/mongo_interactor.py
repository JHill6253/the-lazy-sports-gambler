
import os
import requests
import json
from nba_api.live.nba.endpoints import scoreboard

from cleaner import clean_new_games

from dotenv import load_dotenv
# from sports_api_cli import sports_api_cli

load_dotenv()

MONGO_FLASK_ENDPOINT_ROOT = os.getenv("MONGO_FLASK_ENDPOINT_ROOT") 
MAIN_MONGO_API = os.getenv("MAIN_MONGO_API")
DATE_MONGO_API = os.getenv("DATE_MONGO_API")
ML_API = os.getenv("ML_API_ENDPOINT")

#---------------------------------------------------GET REQUESTS------------------------------------------------------------
def get_user_numbers():
    url = MONGO_FLASK_ENDPOINT_ROOT+MAIN_MONGO_API
    payload = json.dumps({
    "database": "nba_test",
    "collection": "user"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response

def get_predictions_today():
    url = MONGO_FLASK_ENDPOINT_ROOT+DATE_MONGO_API
    payload = json.dumps({
    "database": "nba_test",
    "collection": "predictions"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload).json()
    try:
        return response[0]["games"]
    except IndexError:
        return "No Games"
def get_games_today():
    url = MONGO_FLASK_ENDPOINT_ROOT+DATE_MONGO_API
    payload = json.dumps({
    "database": "nba_test",
    "collection": "game"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload).json()
    try:
        return response[0]["games"]
    except IndexError:
        return "No Games"


#---------------------------------------------------POST REQUESTS------------------------------------------------------------
def post_games_db():
    board = scoreboard.ScoreBoard()
    games = board.games.get_dict()
    db_format = clean_new_games(games)
    if len(db_format) > 0:
        url = MONGO_FLASK_ENDPOINT_ROOT+MAIN_MONGO_API
        json_data = {"database": "nba_test", "collection": "game", "Document":db_format}
        headers = {'Content-type':'application/json', 'Accept':'application/json'}
        response = requests.post(url, json= json_data, headers=headers)
        response_dict = json.loads(response.text)
        return response_dict










