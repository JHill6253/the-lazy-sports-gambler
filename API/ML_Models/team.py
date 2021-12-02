import pandas as pd 
import time
import math
from nba_api.stats.static import teams
from nba_api.stats.endpoints import  teamgamelogs

class Team(object):
    def __init__(self, team_abbreviation, teamId):
        self.team_abbreviation = team_abbreviation
        self.TeamID =  teamId
        self.TeamName = teams.find_team_name_by_id(team_id=self.TeamID)['full_name']
        self.StartYear = 2020 #First year data is avalible
        self.LastYear = 2021 #Current year
        
        
    #Complile the Team Data
    def compile_active_team_data(self):
    
        team_season_point_average_raw_data = []
        team_points_raw_data = []
        opponent_season_point_average_raw_data = []

        
        team_season_FT_average_raw_data = []
        team_season_FG_average_raw_data = []
        team_season_FG3_average_raw_data = []

            
        
        print(self.StartYear, self.LastYear)
        for year in range((self.StartYear), (self.LastYear)):
            print("-------------------------------------------------")
            season = str(year) + "-" + str(((year+1)-2000)) #format the season correctly for the API
            teamLogs = teamgamelogs.TeamGameLogs(team_id_nullable=self.TeamID, season_nullable=season) #Get the TeamLogs for the season
            print(season)
            

            matchup_api_data = teamLogs.get_data_frames()[0]["MATCHUP"]
            team_season_points_api_data=teamLogs.get_data_frames()[0]["PTS"]
            self.team_abbreviation = teamLogs.get_data_frames()[0]["TEAM_ABBREVIATION"][0]
            

            team_season_points = []
            for game in range(0, len(teamLogs.get_data_frames()[0])):
                   
                    #Isolate the opponent abbreviation
                    try:   
                        matchup_api_data[game] = matchup_api_data[game].replace(self.team_abbreviation, "")
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
                    team_season_FT_average_raw_data.append(past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(self.team_abbreviation, opponentAbbreviation),"{} vs. {}".format(self.team_abbreviation, opponentAbbreviation)])]["FTM"].mean())
                    team_season_FG_average_raw_data.append(past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(self.team_abbreviation, opponentAbbreviation),"{} vs. {}".format(self.team_abbreviation, opponentAbbreviation)])]["FGM"].mean())
                    team_season_FG3_average_raw_data.append(past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(self.team_abbreviation, opponentAbbreviation),"{} vs. {}".format(self.team_abbreviation, opponentAbbreviation)])]["FG3M"].mean())
                    
                    
                    if game == 0:
                        opponent_season_point_average_raw_data.append(opponent_season_points_api_data[game])
                        team_season_point_average_raw_data.append(teamLogs.get_data_frames()[0]["PTS"][game])
                        
                        
                    elif game<(len(opponentLogs.get_data_frames()[0]['PTS'])):
                        opponent_season_point_average_raw_data.append(opponent_season_points_api_data.head(game).mean())
                        team_season_point_average_raw_data.append((sum(team_season_points)/len(team_season_points)))
                                              
                        
                    else:
                        opponent_season_point_average_raw_data.append(opponent_season_points_api_data.mean())
                        team_season_point_average_raw_data.append((sum(team_season_points)/len(team_season_points)))
                    
                                            
                    time.sleep(20)
        #adding the lists to the team data dictionary to be made into a dataframe
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
    def get_active_team_data(self):
            return(self.compile_active_team_data())
    def compile_data_for_prediction(self, opponentAbbreviation_for_prediction):
        
        season = "2020-21"
        teamLogs = teamgamelogs.TeamGameLogs(team_id_nullable=self.TeamID, season_nullable=season)
        team_season_points_api_data = teamLogs.get_data_frames()[0]["PTS"]
       
        team_season_point_average = [team_season_points_api_data.mean()]
        
        
        opponentID = int(teams.find_team_by_abbreviation(opponentAbbreviation_for_prediction)["id"])
        opponentLogs = teamgamelogs.TeamGameLogs(team_id_nullable=opponentID, season_nullable=season)
        opponent_season_points_api_data = opponentLogs.get_data_frames()[0]["PTS"]
        opponent_season_point_average = [opponent_season_points_api_data.mean()]

        past_games = teamLogs.get_data_frames()[0].copy()
        
        
        team_season_FT_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction)])]["FTM"].mean())
        team_season_FG_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction)])]["FGM"].mean())
        team_season_FG3_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction)])]["FG3M"].mean())
        
        #If there is not enough data for this season, refer to the last season
        if math.isnan(team_season_FT_average):
            
            teamLogs = teamgamelogs.TeamGameLogs(team_id_nullable=self.TeamID, season_nullable="2019-20")
            past_games = teamLogs.get_data_frames()[0].copy()                                     
            team_season_FT_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction)])]["FTM"].mean())
            team_season_FG_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction)])]["FGM"].mean())
            team_season_FG3_average = (past_games.loc[past_games['MATCHUP'].isin(["{} @ {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction),"{} vs. {}".format(self.team_abbreviation, opponentAbbreviation_for_prediction)])]["FG3M"].mean())
       
       
        
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
        
    def get_data_for_prediction(self, opponentAbbreviation_for_prediction):
        return(self.compile_data_for_prediction(opponentAbbreviation_for_prediction))
        
