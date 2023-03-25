import boto3
import json
import os
import requests
import tarfile
import zipfile

def handler(event, context):

    ssm = boto3.client('ssm')

    secret = ssm.get_parameter(
        Name = os.environ['SSM_PARAMETER'], 
        WithDecryption = True
    )

    url = 'https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key='+secret['Parameter']['Value']+'&suffix=tar.gz'
    response = requests.get(url)  
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

    url = 'https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN&license_key='+secret['Parameter']['Value']+'&suffix=tar.gz'
    response = requests.get(url)  
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

    os.system('cd /tmp && python3 -m pip install --target=./ geoip2 --upgrade')
    os.system('cd /tmp && python3 -m pip install --target=./ maxminddb --upgrade')

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

    return {
        'statusCode': 200,
        'body': json.dumps('This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.')
    }