# Network-first practice examination

## Case identity and scope

**Case ID:** `WIRESHARK-PRACTICE-001`
**Classification:** public practice sample; not incident-acquired evidence
**Objective:** examine the supplied `http.cap`, preserve packet-level references for visible HTTP/DNS observations, and state what the capture supports without making an attribution claim.

The capture is 25,803 bytes, PCAP 2.4 with Ethernet link type, and contains 43 frames. Its SHA-256 is `25a72bdf10339f2c29916920c8b9501d294923108de8f29b19aba7cc001ab60d`. The digest was recalculated during this work and compared with the value embedded in the generated observation export. No independent acquisition-time baseline was supplied.

## Examination method

The available local packet tool was `tcpdump 4.99.1 -- Apple version 161`. Neither `tshark` nor the Wireshark GUI was available in this environment. The supplied screenshots show Wireshark HTTP and DNS display-filter results; Shreya’s notes report Wireshark 4.6.9, which was not independently verified here.

Regenerate the JSON observation export from the repository root with:

```bash
.venv/bin/python data/extract_http_cap.py
```

The script calls `tcpdump -nn -tt -r` for packet summaries and `tcpdump -nn -tt -A -r` to retain visible HTTP `Host` and `User-Agent` fields. It records the tool version, capture digest, packet frame number, source/destination endpoints, raw epoch time, UTC normalization, and stable export record reference. Wireshark filter annotations are recorded separately with the screenshot path that supports them.

Chronicle processes `data/cases/wireshark-practice/http-cap-observations.json`. It does **not** parse the PCAP. On each investigation run, Chronicle hashes the PCAP, export, Wireshark screenshots, and analysis notes; it validates the exported capture digest and each frame reference against the current capture.

## Supported observations

The supplied HTTP screenshot lists frames 4, 18, 27, and 38. The DNS screenshot lists frames 13 and 17. Times below use the capture-relative values displayed in the screenshots; normalized timestamps in Chronicle are the PCAP epoch values represented as UTC.

| Frame | Time from capture start | Supported observation | Source reference |
|---:|---:|---|---|
| 4 | 0.911310 s | Client `145.254.160.237:3372` sends `GET /download.html` to `65.208.228.223:80`; Host is `www.ethereal.com`. The client-reported User-Agent includes `Windows NT 5.1`. | `evidence/captures/http.cap#frame=4`; HTTP screenshot |
| 13 | 2.553672 s | A DNS A query for `pagead2.googlesyndication.com` goes from `145.254.160.237:3009` to `145.253.2.203:53`. | `evidence/captures/http.cap#frame=13`; DNS screenshot |
| 17 | 2.914190 s | DNS response has transaction ID `0x0023`; tcpdump decodes CNAMEs `pagead2.google.com.` and `pagead.google.akadns.net.` and A records `216.239.59.104`, `216.239.59.99`. It matches frame 13 by ID and reversed endpoints. | `evidence/captures/http.cap#frame=17`; DNS screenshot |
| 18 | 2.984291 s | Client requests `/pagead/ads` from `216.239.59.99:80`; the decoded request includes the Ethereal download-page URL. | `evidence/captures/http.cap#frame=18`; HTTP screenshot |
| 27 | 3.955688 s | Supplied Wireshark screenshot labels this frame `HTTP/1.1 200 OK (text/html)`. | `evidence/captures/http.cap#frame=27`; HTTP screenshot |
| 38 | 4.846969 s | Supplied Wireshark screenshot labels this frame `HTTP/1.1 200 OK`. | `evidence/captures/http.cap#frame=38`; HTTP screenshot |

## Decoder reconciliation

The Wireshark screenshot’s HTTP filter shows four frames (4, 18, 27, 38). The local tcpdump summary heuristically labels HTTP on additional adjacent TCP segments and reports HTTP response status on frames 6, 26, and 36. This is a decoder/reassembly difference in the supplied exhibits and local summary output. Chronicle retains the tcpdump per-frame summary and attributes the four Wireshark-filter annotations to the actual screenshot; it does not silently make the two decoders equivalent. A fresh Wireshark examination is appropriate if stream reassembly details are needed.

The previous note spelling `pagead2.google.` omitted `.com`. The packet decode supports `pagead2.google.com.`; this correction is recorded here and in the analysis note.

## Correlation and interpretation

`CORR-004` links frames 13 and 17 because the DNS transaction ID and reversed endpoints agree. The rule is supported by source fields and produces one low-consequence informational lead. This is an ordinary DNS query/response association; it is not evidence of malicious activity or proof that DNS caused subsequent traffic.

The HTTP rows show a page request, a request for an advertising resource, and server responses. An HTTP 200 status indicates a successful protocol response, not a security finding. The User-Agent is client-reported text, not verified operating-system or human identity. The evidence does not establish unauthorized access, exfiltration, a malicious actor, or a connection to C-001 or Operation Glasshouse.

## Autopsy material boundary

The supplied Autopsy screenshot shows one logical-file-set item named `incident-note.txt` with synthetic C-001 text. It is registered in the supporting exhibit documentation, not as a source for this network case. No disk image, Autopsy case database, or structured artifact export was found. Chronicle has not performed an Autopsy examination. Filesystem analysis would require the source disk image or a validated structured export and acquisition context.
