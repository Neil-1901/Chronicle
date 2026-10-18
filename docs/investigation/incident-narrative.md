# Simulated Incident C-001

## 1. Purpose
This scenario demonstrates how Chronicle organises controlled synthetic
digital evidence, verifies file integrity using SHA-256, reconstructs a
chronological timeline, and correlates events using explainable rules.

## 2. Scenario
A fictional workstation has a set of simulated file-activity records,
browser-activity records, system events, and network observations.
The investigation examines whether these records can be placed on a
consistent timeline and whether relationships between events are
supported by the available evidence.

This is a test scenario, not a claim that a real security incident occurred.

## 3. Investigation Questions
1. What evidence records are available?
2. Can the integrity of evidence files be checked using SHA-256?
3. What chronological sequence can be reconstructed from timestamps?
4. Which events can be correlated using documented rules?
5. What source records support each finding?

## 4. Planned Evidence Sources
- Controlled synthetic file-activity records
- Controlled synthetic browser-activity records
- Controlled synthetic system-event records
- A network capture, if suitable and its origin and relevance are documented

Each evidence source must be labelled as synthetic or sample data.
A practice capture must not be presented as belonging to this scenario
unless its contents and relationship to the scenario are established.

## 5. Analysis Method
1. Preserve the original evidence files.
2. Record SHA-256 hashes and file details.
3. Examine relevant artefacts using appropriate tools.
4. Normalise available timestamps and record any timezone assumptions.
5. Build a timeline from observed records.
6. Apply documented, explainable correlation rules.
7. Link findings to their supporting evidence.

## 6. Tools
- Autopsy: examine supported file-system or logical-file artefacts.
- Wireshark: inspect packets in a suitable network capture.
- Chronicle analysis engine: process records, reconstruct timelines,
  correlate events, and support report generation.
- Visual Studio Code: maintain investigation documentation and project files.

Record the actual installed tool versions and steps performed.

## 7. Limitations and Ethics
All scenario evidence must be controlled synthetic or clearly identified
sample data. No unauthorised systems will be accessed. A matching timestamp
or correlation between records does not by itself prove identity, intent,
or causation. A hash helps check whether content has changed relative to
a recorded hash; it does not independently prove authenticity.

## 8. Findings
Pending examination. Findings will be added only after the evidence has
actually been inspected and the results recorded.
