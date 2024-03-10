"""
Handle call which lists all shopprofiles
Returns a HTTP Response object, otherwise cannot work with API Gateway

The handler has the name of the table hardcoded, this is determined by the config file config/db_schema.json upon deployment
"""
import os
import boto3
import json
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

HTTP_RESPONSE_DICT = {
    'statusCode' : '',
    'headers' : {},
    'body' : '' # Returns a JSON as a string
}

def handler(event, context) -> list[dict]:
    
    print("list_shopprofiles invoked")

    try:
        TableName = os.environ["TableName"]
    except KeyError:
        print("env var TableName not found!")
        print(os.environ)

    print(f"Using table {TableName}")

    print("Creating dynamo table object ...")
    dynamo_resource = boto3.resource("dynamodb")
    dynamo_table = dynamo_resource.Table(TableName)

    print("Scanning table")
    response_scan = dynamo_table.scan(TableName = "shopprofiles")
    print(type(response_scan))
    pp.pprint(response_scan)
    
    print("Extracting items")
    body = json.dumps(response_scan['Items'])

    print("Return HTTP object")
    HTTP_RESPONSE_DICT['statusCode'] = '200'
    HTTP_RESPONSE_DICT['headers'] = {"Content-Type": "application/json"}
    HTTP_RESPONSE_DICT['body'] = body

    return HTTP_RESPONSE_DICT

if __name__ == "__main__":
    print(handler(None, None))
