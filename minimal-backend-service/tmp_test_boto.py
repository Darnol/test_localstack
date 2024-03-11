import os
from pyperclip import copy

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

# Deploy a dummy lambda function
# zip the lambda handler function file to create a deployment package
with zipfile.ZipFile(f'dummy_lambda.zip', mode='w') as tmp:
    tmp.write("dummy_lambda.py")
lambda_client.create_function(
    FunctionName = "dummy_lambda",
    Role = "arn:aws:iam::000000000000:role/lambda-role", # given by localstack
    Handler = "dummy_lambda.handler",
    Runtime = "python3.10",
    Code = {'ZipFile': open('dummy_lambda.zip', 'rb').read()}
    )

# Get the ARN of the desired lambda function to integrate
pp.pprint(lambda_client.list_functions())
lambda_arn = [function_def['FunctionArn'] for function_def in lambda_client.list_functions()['Functions'] if function_def['FunctionName']=="dummy_lambda"][0]

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
    pathPart = "testcall"
)

# Put a HTTP method to a resource
apig_new_method = apig_client.put_method(
    restApiId = apig_id,
    resourceId = apig_new_resource['id'],
    httpMethod = "GET",
    authorizationType = "NONE",
    apiKeyRequired = False
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
    stageName = APIG_NAME
)
pp.pprint(apig_deployment)

apig_client.get_deployments(
    restApiId = apig_id
)

# Test - Create a url to curl
copy(f"http://{apig_id}.execute-api.localhost.localstack.cloud:4566/{APIG_NAME}/testcall")