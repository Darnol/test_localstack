from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

def handler(event, context):
    print("THIS IS THE EVENT\n")
    pp.pprint(event)
    print("-------------------")

    print("NOW WE PROCESS event\n")
    body = event['body']
    path_params = event['pathParameters']
    
    print("BODY\n")
    pp.pprint(body)
    
    print("PATHPARAMS\n")
    pp.pprint(path_params)

    return({
        "statusCode":200,
        "headers":{},
        "body":{
            "did i process?": "yes, I processed",
            "body of event": body,
            "path parameter": path_params    
        }
    })