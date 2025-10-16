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
| **version** | Indicates IPv4 (`4`) or IPv6 (`6`). | Determines protocol handling. |
| **multicast** | True if IP is in multicast range (`224.0.0.0/4`, `ff00::/8`). | Identify non-unicast traffic. |
| **private** | True if IP is in a private range (`10.0.0.0/8`, `fc00::/7`). | Detect internal network traffic. |
| **global** | True if the IP is globally routable (public). | Confirms external Internet accessibility. |
| **unspecified** | True if IP is unspecified (`0.0.0.0`, `::`). | Marks placeholder or default IPs. |
| **reserved** | True for reserved ranges (`240.0.0.0/4`). | Exclude non-routable IPs. |
| **loopback** | True if IP is loopback (`127.0.0.0/8`, `::1`). | Identify self-referential traffic. |
| **link_local** | True if IP is link-local (`169.254.0.0/16`, `fe80::/10`). | Detect local-only addresses. |
| **site_local** | True for site-local IPv6 (`fec0::/10`), deprecated. | Detects legacy IPv6 internal ranges. |
| **ipv4_mapped** | IPv4 address embedded within an IPv6 (`::ffff:0:0/96`), or `None`. | Useful in dual-stack environments. |
| **ipv6_mapped** | IPv6 representation of an IPv4 address, or `None`. | Facilitates IPv4–IPv6 interoperability. |
| **sixtofour** | Extracts IPv4 from 6to4 addresses (`2002::/16`). | Detect legacy IPv6-over-IPv4 tunnels. |
| **teredo** | Returns IPv4 tuple for Teredo (`2001::/32`) addresses. | Diagnose IPv6-over-IPv4 tunnels. |

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
