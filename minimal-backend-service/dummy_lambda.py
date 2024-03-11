def handler(event, context):
    print(event)
    return({
        "statusCode":200,
        "headers":{},
        "body":"THISISTHEBODY"
    })