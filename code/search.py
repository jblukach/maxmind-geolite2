import geoip2.database
import ipaddress
import json

def handler(event, context):

    print(event)

    ip = event['rawQueryString']

    try:

        ipaddr = ipaddress.ip_address(ip)
        multicast = ipaddr.is_multicast
        private = ipaddr.is_private
        unspecified = ipaddr.is_unspecified
        reserved = ipaddr.is_reserved
        loopback = ipaddr.is_loopback
        link_local = ipaddr.is_link_local
        version = ipaddress.ip_network(ip).version
        try:
            ipv4mapped = ipaddr.ipv4_mapped
            sixtofour = ipaddr.sixtofour
            teredo = ipaddr.teredo
        except:
            ipv4mapped = None
            sixtofour = None
            teredo = None

        try:
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

        try:
            with geoip2.database.Reader('GeoLite2-ASN.mmdb') as reader2:
                response2 = reader2.asn(ip)
                asn = response2.autonomous_system_number
                org = response2.autonomous_system_organization
                net = response2.network
        except:
            asn = None
            org = None
            net = None

        f = open('asn.updated', 'r')
        asnupdated = f.read()
        f.close()

        f = open('city.updated', 'r')
        cityupdated = f.read()
        f.close()

        desc = 'This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.'

        code = 200
        msg = {
            'ip':str(ipaddr),
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
            'net':str(net),
            'version':version,
            'multicast':multicast,
            'private':private,
            'unspecified':unspecified,
            'reserved':reserved,
            'loopback':loopback,
            'link_local':link_local,
            'ipv4_mapped':str(ipv4mapped),
            'sixtofour':str(sixtofour),
            'teredo':str(teredo),
            'attribution':desc,
            'geolite2-asn.mmdb':asnupdated,
            'geolite2-city.mmdb':cityupdated
        }

    except:
        code = 404
        msg = 'Invalid IP Address'
        pass

    return {
        'statusCode': code,
        'body': json.dumps(msg, indent = 4)
    }