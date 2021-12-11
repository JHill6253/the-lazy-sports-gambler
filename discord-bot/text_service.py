import os
from twilio.rest import Client

from dotenv import load_dotenv

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
class textCLI:
    def __init__(self):
        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.client = Client(self.account_sid, self.auth_token)

    def sendMessage(self, number, messageBody):
        message = self.client.messages \
                    .create(
                        body=messageBody,
                        from_='+18339482016',
                        to='+1'+ number
                    )

        return message.sid
