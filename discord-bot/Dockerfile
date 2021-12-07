FROM python:3
FROM gorialis/discord.py

# RUN mkdir -p /usr/src/bot
WORKDIR /code
ENV DISCORD_TOKEN=OTE3MTg1NzMzMjEzNjkxOTE1.Ya1Bxw.hNX-KOYZu2AcTv1wJMxUHy7Mkg0
ENV MONGO_ENDPOINT = mongodb+srv://new-user:demoPassword@cluster0.hwovc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
ENV TWILIO_ACCOUNT_SID = ACbe09a36be57c1ee1615bcedeebc1b9ea
ENV TWILIO_AUTH_TOKEN = 308676297e51cc80872e60553f0257f7
ENV MONGO_FLASK_ENDPOINT_ROOT = https://lazy-gambler-flask-service.jhill6253.repl.co/
ENV MAIN_MONGO_API = mongodb
ENV DATE_MONGO_API = date
COPY . .
# RUN python3 -m pip install --upgrade https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-0.12.0-py3-none-any.whl
# RUN python3 -m pip install dotenv
# RUN python3 -m pip install tensorflow tensorflow-gpu
RUN python3 -m pip install -r requirements.txt
CMD [ "python3", "main.py" ]