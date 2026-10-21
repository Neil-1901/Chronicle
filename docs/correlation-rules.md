# Correlation rules

All rules are deterministic leads, not conclusions. Rule parameters and match counts are included in the generated pipeline report.

| Rule | Match condition | Interpretation and limits |
|---|---|---|
| CORR-001 | At least 3 `login_failure` events for an account followed by `login_success` within 10 minutes | Suggests a sequence worth examining; it does not identify an operator or show whether access was authorized. |
| CORR-002 | A `login_success` followed within 10 minutes by file activity for the same account | Temporal association only. Repeated logins may generate multiple low-severity leads. |
| CORR-003 | `archive_created` followed within 15 minutes by `network_upload` for the same account and compatible host | Does not inspect payloads or prove uploaded bytes came from the archive. The benign backup fixture also matches. |
| CORR-004 | A DNS response with the same transaction ID and reversed source/destination endpoints as a query | Links two packet observations in the public practice capture. It is an informational protocol relationship, not evidence of intent, malware, or identity. |

Findings include supporting event IDs and normalized source-record details (timestamp, source ID, source reference, source type, action). In the UI, selecting a supporting event ID opens the corresponding timeline or network observation.
