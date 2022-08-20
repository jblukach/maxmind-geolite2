import base64
import boto3
import gzip
import json
import os

def handler(event, context):

    base64data = base64.b64decode(event['awslogs']['data'])
    gzipdata = gzip.decompress(base64data).decode()

    client = boto3.client('sns')

    response = client.publish(
        TopicArn = os.environ['SNS_TOPIC'],
        Subject = 'MaxMind GEOLite2 Error',
        Message = str(gzipdata)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('MaxMind GEOLite2 Error')
    }