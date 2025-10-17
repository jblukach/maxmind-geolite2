import geoip2.database
import boto3
import ipaddress
import json

def handler(event, context):

    print(event)

    ip = event['rawQueryString']

    try:

        ipaddr = ipaddress.ip_address(ip)
        code = 200

        data = {}
        data['ip'] = ip
        data['geo'] = []
        data['asn'] = []
        data['attribution'] = 'This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.'

        s3 = boto3.client('s3')

        objects = s3.list_objects(
            Bucket = 'maxmindgeolite2archive',
        )

        for key in objects['Contents']:

            fname = key['Key'].split('/')[4]

            if fname == 'GeoLite2-ASN.mmdb':

                s3path = '/'.join(key['Key'].split('/')[:-1])
                s3.download_file('maxmindgeolite2archive', s3path+'/asn.updated', '/tmp/asn.updated')
                s3.download_file('maxmindgeolite2archive', key['Key'], '/tmp/'+fname)

                f = open('/tmp/asn.updated', 'r')
                updated = f.read()
                f.close()

                try:
                    with geoip2.database.Reader('/tmp/GeoLite2-ASN.mmdb') as reader2:
                        response2 = reader2.asn(ip)
                        asn = response2.autonomous_system_number
                        org = response2.autonomous_system_organization
                        net = response2.network
                except:
                    asn = None
                    org = None
                    net = None

                tmp = {
                    'id': asn,
                    'org': org,
                    'net': str(net),
                    'updated': updated
                }

                data['asn'].append(tmp)

            elif fname == 'GeoLite2-City.mmdb':

                s3path = '/'.join(key['Key'].split('/')[:-1])
                s3.download_file('maxmindgeolite2archive', s3path+'/city.updated', '/tmp/city.updated')
                s3.download_file('maxmindgeolite2archive', key['Key'], '/tmp/'+fname)

                f = open('/tmp/city.updated', 'r')
                updated = f.read()
                f.close()

                try:
                    with geoip2.database.Reader('/tmp/GeoLite2-City.mmdb') as reader:
                        response = reader.city(ip)
                        country_code = response.country.iso_code
                        country_name = response.country.name
                        state_code = response.subdivisions.most_specific.iso_code
                        state_name = response.subdivisions.most_specific.name
                        city_name = response.city.name
                        zip_code = response.postal.code
                        latitude = response.location.latitude
                        longitude = response.location.longitude
                        cidr = response.traits.network
                except:
                    country_code = None
                    country_name = None
                    state_code = None
                    state_name = None
                    city_name = None
                    zip_code = None
                    latitude = None
                    longitude = None
                    cidr = None

                tmp = {
                    'country':country_name,
                    'c_iso':country_code,
                    'state':state_name,
                    's_iso':state_code,
                    'city':city_name,
                    'zip':zip_code,
                    'latitude':latitude,
                    'longitude':longitude,
                    'cidr':str(cidr),
                    'updated': updated
                }

                data['geo'].append(tmp)

    except:
        code = 404
        data = 'Invalid IP Address'
        pass

    return {
        'statusCode': code,
        'body': json.dumps(data, indent = 4)
    }