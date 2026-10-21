# Evidence provenance and case boundaries

## Executable synthetic cases

| Case | Input | Status |
|---|---|---|
| `CHRONICLE-DEMO-001` | `data/raw/events.csv` | Six fabricated records retained as the original regression demonstration |
| `OPERATION-GLASSHOUSE` | `data/cases/operation-glasshouse/events.csv` | 240 reproducible fabricated records |
| `WIRESHARK-PRACTICE-001` | `evidence/captures/http.cap` and derived `data/cases/wireshark-practice/http-cap-observations.json` | Public practice capture examined outside Chronicle; derived 43-frame export imported and provenance-checked by Chronicle |

Chronicle calculates SHA-256 values for registered files during each run. For the network case, the capture digest is compared with the digest in the derived export, and observation-level capture digests/frame references are validated. This proves the current export refers to the currently fingerprinted capture bytes; it is not comparison to a trusted acquisition-time baseline. The manifest collection timestamp is when Chronicle calculated the digest.

## Shreya’s contributed forensic materials

Shreya contributed the public Wireshark practice capture (`evidence/captures/http.cap`), its HTTP/DNS analysis notes and screenshots, an Autopsy screenshot, and incident/evidence-integrity documentation. The capture is identified in the notes as a public practice sample. It is not connected to C-001 or Operation Glasshouse. `data/extract_http_cap.py` invokes the installed tcpdump tool to create the structured summary export; Chronicle ingests that export and does not itself parse the PCAP. Wireshark screenshot annotations in the export identify their screenshot exhibit path.

The Autopsy screenshot is registered as a visual C-001 exhibit (107,722 bytes; SHA-256 `52d4ad309a391ef4d759689c9cfcf9ee8991a002b5387ee499e1e8ce3408a7e4`). It shows `incident-note.txt` in a logical-file-set view and synthetic C-001 text. It is not an input to the network case or the executable synthetic case pipelines. Repository inspection found no disk image, Autopsy case database, or structured artifact export. Chronicle did not perform this Autopsy examination. A structured filesystem examination requires its source image or validated export and acquisition/case context.

The supplied HTTP screenshot shows frames 4, 18, 27, and 38; the DNS screenshot shows frames 13 and 17. Local tcpdump labels additional adjacent TCP segments as HTTP and reports status lines at frames 6, 26, and 36. Chronicle retains both sets with their distinct provenance and documents the decoder difference rather than silently merging them.

The network capture’s current-run SHA-256 is `25a72bdf10339f2c29916920c8b9501d294923108de8f29b19aba7cc001ab60d` (25,803 bytes). No independent trusted collection-time digest was supplied.

## C-001

`docs/investigation/incident-narrative.md` describes a fictional scenario and states that findings are pending examination. `evidence/synthetic/incident-note.txt` is a synthetic fixture. Do not present the Glasshouse or original-demo report as C-001 findings.

## Ground truth

`data/evaluation/operation-glasshouse-ground-truth.json` describes generator-intended event sequences. It is separate from the analyzer input and never appears as an investigative finding. Its labels do not establish real-world ground truth.
