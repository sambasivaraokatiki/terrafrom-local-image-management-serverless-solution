import base64, boto3

endpoint_url = "https://localhost.localstack.cloud:4566"

s3 = boto3.client("s3", endpoint_url=endpoint_url)
dynamodb= boto3.client("dynamodb", endpoint_url=endpoint_url)

s3_bucket_name="montycloud-l2-storage"
dynamodb_table_name="montycloud_l2_file_metadata_table"
    
def handler(event,context):
    eventData=event['path'].split("/")
    operation=eventData[-2]
    imageName=eventData[-1]
    print(eventData)
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
        print(http_response)
        return http_response
    except Exception as e:
        print("Error:", e)
        return {
            "statusCode": 500,
            "body": "Internal Server Error"
        }