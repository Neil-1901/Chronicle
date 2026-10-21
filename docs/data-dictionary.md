# Data dictionary

`data/cases/operation-glasshouse/events.csv` contains 240 chronologically generated records. Required parser fields are `timestamp`, `source_type`, `action`, and `source_reference`.

| Field | Meaning |
|---|---|
| `event_id` | Stable generated ID (`GH-E0001`…`GH-E0240`) |
| `source_id` | Logical source label such as `AUTH-01`, `ENDPOINT-01`, or `NETWORK-02` |
| `timestamp` | Synthetic ISO-8601 timestamp in UTC (`Z`) |
| `source_type` | `authentication`, `file_activity`, or `network` |
| `account_id` | Synthetic account/service label; not a human identity |
| `host` | Synthetic workstation/server label, preserved in normalized `attributes` |
| `action` | Event action consumed by Chronicle’s correlation rules |
| `object_reference` | Synthetic object, path, service, or archive name |
| `source_reference` | Stable reference to the originating synthetic log row |
| `bytes` | Synthetic transfer size where relevant |
| `destination` | Synthetic network destination string |
| `disposition` | Scenario context such as routine, unknown, or approved backup |

The original demo uses its existing six-row schema. When no `event_id` is supplied, the parser creates an order-based `E####` ID. Duplicate IDs in an input are rejected.
