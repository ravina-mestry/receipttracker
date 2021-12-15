import logging
import boto3
import json
from botocore.exceptions import ClientError

# This file contains all the aws functions using boto3.

# s3_list_buckets function returns the list of buckets in s3 for the aws account
def s3_list_buckets():
    s3 = boto3.client('s3')
    try:
        s3Response = s3.list_buckets()
    except ClientError as e:
        logging.error(e)
        return None
    return s3Response

# s3_upload_fileobj function uploads the file object to s3 with specified bucket name and object name
def s3_upload_fileobj(file, s3BucketName, objectName):
    s3 = boto3.client('s3')
    try:
        s3Reseponse = s3.upload_fileobj(file, s3BucketName, objectName)
    except ClientError as e:
        logging.error(e)
        return None
    return s3Reseponse

# s3_presigned_url function returns a secure presigned url to grant time-limited permission to download the object without making them public
def s3_presigned_url(s3BucketName, objectName):
    s3 = boto3.client('s3')
    try:
        presigned_url = s3.generate_presigned_url('get_object', Params = {'Bucket': s3BucketName, 'Key': objectName}, ExpiresIn = 3600)
    except ClientError as e:
        logging.error(e)
        return None
    return presigned_url

# textract_analyze_expense function returns textract response for detect_document_text for the specified object name in specified s3 bucket
def textract_analyze_expense(s3BucketName, objectName):
    textract = boto3.client('textract')
    try:
        textractResponse = textract.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': s3BucketName,
                    'Name': objectName
                }
        })
    except ClientError as e:
        logging.error(e)
        return None
    return textractResponse

# rekognition_detect_text function returns rekognition response for detect_text for the specified object name in specified s3 bucket
# it also converts rekognition response into json format and stores on s3 bucket.
def rekognition_detect_text(s3BucketName, objectName):
    rekognition = boto3.client('rekognition', region_name='us-east-1')
    s3 = boto3.client('s3')
    try:
        rekognitionResponse = rekognition.detect_text(
            Image={
                'S3Object': {
                    'Bucket': s3BucketName,
                    'Name': objectName
                }
        })
        
        s3.put_object(Body=json.dumps(rekognitionResponse).encode(), Bucket=s3BucketName, Key=objectName + '-rekognitionresponse.json')
    except ClientError as e:
        logging.error(e)
        return None
    return rekognitionResponse
