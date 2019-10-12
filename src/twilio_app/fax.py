#from twilio.twiml.fax_response import FaxResponse
import logging
from twilio.rest import Client
from datetime import datetime
import os
import boto3
import requests

account_access = os.environ["AccountAccess"]
accouunt_secret = os.environ["AccountSecret"]
from_number = os.environ["PhoneNumber"]
#TODO: Set Environment Variable
bucket = os.environ.get("SavedMediaBucket","")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_fax(fax_sid):
    """
    Wrapper to get fax info from Twilio API.
    """
    client = Client(account_access,account_secret)
    fax = client.fax.faxes(fax_sid)
    
    return fax

def send_fax(to,media_url):
    """
    Wrapper to send fax using Twilio API.
    """
    client = Client(account_access,account_secret)
    fax = client.fax.faxes.create(
                from_ = from_number,
                to = to,
                media_url = media_url )

    return fax.sid

def delete_fax(fax_sid):
    #Deletes fax media AND metadata. Cannot be undone.
    fax = get_fax(fax_sid)
    fax.delete()

def save_fax(filename, fax_media):
    #Download fax from Twilio to S3
    s3 = boto3.client('s3')
    today_str = str(datetime.date.today())
    
    s3.put_object(Bucket=bucket,Key='fax/'+today_str+'/'+filename,Body=fax_media)
    logger.info("Object uploaded to s3://{bucket}/{key}".format(bucket=bucket,key='fax/'+today_str+'/'+filename))

def fax_handler(fax_sid,_from,to,error_tuple,num_pages=None,media_url=None,media=None):
    """
    EXAMPLE HANDLER
    Place code here to handle fax
    Unfortunately, the FaxResponse has not been implemented in the Twilio Python module, so responses are written in XML.
    """
    response = "<Response />"
    if media_url is None and media is None:
        #Other element attributes for Receive are method, mediaType, pageSize, and storeMedia
        response = """
            <Response>
                <Receive action="/Prod/hello">
            </Response>
        """
    elif media_url is not None:
        logger.info("Fax Received at: {}".format(media_url))
        fax_media = requests.get(media_url)
        #save_fax(_from+"_"+to+"_"+fax_sid+".tiff",fax_media)

    elif media is not None:
        logger.info("Fax {} Received, but the media was deleted".format(fax_sid)) 
        #save_fax(_from+"_"+to+"_"+fax_sid+".tiff",media)
    
    return response
