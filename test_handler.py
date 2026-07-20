# test_handler.py
import boto3
from moto import mock_aws
import os

@mock_aws
def test_lambda():
    # Set up fake SSM parameters
    ssm = boto3.client('ssm', region_name='us-east-1')
    ssm.put_parameter(Name='RecipientCell', Value='+15555555555', Type='String')
    ssm.put_parameter(Name='RecipientEmail', Value='you@example.com', Type='String')
    ssm.put_parameter(Name='SenderEmail', Value='sender@gmail.com', Type='String')
    ssm.put_parameter(Name='SenderEmailAppPassword', Value='dummy-app-password', Type='SecureString')

    # Set up fake DynamoDB table
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    dynamodb.create_table(
        TableName='flight_pricing',
        KeySchema=[{'AttributeName': 'flight', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'flight', 'AttributeType': 'N'}],
        BillingMode='PAY_PER_REQUEST'
    )

    os.environ['FLIGHT1'] = '1234'
    os.environ['URL1'] = 'https://www.google.com/travel/flights/booking?tfs=CBwQAhpFEgoyMDI2LTA4LTA0Ih8KA0xHQRIKMjAyNi0wOC0wNBoDREZXKgJETDIDODU2ag0IAhIJL20vMDJfMjg2cgcIARIDREZXQAFIAXABggELCP___________wGYAQI&tfu=CmxDalJJTTFWdlVIRmpjMncxYlVGQlQyVlBXR2RDUnkwdExTMHRMUzB0TFhscGJISXhNRUZCUVVGQlIzQmtaMjQwVEhRM1VGVkJFZ1ZFVERnMU5ob0xDTnp4QVJBQ0dnTlZVMFE0SEhEYzhRRT0SAggAIgA&hl=en'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

    from lambda_function import lambda_handler
    result = lambda_handler({}, {})
    print(result)

test_lambda()