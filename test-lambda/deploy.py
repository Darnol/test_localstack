import os
import zipfile
import boto3

# # Set env variables - Should be given by docker-compose
# os.environ['AWS_DEFAULT_REGION']='us-east-1'
# os.environ['AWS_ENDPOINT_URL']='http://localhost.localstack.cloud:4566'
# os.environ['AWS_ACCESS_KEY_ID']='fakecredentials'
# os.environ['AWS_SECRET_ACCESS_KEY']='fakecredentials'

lambda_client = boto3.client("lambda")

lambda_function_name = "test1"

# zip the lambda handler function file to create a deployment package
with zipfile.ZipFile(f'lambdas/{lambda_function_name}/handler.zip', mode='w') as tmp:
    complete_file_path = f'lambdas/{lambda_function_name}/handler.py'
    tmp.write(complete_file_path, arcname=os.path.basename(complete_file_path))

# deploy a simple lambda function
response_create = lambda_client.create_function(
    FunctionName = lambda_function_name,
    Role = "arn:aws:iam::000000000000:role/lambda-role",
    Handler = "handler.handler",
    Runtime = "python3.10",
    Code = {'ZipFile': open(f'./lambdas/{lambda_function_name}/handler.zip', 'rb').read()}
)
# Create an URL to invoke
response_create_url = lambda_client.create_function_url_config(
    FunctionName=lambda_function_name,
    AuthType='NONE'
)
print(response_create_url)

# lambda_client.invoke(FunctionName = lambda_function_name)['Payload'].readlines()
