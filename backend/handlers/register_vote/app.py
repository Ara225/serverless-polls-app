import json
import boto3
import os
from boto3.dynamodb.conditions import Key
from decimal import Decimal
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
    if os.environ.get('AWS_SAM_LOCAL'):
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://dynamo:8000')
        table = dynamodb.Table("pollsStorageDB")
    elif 'local' == os.environ.get('APP_STAGE'):
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
        table = dynamodb.Table("pollsStorageDB")
    else:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ["DDB_TABLE_NAME"])
    body = json.loads(event["body"].replace("'", '"'))
    try:
        response = table.update_item(
            Key={
                'id': body["id"]
            },
            UpdateExpression="set responses." + body["response"] + " = responses." + body["response"] + "+ :r",
            ExpressionAttributeValues={
                ':r': Decimal(1)
            },
            ReturnValues="UPDATED_NEW"
        )
        return {
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            "statusCode": 200,
            "body": json.dumps({
                "success": True
            }), 
        }
    except BaseException as e:
        print(e)
        return {
        'headers': {
             'Access-Control-Allow-Headers': 'Content-Type',
             'Access-Control-Allow-Origin': '*',
             'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": "Unable to register vote" 
            }),
        }
