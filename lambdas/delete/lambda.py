import typing
import os
import base64, boto3

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

def handler(event,context):
    try:
        imageName=event['path'].split("/")[1]
        # Delete file from S3 bucket
        s3.delete_object(Bucket=s3_bucket_name, Key=imageName)
        
        # Delete item from DynamoDB
        dynamodb.delete_item(
            TableName=dynamodb,
            Key={
                'PartitionKey': {'S': imageName}
            }
        )
        
        return {
            "statusCode": 200,
            "body": "File deleted from S3 and item deleted from DynamoDB"
        }
    except Exception as e:
        print("Error:", e)
        return {
            "statusCode": 500,
            "body": "Internal Server Error"
        }