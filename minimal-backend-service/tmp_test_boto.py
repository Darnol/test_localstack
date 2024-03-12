import os
import re
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

def deploy_lambda(fct_name: str):
    """
    Wrapper to create a lambda function, assume tmp_handler.py file in root dir, consisting of handler function called handler
    Error if lambda function already exists
    """
    ZIP_NAME = "tmp_lambda.zip"
    # zip the lambda handler function file to create a deployment package
    with zipfile.ZipFile(ZIP_NAME, mode='w') as tmp:
        tmp.write("tmp_lambda.py")
    lambda_client.create_function(
        FunctionName = fct_name,
        Role = "arn:aws:iam::000000000000:role/lambda-role", # given by localstack
        Handler = "tmp_lambda.handler",
        Runtime = "python3.10",
        Code = {'ZipFile': open(ZIP_NAME, 'rb').read()}
        )
    
deploy_lambda(fct_name="lambda_test2")
 
def create_api(api_name: str):
    """
    Wrapper to create API Gateway
    """
    # Create the REST API
    apig_rest_api = apig_client.create_rest_api(name = api_name)
create_api("api_test2")

def add_lambda_integration(api_name: str, lambda_name: str, resource_path: str):
    """
    Wrapper to create an integration to a lambda function for a given api gateway
    """

    # Get API ID
    try:
        api_id = [x['id'] for x in apig_client.get_rest_apis()['items'] if x['name'] == api_name][0]
    except IndexError:
        raise ValueError(f"api {api_name} not found")

    # Get the ARN of the desired lambda function to integrate
    lambda_arn = [function_def['FunctionArn'] for function_def in lambda_client.list_functions()['Functions'] if function_def['FunctionName']==lambda_name][0]

    # Fetch all resources
    apig_resources = apig_client.get_resources(restApiId = api_id)
    
    # Add resource
    apig_new_resource = apig_client.create_resource(
        restApiId = api_id,
        parentId = apig_resources['items'][0]['id'],
        pathPart = resource_path
    )

    # Put a HTTP method to a resource
    apig_new_method = apig_client.put_method(
        restApiId = api_id,
        resourceId = apig_new_resource['id'],
        httpMethod = "GET", # The request to call a lambda function is always a GET?
        authorizationType = "NONE",
        apiKeyRequired = False
    )

    # Put an integration
    apig_new_integration = apig_client.put_integration(
        restApiId = api_id,
        resourceId = apig_new_resource['id'],
        httpMethod = "GET",
        type = "AWS_PROXY", # I think thats given if we use lambda
        integrationHttpMethod = "GET", # Must match the lambda function?
        uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
    )
    
    # TODO: Integration response aka what field should be returned from the lambda handler??

add_lambda_integration(api_name = "api_test2", lambda_name="lambda_test2", resource_path="testcall")

def deploy_api(api_name: str):
    """
    Deploy an api
    NOTE: stage_name is always equal to api_name
    """
    
    # Get API ID
    try:
        api_id = [x['id'] for x in apig_client.get_rest_apis()['items'] if x['name'] == api_name][0]
    except IndexError:
        raise ValueError(f"api {api_name} not found")
    
    # Deploy the API
    apig_deployment = apig_client.create_deployment(
        restApiId = api_id,
        stageName = api_name
    )

deploy_api(api_name = "api_test2")

# Ressrouce path id
api_id = [x['id'] for x in apig_client.get_rest_apis()['items'] if x['name'] == "api_test2"][0]
resource_path_id = [x['id'] for x in apig_client.get_resources(restApiId = api_id)['items'] if x.get('pathPart','') == "testcall"]

# Stage
api_deployment_ids = [x['id'] for x in apig_client.get_deployments(restApiId=api_id)['items']]
for deployment_id in api_deployment_ids:
    pp.pprint(apig_client.get_stages(restApiId = api_id, deploymentId=deployment_id))

def get_resource_path(api_name: str, resource_path: str) -> str:
    """
    According to localstack documentation build the url
    """ 
    url_base = "http://{api_id}.execute-api.{endpoint}/{stage_name}/{resource_path}"

    endpoint = os.environ['AWS_ENDPOINT_URL']
    # Strip protocol
    endpoint = re.sub(r"^.*\/\/","",endpoint)
    
    # Get API ID
    try:
        api_id = [x['id'] for x in apig_client.get_rest_apis()['items'] if x['name'] == api_name][0]
    except IndexError:
        raise ValueError(f"api {api_name} not found")
    
    # Get stage_name, which is ALWAYS equal to api_name
    stage_name = api_name

    # Check if resource_path exists
    res_found = False
    for res in [x for x in apig_client.get_resources(restApiId = api_id)['items']]:
        if res.get("pathPart","") == resource_path:
            res_found = True
            break
    if not res_found:
        raise ValueError(f"Did not find resource with path {resource_path}")

    url = url_base.format(
        api_id = api_id,
        endpoint = endpoint,
        stage_name = stage_name,
        resource_path = resource_path
    )

    return url

get_resource_path(api_name = "api_test2", resource_path="testcall")
copy(get_resource_path(api_name = "api_test2", resource_path="testcall"))
