

import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
class textCLI:
    def __init__(self):
        self.account_sid = None
        self.auth_token = None
        self.client = Client(self.account_sid, self.auth_token)
    def sendMessage(self, number, messageBody):
        message = self.client.messages \
                    .create(
                        body=messageBody,
                        from_='+18339482016',
                        to='+1'+ number
                    )

        return message.sid
