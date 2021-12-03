from flask import Flask, jsonify, request, Response
import pandas as pd
import requests
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
from nba_api.stats.endpoints import (
    playercareerstats,
    leaguegamefinder,
    playerdashboardbyclutch,
    playergamelogs,
    commonplayerinfo,
    teamplayeronoffdetails,
    teamgamelogs,
)
from nba_api.live.nba.endpoints import scoreboard

# from  ML_Models.model import Model
from Text_Service.TextService import textCLI
import pymongo
from pymongo import MongoClient
import logging as log


app = Flask(__name__)

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
    return {"games": games }




@app.route('/games', methods=['GET',"POST"])
def games():
    board = scoreboard.ScoreBoard()
    print("ScoreBoardDate: " + board.score_board_date)
    games = board.games.get_dict()
    temp = cleanGames(games)
    
    url = "http://localhost:5001/mongodb"
    if request.method == 'POST':
        json_data = {"database": "nba_test", "collection": "game", "Document":temp}
        headers = {'Content-type':'application/json', 'Accept':'application/json'}
        response = requests.post(url, json= json_data, headers=headers)
        return jsonify({'games sent to db': response.json()})
    return jsonify({"working":"yes"})

@app.route('/createuser', methods=["POST"])
def createUser():    
    _json = request.json    
    url = "http://localhost:5001/mongodb"
    if request.method == 'POST':
        json_data = {"database": "nba_test", "collection": "user", "Document":_json}
        headers = {'Content-type':'application/json', 'Accept':'application/json'}
        response = requests.post(url, json= json_data, headers=headers)
        return jsonify({'user created': response.json()})
    return jsonify({"working":"yes"})

@app.route('/fetchUsers', methods=['GET'])
def text():
    url = "http://localhost:5001/mongodb"
    payload = json.dumps({
    "database": "nba_test",
    "collection": "user"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)


    
    return {'response': response.text}

@app.route('/sendmessages', methods=['POST'])
def SendMessage():
    url = "http://localhost:5001/mongodb"
    payload = json.dumps({
    "database": "nba_test",
    "collection": "user"
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload).json()
    print(response)
    responses = []
    for res in response:
        if res["sendText"] == "True":
            cli = textCLI()
            messageRes = cli.sendMessage(str(res["phone"]),res["name"]+ ", This is a test of your life alery system")
            responses.append(messageRes)
        
    return jsonify({'response': responses})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
