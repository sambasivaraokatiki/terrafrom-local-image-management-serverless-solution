import requests
import os, json
from PIL import Image, ImageChops
from io import BytesIO

serverURI = "http://obrtdl2eb3.execute-api.localhost.localstack.cloud:4566/dev"

def list_files_in_directory(directory):
    # List all files in the directory
    files = os.listdir(directory)
    return files

def compare_images(image_file_path, image_url):
    local_image = Image.open(image_file_path)
    response = requests.get(image_url)
    remote_image = Image.open(BytesIO(response.content))

    if local_image.size != remote_image.size:
        return False
    diff = ImageChops.difference(local_image, remote_image)
    if diff.getbbox() is None:
        return True
    else:
        return False
    
def uploadTest(filePath,fileName,fileType):
    url=serverURI+'/upload'
    payload = {}
    files=[
    ('file',(fileName,open(filePath+fileName,'rb'),fileType))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return response

def listSearchTest(name=None,value=None):
    url=serverURI+'/list_search'
    payload = json.dumps({
    "name": name,
    "value": value
    })
    headers = {
    'Content-Type': 'application/json'
    }
    if name==None or value==None or name == '' or value == '':
        response=requests.request("POST", url)
        return response
    else:
        response = requests.request("POST", url, headers=headers, data=payload)
        return response


def viewTest(imageName,originalName,localPath):
    url=serverURI+'/view-download/view/'+imageName
    return compare_images(localPath+'/'+originalName,url)


def downloadTest(imageName,originalName,localPath):
    url=serverURI+'/view-download/download/'+imageName
    return compare_images(localPath+'/'+originalName,url)

def deleteTest(imageName):
    url=serverURI+'/delete/'+imageName
    response=requests.request('GET',url=url)
    return response

if __name__ == "__main__":
    directory_path = 'test-images/'
    files = list_files_in_directory(directory_path)
    for eachFile in files:
        fileType='image/'+eachFile.split('.')[-1]
        print(uploadTest(directory_path,eachFile,fileType).content)
    
    name=input("enter attribute name to search: ")
    value=input("enter attribute value to search: ")
    listSearchResponse=json.loads(listSearchTest(name,value).content)

    for eachFileUploaded in listSearchResponse.keys():
        if viewTest(eachFileUploaded,listSearchResponse[eachFileUploaded],directory_path):
            print('image view test successfull for image: ',listSearchResponse[eachFileUploaded])

    for eachFileUploaded in listSearchResponse.keys():
        if downloadTest(eachFileUploaded,listSearchResponse[eachFileUploaded],directory_path):
            print('image download test successfull for image: ',listSearchResponse[eachFileUploaded])

    for eachFileUploaded in listSearchResponse.keys():
        response=json.loads(deleteTest(eachFileUploaded).content)
        print(response,': ',listSearchResponse[eachFileUploaded])