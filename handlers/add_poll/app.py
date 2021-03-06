import json
import boto3
import os
from boto3.dynamodb.conditions import Key
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
def lambda_handler(event, context):
    """
    Add a poll. See README.md for more

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    body = json.loads(event["body"].replace("'", '"'))
    # This allows the function to run locally by sending requests to a local DynamoDB. Option one is for when it's
    #  being run by SAM, option two for when the tests are being run, and three for production
    if os.environ.get('AWS_SAM_LOCAL'):
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://dynamo:8000')
        table = dynamodb.Table("pollsStorageDB")
    elif 'local' == os.environ.get('APP_STAGE'):
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        table = dynamodb.Table("pollsStorageDB")
    else:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ["DDB_TABLE_NAME"])
    # Create dict to contain the number of votes for each possible response
    responses = {}
    for answer in body["answersList"]:
        responses[answer] = 0
    
    # Sort out the expiry date
    if body.get("expiresIn"):
        try:
            expiresIn = (datetime.now() + timedelta(days=int(body["expiresIn"]))).timestamp()
        except BaseException as e:
            print(e)
    else:
        expiresIn = (datetime.now() + timedelta(days=30)).timestamp()

    # Create unique ID for the poll
    randomString = ''.join([random.choice(string.ascii_letters 
            + string.digits) for n in range(32)]) 
    poll = {
                "id": randomString,
                'question': body["question"],
                'answersList': body["answersList"],
                'responses': responses,
                'created': datetime.now().timestamp(),
                "expires": Decimal(expiresIn)
           }
    response = table.put_item(
        Item=poll
    )
    
    return {
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
            "polls": [poll]
        }),
    }
