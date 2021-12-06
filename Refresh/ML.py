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
from datetime import date
# import nba_api
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import playercareerstats, leaguegamefinder, playerdashboardbyclutch, playergamelogs, commonplayerinfo, teamplayeronoffdetails, teamgamelogs



class Prediction(object):
    
    def __init__(self, data):
        self.data = data.copy()
        
    #Normalize the data
    def sigmoid(self, dataframe):
        
        return((dataframe - self.train_stats['mean'])/self.train_stats['std'])
        
    #Defining the model
    def build_model(self):
        
        input_layer=tf.keras.layers.Input(([len(self.train_dataset.keys())]))
        densel_layer = tf.keras.layers.Dense(units=1, input_shape=([len(self.train_dataset.keys())],))
        output = densel_layer(input_layer)
        model = tf.keras.Model(inputs=input_layer,outputs=output)

        model.compile(loss="mse",optimizer=tf.keras.optimizers.Adam(0.01), metrics=['mae', 'mse'])

        return model
        
    def make_prediction(self, prediction_data):
        
        #set up train and testing data
        self.train_dataset = self.data.sample(frac=0.90, random_state=0)
        self.test_dataset = self.data.drop(self.train_dataset.index)
    
        self.train_labels = self.train_dataset.pop("Points Scored")
        self.test_labels = self.test_dataset.pop("Points Scored")
        
        self.train_stats = self.train_dataset.describe()
        #self.train_stats.pop("Points Scored")
        self.train_stats = self.train_stats.transpose()
        
        #normalize the data
        normed_train_data = self.sigmoid(self.train_dataset)
        normed_test_data = self.sigmoid(self.test_dataset)

        #build the model
        model = self.build_model()
     #   model.summary()
        example_batch = normed_train_data
   #     print((example_batch.keys()))
        example_result = model.predict(example_batch)
    #    example_result

        EPOCHS = 1000
        early_stop = keras.callbacks.EarlyStopping(monitor='loss', patience=10)
        history = model.fit(normed_train_data, self.train_labels, epochs=EPOCHS, callbacks=[early_stop])

        #get key metrics
        loss, mae, mse = model.evaluate(normed_test_data, self.test_labels, verbose=0)

        
        #make predictions and then plot them in realation to the actual values
        test_predictions = model.predict(normed_test_data).flatten()
        
        #make prediction
        normed_prediction_data = self.sigmoid(prediction_data)
        game_prediction = model.predict(normed_prediction_data).flatten()
        
        return(game_prediction, mae) #return predicted values



        
class ActiveTeamData(object):

    def __init__(self, data):
        self.team_abbrev = data
        self.data =  self.getActiveTeamData()

    def getActiveTeamData(self):      
        team_abbreviation = self.team_abbrev
        TeamID =  int(teams.find_team_by_abbreviation(team_abbreviation)["id"])
        TeamName = teams.find_team_name_by_id(team_id=TeamID)['full_name']
        StartYear = 2020 #First year data is avalible
        LastYear = 2021 #Current year
            
            
        #Complile the Team Data
        
        team_season_point_average_raw_data = []
        team_points_raw_data = []
        opponent_season_point_average_raw_data = []
        opponent_season_points_raw_data = []
        
        team_season_FT_average_raw_data = []
        team_season_FG_average_raw_data = []
        team_season_FG3_average_raw_data = []
        opponent_season_FT_average_raw_data = []
        opponent_season_FG_average_raw_data = []
        opponent_season_FG3_average_raw_data = []
            
        
        print(StartYear, LastYear)
        for year in range((StartYear), (LastYear)):
            print("-------------------------------------------------")
            season = str(year) + "-" + str(((year+1)-2000)) #format the season correctly for the API
            teamLogs = teamgamelogs.TeamGameLogs(team_id_nullable=TeamID, season_nullable=season) #Get the TeamLogs for the season
            print(season)
            

            matchup_api_data = teamLogs.get_data_frames()[0]["MATCHUP"]
            team_season_points_api_data=teamLogs.get_data_frames()[0]["PTS"]
            team_abbreviation = teamLogs.get_data_frames()[0]["TEAM_ABBREVIATION"][0]
            

            team_season_points = []
            for game in range(0, len(teamLogs.get_data_frames()[0])):
                    
                    #Isolate the opponent abbreviation
                    try:   
                        matchup_api_data[game] = matchup_api_data[game].replace(team_abbreviation, "")
                    except:
                        print("Unexpected Error with removing player team")
                    try:
                        matchup_api_data[game] = matchup_api_data[game].replace(" @ ", "")
                        matchup_api_data[game] = matchup_api_data[game].replace(" vs. ", "")
                    except:
                        print("Error while isolating the opponent abbreviation")
                    
                    opponentAbbreviation = matchup_api_data[game]
                    
                    #Account for special cases where team names have changed since 2009
                    matchup_api_data[game] = matchup_api_data[game].replace('NOH', 'NOP')
                    matchup_api_data[game] = matchup_api_data[game].replace('NJN', 'BKN')
                    
                    #get the opponent ID
                    opponentAbbreviation_for_search = matchup_api_data[game]    
                    opponentID = int(teams.find_team_by_abbreviation(opponentAbbreviation_for_search)["id"])
                    
                    
                    if (game%10==0):
                        print("processing game {} out of {} for the {} season".format(game, len(teamLogs.get_data_frames()[0]), season))
                        
                    opponentLogs = teamgamelogs.TeamGameLogs(team_id_nullable=opponentID, season_nullable=season) #get Team logs for the opposing team
                    opponent_season_points_api_data = opponentLogs.get_data_frames()[0]['PTS']
                    
                    
                    team_points_raw_data.append(team_season_points_api_data[game])
                    team_season_points.append(team_season_points_api_data[game])
                    
                    past_games = teamLogs.get_data_frames()[0].head(game+1).copy()
                    team_season_FT_average_raw_data.append(past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(team_abbreviation, opponentAbbreviation),"{} vs. {}".format(team_abbreviation, opponentAbbreviation)])]["FTM"].mean())
                    team_season_FG_average_raw_data.append(past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(team_abbreviation, opponentAbbreviation),"{} vs. {}".format(team_abbreviation, opponentAbbreviation)])]["FGM"].mean())
                    team_season_FG3_average_raw_data.append(past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(team_abbreviation, opponentAbbreviation),"{} vs. {}".format(team_abbreviation, opponentAbbreviation)])]["FG3M"].mean())
                    
                    
                    if game == 0:
                        opponent_season_point_average_raw_data.append(opponent_season_points_api_data[game])
                        team_season_point_average_raw_data.append(teamLogs.get_data_frames()[0]["PTS"][game])
                        
                        
                    elif game<(len(opponentLogs.get_data_frames()[0]['PTS'])):
                        opponent_season_point_average_raw_data.append(opponent_season_points_api_data.head(game).mean())
                        team_season_point_average_raw_data.append((sum(team_season_points)/len(team_season_points)))
                                                
                        
                    else:
                        opponent_season_point_average_raw_data.append(opponent_season_points_api_data.mean())
                        team_season_point_average_raw_data.append((sum(team_season_points)/len(team_season_points)))
                    
                                            
                    time.sleep(1)
                    
        team_data = {
        "Points Scored": team_points_raw_data,
        "Team Point Average" : team_season_point_average_raw_data,
        "Opponent Team Point Average": opponent_season_point_average_raw_data, 
        "Team Season FTM Average Specific": team_season_FT_average_raw_data,
        "Team Sesason FGM Average Specific": team_season_FG_average_raw_data,
        "Team Season FG3M Average Specific": team_season_FG3_average_raw_data,
        }

        team_dataFrame = pd.DataFrame(data=team_data)
        

        return(team_dataFrame)


        
def compile_data_for_prediction(opp_abbrev,team_abbrev):
    team_abbreviation = team_abbrev
    opponentAbbreviation_for_prediction = opp_abbrev
    TeamID =  int(teams.find_team_by_abbreviation(team_abbreviation)["id"])
    season = "2020-21"
    teamLogs = teamgamelogs.TeamGameLogs(team_id_nullable=TeamID, season_nullable=season)
    team_season_points_api_data = teamLogs.get_data_frames()[0]["PTS"]

    team_season_point_average = [team_season_points_api_data.mean()]


    opponentID = int(teams.find_team_by_abbreviation(opponentAbbreviation_for_prediction)["id"])
    opponentLogs = teamgamelogs.TeamGameLogs(team_id_nullable=opponentID, season_nullable=season)
    opponent_season_points_api_data = opponentLogs.get_data_frames()[0]["PTS"]
    opponent_season_point_average = [opponent_season_points_api_data.mean()]

    past_games = teamLogs.get_data_frames()[0].copy()


    team_season_FT_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(team_abbreviation, opponentAbbreviation_for_prediction)])]["FTM"].mean())
    team_season_FG_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(team_abbreviation, opponentAbbreviation_for_prediction)])]["FGM"].mean())
    team_season_FG3_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(team_abbreviation, opponentAbbreviation_for_prediction)])]["FG3M"].mean())

    #If there is not enough data for this season, refer to the last season
    if math.isnan(team_season_FT_average):
        
        teamLogs = teamgamelogs.TeamGameLogs(team_id_nullable=TeamID, season_nullable="2019-20")
        past_games = teamLogs.get_data_frames()[0].copy()                                     
        team_season_FT_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(team_abbreviation, opponentAbbreviation_for_prediction)])]["FTM"].mean())
        team_season_FG_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(team_abbreviation, opponentAbbreviation_for_prediction)])]["FGM"].mean())
        team_season_FG3_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(team_abbreviation, opponentAbbreviation_for_prediction)])]["FG3M"].mean())



    prediction_data = {
    "Team Point Average" : team_season_point_average,
    "Opponent Team Point Average": opponent_season_point_average, 
    "Team Season FTM Average Specific": team_season_FT_average,
    "Team Sesason FGM Average Specific": team_season_FG_average,
    "Team Season FG3M Average Specific": team_season_FG3_average
    }
    prediction_dataframe = pd.DataFrame(data=prediction_data)
    #  print(prediction_dataframe)
    return(prediction_dataframe)




def Game_Res(team1_abbreviation,team2_abbreviation):

    team1 = team1_abbreviation
    team2 = team2_abbreviation

    team1_data = ActiveTeamData(team1).data
    team2_data = ActiveTeamData(team2).data


    team1_prediction_class = Prediction(team1_data)
    team2_prediction_class = Prediction(team2_data)

    oppData1 = compile_data_for_prediction(team2,team1)
    oppData2 = compile_data_for_prediction(team1,team2)



    team1_prediction_data = oppData1
    team1_prediction, team1_margin = team1_prediction_class.make_prediction(team1_prediction_data)

    team2_prediction_data = oppData2
    team2_prediction, team2_margin = team2_prediction_class.make_prediction(team2_prediction_data)


    print("check1")

    team1ptavg = team1_prediction_data['Team Point Average']
    team1ptavg = round(team1ptavg.iloc[0],0)
    team2ptavg = team2_prediction_data['Team Point Average']
    team2ptavg = round(team2ptavg.iloc[0],0)
    today = date.today()
    game = {'Home' : team1_abbreviation,'HomeScore' : str(round((team1_prediction.item(0)+team1_margin),0)),'Away' : team2_abbreviation,'AwayScore': str(round((team2_prediction.item(0)+team2_margin),0)),'Date': today.strftime("%m/%d/%y"),'HomePointAvg': str(team1ptavg),'AwayPoint Avg': str(team2ptavg) }
    return game 
