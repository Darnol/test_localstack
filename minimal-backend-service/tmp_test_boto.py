import os

os.chdir("./test-lambda")

import boto3
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

# Set env variables
os.environ['AWS_DEFAULT_REGION']='us-east-1'
os.environ['AWS_ENDPOINT_URL']='http://localhost.localstack.cloud:4566'
os.environ['AWS_ACCESS_KEY_ID']='fakecredentials'
os.environ['AWS_SECRET_ACCESS_KEY']='fakecredentials'

lambda_client = boto3.client("lambda")
function_name = "testlambda_function"

pp.pprint(lambda_client.list_functions())

# Tabula rasa, delete all lambda functions
for fct in lambda_client.list_functions()['Functions']:
    lambda_client.delete_function(FunctionName = fct['FunctionName'])

response_create = lambda_client.create_function(
    FunctionName = function_name,
    Role = "arn:aws:iam::000000000000:role/lambda-role",
    Handler = "handler.handler",
    Runtime = "python3.10",
    Code = {'ZipFile': open('./lambdas/test1/handler.zip', 'rb').read()}
)
pp.pprint(response_create)

response_create_url = lambda_client.create_function_url_config(
    FunctionName=function_name,
    AuthType='NONE'
)
pp.pprint(response_create_url)

pp.pprint(lambda_client.invoke(FunctionName = function_name))
lambda_client.invoke(FunctionName = function_name)['Payload'].readlines()



# DYNAMO

# Define the attributes and schema of the DB
DYNAMO_DB_CONFIG = {
    "TableName":'shopprofiles',
    "KeySchema":[
        {
            'AttributeName': 'shopemail',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'shoppassword',
            'KeyType': 'RANGE'
        }
    ],
    "AttributeDefinitions":[
        {
            'AttributeName': 'shopemail',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'shoppassword',
            'AttributeType': 'S'
        }
    ],
    "BillingMode":"PAY_PER_REQUEST"
}
FAKE_PROFILES = [
    {
        'shopemail':'shop_1_at_asdf',
        'shoppassword':'shop_1_password',
    },
    {
        'shopemail':'shop_2_at_asdf',
        'shoppassword':'shop_2_password',
    }
]

dynamo_resource = boto3.resource("dynamodb")
dynamo_resource.create_table(**DYNAMO_DB_CONFIG)

# Get the Table object
dynamo_table = dynamo_resource.Table("shopprofiles")
print(dynamo_table.creation_date_time)

# Put an item
dynamo_table.put_item(Item = FAKE_PROFILES[0])

# Retreive an item with wrong key -> Error
response_get = dynamo_table.get_item(Key = {'NONEXISTENTKEY':'shop_1_at_adsf', 'shoppassword':'shop_1_password'})

# Retreive an item with missing key -> Error
response_get = dynamo_table.get_item(Key = {'shopemail':'shop_1_at_adsf'})

# Retreive an item with a key that is not in the table -> Item does not exist, returns empty, but no error
response_get = dynamo_table.get_item(Key = {'shopemail':'TYPO_IN_KEY', 'shoppassword':'shop_1_password'})
pp.pprint(response_get)

# Retreive an item -> Success
response_get = dynamo_table.get_item(Key = {'shopemail':'shop_1_at_asdf', 'shoppassword':'shop_1_password'})
pp.pprint(response_get)