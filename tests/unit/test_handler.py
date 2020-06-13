import simplejson as json
import pytest
from sys import path
path.append("../../")
from os import environ
from handlers.get_polls import app as getpolls
from handlers.add_poll import app as addpolls
from handlers.register_vote import app as registervote
from decimal import Decimal

def add_a_sample_poll():
    ret = addpolls.lambda_handler(json.load(open("../../events/addSamplePollEvent.json")), "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "What?" in data["polls"][0]["question"]
    return data["polls"][0]['id']

def test_get_all_polls():
    ret = getpolls.lambda_handler(json.load(open("../../events/getPollsEvent.json")), "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "success" in ret["body"]
    assert data["success"] == True

def test_get_poll_by_Id():
    event = json.load(open("../../events/getPollsEvent.json"))
    event["queryStringParameters"] = {"id": environ['SamplePollId']}
    ret = getpolls.lambda_handler(event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "success" in ret["body"]
    assert data["success"] == True
    assert len(data["polls"]) == 1
    assert "What?" in data["polls"][0]["question"]
    assert data["polls"][0]['id'] == environ['SamplePollId']

def test_get_poll_with_invalid_Id():
    event = json.load(open("../../events/getPollsEvent.json"))
    event["queryStringParameters"] = {"id": "notAnID"}
    ret = getpolls.lambda_handler(event, "")
    print(ret)
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 500
    assert "success" in ret["body"]
    assert data["success"] == False

def test_register_vote():
    event = json.load(open("../../events/registerVoteEvent.json"))
    event["body"] = "{\"id\": \"" + environ['SamplePollId'] + "\", \"response\": \"Yes\"}" 
    ret = registervote.lambda_handler(event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "success" in ret["body"]
    assert data["success"] == True
    event = json.load(open("../../events/getPollsEvent.json"))
    event["queryStringParameters"] = {"id": environ['SamplePollId']}
    ret = getpolls.lambda_handler(event, "")
    data = json.loads(ret["body"])
    assert data["polls"][0]["responses"]["Yes"] == Decimal(1)

def test_register_vote_invalid_id():
    event = json.load(open("../../events/registerVoteEvent.json"))
    ret = registervote.lambda_handler(event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 500
    assert "success" in ret["body"]
    assert data["success"] == False

def test_register_vote_invalid_response():
    event = json.load(open("../../events/registerVoteEvent.json"))
    event["body"] = "{\"id\": \"" + environ['SamplePollId'] + "\", \"response\": \"Maybe\"}" 
    ret = registervote.lambda_handler(event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 500
    assert "success" in ret["body"]
    assert data["success"] == False

if __name__ == "__main__":
    environ['APP_STAGE'] = "local"
    environ['SamplePollId'] = add_a_sample_poll()
    pytest.main()