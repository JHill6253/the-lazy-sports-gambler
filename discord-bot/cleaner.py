from datetime import date,datetime,timedelta


def clean_new_games(data):
    games = []
    today = date.today() - timedelta(hours=5)
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
    games = {
        "games" :games,
        "date" : today.strftime("%m/%d/%y")
        }
    return games 

def format_discord_game_message(data):
    msg = "Here are the games for today:"
    for game in data:
        home = game["home"]["teamAbrev"]
        away = game["away"]["teamAbrev"]
        msg += f"\n{home} vs {away}"
    return msg
def format_discord_prediction_message(data):
    msg = "here are the predictions for today:"
    for game in data:
        home = game["Home"]
        away = game["Away"]
        homeScore = game["HomeScore"]
        awayScore = game["AwayScore"]
        msg += f"\n{home}: {homeScore} vs {away}: {awayScore}"
    return msg