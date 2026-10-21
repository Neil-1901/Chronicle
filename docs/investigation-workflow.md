# Investigation workflow

## Primary network-practice case

1. **Register and scope.** Choose `WIRESHARK-PRACTICE-001`. Chronicle labels the original capture as a public practice sample, separate from C-001 and Glasshouse.
2. **Fingerprint.** The engine calculates SHA-256 and size for the capture, derived observations, Wireshark screenshots, and notes. The capture digest is compared with the digest recorded by the export. This is not a trusted acquisition-time baseline.
3. **Examine and import.** `data/extract_http_cap.py` invokes tcpdump for 43 frame summaries and selected readable HTTP headers. Supplied Wireshark screenshots provide separate frame annotations. Chronicle imports JSON; it does not decode the PCAP.
4. **Check packet provenance.** The run verifies the capture hash, export-observation hashes, unique in-range frame numbers, source references, and 43-row count.
5. **Normalize and reconstruct.** PCAP epoch values become timezone-aware UTC strings. Original epoch strings remain in event attributes. The source timezone context is not independently known.
6. **Correlate.** CORR-004 joins the DNS query and response by transaction ID and reversed endpoints. The report labels this as ordinary protocol association, not malicious activity.
7. **Report and validate.** Finding event/source references are checked and the saved report is read back before the API returns the run.

## Supporting synthetic cases

Operation Glasshouse and the six-event demo use the common parser, timeline, correlation, reporting, and report-validation path. Glasshouse generator labels are kept outside analyzer inputs. Their records and findings are not represented as packet-derived or connected to the public sample.

## Examiner navigation

- **Overview:** case scope, status, evidence summary, selected packet trail, and next action.
- **Evidence Ledger:** file identities, provenance, size, current-run hash, and capture-to-export comparison.
- **Network Examination:** filter and select a packet observation; inspect endpoint fields, timestamp normalization, annotation source, and original frame reference.
- **Timeline:** inspect the chronologically ordered normalized event records.
- **Correlation & Findings:** inspect the rule, rationale, event IDs, alternatives, and limitation; select a supporting event to return to its record.
- **Case Dossier:** read the methodology and scope, including the separate C-001 Autopsy screenshot boundary.
- **Processing Pipeline:** inspect actual stage inputs, outputs, counts, checks, and measured durations.
- **Investigation Report:** review or download JSON/Markdown generated from the current run.

## Failures and caveats

Parsing and provenance validation are fail-fast. A malformed observation or bad capture/frame reference returns an API error rather than silently dropping evidence. The capture export is only a packet summary; stream reassembly, complete protocol decoding, and underlying filesystem analysis are not implemented.
