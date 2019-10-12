import logging
from twilio.twiml.messaging_response import Message, MessagingResponse
from twilio.rest import Client
from datetime import datetime
import os

account_access = os.environ["AccountAccess"]
accouunt_secret = os.environ["AccountSecret"]
from_number = os.environ["PhoneNumber"]

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_message(message_sid):
    #Wrapper to get message from Twilio API
    logger.info("Getting Message {}".format(message_sid))
    client = Client(account_access,account_secret)
    message = client.messages(message_sid)
    
    return message

def send_message(to,body):
    #Wrapper to send message via SMS.
    logger.info("Sending Message from {} to {} [{}]chars".format(from_number,to,len(body)))
    client = Client(account_access,account_secret)
    message = client.messages.create(
                from_ = from_number,
                to = to,
                body = body )

    return message.sid

def delete_message(message_sid):
    #Wrapper to message record from Twilio.
    logger.info("Deleting Message {}".format(message_sid))
    message = get_message(message_sid)
    message.delete()

def message_handler(message_sid,_from,to,body,num_media,messaging_service_sid,error_tuple):
    """
    EXAMPLE HANDLER
    Place code here to handle messages
    """
    response = MessagingResponse()
    response.message("Hello! It's {}, your serverless application is working!".format(datetime.now()))
    
    return response
