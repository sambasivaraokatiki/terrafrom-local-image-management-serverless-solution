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
    eventData=event['path'].split("/")
    operation=eventData[1]
    imageName=eventData[2]
    try:
        # Download the image file from S3
        response = s3.get_object(Bucket=s3_bucket_name, Key=imageName)
         # Get the StreamingBody object from the response
        image_data = response['Body'].read()
        base64Encoded=False
        image_data,base64Encoded = base64.b64encode(image_data), True
        if operation=='view':
            http_response = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "image/"+imageName.split(".")[-1],
                    "Content-Disposition": "inline"
                },
                "body": image_data,
                "isBase64Encoded": base64Encoded
            }
        else:
            http_response = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "image/"+imageName.split(".")[-1],
                    "Content-Disposition": "attachment"
                },
                "body": image_data,
                "isBase64Encoded": base64Encoded
            }
        
        return http_response
    except Exception as e:
        print("Error:", e)
        return {
            "statusCode": 500,
            "body": "Internal Server Error"
        }