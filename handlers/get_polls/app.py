import json
import boto3
import os
from boto3.dynamodb.conditions import Key
import simplejson as json
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
    if event.get("queryStringParameters"):
        if event["queryStringParameters"].get("id"):
            try:
                response = table.query(
                    KeyConditionExpression=Key('id').eq(event["queryStringParameters"]["id"])
                )
                if response['Items'] == []:
                    return {
                        'headers': {
                            'Access-Control-Allow-Headers': 'Content-Type',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                        },
                        "statusCode": 500,
                            "body": json.dumps({
                                "success": False,
                                "error": "Database query returned an empty body. If an ID was supplied, this means there was no matching item" 
                            }),
                    }
                else:
                    return {
                        'headers': {
                            'Access-Control-Allow-Headers': 'Content-Type',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                        },
                        "statusCode": 200,
                        "body": json.dumps({
                            "success": True,
                            "polls": response['Items']
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
                        "error": "Unable to retrieve items" 
                    }),
                }
    try:
        response = None
        # Large requests are truncated by the DB. The continueKey param provides a way for the client-side code to get the next keys
        # Limit simply limits the amount of keys. This can be used to only retrieve the amount of items we need, so these work together 
        # to minmize DB load
        if event.get("queryStringParameters"):
            print(event["queryStringParameters"])
            if event["queryStringParameters"].get("continueKey") and event["queryStringParameters"].get("limit"):
                response = table.scan(ExclusiveStartKey={"id": event["queryStringParameters"]["continueKey"]}, Limit=int(event["queryStringParameters"]["limit"]))
            elif event["queryStringParameters"].get("continueKey"):
                response = table.scan(ExclusiveStartKey={"id": event["queryStringParameters"]["continueKey"]})
            elif event["queryStringParameters"].get("limit"):
                response = table.scan(Limit=int(event["queryStringParameters"]["limit"]))
            else:
                response = table.scan()
        else:
            response = table.scan()
        if response['Items'] == []:
            return {
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                "statusCode": 500,
                    "body": json.dumps({
                        "success": False,
                        "error": "Database query returned an empty body. If an ID was supplied, this means there was no matching item" 
                    }),
            }
        # If a last evaluated key is provided, we return this so the client app can use it to get the next items later
        if response.get("LastEvaluatedKey"):
            key = response["LastEvaluatedKey"]['id']
        else:
            key = None
        return {
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "polls": response['Items'],
                "count": response['Count'],
                "continueKey": key
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
                "error": "Unable to retrieve items" 
            }),
        }
