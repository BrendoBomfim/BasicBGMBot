#Python libraries that we need to import for our bot
import random
import base64
import requests
from flask import Flask, request
from pymessenger.bot import Bot
import os 
app = Flask(__name__)
#ACCESS_TOKEN = 'ACCESS_TOKEN'   
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
#VERIFY_TOKEN = 'VERIFY_TOKEN'   
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot (ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                print(message)
                if message['message'].get('text'):
                    response_sent_text =  message['message']['text']
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    for att in message['message'].get('attachments'):
                        file_type = att['type']
                        print(file_type)
                        url = 'https://drive.google.com/a/sciosolutions.com.br/uc?id=1emodK6WomZ6s96oIUgxfrohqu-nulXsb&export=download'
                        file_name = url.split("/")[5].split("?")[0]
                        file_location = "/tmp/" + file_name
                        base64_string = download_file(url)
                        save_file(base64_string, file_location)
                        #print(send_attachment_message(recipient_id, file_type, file_location))
                        #print(os.listdir("/tmp"))
                        print(send_attachment_url_message(recipient_id, file_type, url))
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

def send_attachment_url_message(recipient_id, file_type, url):
    #sends user the text message provided via input response parameter
    response = bot.send_attachment_url(recipient_id, file_type, url)
    return response

def send_attachment_message(recipient_id, file_type, file_location):
    return bot.send_attachment(recipient_id, file_type, file_location)

def save_file(data, file_location):
    with open(file_location, "wb") as fh:
        fh.write(base64.decodebytes(data))

def download_file(url):
    return base64.b64encode(requests.get(url).content)

if __name__ == "__main__":
    app.run()
