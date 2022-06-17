from flask import Flask, jsonify,request
import pandas as pd 
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import time
import matplotlib.pyplot as plt
import math
import numpy as np
import datetime
import json
from dateutil import parser
from datetime import datetime, timezone
import nba_api
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import playercareerstats, leaguegamefinder, playerdashboardbyclutch, playergamelogs, commonplayerinfo, teamplayeronoffdetails, teamgamelogs
from nba_api.live.nba.endpoints import scoreboard
from  model import Model
from TextService import textCLI
import pymongo
from pymongo import MongoClient



app = Flask(__name__)


def get_db():
    client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")
    db = client["games_db"]
    return db

@app.route('/')
def ping_server():
    return {"health":"Welcome to the world of ML NBA Bets."}

@app.route('/get')
def get_stored_games():
    db=""
    try:
        db = get_db()
        _games = db.games_tb.find()
        games = [{"id": game["id"], "name": game["name"], "type": game["type"]} for game in _games]
        return jsonify({"games": games})
    except:
        pass
    finally:
        if type(db)==MongoClient:
            db.close()


@app.route('/games', methods=['GET'])
def games():
    board = scoreboard.ScoreBoard()
    gamesTonight = []
    print("ScoreBoardDate: " + board.score_board_date)
    games = board.games.get_dict()
    for game in games:
        gamesTonight.append({
            game["gameId"]: 
                {"Date": board.score_board_date, "home": game['homeTeam']['teamTricode'],"away":game['awayTeam']['teamTricode']}
            })

    return jsonify({'games': gamesTonight})

@app.route('/predict', methods=['GET'])
def Predict():
    gameDF = Model()
    print(gameDF.games)
    return jsonify({'predictions': "working"})
@app.route('/sendmessage', methods=['POST'])
def SendMessage():
    _json = request.json
    cli = textCLI()
    messageRes = cli.sendMessage(str(_json["number"]),_json["message"])
    return jsonify({'response': messageRes})

if __name__ =='__main__':
    app.run(debug=True,host='0.0.0.0', port = 5002)