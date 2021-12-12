import logging
import boto3
from botocore.exceptions import ClientError

def s3_list_buckets():
    s3 = boto3.client('s3')
    try:
        s3Response = s3.list_buckets()
    except ClientError as e:
        logging.error(e)
        return None
    return s3Response

def s3_upload_fileobj(file, s3BucketName, objectName):
    s3 = boto3.client('s3')
    try:
        s3Reseponse = s3.upload_fileobj(file, s3BucketName, objectName)
    except ClientError as e:
        logging.error(e)
        return None
    return s3Reseponse

def s3_presigned_url(s3BucketName, objectName):
    s3 = boto3.client('s3')
    try:
        presigned_url = s3.generate_presigned_url('get_object', Params = {'Bucket': s3BucketName, 'Key': objectName}, ExpiresIn = 3600)
    except ClientError as e:
        logging.error(e)
        return None
    return presigned_url

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
    
def rekognition_detect_text(s3BucketName, objectName):
    rekognition = boto3.client('rekognition', region_name='us-east-1')
    try:
        rekognitionResponse = rekognition.detect_text(
            Image={
                'S3Object': {
                    'Bucket': s3BucketName,
                    'Name': objectName
                }
        })
    except ClientError as e:
        logging.error(e)
        return None
    return rekognitionResponse

def parse_rekognition_response_receipt_text(rekognitionResponse, vendorNameList):
    
    receiptText = dict()

    isVendorName = False
    numTotal = 0
    isAmountTotal = False

    for text in rekognitionResponse['TextDetections']:
        print( text['Type'] + ' ' + text['DetectedText'].lower() + ' : ' + str(text['Confidence']))

        if numTotal == 1:
            numTotal = 2
        
        if not isVendorName:
            for vendorName in vendorNameList:
                if text['DetectedText'].lower() == vendorName.lower():
                    receiptText['vendorName'] = vendorName
                    isVendorName = True

        if numTotal == 0:
            if text['DetectedText'].lower() == 'total':
                numTotal = 1
        
        if numTotal == 2:
            numTotal = 0
            amountTotal = text['DetectedText'].lower().replace('eur', '')
            if amountTotal.replace('.', '').isnumeric():
                receiptText['amountTotal'] = float(amountTotal)
                isAmountTotal = True
        
        if isVendorName and isAmountTotal:
            break

    return receiptText
