# to copy the file to a running container to run and run it right away
# run this from a terminal in the host machine, not a container
# docker cp test\test_services.py shopprofile-debugger:/app && docker exec shopprofile-debugger /bin/sh -c "python test_services.py"

import boto3
from botocore import response
import json
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

# Fetch the dynamo config
print("Try to load the DB schema ...")
try:
    with open("config/db_schema.json","r") as file:
        db_schema = json.load(file)
except FileNotFoundError:
    print("Did not find json file with db config")
DYNAMO_TABLE_NAME = db_schema['TableName']

# Create clients
lambda_client = boto3.client("lambda")
dynamo_resource = boto3.resource("dynamodb")
dynamo_table = dynamo_resource.Table(DYNAMO_TABLE_NAME)



###
# Test invoking list. list does not need payload
response_invoke = lambda_client.invoke(
    FunctionName = "list_shopprofiles",
    Payload = '{"asdf":"asdf"}'
)
# Parse the actual payload of the lambda function that was returned
pp.pprint(response_invoke)
print("--------------")
response_invoke = json.loads(response_invoke['Payload'].read())
pp.pprint(response_invoke)




# ###
# # Test invoking write. Needs an item to put
# # Test with invalid payload -> Returns a parsable error object
# response_invoke_write = lambda_client.invoke(
#     FunctionName = "write_shopprofile",
#     Payload = '{"asdf":"asdf"}'
# )
# # Parse the actual payload of the lambda function that was returned
# print("-------------")
# pp.pprint(response_invoke_write)
# # response_invoke_write = json.loads(response_invoke_write['Payload'].read())
# # pp.pprint(response_invoke_write)

# # Test with valid object
# response_invoke_write = lambda_client.invoke(
#     FunctionName = "write_shopprofile",
#     Payload = '{"shopemail":"asdfasdfasdfasdf", "shoppassword":"asdasdfasdfasdff"}'
# )
# # Parse the actual payload of the lambda function that was returned
# print("-------------")
# # pp.pprint(response_invoke_write)
# response_invoke_write = json.loads(response_invoke_write['Payload'].read())
# pp.pprint(response_invoke_write)






# # Test querying dynamo DB
# response_scan = dynamo_table.scan(TableName = "shopprofiles")
# pp.pprint(response_scan)

# # Test putting items to dynamo DB
# VALID_ITEM = {"shopemail":"asdfasdf", "shoppassword":"asdfasdf"}
# INVALID_ITEM = {"asdf":"asdfasdf", "shoppassword":"asdfasdf"}
# response_put_item = dynamo_table.put_item(
#     TableName = "shopprofiles",
#     ReturnValues = "ALL_OLD",
#     Item = INVALID_ITEM
#     # Item = {
#     #     "shopemail":"test1_shopemail_at_asdf",
#     #     "shoppassword":"test1_shoppassword"
#     # }
# )
# pp.pprint(response_put_item)

# # Scan table again
# response_scan = dynamo_table.scan(TableName = "shopprofiles")
# pp.pprint(response_scan)

# # Test querying dynamo DB
# response_get_item = dynamo_table.get_item(
#    Key = {
#         "shopemail":"test1_shopemail_at_asdf",
#         "shoppassword":"test1_shoppassword"
#    } 
# )
# pp.pprint(response_get_item['Item'])
