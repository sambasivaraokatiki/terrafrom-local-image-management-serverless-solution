import boto3, json

endpoint_url = "https://localhost.localstack.cloud:4566"

s3 = boto3.client("s3", endpoint_url=endpoint_url)
dynamodb= boto3.client("dynamodb", endpoint_url=endpoint_url)

s3_bucket_name="montycloud-l2-storage"
dynamodb_table_name="montycloud_l2_file_metadata_table"

def handler(event,context):
    try:
        imageName=event['path'].split("/")[-1]
        # Delete file from S3 bucket
        s3.delete_object(Bucket=s3_bucket_name, Key=imageName)
        
        # Delete item from DynamoDB
        dynamodb.delete_item(
            TableName=dynamodb_table_name,
            Key={
                'id': {'S': imageName}
            }
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps("File deleted from S3 and item deleted from DynamoDB")
        }
    except Exception as e:
        print("Error:", e)
        return {
            "statusCode": 500,
            "body": "Internal Server Error"
        }