import typing
import os
import boto3, json

if typing.TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_dynamodb import DynamoDBClient

endpoint_url = None
if os.getenv("STAGE") == "local":
    endpoint_url = "https://localhost.localstack.cloud:4566"

s3: "S3Client" = boto3.client("s3", endpoint_url=endpoint_url)
dynamodb: "DynamoDBClient"=boto3.client("dynamodb", endpoint_url=endpoint_url)

s3_bucket_name="montycloud_l2_storage"
dynamodb_table_name="montycloud_l2_file_metadata_table"

def searchDynamoDB(searchAttributeName=None,searchAttributeValue=None):
    try:
        if searchAttributeName is None or searchAttributeValue is None:
            response = dynamodb.scan(
                TableName='montycloud_l2'
            )
            items = response['Items']
            items={i['id']['S']:i['originalName']['S']+'.'+i['type']['S'] for i in items}
            return items
        response = dynamodb.scan(
            TableName='montycloud_l2',
            FilterExpression="contains (#attr, :val)",
            ExpressionAttributeNames={"#attr": searchAttributeName},
            ExpressionAttributeValues={":val": {"S": searchAttributeValue.lower()}}
        )
        items = response['Items']
        items={i['id']['S']:i['originalName']['S']+'.'+i['type']['S'] for i in items}
        return items
    except Exception as e:
        print("Error querying DynamoDB:", e)
        return None

def listImages(attribute):
    try:
        # List objects in the bucket
        response = s3.list_objects_v2(Bucket='sampleaccountresources')
        objects = response['Contents']
        objectsList=[]
        for obj in objects:
            objectsList.append(obj['Key'])
        if attribute==None:
            return objectsList
        return searchDynamoDB(attribute['name'],attribute['value'])
        
    except Exception as e:
        print("Error listing objects:", e)
        return None

def handler(event, context):
    print(event)
    body=event['body']
    if body != None:
        body=json.loads(body)
        if 'name' in body and 'value' in body:
            return {
                'statusCode': 200,
                'body':json.dumps(searchDynamoDB(body['name'],body['value']))
            }
        return {
            'statusCode': 200,
            'body':json.dumps(searchDynamoDB())
        }
    return {
            'statusCode': 200,
            'body':json.dumps(searchDynamoDB())
        }
    
