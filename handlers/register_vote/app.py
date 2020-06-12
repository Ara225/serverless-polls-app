import json
import boto3
import os
from boto3.dynamodb.conditions import Key

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
    dynamodb = boto3.resource('dynamodb')
    
    table = dynamodb.Table(os.environ["DDB_TABLE_NAME"])
    print(event["queryStringParameters"])
    try:
        response = table.update_item(
            Key={
                'id': event["queryStringParameters"]["id"]
            },
            UpdateExpression="set responses." + event["queryStringParameters"]["response"] + " = responses." + event["queryStringParameters"]["response"] + "+ :r",
            ExpressionAttributeValues={
                ':r': event["queryStringParameters"]["value"]
            },
            ReturnValues="UPDATED_NEW"
        )
    except BaseException as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": "Unable to register vote" 
            }),
        }
