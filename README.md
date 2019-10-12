# TwilioServerlessApplicationTemplate
A template to interact with Twilio using AWS SAM. Deploy your Twilio app in a serverless architecture with ease!

## Premise
Setting up servers sucks, especially if your ultimate goal is just to set up a phone app. 
Using [AWS Serverless Application Model](https://aws.amazon.com/serverless/sam/) you can leave the
deployment, management of resources, and the "hard part" of managing a serverless application to
AWS, leaving you more time to write the code for your application and getting on with your life. 

What's a serverless application and why do I want one for my Twilio application? A serverless
application is a web application which runs using serverless architecture. AWS Services like Lambda,
S3, and API Gateway will handle incoming requests, execute your code, and host your static content
without you having to worry about the execution environment. One of the biggest wins with moving to
serverless architecture for Twilio is that scaling and capacity planning are simplified and
eliminated, and test/hobbiest environments can be identical to production environments with the cost
only scaling with usage. 

## Costs
**NOTE: costs are subject to change, please refer to the service provider for current pricing.**

Going Serverless for Twilio will almost certainly save you money at any scale. Excluding free tier,
here's a breakdown of the prices:

|Service|Function|Invocation Cost|
|-------|:------:|----------:|
|Twilio|Phone Number| $1/month|
|Twilio|Call Received|$0.0085/min|
|Twilio|SMS|$0.0075/message|
|AWS|Lambda Request|$0.00000002/request|
|AWS|Lambda Duration|$0.000016667/GB-Second|
|AWS|API Gateway|$0.0000035/request|
|AWS|S3 Storage|$0.00000225/Mb month|
|AWS|EC2 t2.micro box usage (AKA server)|$0.86/month|

Your Twilio costs are the same whether you use EC2 or SAM, but your cost per request with SAM is
approxmatly $0.0000056. You would have to serve over 153,000 requests a month, about 3.5 calls a minute to break even using EC2, excluding the perpetual free tier of Lambda.
This means for a Twilio bill of over $1,300, your AWS bill is less than $1.

# Getting Set Up

## Pre-requisites

You will need an account on both [AWS](https://aws.amazon.com/) and
[Twilio](https://www.twilio.com/). On your Twilio account, you will also need to get a [phone
number](https://www.twilio.com/docs/voice/quickstart/python#sign-up-for-twilio-and-get-a-phone-number). 

You will need to install the following:
* git
* [AWS SAM
  CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* AWS CLI

## Quick Start
Set environment variables for your Twilio Phone Number, SID, API Key, and API Secret. If you haven't
created an alternate API key, you can use the SID as the API key as well, although that is not
recommended.
```
export TWILIO_PHONE_NUMBER=**phonenumber**
export TWILIO_SID=**SID**
export TWILIO_API_KEY=**APIKey**
export TWILIO_API_SECRET=**APISecret**
```

Set environment variables for building and deploying via SAM
```
export REGION=us-west-2 #Set to any region
export BUCKET=sam-package-$$ #S3 Bucket name where packaged applications are stored
```

Use git to get the latest version of the repository.
```
git clone git@github.com:trafficone/TwilioServerlessApplicationTemplate.git
cd TwilioServerlessApplicationTemplate
```


Use AWS CLI and AWS SAM CLI to build and package the default application
```
#create a bucket to package your application to
aws s3 mb s3://$BUCKET --region $REGION

#build the application
sam build

#package the application
sam package --output-template packaged.yaml --s3-bucket $BUCKET
```

Using the environment variables, deploy the application to AWS with your Twilio settings.
```
sam deploy --region $REGION \
    --template-file packaged.yaml \
    --capabilities CAPABILITY_IAM \
    --stack-name TwilioServerlessExample
    --parameter-overrides TwilioAccountSid=$TWILIO_SID \
                          TwilioAccountAccess=$TWILIO_API_KEY \
                          TwilioAccessKey=$TWILIO_API_SECRET \
                          TwilioPhoneNumber=TWILIO_PHONE_NUMBER
#get the endpoint URL
aws cloudformation describe-stacks ---region $REGION\
    --stack-name TwilioServerlessExample 
    --query "Stacks[0].Outputs[1].OutputValue"
```

Set the endpoint URL as the handler for your Twilio phone number and you're set up!

