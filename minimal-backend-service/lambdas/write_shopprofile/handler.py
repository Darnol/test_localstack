"""
Handle call which writes an item to the shopprofiles DB
Return an answer object according to put_item
If an error occurs within the handler (not wrong parameters for the lambda invocation itself), 200 is returned and an object that contains the error description
- This handler does not handle that but simply returns the object

TODO: Error handling (either let handler function fail, or wrap?), duplicates?

The handler has the name of the table hardcoded, this is determined by the config file config/db_schema.json upon deployment
"""
import os
import boto3

# TODO: Remove later
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

def handler(event: dict, context):
    """
    event is a dict which contains the payload
    It is passed as is as the Item, assuming that the invoking entity specified all neccessary fields in the DB
    If a field is missing, the handler will throw an error which will be returned as an error object
    """
    
    print("write_shopprofile invoked")
    
    try:
        TableName = os.environ["TableName"]
    except KeyError:
        print("env var TableName not found!")
        print(os.environ)

    print(f"Using table {TableName}")

    print("Creating dynamo table object ...")
    dynamo_resource = boto3.resource("dynamodb")
    dynamo_table = dynamo_resource.Table(TableName)

    print("Try writing item")
    response_put = dynamo_table.put_item(
        TableName = TableName,
        ReturnValues = "ALL_OLD",
        Item = event
    )
    return(response_put)

if __name__ == "__main__":
    print(handler(None, None))
