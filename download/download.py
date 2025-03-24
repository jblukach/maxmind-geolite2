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

    s3_client = boto3.client('s3')

    url = 'https://download.maxmind.com/geoip/databases/GeoLite2-ASN-CSV/download?suffix=zip'
    response = requests.get(url, auth=(account['Parameter']['Value'], secret['Parameter']['Value']))
    with open('/tmp/GeoLite2-ASN-CSV.zip', 'wb') as f:
        f.write(response.content)
    f.close()

    response = s3_client.upload_file('/tmp/GeoLite2-ASN-CSV.zip',os.environ['S3_BUCKET'],'GeoLite2-ASN-CSV.zip')

    url = 'https://download.maxmind.com/geoip/databases/GeoLite2-City-CSV/download?suffix=zip'
    response = requests.get(url, auth=(account['Parameter']['Value'], secret['Parameter']['Value']))
    with open('/tmp/GeoLite2-City-CSV.zip', 'wb') as f:
        f.write(response.content)
    f.close()

    response = s3_client.upload_file('/tmp/GeoLite2-City-CSV.zip',os.environ['S3_BUCKET'],'GeoLite2-City-CSV.zip')

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

    with zipfile.ZipFile('/tmp/geoip2.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:

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

    zipf.close()

    response = s3_client.upload_file('/tmp/geoip2.zip',os.environ['S3_BUCKET'],'geoip2.zip')

    client = boto3.client('lambda')

    response = client.update_function_code(
        FunctionName = os.environ['LAMBDA_FUNCTION'],
        S3Bucket = os.environ['S3_BUCKET'],
        S3Key = 'geoip2.zip'
    )

    token = ssm.get_parameter(
        Name = os.environ['SSM_PARAMETER_GIT'], 
        WithDecryption = True
    )

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer '+token['Parameter']['Value'],
        'X-GitHub-Api-Version': '2022-11-28'
    }

    year = datetime.datetime.now().strftime('%Y')
    month = datetime.datetime.now().strftime('%m')
    day = datetime.datetime.now().strftime('%d')
    epoch = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    data = '''{
        "tag_name":"v'''+str(year)+'''.'''+str(month)+str(day)+'''.'''+str(epoch)+'''",
        "target_commitish":"main",
        "name":"GeoLite2",
        "body":"This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.",
        "draft":false,
        "prerelease":false,
        "generate_release_notes":false
    }'''

    response = requests.post(
        'https://api.github.com/repos/jblukach/maxmind-geolite2/releases',
        headers=headers,
        data=data
    )

    print(response.json())

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'Bearer '+token['Parameter']['Value'],
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/octet-stream'
    }

    params = {
        "name":"GeoLite2.zip"
    }

    url = 'https://uploads.github.com/repos/jblukach/maxmind-geolite2/releases/'+str(response.json()['id'])+'/assets'

    with open('/tmp/geoip2.zip', 'rb') as f:
        data = f.read()
    f.close()

    response = requests.post(url, params=params, headers=headers, data=data)

    print(response.json())

    return {
        'statusCode': 200,
        'body': json.dumps('This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.')
    }