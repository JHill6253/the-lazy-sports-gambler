from datetime import date
import discord
import os
from discord import message
from discord.message import Message
import datetime
from discord.ext import tasks, commands

from ML import Game_Res
from cleaner import clean_new_games, format_discord_game_message, format_discord_prediction_message
from text_service import textCLI
from dotenv import load_dotenv

from mongo_interactor import get_user_numbers,get_predictions_today,get_games_today,post_predictions_db, post_games_db
load_dotenv()

MONGO_FLASK_ENDPOINT_ROOT = os.getenv("MONGO_FLASK_ENDPOINT_ROOT") 
MAIN_MONGO_API = os.getenv("MAIN_MONGO_API")
DATE_MONGO_API = os.getenv("DATE_MONGO_API")



DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time) # days always >= 0

    return (future_exec - now).total_seconds()



def sendTexts(games):
    users = get_user_numbers()
    mes = format_discord_prediction_message(games)
    responses = []
    for res in users:
        if res["sendText"] == "True":
            cli = textCLI()
            name= res["name"]
            message = f"Hi {name}, {mes}"
            messageRes = cli.sendMessage(str(res["phone"]),str(message))
            responses.append(messageRes)
        
    return (responses)

def run_game_ml(game):
    home = game["home"]["teamAbrev"]
    away = game["away"]["teamAbrev"]
    res = Game_Res(home,away)
    return res

def run_morning_ml():
    today = date.today()
    games = get_games_today()
    predictionResults = []    
    for i in range(2):#len(games)):
        res = run_game_ml(games[i])
        print(res)
        predictionResults.append(res)
    print(predictionResults)
    post_predictions_db({"games":predictionResults,
    "date": today.strftime("%m/%d/%y") })
        




client = discord.Client()


@tasks.loop(seconds=1)
async def master_loop():
    await client.wait_until_ready()
    now = datetime.datetime.now()
    currentTime = now.strftime("%H:%M:%S")
    print(currentTime)
    if currentTime == "04:30:30":

        update_game_db.start()
        
    if currentTime == "04:35:30":
        get_todays_games.start()
        run_ml.start()
    if currentTime == "08:00:00":
        get_todays_predictions.start()
        text_todays_predictions.start()
        
@tasks.loop(hours=24)
async def text_todays_predictions():
    await client.wait_until_ready()
    channel = client.get_channel(id=855581170201133109) 
    await channel.send("Sending Texts...")
    res = get_predictions_today()
    if res != "No Games":
        text = sendTexts(res)
        await message.channel.send("texts sending....") 
    else:
        await message.channel.send("Texts Failed...")

@tasks.loop(hours=24)
async def get_todays_games():
    await client.wait_until_ready()
    channel = client.get_channel(id=855581170201133109) 
    await channel.send("Grabbing todays games...")
    res = get_games_today()
    if res !="No Games":
        mes = format_discord_game_message(res)
        await channel.send(mes)
    else:
        await channel.send("Must be no games today...")

@tasks.loop(hours=24)
async def update_game_db():
    await client.wait_until_ready()
    channel = client.get_channel(id=855581170201133109) 
    await channel.send("Updating Games db...")
    res = post_games_db()
    if res["Status"] == "Successfully Inserted":
        await channel.send("Succesfully updated! :)")
    else:
        await channel.send("Something went wrong :(")


@tasks.loop(hours=24)
async def run_ml():
    await client.wait_until_ready()
    channel = client.get_channel(id=855581170201133109) 
    await channel.send("Running ML...")
    today = date.today()
    games = get_games_today()
    predictionResults = []    
    for i in range(len(games)):
        res = run_game_ml(games[i])
        print(res)
        predictionResults.append(res)
    res = post_predictions_db({"games":predictionResults,
    "date": today.strftime("%m/%d/%y") })
    if res["Status"] == "Successfully Inserted":
        await channel.send("Succesfully updated! :)")
    else:
        await channel.send("Something went wrong :(")


@tasks.loop(hours=24)
async def get_todays_predictions():
    await client.wait_until_ready()
    channel = client.get_channel(id=855581170201133109) 
    await channel.send("Grabbing todays predictions...")
    res = get_predictions_today()
    if res != "No Games":
        mes = format_discord_prediction_message(res)
        await channel.send(mes)
    else:
        await channel.send("Must be no games today...")



@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == 'update game database':
        await message.channel.send("Updating...")
        res = post_games_db()
        if res["Status"] == "Successfully Inserted":
            await message.channel.send("Succesfully updated! :)")
        else:
            await message.channel.send("Something went wrong :(")
    if message.content.lower() == 'get game predictions':
        await message.channel.send("Grabbing todays predictions...")
        res = get_predictions_today()
        print(res)
    if message.content.lower() == 'get games':
        await message.channel.send("Grabbing todays games...")
        res = get_games_today()
        if len(res) >0:
            mes = format_discord_game_message(res)
            await message.channel.send(mes)

    if message.content.lower() == 'run ml':
        await message.channel.send("Running ML...")
        run_morning_ml()
    if message.content.lower() == 'send text':
        await message.channel.send("Sending Texts...")
        res = get_predictions_today()
        if res != "No Games":
            mes = format_discord_prediction_message(res)
            text = sendTexts(res)
            await message.channel.send("text send")
            
        else:
            await message.channel.send("Must be no games today...")

# get_todays_games.start()
# run_ml.start()

#update_game_db.start()
# get_todays_predictions.start()
master_loop.start()
client.run(DISCORD_TOKEN)  

