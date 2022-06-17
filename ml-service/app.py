from flask import Flask, request, json, Response
from flask_cors import CORS
from pymongo import MongoClient
import logging as log
import os
from threading import Thread
from datetime import date
from nba_ml import game_res
from mongo_interactor import post_predictions_db, get_games_today
from Classes.Compute import Compute
from Classes.Game import Game
MONGO_ENDPOINT = os.getenv("MONGO_ENDPOINT")
app = Flask(__name__)
CORS(app)


@app.route('/')
def base():
    return Response(response=json.dumps({"Status": "UP"}),
                    status=200,
                    mimetype='application/json')


@app.route('/nba', methods=["GET", "POST"])
def nba_ml():
    data = request.json
    if data is None:
        thread_a = Compute(request.__copy__())
        thread_a.start()
        return Response(response=json.dumps({"sucess": " ML Running"}),
                        status=200,
                        mimetype='application/json')


@app.route('/nba/game', methods=["POST"])
def nba_game_ml():
    data = request.json
    if data is not None:
        thread_a = Game(request.__copy__())
        thread_a.start()
        return Response(response=json.dumps({"sucess": " ML Running"}),
                        status=200,
                        mimetype='application/json')
