import pandas as pd 
import numpy as np
from datetime import datetime, timezone
from nba_api.live.nba.endpoints import scoreboard
from team import Team
from prediction import Prediction

class Model():
    def __init__(self):
        self.gamesTonight = self.getTonightsGames()
        self.teamPredictionData = self.getTeamPredData()
        self.games = self.getGameResults()
    def getTonightsGames(self):
        board = scoreboard.ScoreBoard()
        teamsTonight = []
        print("ScoreBoardDate: " + board.score_board_date)
        games = board.games.get_dict()
        for game in games:
            teamsTonight.append({"teamAbrev" : game['homeTeam']['teamTricode'],"teamId":game['homeTeam']['teamId'] })
            teamsTonight.append({"teamAbrev" : game['awayTeam']['teamTricode'],"teamId":game['awayTeam']['teamId'] })
        return teamsTonight
    def getTeamPredData(self):
        teamPredData = []
        for i in range(0,len(self.gamesTonight),2):
            homeTeam = Team(self.gamesTonight[i]['teamAbrev'], self.gamesTonight[i]['teamId'])
            homeTeamData = homeTeam.get_active_team_data()
            homeTeamPredictions = Prediction(homeTeamData)
            awayTeam = Team(self.gamesTonight[i+1]['teamAbrev'], self.gamesTonight[i+1]['teamId'])
            awayTeamData = awayTeam.get_active_team_data()
            awayTeamPredictions = Prediction(awayTeamData)
            teamPredData.append({"homeAbrev":self.gamesTonight[i]['teamAbrev'],"homeId": self.gamesTonight[i]['teamId'], "homeTeam": homeTeam, "homeTeamPredictions": homeTeamPredictions,"awayAbrev":self.gamesTonight[i+1]['teamAbrev'],"awayId": self.gamesTonight[i+1]['teamId'], "awayTeam": awayTeam, "awayTeamPredictions": awayTeamPredictions})
        return teamPredData
        
    def getGameResults(self):
        games = []
        for i in range(len(self.teamPredData)):
            team1 = self.teamPredData[i]["homeTeam"]
            team2_abbreviation = self.teamPredData[i]["awayAbrev"]
            team1_prediction_class = self.teamPredData[i]["homeTeamPredictions"]
            team1_prediction_data = team1.get_data_for_prediction(team2_abbreviation)
            team1_prediction, team1_margin = team1_prediction_class.make_prediction(team1_prediction_data)

            team2 = self.teamPredData[i]["awayTeam"] 
            team1_abbreviation = self.teamPredData[i]["homeAbrev"]
            team2_prediction_class = self.teamPredData[i]["awayTeamPredictions"]
            team2_prediction_data = team2.get_data_for_prediction(team1_abbreviation)
            team2_prediction, team2_margin = team2_prediction_class.make_prediction(team2_prediction_data)
            
            team1ptavg = team1_prediction_data['Team Point Average']
            team1ptavg = round(team1ptavg.iloc[0],0)
            team2ptavg = team2_prediction_data['Team Point Average']
            team2ptavg = round(team2ptavg.iloc[0],0)

            game = pd.DataFrame([[team1_abbreviation,(round((team1_prediction.item(0)+team1_margin),0)),team2_abbreviation,(round((team2_prediction.item(0)+team2_margin),0)),datetime.today(), team1ptavg, team2ptavg]],columns=['Home','HomeScore','Away','AwayScore','Date','Home Point Avg','Away Point Avg'])
            games.append(game)
        return pd.concat(games)
