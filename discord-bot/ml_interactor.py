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
ML_API = os.getenv("ML_API_ENDPOINT")



def run_ml():
      url = f"{ML_API}nba"
      print(url)
      json_data = json.dumps({"command":"run ml"})
      headers = {'Content-type':'application/json'}
      response = requests.post(url, data= json_data, headers=headers)
      response_dict = json.loads(response.text)
      return response_dict["status"]