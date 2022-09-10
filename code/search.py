import boto3
import geoip2.database
import ipaddress
import json
import os

def handler(event, context):

    try:
        ipaddr = event['item']
        iptype = ipaddress.ip_address(ipaddr)
        with geoip2.database.Reader('GeoLite2-City.mmdb') as reader:
            response = reader.city(ipaddr)
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
            response2 = reader2.asn(ipaddr)
            asn = response2.autonomous_system_number
            org = response2.autonomous_system_organization
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
        msg = {"RequiredFormat": {"item": "134.129.111.111"}}
        pass

    return {
        'statusCode': 200,
        'body': json.dumps(msg)
    }