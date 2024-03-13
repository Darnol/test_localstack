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
    response_lambda_create = lambda_client.create_function(
        FunctionName = fct_name,
        Role = "arn:aws:iam::000000000000:role/lambda-role", # given by localstack
        Handler = "tmp_lambda.handler",
        Runtime = "python3.10",
        Code = {'ZipFile': open(ZIP_NAME, 'rb').read()}
        )
    return response_lambda_create['FunctionArn']
    
def create_api(api_name: str):
    """
    Wrapper to create API Gateway
    """
    # Create the REST API
    apig_rest_api = apig_client.create_rest_api(name = api_name)
    return apig_rest_api

def create_resource(api_id: str, parent_id: str, resource_path: str) -> str:
    """
    Wrapper for creating a resource

    Arguments:
        api_id : ID of the API to create the resource in
        parent_id : ID of the resource that the resource_path is appended to. If None defaults to root
        resource_path : The 'unique' part of the path that will be appended to parent_id path

    Return:
        id of resource created
    """

    # Check API ID
    if not api_id in [x['id'] for x in apig_client.get_rest_apis()['items']]:
        raise ValueError(f"api {api_id} not found")
    
    # Check parent_id
    if not parent_id:
        # Use root if nothing is specified
        parent_id = [res['id'] for res in apig_client.get_resources(restApiId = api_id)['items']][0]
    elif not parent_id in [res['id'] for res in apig_client.get_resources(restApiId = api_id)['items']]:
        raise ValueError(f"parent resource id {parent_id} not found")
    
    # Add resource
    apig_new_resource = apig_client.create_resource(
        restApiId = api_id,
        parentId = parent_id,
        pathPart = resource_path
    )
    
    return apig_new_resource['id']

def add_lambda_method_and_integration_to_resource(api_id: str, resource_id: str, lambda_arn: str, method: str):
    """
    Wrapper to add a method to an existing resource
    """

    # Check API ID
    if not api_id in [x['id'] for x in apig_client.get_rest_apis()['items']]:
        raise ValueError(f"api {api_id} not found")
    
    # Check resource_id
    if not resource_id in [res['id'] for res in apig_client.get_resources(restApiId = api_id)['items']]:
        raise ValueError(f"resource id {resource_id} not found")

    # Get the ARN of the desired lambda function to integrate
    if not lambda_arn in [function_def['FunctionArn'] for function_def in lambda_client.list_functions()['Functions']]:
        raise ValueError(f"lambda arn {lambda_arn} not found")

    # Put a HTTP method to a resource
    apig_new_method = apig_client.put_method(
        restApiId = api_id,
        resourceId = resource_id,
        httpMethod = method,
        authorizationType = "NONE",
        apiKeyRequired = False
    )

    # NOTE: query string parameters ( a la /getsomething?param=1) is NOT SUPPORTED by boto3

    # Put an integration
    apig_new_integration = apig_client.put_integration(
        restApiId = api_id,
        resourceId = resource_id,
        httpMethod = method,
        type = "AWS_PROXY", # I think thats given if we use lambda
        integrationHttpMethod = "POST", # I think this is always POST, we forward the request to the lambda function
        uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
    )

    return apig_new_method, apig_new_integration

def deploy_api(api_id: str):
    """
    Deploy an api
    NOTE: stage_name is always equal to "PROD"
    """
    
    # Check API ID
    if not api_id in [x['id'] for x in apig_client.get_rest_apis()['items']]:
        raise ValueError(f"api {api_id} not found")
    
    # Deploy the API
    apig_deployment = apig_client.create_deployment(
        restApiId = api_id,
        stageName = "PROD"
    )

    return apig_deployment

def get_resource_path(api_id: str, resource_path: str) -> str:
    """
    According to localstack documentation build the url
    """ 
    url_base = "http://{api_id}.execute-api.{endpoint}/{stage_name}{resource_path}"

    endpoint = os.environ['AWS_ENDPOINT_URL']
    # Strip protocol
    endpoint = re.sub(r"^.*\/\/","",endpoint)
    
    # Check API ID
    if not api_id in [x['id'] for x in apig_client.get_rest_apis()['items']]:
        raise ValueError(f"api {api_id} not found")
    
    # Get stage_name, which is ALWAYS equal to PROD
    stage_name = "PROD"

    url = url_base.format(
        api_id = api_id,
        endpoint = endpoint,
        stage_name = stage_name,
        resource_path = resource_path
    )

    return url




###
# Deploy
tag_to_use = "4"
lambda_arn = deploy_lambda(fct_name=f"lambda_test_{tag_to_use}")

paths_and_methods_to_create = {
    'getSomething' : [
        {"path":"getSomething", "method":"GET", "lambda_arn":lambda_arn},
        {"path":"{getSomething_id}", "method":"GET", "lambda_arn":lambda_arn},
    ],
    'postSomething' : [
        {"path":"postSomething", "method":"POST", "lambda_arn":lambda_arn},
    ]
}

response_create_api = create_api(f"api_test_{tag_to_use}")
pp.pprint(response_create_api)
api_id = response_create_api['id']

# Create resources, for each elemetn in paths_and_methods_to_create
# Each element contains a tuple with PATH,METHOD,LAMBDA_ARN
# Each subsequent tuple uses the newly created resource of the previous as parent resource

for resource_type, resource_list in paths_and_methods_to_create.items():
    print(f"create {resource_type} ... ")
    for i,resource_tuple in enumerate(resource_list):
        if i == 0:
            tmp_parent_res_id = None
        tmp_parent_res_id = create_resource(api_id = api_id, parent_id = tmp_parent_res_id, resource_path=resource_tuple['path'])
        resource_tuple['resource_id'] = tmp_parent_res_id
        _,_ = add_lambda_method_and_integration_to_resource(api_id = api_id, resource_id=tmp_parent_res_id, lambda_arn = resource_tuple['lambda_arn'], method = resource_tuple['method'])

response_deploy_api = deploy_api(api_id = api_id)

# Now generate URLs
copy(get_resource_path(api_id = api_id , resource_path="/getSomething/1"))



