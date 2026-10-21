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
- The response contains CNAME records for pagead2.google.com. and pagead.google.akadns.net.
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

## Re-examination and reconciliation

The capture was independently read with local tcpdump 4.99.1. It is a 25,803-byte PCAP 2.4 Ethernet capture with 43 frames. Current SHA-256: `25a72bdf10339f2c29916920c8b9501d294923108de8f29b19aba7cc001ab60d`.

The supplied screenshots show Wireshark HTTP-filter frames 4, 18, 27, and 38, and DNS-filter frames 13 and 17. Tcpdump's per-frame summary labels HTTP on additional adjacent TCP segments and reports response status at frames 6, 26, and 36. These are retained as a decoder/reassembly difference; the screenshots and tcpdump summaries are not represented as identical dissections. See [the network practice case study](../case-study-network-practice.md) for methods, source-linked observations, and interpretation limits.

The earlier note text omitted `.com` from `pagead2.google.com.`. The correction is based on tcpdump's decoded DNS response. It does not change the incident boundary: the capture remains a public practice sample and is not linked to C-001.
