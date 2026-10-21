# Limitations

- The public Wireshark practice capture is a training sample, not evidence of the C-001 incident. Glasshouse and the six-event demo are synthetic. No person attribution is supported.
- Chronicle does not parse PCAP bytes natively. The reproducible examination export is produced using the installed `tcpdump` text decoder. Supplied Wireshark screenshots document filter results; tcpdump's segment-level hints can differ from the Wireshark frame list and are labelled accordingly.
- No original disk image, Autopsy case database, or structured Autopsy export is present. The Autopsy screenshot is a visual exhibit and does not enable structured filesystem analysis.
- File hashes are recalculated at run time. Trusted baseline verification, acquisition authentication, and chain-of-custody recording are not implemented.
- Three fixed, separate cases are registered: the network practice sample, synthetic Operation Glasshouse, and synthetic six-event regression demo. There is no user evidence upload, case creation, or general source adapter system.
- Parsing is all-or-error. Invalid records stop the run; partial quarantine and per-row rejection reports are not implemented.
- Correlation operates on synthetic account, host, action, and timestamp fields. It does not establish authorization, causation, human identity, or exfiltration.
- The scenario labels are stored separately and are not a defensible real-world benchmark.
- The frontend uses a local API origin at port 8000 and the Vite development server at port 5173.
- Capture timestamps are normalized to UTC for the timeline, but the source capture's original timezone context is unknown. UTC display must not be mistaken for a verified acquisition timezone.
