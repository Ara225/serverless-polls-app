# polls-app-backend
## API 
### /addpoll 
##### Body Validation schema
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
##### Returns
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

### /getpolls
Either get all the polls (with primitive pagination using the continueKey returned and the request parameter limit), or a
single poll
##### Query params
* id - ID of the pool
* limit - the amount of polls to get with this request
* continueKey - The continueKey the API returned with the last request, to get the next keys
##### Returns
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

## Deploy
```bash
sam build --use-container
sam deploy --guided
```