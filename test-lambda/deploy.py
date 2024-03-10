import os
import zipfile
import boto3
from botocore import exceptions

# FOR MANUAL RUNING ONLY
# os.chdir("./test-lambda")

# Parameters
LAMBDA_FUNCITON_NAME = "test1"
LAMBDA_ROLE = "arn:aws:iam::000000000000:role/lambda-role" # given by localstack

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

# Create client
lambda_client = boto3.client("lambda")

# zip the lambda handler function file to create a deployment package
with zipfile.ZipFile(f'lambdas/{LAMBDA_FUNCITON_NAME}/handler.zip', mode='w') as tmp:
    complete_file_path = f'lambdas/{LAMBDA_FUNCITON_NAME}/handler.py'
    tmp.write(complete_file_path, arcname=os.path.basename(complete_file_path))

# purge all lambda functions with the name we want to deploy, if it exists
try:
    lambda_client.delete_function(FunctionName = LAMBDA_FUNCITON_NAME)
except exceptions.ClientError as error:
    if error.response['Error']['Code'] == 'ResourceNotFoundException':
        print(f'Delete funciton: function does not exist')
    else:
        raise error

# deploy a simple lambda function
response_create = lambda_client.create_function(
    FunctionName = LAMBDA_FUNCITON_NAME,
    Role = LAMBDA_ROLE,
    Handler = "handler.handler",
    Runtime = "python3.10",
    Code = {'ZipFile': open(f'./lambdas/{LAMBDA_FUNCITON_NAME}/handler.zip', 'rb').read()}
)
# Create an URL to invoke
response_create_url = lambda_client.create_function_url_config(
    FunctionName=LAMBDA_FUNCITON_NAME,
    AuthType='NONE'
)
print(response_create_url) # To print the URL we can invoke the function with

# Wait until the lambda is active
lambda_client.get_waiter("function_active_v2").wait(FunctionName = LAMBDA_FUNCITON_NAME)

# When ready, invoke the lambda function
print("Waiting over")
response_invocation = lambda_client.invoke(FunctionName = LAMBDA_FUNCITON_NAME)['Payload'].readlines()
print(response_invocation)
print("Invocation over")
