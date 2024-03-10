"""
Handle call which lists all shopprofiles
Returns a list with a dict per profile returned

The handler has the name of the table hardcoded, this is determined by the config file config/db_schema.json upon deployment
"""
import os
import boto3

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
    return(response_scan)

if __name__ == "__main__":
    print(handler(None, None))
