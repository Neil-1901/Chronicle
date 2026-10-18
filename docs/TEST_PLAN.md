# Chronicle — Test Plan

All tests below are planned, not yet executed.

| ID | Test | Expected result |
|---|---|---|
| TC-01 | Hash an unchanged file twice | Hashes match |
| TC-02 | Modify a file after hashing | New hash differs |
| TC-03 | Load valid CSV/JSON | Records parse correctly |
| TC-04 | Invalid timestamp | Clear error handling |
| TC-05 | Unsorted events | Timeline is chronological |
| TC-06 | Different time zones | Documented normalisation |
| TC-07 | Different accounts | Not merged solely due to nearby timestamps |
| TC-08 | Matching correlation rule | Finding cites source event IDs |
| TC-09 | No rule match | No unsupported finding |
| TC-10 | Generate report | Findings and source references appear |
| TC-11 | Missing input file | Actionable error |
| TC-12 | Empty dataset | Clear empty result or message |

Record inputs, steps, expected result, actual result and status. Do not mark tests PASS until executed.
