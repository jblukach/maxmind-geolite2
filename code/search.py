import geoip2.database
import ipaddress
import json

def handler(event, context):

    print(event)

    try:

        ip = event['rawQueryString']
        iptype = ipaddress.ip_address(ip)

        with geoip2.database.Reader('GeoLite2-City.mmdb') as reader:
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
            desc = 'This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.'
        with geoip2.database.Reader('GeoLite2-ASN.mmdb') as reader2:
            response2 = reader2.asn(ip)
            asn = response2.autonomous_system_number
            org = response2.autonomous_system_organization
        code = 200
        msg = {
            'country':country_name,
            'c_iso':country_code,
            'state':state_name,
            's_iso':state_code,
            'city':city_name,
            'zip':zip_code,
            'latitude':latitude,
            'longitude':longitude,
            'cidr':str(cidr),
            'asn':asn,
            'org':org,
            'attribution':desc
        }
    except:
        code = 404
        msg = 'Where the Internet Ends'
        pass

    return {
        'statusCode': code,
        'body': json.dumps(msg, indent = 4)
    }