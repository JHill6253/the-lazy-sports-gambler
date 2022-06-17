from datetime import date, datetime,timedelta
import discord
import os
from discord import message
import datetime
from discord.ext import tasks
from keep_alive import keep_alive

from cleaner import clean_new_games, format_discord_game_message, format_discord_prediction_message
from text_service import textCLI
from dotenv import load_dotenv

from mongo_interactor import get_user_numbers,get_predictions_today,get_games_today, post_games_db 
from ml_interactor import run_ml
load_dotenv()


MONGO_FLASK_ENDPOINT_ROOT = os.getenv("MONGO_FLASK_ENDPOINT_ROOT") 
MAIN_MONGO_API = os.getenv("MAIN_MONGO_API")
DATE_MONGO_API = os.getenv("DATE_MONGO_API")



DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = (datetime.datetime.now() - timedelta(hours=5))
    return(now)
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

  




client = discord.Client()



@tasks.loop(seconds=1)
async def master_loop():
    await client.wait_until_ready()
    now = datetime.datetime.now() - timedelta(hours=5)
    currentTime = now.strftime("%H:%M:%S")
    print(currentTime)
    if currentTime == "12:35:30":
        get_todays_games.start()
    if currentTime == "15:00:00":
        get_todays_predictions.start()
        text_todays_predictions.start()
        
@tasks.loop(hours=24)
async def text_todays_predictions():
    await client.wait_until_ready()
    channel = client.get_channel(id=855581170201133109) 
    await channel.send("Sending Texts...")
    res = get_predictions_today()
    if res != "No Games":
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
    if message.content.lower() == 'update db':
        print(datetime.datetime.today() - timedelta(hours=5))
        await message.channel.send("Updating...")
        res = post_games_db()
        if res["Status"] == "Successfully Inserted":
            await message.channel.send("Succesfully updated! :)")
        else:
            await message.channel.send("Something went wrong :(")
    if message.content.lower() == 'get predictions':
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
        res = run_ml()
        print(res)
        if res == "sucess":
          await message.channel.send("Succesfully running! :)")
        else:
          await message.channel.send("Something went wrong :(")
    if message.content.lower() == 'send texts':
        await message.channel.send("Sending Texts...")
        res = get_predictions_today()
        print(res)
        if res != "No Games":
            mes = format_discord_prediction_message(res)
            sendTexts(res)
            await message.channel.send("text's sent")
            
        else:
            await message.channel.send("Must be no games today...")
master_loop.start()
keep_alive()
client.run(DISCORD_TOKEN)  

