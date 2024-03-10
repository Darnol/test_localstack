"""
Deploy one Dynamo DB
- shopprofiles with the following keys
    - shopemail
    - shoppassword

Deploy two lambda functions
- list_shopprofiles for listing all currently saved shop profile items
- write_shopprofile for writing a new shopprofile

NOT YET IMPLEMENTED:
- API Gateway
"""

import os
import zipfile
import boto3
from botocore import exceptions
import json

# FOR MANUAL RUNING ONLY
# os.chdir("./minimal-backend-service")
# Also set ENDPOINT_URL to the localhost container, if running manually
# os.environ['AWS_ENDPOINT_URL']='http://localstack:4566'

def get_db_config() -> dict[str]:
    """
    Retreive all configurations for the dynamo db
    """
    print("Try to load the DB schema ...")
    try:
        with open("config/db_schema.json","r") as file:
            db_schema = json.load(file)
    except FileNotFoundError:
        print("Did not find json file with db config")
    return db_schema

# Parameters
LAMBDA_FUNCTIONS_TO_DEPLOY = ["list_shopprofiles","write_shopprofile"]
LAMBDA_ROLE = "arn:aws:iam::000000000000:role/lambda-role" # given by localstack
db_schema = get_db_config()
DYNAMO_DB_NAME = db_schema['TableName']

# Set env variables - Should be given by docker-compose
CONFIG_ENV = {
    'AWS_DEFAULT_REGION' : 'us-east-1',
    'AWS_ENDPOINT_URL' : 'http://localhost.localstack.cloud:4566',
    'AWS_ACCESS_KEY_ID' : 'fakecredentials',
    'AWS_SECRET_ACCESS_KEY' : 'fakecredentials',
}
for env_var, env_value in CONFIG_ENV.items():
    try:
        print(f"{env_var} set to {os.environ[env_var]})")
    except KeyError:
        os.environ[env_var] = env_value

# Create clients
lambda_client = boto3.client("lambda")
dynamo_client = boto3.client("dynamodb")

###
# Dynamo DB deployment  
dynamo_client.create_table(**db_schema)
print("Dynamo DB created")


###
# Lambda deployment

# zip the lambda handler function file to create a deployment package
for lambda_function in LAMBDA_FUNCTIONS_TO_DEPLOY:
    with zipfile.ZipFile(f'lambdas/{lambda_function}/handler.zip', mode='w') as tmp:
        complete_file_path = f'lambdas/{lambda_function}/handler.py'
        tmp.write(complete_file_path, arcname=os.path.basename(complete_file_path))

# purge all lambda functions with the name we want to deploy, if it exists
# For error handling see here: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html#aws-service-exceptions
for lambda_function in LAMBDA_FUNCTIONS_TO_DEPLOY:
    try:
        lambda_client.delete_function(FunctionName = lambda_function)
    except exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f'Delete function {lambda_function}: function does not exist in the first place')
        else:
            raise error

# deploy the functions
for lambda_function in LAMBDA_FUNCTIONS_TO_DEPLOY:
    print(f"Deploying function {lambda_function} ...")
    response_create = lambda_client.create_function(
        FunctionName = lambda_function,
        Role = LAMBDA_ROLE,
        Handler = "handler.handler",
        Runtime = "python3.10",
        Code = {'ZipFile': open(f'./lambdas/{lambda_function}/handler.zip', 'rb').read()},
        # Pass the table name as environment variable
        Environment={
            'Variables': {"TableName" : db_schema['TableName']}
        },
    )
    # Create an URL to invoke
    response_create_url = lambda_client.create_function_url_config(
        FunctionName=lambda_function,
        AuthType='NONE'
    )
    print(response_create_url) # To print the URL we can invoke the function with
    # TODO: Print the URL to console for easier usability

    # Wait until the lambda is active
    lambda_client.get_waiter("function_active_v2").wait(FunctionName = lambda_function)

    # When ready, invoke the lambda function
    print("Waiting over, function is ready")

