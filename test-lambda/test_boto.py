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