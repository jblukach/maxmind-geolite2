# maxmind-geolite2

GeoLite2 databases are free IP geolocation databases from MaxMind that contain Country, City, and ASN information, updated every Tuesday.

https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

MaxMind-GeoLite2 provides AWS Chatbot integration with Slack Channels for geolocation lookups.

```
@aws invoke geo --payload {"ip": "134.129.111.111”}
```

or

```
https://geo.tundralabs.net/134.129.111.111
```

This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.
