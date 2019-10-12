import logging
from twilio.twiml.voice_response import VoiceResponse, Say
from twilio.rest import Client
from datetime import datetime
import os

account_access = os.environ["AccountAccess"]
accouunt_secret = os.environ["AccountSecret"]
from_number = os.environ["PhoneNumber"]

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_call(call_sid):
    """
    Wrapper for getting call information from Twilio API.
    """
    logger.info("Getting Call {}".format(call_sid))
    client = Client(account_access,account_secret)
    call = client.calls(call_sid)

    return call

def place_call(to, action):
    """
    Wrapper for placing call information to Twilio API. If you use this, make sure to include logic to handle the case where to = from_number in call_handler.
    """
    logger.info("Placing Call From {} To {} with action {}".format(from_number,to,action))
    client = Client(account_access,account_secret)
    call = client.calls.create(
                from_ = from_number,
                to = to,
                action = action
                )

    return call.sid

def call_handler(call_sid,_from,to,call_status,error_tuple,direction,forwarded_from,parent_call_sid,digits):
    """
    EXAMPLE HANDLER
    Place Code Here to Handle Calls
    """
    response = VoiceResponse()
    #Review Say Command Documentationhttps://www.twilio.com/docs/voice/twiml/say
    say = Say("Hello, your Serverless Application is Working.",voice="Polly.Joanna")
    response.append(say)
    response.hangup()

    return response


