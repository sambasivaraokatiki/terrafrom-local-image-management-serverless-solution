import base64, boto3, os, json

endpoint_url = os.environ.get('localstack_endpoint')
s3_bucket_name= os.environ.get('image_bucket_name')
dynamodb_table_name= os.environ.get('image_metadata_table_name')

s3 = boto3.client("s3", endpoint_url=endpoint_url)
dynamodb= boto3.client("dynamodb", endpoint_url=endpoint_url)
    
def handler(event,context):
    eventData=event['path'].split("/")
    operation=eventData[-2]
    imageName=eventData[-1]
    print(eventData)
    try:
        s3.head_object(Bucket=s3_bucket_name, Key=imageName)
        response = s3.get_object(Bucket=s3_bucket_name, Key=imageName)
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
        if e.response['Error']['Code'] == '404':
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'image file not found'})
            }
        else:
            # If there is an error other than 404, return a 500 response
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Error while getting image'})
            }