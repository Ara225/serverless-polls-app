import json
import boto3
import os
from boto3.dynamodb.conditions import Key
import random
import string
from datetime import datetime, timedelta
def lambda_handler(event, context):
    """Sample pure Lambda function

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
    if event.get("body"):
        body = json.loads(event["body"].replace("'", '"'))
        if not body.get("question") or not body.get("answersList"):
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "success": False,
                    "error": "Unable to validate the content of the body of the request"
                }),
            }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": "Request body not supplied"
            }),
        }
    dynamodb = boto3.resource('dynamodb')
    
    table = dynamodb.Table(os.environ["DDB_TABLE_NAME"])
    # Create dict to contain the number of votes for each
    responses = {}
    for answer in body["answersList"]:
        responses[answer] = 0
    
    # Sort out the expiry date
    if body.get("expiresIn"):
        try:
            if int(body["expiresIn"]) < 90:
                expiresIn = (datetime.now() + timedelta(days=int(body["expiresIn"]))).isoformat()
            else:
                expiresIn = (datetime.now() + timedelta(days=30)).isoformat()
        except BaseException as e:
            print(e)
    else:
        expiresIn = (datetime.now() + timedelta(days=30)).isoformat()

    # Create unique ID for the poll
    randomString = ''.join([random.choice(string.ascii_letters 
            + string.digits) for n in range(32)]) 
    poll = {
                "id": randomString,
                'question': body["question"],
                'answersList': body["answersList"],
                'responses': responses,
                'created': datetime.now().isoformat(),
                "expires": expiresIn
           }
    response = table.put_item(
        Item=poll
    )
    return {
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
            "polls": poll
        }),
    }
