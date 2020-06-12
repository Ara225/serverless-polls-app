# polls-app-backend
## API 
### /addpoll 
##### Body Validation schema
```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Poll",
    "type": "object",
    "properties": {
        "question": {
            "description": "The poll question",
            "type": "string"
        },
        "answersList": {
            "description": "List of answers",
            "type": "array",
            "minItems": 2,
            "uniqueItems": true
        },
        "expiresIn": {
            "description": "Days poll will run for",
            "type": "integer",
            "maximum": 90
        }
    },
    "required": ["question", "answersList"]
}
```
##### Sample Request
```bash
curl http://endpoint_url/addpoll --data "{'question': 'What?', 'answersList': ['Yes', 'No']}" -H 'Content-Type: application/json'
```

##### Query params
None
##### Returns
```json
{
    "success": true, 
    "polls": {
          "id": "dA735dLfjdrGbP3WvFisTZioOIHw8SHK", 
          "question": "blah", 
          "answersList": ["blah", "blah2"],
          "responses": {"blah": 0, "blah2": 0}, 
          "created": "2020-06-11T19:53:46.967607", 
          "expires": "2020-07-11T19:53:46.967510"
    }
}
```
### /getpolls
Either get all the polls (with primitive pagination using the continueKey returned and the request parameter limit), or a
single poll
##### Sample Request
All polls (unless DB truncates request)
```bash
curl http://endpoint_url/getpolls
```
Get 50 polls
```bash
curl http://endpoint_url/getpolls?limit=1
```
```bash
curl http://endpoint_url/getpolls?
```
##### Query params
* id - ID of the pool
* limit - the amount of polls to get with this request
* continueKey - The continueKey the API returned with the last request, to get the next keys
##### Returns
```json
{
    "success": true,
    "polls": [{
        "id": "dA735dLfjdrGbP3WvFisTZioOIHw8SHK", 
        "question": "blah", 
        "answersList": ["blah", "blah2"],
        "responses": {"blah": 0, "blah2": 0}, 
        "created": "2020-06-11T19:53:46.967607", 
        "expires": "2020-07-11T19:53:46.967510"
    }],
    "continueKey": { "id": "key" }
}
```

### /registervote
Register vote for a poll in the DB
##### Sample Request 


##### Query params
None


## Test Locally

#### Create the dynamoDB container
Assuming you're in the project folder:
```bash
cd ./sam-local-resources
docker-compose up -d dynamo
```
(docker-compose.yml taken from [rynop's answer on StackOverflow](https://stackoverflow.com/questions/48926260/connecting-aws-sam-local-with-dynamodb-in-docker))

#### Create the table 
```bash
aws dynamodb create-table --cli-input-json file://local-db-create.json --endpoint-url http://localhost:8000
```
#### Run API locally via SAM
Code detects that it's being run locally and calls the local DB instead of one in AWS
```bash
cd ..
sam build --use-container
sam local start-api --docker-network abp-sam-backend --skip-pull-image --profile default --parameter-overrides 'ParameterKey=StageName,ParameterValue=local'
```

## Deploy
```bash
sam build --use-container
sam deploy --guided
```