def handler(event, context):
    print("THIS IS THE EVENT\n")
    print(event)
    print("-------------------")

    print("NOW WE PROCESS event\n")
    body = event['body']
    url_params = event['queryStringParameters']

    return({
        "statusCode":200,
        "headers":{},
        "body":{"key1":"value1"}
    })