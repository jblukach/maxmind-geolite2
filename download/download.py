import boto3
import datetime
import json
import os
import requests
import tarfile
import zipfile

def handler(event, context):

    ssm = boto3.client('ssm')

    account = ssm.get_parameter(
        Name = os.environ['SSM_PARAMETER_ACCT'], 
        WithDecryption = True
    )

    secret = ssm.get_parameter(
        Name = os.environ['SSM_PARAMETER_KEY'], 
        WithDecryption = True
    )

    url = 'https://download.maxmind.com/geoip/databases/GeoLite2-City/download?suffix=tar.gz'
    response = requests.get(url, auth=(account['Parameter']['Value'], secret['Parameter']['Value']))
    with open('/tmp/maxmind.tar.gz', 'wb') as f:
        f.write(response.content)
    f.close()

    with open('/tmp/GeoLite2-City.mmdb', 'wb') as w:
        with tarfile.open('/tmp/maxmind.tar.gz', 'r:gz') as tar:
            for member in tar.getmembers():
                if os.path.splitext(member.name)[1] == '.mmdb':
                    r = tar.extractfile(member)
                    if r is not None:
                        content = r.read()
                    r.close
                    w.write(content)
        tar.close()
    w.close()

    s3_client = boto3.client('s3')

    response = s3_client.upload_file('/tmp/GeoLite2-City.mmdb',os.environ['S3_BUCKET'],'GeoLite2-City.mmdb')

    url = 'https://download.maxmind.com/geoip/databases/GeoLite2-ASN/download?suffix=tar.gz'
    response = requests.get(url, auth=(account['Parameter']['Value'], secret['Parameter']['Value']))
    with open('/tmp/maxmind2.tar.gz', 'wb') as f:
        f.write(response.content)
    f.close()

    with open('/tmp/GeoLite2-ASN.mmdb', 'wb') as w:
        with tarfile.open('/tmp/maxmind2.tar.gz', 'r:gz') as tar:
            for member in tar.getmembers():
                if os.path.splitext(member.name)[1] == '.mmdb':
                    r = tar.extractfile(member)
                    if r is not None:
                        content = r.read()
                    r.close
                    w.write(content)
        tar.close()
    w.close()

    response = s3_client.upload_file('/tmp/GeoLite2-ASN.mmdb',os.environ['S3_BUCKET'],'GeoLite2-ASN.mmdb')

    with open('/tmp/search.py', 'wb') as f:
        s3_client.download_fileobj(os.environ['S3_BUCKET'], 'search.py', f) 
    f.close()

    with zipfile.ZipFile('/tmp/geoip2.zip', 'w') as zipf:

        zipf.write('/tmp/search.py','search.py')
        zipf.write('/tmp/GeoLite2-ASN.mmdb','GeoLite2-ASN.mmdb')
        zipf.write('/tmp/GeoLite2-City.mmdb','GeoLite2-City.mmdb')

        for root, dirs, files in os.walk('/tmp/geoip2'):
            for file in files:
                fullpath = os.path.join(root, file)
                zipf.write(fullpath, fullpath[5:])

        for root, dirs, files in os.walk('/tmp/maxminddb'):
            for file in files:
                fullpath = os.path.join(root, file)
                zipf.write(fullpath, fullpath[5:])

    response = s3_client.upload_file('/tmp/geoip2.zip',os.environ['S3_BUCKET'],'geoip2.zip')

    client = boto3.client('lambda')

    response = client.update_function_code(
        FunctionName = os.environ['LAMBDA_FUNCTION'],
        S3Bucket = os.environ['S3_BUCKET'],
        S3Key = 'geoip2.zip'
    )

    f = open('/tmp/maxmind.updated','w')
    f.write(str(datetime.datetime.now()))
    f.close()

    s3 = boto3.resource('s3')

    s3.meta.client.upload_file(
        '/tmp/maxmind.updated',
        'static.tundralabs.net',
        'maxmind.updated',
        ExtraArgs = {
            'ContentType': "text/plain"
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps('This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.')
    }