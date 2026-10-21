# Chronicle IA video demonstration script

**Target duration:** 7 minutes 30 seconds (assignment limit: 7–8 minutes)
**Speaking order:** Neil, then Shreya, then Aarohi. Each person completes their full section before the next person begins. No alternating narration or shared closing.
**Scope:** public Wireshark practice capture as the primary demonstration, followed by the separate synthetic Glasshouse case.

Speaker allocation is only for the recording and does not assign implementation responsibilities. Shreya's confirmed contribution includes the public practice capture, Wireshark HTTP/DNS notes and screenshots, Autopsy screenshot, and incident/evidence-integrity materials. Neil and Aarohi should describe only what they can substantiate.

## Before recording

1. From the repository root, start the API:

   ```bash
   .venv/bin/uvicorn src.api:app --host 127.0.0.1 --port 8000
   ```

2. Confirm `http://127.0.0.1:8000/api/health` returns the Chronicle health response.
3. In another terminal, start the UI:

   ```bash
   cd frontend
   npm run dev -- --host 127.0.0.1
   ```

4. Open `http://127.0.0.1:5173`, select **WIRESHARK-PRACTICE-001**, and run the examination.
5. Have the supplied Wireshark screenshots and analysis notes ready. If Wireshark is not open, describe them as supplied exhibits.
6. Capture genuine Chronicle UI screenshots for the report. Do not present placeholders as screenshots.

## Timed spoken script and screen actions

### 0:00–2:15 — Neil: introduction, integrity, and report

**Show in order:** Chronicle case selector with `WIRESHARK-PRACTICE-001`; Evidence Ledger with `evidence/captures/http.cap`; SHA-256 and integrity caveat; then the investigation report overview.

**Say:** “We are presenting Chronicle, our Cyber Forensics and Laws IA project on digital forensic investigation and user attribution in a simulated cybersecurity incident. I’ll begin with the case scope and show how Chronicle records evidence and produces an investigation report.

The selected case is `WIRESHARK-PRACTICE-001`. It uses a public Wireshark practice capture contributed by Shreya. It is a training sample, not evidence from a real incident, and it is not connected to C-001 or Operation Glasshouse. We keep those case tracks separate.

Chronicle registers this capture as a source. It is 25,803 bytes, and its current SHA-256 is shown here. The digest matches the value recorded in the derived packet export. That checks the current capture against the export. We do not have an independent acquisition-time hash, so this does not prove the file’s history or authenticity before it entered the project.

The report includes the registered sources, current-run hashes, method, timeline, correlation result, evidence references, alternative explanation, and limitations. A reviewer can follow findings to their source records. The report describes this run; the hash manifest is not a complete chain-of-custody system.

I’ll hand over to Shreya, who will walk through the packet capture materials and network observations.”

### 2:15–5:00 — Shreya: network evidence and Autopsy exhibit

**Show in order:** Wireshark HTTP screenshot and notes; DNS screenshot; Chronicle Network Examination with frames 13 and 17 selected; then the Autopsy screenshot in the case dossier.

**Say:** “I contributed this public practice capture, its Wireshark HTTP and DNS analysis notes and screenshots, the Autopsy screenshot, and supporting incident and evidence-integrity materials. The HTTP exhibit lists frames 4, 18, 27, and 38. The DNS exhibit shows a query at frame 13 and response at frame 17.

In Chronicle, the network case contains 43 packet-summary observations. The application uses a structured export generated with tcpdump; Chronicle does not decode the PCAP itself. The records retain stable event IDs, timestamps, endpoints, frame numbers, and references back to the capture. Here, frames 13 and 17 share DNS transaction ID `0x0023` and have reversed endpoints, which supports linking this query and response.

These are observations in a public practice sample. An IP address, domain, or client-reported User-Agent does not identify a person or establish malicious intent.

The Autopsy screenshot shows a logical-file-set view with a synthetic C-001 note. We do not have its disk image, Autopsy case database, or a structured artifact export in this repository. Chronicle registers this screenshot as an exhibit; it has not performed a filesystem examination from it. This exhibit stays separate from the packet capture.

I’ll hand over to Aarohi to follow the finding through the timeline and explain what it does and does not establish.”

### 5:00–7:30 — Aarohi: finding, separate synthetic case, and conclusion

**Show in order:** Timeline with frame 13 or 17; `CORR-004` finding and its source records; then switch to `OPERATION-GLASSHOUSE`, run it, and show a finding with its source events.

**Say:** “The timeline orders the 43 observations using the capture timestamps and retains their packet frame references. The `CORR-004` finding links exactly two records: `PCAP-E0013` at frame 13 and `PCAP-E0017` at frame 17. The report carries both timestamps and source references. The values are normalized to UTC, but the capture’s original timezone context has not been independently established.

This is one informational correlation lead, not a security verdict. Matching transaction ID and reversed endpoints are the basis for the link. Ordinary DNS resolution is a plausible explanation. The result does not prove malicious activity, identify a user, or show that later HTTP traffic was caused by this DNS response.

Operation Glasshouse is a separate deterministic synthetic case with 240 generated event records. Its rules produce 15 leads. One archive-to-upload pattern also matches a scheduled service-account backup, which is a competing benign explanation. This demonstrates rule behavior; it does not establish real-world ground truth, human identity, or actual exfiltration. Glasshouse is not joined to the packet capture or C-001.

Chronicle demonstrates a documented examination workflow and a report that links findings to supplied records. The network sample supports a narrow DNS query-response observation, while the synthetic case shows the rule pipeline separately. Thank you.”

## Recording guardrails

- Keep the final recording between 7:00 and 8:00. Speaking order is Neil, Shreya, then Aarohi, with each member completing their section before the next begins.
- Do not say the practice capture is from C-001, Glasshouse, or a real incident.
- Do not claim the capture proves an attack, exfiltration, attribution, or user identity.
- Do not describe the Autopsy screenshot as a Chronicle filesystem analysis.
- Do not say Chronicle parses PCAP directly; its current network input is the tcpdump-derived observation export.
- If a page or report is not visible, resolve that before recording; do not narrate an unobserved successful action.
