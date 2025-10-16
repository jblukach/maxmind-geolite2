# IP Intelligence Enrichment with GeoLite2 Databases and Python’s `ipaddress` Library

## Overview

The **GeoLite2** databases (by **MaxMind**) and Python’s **`ipaddress`** module together provide a complete framework for **IP enrichment and intelligence**.  

- **GeoLite2-City.mmdb**: Adds *geographic context* — where an IP is located.  
- **GeoLite2-ASN.mmdb**: Adds *organizational context* — who owns or operates the IP range.  
- **`ipaddress` library**: Adds *technical context* — what type of IP it is and how it can be used.  

Combining these sources delivers a **three-dimensional understanding** of IP data: **geographical**, **organizational**, and **technical**, supporting use cases in **cybersecurity**, **fraud detection**, **analytics**, and **network engineering**.

---

## 1. GeoLite2-City.mmdb

### Purpose
Maps an IP address to its **geographic attributes** down to the **city** level.

### Field Descriptions

| **Field** | **Description** | **Use** |
|------------|------------------|---------|
| **country** | Country name associated with the IP. | Regional reporting, policy enforcement. |
| **c_iso** | ISO 3166-1 alpha-2 country code. | Standardized international reference. |
| **state** | State or region name. | Regional segmentation or service routing. |
| **s_iso** | ISO 3166-2 code for the state. | Consistent data integration. |
| **city** | City associated with the IP. | Targeted analytics, fraud prevention. |
| **zip** | Postal code. | Demographic or proximity analysis. |
| **latitude** | Approximate latitude. | Mapping and distance calculations. |
| **longitude** | Approximate longitude. | Geospatial visualization. |
| **cidr** | CIDR block covering the IP. | Network grouping and lookup efficiency. |

---

## 2. GeoLite2-ASN.mmdb

### Purpose
Maps IP addresses to **Autonomous System Numbers (ASNs)** and network operators.

### Field Descriptions

| **Field** | **Description** | **Use** |
|------------|------------------|---------|
| **asn** | Unique identifier for the network (Autonomous System Number). | ISP or organization attribution. |
| **org** | Organization operating the ASN. | Ownership and routing analysis. |
| **net** | CIDR block of the ASN’s network. | Defines network boundaries for correlation. |

---

## 3. IPAddress Enrichment using Python’s `ipaddress` Library

### Purpose
Python’s built-in **`ipaddress`** module provides IP validation and classification for both IPv4 and IPv6, revealing **address scope**, **type**, and **routability**.

### Field Descriptions

| **Field** | **Description (from Python docs)** | **Use** |
|------------|------------------------------------|---------|
| **version** | IP protocol version: `4` for IPv4 or `6` for IPv6. Example: `192.0.2.1` → IPv4, `2001:db8::1` → IPv6. | Distinguishes parsing and handling logic for IPv4 vs. IPv6 systems. |
| **multicast** (`is_multicast`) | True if the address is in a multicast range: <br>• IPv4: `224.0.0.0/4` ([RFC 1112](https://datatracker.ietf.org/doc/html/rfc1112)) <br>• IPv6: `ff00::/8` ([RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291)) <br>Examples: `239.255.255.250`, `ff02::1`. | Identify multicast traffic (e.g., streaming, discovery protocols). |
| **private** (`is_private`) | True for private/local ranges: <br>• IPv4: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` ([RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918)) <br>• IPv6: `fc00::/7` (Unique Local, [RFC 4193](https://datatracker.ietf.org/doc/html/rfc4193)) <br>Examples: `192.168.1.10`, `fd00::1`. | Detect LAN or VPN IPs excluded from public routing. |
| **global** (`is_global`) | True if the address is globally routable (not private, loopback, or reserved): <br>• IPv4 public space per [RFC 5735](https://datatracker.ietf.org/doc/html/rfc5735) <br>• IPv6 global unicast (`2000::/3`, [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291)) <br>Example: `8.8.8.8`, `2001:4860:4860::8888`. | Identify external, Internet-facing hosts or endpoints. |
| **unspecified** (`is_unspecified`) | True if IP is the “unspecified” address — used when no real address is assigned: <br>• IPv4: `0.0.0.0` <br>• IPv6: `::` ([RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291)) | Identify placeholder or default routes before configuration. |
| **reserved** (`is_reserved`) | True for ranges held for future or special use: <br>• IPv4: `240.0.0.0/4` ([RFC 5735](https://datatracker.ietf.org/doc/html/rfc5735)) <br>• IPv6: reserved blocks per [RFC 5156](https://datatracker.ietf.org/doc/html/rfc5156). <br>Examples: `240.0.0.1`, `2001:10::`. | Exclude non-standard or experimental addresses from analytics. |
| **loopback** (`is_loopback`) | True if IP is for self-reference: <br>• IPv4: `127.0.0.0/8` ([RFC 1122](https://datatracker.ietf.org/doc/html/rfc1122)) <br>• IPv6: `::1` ([RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291)) | Detect internal host testing or local service communication. |
| **link_local** (`is_link_local`) | True for addresses valid only within one network segment: <br>• IPv4: `169.254.0.0/16` ([RFC 3927](https://datatracker.ietf.org/doc/html/rfc3927)) <br>• IPv6: `fe80::/10` ([RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291)) <br>Examples: `169.254.1.1`, `fe80::1`. | Identify auto-assigned addresses limited to local broadcast domains. |
| **site_local** (`is_site_local`) | True for deprecated IPv6 site-local addresses (`fec0::/10`, [RFC 3879](https://datatracker.ietf.org/doc/html/rfc3879)). Example: `fec0::1`. | Detect legacy internal IPv6 addressing in older systems. |
| **ipv4_mapped** | For IPv6-mapped IPv4 addresses (`::ffff:0:0/96`, [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291)): returns the embedded IPv4 or `None`. <br>Example: `::ffff:192.0.2.128`. | Enables IPv4 compatibility within IPv6-only systems. |
| **ipv6_mapped** | Returns IPv6 equivalent for an IPv4 address when mapped, or `None`. <br>Example: IPv4 `203.0.113.45` → IPv6 `::ffff:203.0.113.45`. | Facilitates IPv4–IPv6 dual-stack interoperability. |
| **sixtofour** | For 6to4 transition addresses (`2002::/16`, [RFC 3056](https://datatracker.ietf.org/doc/html/rfc3056)): extracts embedded IPv4; else `None`. <br>Example: `2002:c000:0204::` → `192.0.2.4`. | Detect older IPv6-over-IPv4 tunneling deployments. |
| **teredo** | For Teredo tunneling (`2001::/32`, [RFC 4380](https://datatracker.ietf.org/doc/html/rfc4380)): returns `(server, client)` IPv4 tuple; else `None`. <br>Example: `2001:0000:4136:e378:8000:63bf:3fff:fdd2`. | Diagnose IPv6 connectivity through NAT traversal (Teredo tunnels). |

---

## 4. Integrated IP Intelligence Workflow

| **Data Source** | **Question Answered** | **Example Insight** |
|------------------|------------------------|----------------------|
| **GeoLite2-City** | *Where is the IP located?* | Fargo, North Dakota, United States |
| **GeoLite2-ASN** | *Who owns the network?* | ASN 19530 — NDIN-STATE |
| **`ipaddress`** | *What kind of IP is it?* | IPv4, public, unicast, globally routable |

### Common Applications
- **Cybersecurity:** Identify malicious or anomalous public IPs by ASN and location.  
- **Fraud Detection:** Correlate user activity with IP ownership and geolocation.  
- **Network Engineering:** Understand IP scope and routing properties.  
- **Analytics:** Combine region and ownership data for insight segmentation.  

---

## 5. How to Use

### Lookup Process
1. **Input** an IP address (e.g., `134.129.111.111`).  
2. **Query** GeoLite2 databases for **City** and **ASN** data.  
3. **Evaluate** IP characteristics using Python’s `ipaddress` module.  
4. **Combine** all enrichment results into a unified record.

You can test this process online at:  
🔗 **[https://geo.4n6ir.com/?134.129.111.111](https://geo.4n6ir.com/?134.129.111.111)**

### Sample Output
```json
{
    "ip": "134.129.111.111",
    "geo": {
        "country": "United States",
        "c_iso": "US",
        "state": "North Dakota",
        "s_iso": "ND",
        "city": "Fargo",
        "zip": "58102",
        "latitude": 46.9182,
        "longitude": -96.8313,
        "cidr": "134.129.96.0/19"
    },
    "asn": {
        "id": 19530,
        "org": "NDIN-STATE",
        "net": "134.129.0.0/16"
    },
    "ipaddress": {
        "version": 4,
        "multicast": false,
        "private": false,
        "global": true,
        "unspecified": false,
        "reserved": false,
        "loopback": false,
        "link_local": false,
        "site_local": null,
        "ipv4_mapped": "None",
        "ipv6_mapped": "::ffff:134.129.111.111",
        "sixtofour": "None",
        "teredo": "None"
    },
    "attribution": "This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.",
    "geolite2-asn.mmdb": "Thu, 16 Oct 2025 08:30:04 GMT",
    "geolite2-city.mmdb": "Tue, 14 Oct 2025 14:46:21 GMT"
}
```

This unified enrichment result provides **location**, **ownership**, and **technical classification** in one structured record.

---

## 6. References

- **MaxMind GeoLite2 Developer Documentation**  
  🔗 [https://dev.maxmind.com/geoip/geolite2-free-geolocation-data](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)

- **Python `ipaddress` Standard Library Documentation**  
  🔗 [https://docs.python.org/3/library/ipaddress.html](https://docs.python.org/3/library/ipaddress.html)

---

## Conclusion

The integration of **GeoLite2-City**, **GeoLite2-ASN**, and **Python’s `ipaddress`** module creates a comprehensive, layered understanding of IP data:

| **Layer** | **Source** | **Insight** |
|------------|-------------|-------------|
| **Geographical** | GeoLite2-City | Where the IP is located |
| **Organizational** | GeoLite2-ASN | Who owns or operates the IP |
| **Technical** | ipaddress | What type of IP it is and how it behaves |

Together, these tools provide the foundation for a powerful **IP enrichment pipeline**, enabling accurate, multi-dimensional insights across **security**, **analytics**, and **infrastructure monitoring**.
