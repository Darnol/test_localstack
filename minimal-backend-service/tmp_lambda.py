from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

def handler(event, context):
    print("THIS IS THE EVENT\n")
    pp.pprint(event)
    print("-------------------")

    print("NOW WE PROCESS event\n")
    body = event['body']
    query_string_params = event['queryStringParameters']

    print("BODY\n")
    pp.pprint(body)
    
    print("QUERYSTRINGPARAMS\n")
    pp.pprint(query_string_params)

    return({
        "statusCode":200,
        "headers":{},
        "body":{"processed":"yes processed"}
    })