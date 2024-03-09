# # Check that AWS_ENDPOINT_URL is set to ping the localstack container
# if not os.getenv("AWS_ENDPOINT_URL"):
#     raise ValueError("AWS_ENDPOINT_URL not set in environment")
# endpoint_url = "https://localhost.localstack.cloud:4566"

def handler(event, context):
    return {'return_message' : "function invoked"}

if __name__ == "__main__":
    print(handler(None, None))
