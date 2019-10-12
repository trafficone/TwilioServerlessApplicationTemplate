import logging
import json
from urllib.parse import parse_qs
#from urllib3.response import HTTPResponse
import os
from twilio_app.call import call_handler
from twilio_app.sms import message_handler
from twilio_app.fax import fax_handler

twilio_account_sid = os.environ["AccountSid"]
twilio_phone_number = os.environ["PhoneNumber"]

logger = logging.getLogger()
#logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

def server_error_reply(message,statusCode=500):
    logger.error("Returning 500 result with payload: {}".format(message))
    return {
            "statusCode": statusCode,
            "body": str(message)
            }

def server_reply(message):
    logger.debug("Returning 200 result with payload: {}".format(message))
    return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/xml"},
            "body": str(message)
            }

def handle_fax(parameters,http_method):
    """
    Get parameters from an incoming fax message. Passes parameters on to your app's 
    Fax handler code. Twilio Fax will use GET to initialize receiving the fax, and then POST to provide the details of the result.
    """
    fax_sid = parameters["FaxSid"]
    _from = parameters["From"]
    to = parameters["To"]
    error_tuple = (parameters.get("ErrorCode","0"),parameters.get("ErrorMessage",""))
    if http_method == "POST":
        num_pages = parameters["NumPages"]
        media_url = parameters.get("MediaUrl","")
        media = parameters.get("Media",b"")
        return fax_handler(fax_sid,_from,to,error_tuple,num_pages=num_pages,media_url=media_url,media=media)
    else:
        return fax_handler(fax_sid,_from,to,error_tuple)

def handle_call(parameters):
    """
    Get the parameters for an incoming phone call. Passes parameters to your app's 
    call handler code. If Digits were provided, those will be passed on as well.
    However, if you want to incorporate other parameters which Twilio exposes, 
    such as FromState or SpeechResult, you will need to add logic to handle them.
    """
    call_sid = parameters["CallSid"]
    _from = parameters["From"]
    to = parameters["To"]
    call_status = parameters["CallStatus"]
    direction = parameters["Direction"]
    forwarded_from = parameters.get("ForwardedFrom",None)
    parent_call_sid = parameters.get("ParentCallSid",None)
    digits = parameters.get("Digits",None)
    error_tuple = (parameters.get("ErrorCode","0"),parameters.get("ErrorMessage",""))
    return call_handler(call_sid,_from,to,call_status,error_tuple,direction,forwarded_from,parent_call_sid,digits)

def handle_message(parameters):
    """
    Get the parameters for an incoming SMS message. Passes those parameters to your apps message handler code. 
    """
    message_sid = parameters["MessageSid"]
    _from = parameters["From"]
    to = parameters["To"]
    body = parameters["Body"]
    messaging_service_sid = parameters.get("MessagingServiceSid","")
    num_media = parameters.get("NumMedia",None)
    error_tuple = (parameters.get("ErrorCode","0"),parameters.get("ErrorMessage",""))
    return message_handler(message_sid,_from,to,body,num_media,messaging_service_sid,error_tuple)

def params_from_headers(headers,body):
    #Handles content both as JSON and WWW form
    cf = "Content-Type"
    if cf not in headers:
        cf = cf.lower()
        if cf not in headers:
            logger.error("Invalid Event: Paylad has not Content-Type header")
            raise Exception("Content-Type not found")
    if headers[cf].startswith("application/x-www-form-urlencoded"):
        parameters = parse_qs(body)
        parameters = dict([(x,y[0]) for x,y in parameters.items()])
    elif headers[cf].startswith("application/json"):
        parameters = json.loads(body)
    else:
        logger.error("Content is of type {} and not supported".format(event["headers"][cf]))
        raise Exception("Unsupported Content Type")
    return parameters

def lambda_handler(event, context):
    """
    General Lambda handler, processes HTTP request data, validate request, and routes to fax, message, or call handler.
    """
    logger.info("New event triggered using method {}".format(event['httpMethod']))
    if context == 'test':
        twilio_account_id = 'TestSid'

    if "httpMethod" not in event or "headers" not in event:
        logger.error("Invalid Event Triggered: No HTTP Method and/or headers Found!")
        return server_error_reply("Invalid Resource")

    try:
        parameters = params_from_headers(event["headers"],event.get("body",None))
    except Exception as e:
        return server_error_reply(e)

    logger.debug("Input Parameters: {}".format(parameters))
    if "AccountSid" not in parameters or parameters["AccountSid"] != twilio_account_sid:
        logger.error("Incorrect AccountSid received. Expected: {} Got: {}".format(
            twilio_account_sid,
            parameters.get("AccountSid","Account Sid Not Transmitted")))
        server_error_reply("Not Authorized",statusCode=401)
    if 'To' not in parameters:
        logger.error("[To] number not in parameters")
        return error_server_reply("Invalid Twilio Message")
    if parameters["To"] != twilio_phone_number:
        logger.warn("Called/messaged Unexpected Number. Expected: {}, Got: {}".format(
            twilio_phone_number,
            parameters["To"]
            ))

    resp_message = ""
    try:
        ttype = "Unknown"
        if "CallSid" in parameters:
            ttype = "Call"
            resp_message = handle_call(parameters)
        elif "MessageSid" in parameters:
            ttype = "Message"
            resp_message = handle_message(parameters)
        elif "FaxSid" in parameters:
            ttype = "Fax"
            resp_message = handle_fax(parameters,event["httpMethod"])
        else:
            raise Exception("Unsupported Method of Communication from Twilio")
    except Exception as e:
        logger.error("Could Not Handle {}: {}".format(ttype,e))
        return server_error_reply("{} could not be handled".format(ttype))

    return server_reply(resp_message)
