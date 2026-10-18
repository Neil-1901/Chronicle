# Wireshark Sample Capture Analysis

## Capture Identification
- Filename: http.cap
- Location: evidence/captures/http.cap
- Source: Wireshark Sample Captures website
- Type: Public practice capture; not evidence from simulated incident C-001
- Tool: Wireshark 4.6.9
- SHA-256: 25A72BDF10339F2C29916920C8B9501D294923108DE8F29B19ABA7CC001AB60D

## HTTP Observations
- Total packets in capture: 43
- Packets displayed with the http filter: 4
- Packet 4 contains an HTTP GET request for /download.html.
- Source IPv4 address: 145.254.160.237
- Destination IPv4 address: 65.208.228.223
- TCP source port: 3372
- TCP destination port: 80
- The visible Host header is www.ethereal.com.
- The request includes a User-Agent string reporting Windows NT 5.1.
- Packets 27 and 38 display HTTP 200 OK responses.

## DNS Observations
- Packets displayed with the dns filter: 2
- Packet 13 is a DNS A query for pagead2.googlesyndication.com.
- Query source: 145.254.160.237
- DNS server: 145.253.2.203
- Packet 17 is the corresponding DNS response.
- The response shows a CNAME through pagead2.google.akadns.net.
- IPv4 addresses visible in the response: 216.239.59.104 and 216.239.59.99.
- Query time: 2.553672 seconds from the start of the capture.
- Response time: 2.914190 seconds from the start of the capture.

## Interpretation and Limitations
These observations describe the contents of a public sample capture only.
The HTTP and DNS traffic does not, by itself, establish malicious activity,
the identity of a user, or a connection to simulated incident C-001.
The User-Agent value is a client-reported string, not independent proof
of the actual operating system.

## Screenshots
- evidence/screenshots/wireshark-http.png
- evidence/screenshots/wireshark-dns.png

## Status
Initial inspection completed. Preserve the original capture and recheck
its SHA-256 hash if its integrity needs to be verified later.
