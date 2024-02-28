import boto3, json

endpoint_url = "https://localhost.localstack.cloud:4566"

s3 = boto3.client("s3", endpoint_url=endpoint_url)
dynamodb= boto3.client("dynamodb", endpoint_url=endpoint_url)

s3_bucket_name="montycloud-l2-storage"
dynamodb_table_name="montycloud_l2_file_metadata_table"

def searchDynamoDB(searchAttributeName=None,searchAttributeValue=None):
    try:
        if searchAttributeName is None or searchAttributeValue is None:
            response = dynamodb.scan(
                TableName='montycloud_l2_file_metadata_table'
            )
            items = response['Items']
            items={i['id']['S']:i['originalName']['S']+'.'+i['type']['S'] for i in items}
            return items
        response = dynamodb.scan(
            TableName='montycloud_l2_file_metadata_table',
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
    if body != None and body!='':
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
    
