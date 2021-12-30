import json

def handler(event, context):
    
    print(event)
    
    return {
        'statusCode': 200,
        'body': json.dumps('This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.')
    }