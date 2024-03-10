import os

os.chdir("./minimal-backend-service")

import boto3
import zipfile
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

# Set env variables
os.environ['AWS_DEFAULT_REGION']='us-east-1'
os.environ['AWS_ENDPOINT_URL']='http://localhost.localstack.cloud:4566'
os.environ['AWS_ACCESS_KEY_ID']='fakecredentials'
os.environ['AWS_SECRET_ACCESS_KEY']='fakecredentials'

lambda_client = boto3.client("lambda")
apig_client = boto3.client("apigateway")

APIG_NAME = "apig_test"

# Deploy a lambda function
LAMBDA_FUNCTION_NAME = "list_shopprofiles"
LAMBDA_ROLE = "arn:aws:iam::000000000000:role/lambda-role" # given by localstack
with zipfile.ZipFile(f'lambdas/{LAMBDA_FUNCTION_NAME}/handler.zip', mode='w') as tmp:
    complete_file_path = f'lambdas/{LAMBDA_FUNCTION_NAME}/handler.py'
    tmp.write(complete_file_path, arcname=os.path.basename(complete_file_path))
response_create = lambda_client.create_function(
    FunctionName = LAMBDA_FUNCTION_NAME,
    Role = LAMBDA_ROLE,
    Handler = "handler.handler",
    Runtime = "python3.10",
    Code = {'ZipFile': open(f'./lambdas/{LAMBDA_FUNCTION_NAME}/handler.zip', 'rb').read()},
    # Pass the table name as environment variable
    Environment={
        'Variables': {"TableName" : "shopprofiles"}
    },
)

# Get the ARN of the desired lambda function to integrate
pp.pprint(lambda_client.list_functions())
lambda_arn = [function_def['FunctionArn'] for function_def in lambda_client.list_functions()['Functions'] if function_def['FunctionName']=="list_shopprofiles"][0]

# Create the REST API
apig_rest_api = apig_client.create_rest_api(name = APIG_NAME)
apig_id = apig_rest_api["id"]

# Fetch all resources
apig_resources = apig_client.get_resources(restApiId = apig_id)
pp.pprint(apig_resources)

# Add resource
apig_new_resource = apig_client.create_resource(
    restApiId = apig_id,
    parentId = apig_resources['items'][0]['id'],
    pathPart = "someresource"
)

# Put a HTTP method to a resource
apig_new_method = apig_client.put_method(
    restApiId = apig_id,
    resourceId = apig_new_resource['id'],
    httpMethod = "GET",
    authorizationType = "NONE",
    apiKeyRequired = False,
    operationName = "ListShopprofiles"
)
pp.pprint(apig_new_method)

# Put an integration
apig_new_integration = apig_client.put_integration(
    restApiId = apig_id,
    resourceId = apig_new_resource['id'],
    httpMethod = "GET",
    type = "AWS_PROXY",
    integrationHttpMethod = "GET",
    uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
)
pp.pprint(apig_new_integration)

# Deploy the API
apig_deployment = apig_client.create_deployment(
    restApiId = apig_id,
    stageName = APIG_NAME + "_deployment"
)
pp.pprint(apig_deployment)

apig_client.get_deployments(
    restApiId = apig_id
)

# Test - Create a url to curl
print(f"http://localhost.localstack.cloud:4566/restapis/{apig_id}/{APIG_NAME}/_user_request_/someresource")