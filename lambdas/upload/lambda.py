import typing
import os
import cgi,io, base64, boto3
import uuid

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

def saveToDynamoDB(fileDetails,file_name_in_s3):
    data = {
        'id': {'S': file_name_in_s3},
        'name': {'S': fileDetails[0].lower()},
        'originalName':{'S':fileDetails[0]},
        'type':{'S':fileDetails[1]}
    }
    table_name = dynamodb_table_name
    response = dynamodb.put_item(
        TableName=table_name,
        Item=data
    )
    print("Item saved successfully:", response)
    return None
    
def metaDataExtractor(filename):
    file_name_in_s3=None
    random_uuid = uuid.uuid4()
    fileDetails=filename.split(".")
    file_name_in_s3=str(random_uuid)+'.'+fileDetails[1]
    saveToDynamoDB(fileDetails,file_name_in_s3)
    return file_name_in_s3
    
def uploadFile(fileAbsPath,filename):
    file_name_in_s3=metaDataExtractor(filename)
    try:
        response = s3.upload_file(fileAbsPath, s3_bucket_name, file_name_in_s3)
    except Exception as e:
        print(e)
        return False
    return True

def save_file(file_item, save_directory):
    # Get the file name
    fileAbsPath = os.path.join(save_directory, file_item.filename)
    # Open the file in write mode
    with open(fileAbsPath, 'wb') as f:
        # Read the file data in chunks
        while True:
            chunk = file_item.file.read(8192)  # Read 8KB at a time
            if not chunk:
                break
            f.write(chunk)
    return uploadFile(fileAbsPath,file_item.filename)

def parseMultiPartFormData(fp,content_type):
    form = cgi.FieldStorage(fp=fp, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type})
    save_directory = '/tmp'  # Use Lambda's temporary directory
    for field in form.keys():
        field_item = form[field]
        if isinstance(field_item, cgi.FieldStorage):
            if field_item.file:
                saved_file = save_file(field_item, save_directory)
                return saved_file
    return False
    
def handler(event, context):
    try:
        # Get the multipart form data from the event
        print(event)
        body = event['body']
        fp = io.BytesIO(base64.b64decode(body))
        content_type_header = event['headers']['Content-Type']
        content_type, params = cgi.parse_header(content_type_header)
        if 'multipart/form-data' == content_type:
            if parseMultiPartFormData(fp,content_type_header):
                return {
                    'statusCode': 200,
                    'body': f"File saved to S3"
                }
            else:
                return {
                    'statusCode': 400,
                    'body': 'Error: No file uploaded.'
                }
        else:
            return {
                'statusCode': 400,
                'body': 'Error: Content type is not multipart/form-data.'
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }