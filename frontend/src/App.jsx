import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

const NAV = [
  { name: "Overview", icon: "◫", group: "INVESTIGATION" },
  { name: "Evidence Ledger", icon: "▤", group: "INVESTIGATION" },
  { name: "Network Examination", icon: "⌁", group: "INVESTIGATION" },
  { name: "Timeline", icon: "◷", group: "INVESTIGATION" },
  { name: "Correlation & Findings", icon: "⊕", group: "INVESTIGATION" },
  { name: "Processing Pipeline", icon: "⇢", group: "INVESTIGATION" },
  { name: "Case Dossier", icon: "▧", group: "CASE OUTPUT" },
  { name: "Investigation Report", icon: "▧", group: "CASE OUTPUT" },
  { name: "Evaluation", icon: "✓", group: "CASE OUTPUT" },
];

function App() {
  const [report, setReport] = useState(null);
  const [cases, setCases] = useState([]);
  const [caseId, setCaseId] = useState("WIRESHARK-PRACTICE-001");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [active, setActive] = useState("Overview");
  const [query, setQuery] = useState("");
  const [timelinePage, setTimelinePage] = useState(0);
  const [selectedObservationId, setSelectedObservationId] = useState("");
  const runningRef = useRef(false);

  async function loadReport() {
    setError("");
    setNotice("");
    try {
      const response = await fetch(`${API}/api/report?case_id=${encodeURIComponent(caseId)}`);
      if (response.status === 404) {
        setReport(null);
        setNotice("No saved report for this case yet. Run the investigation to create one.");
        return;
      }
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      setReport(await response.json());
    } catch (err) {
      setError(`${err.message}. Ensure the Chronicle API is running on port 8000.`);
    }
  }

  useEffect(() => {
    fetch(`${API}/api/cases`).then((response) => response.json())
      .then((payload) => setCases(payload.cases || []))
      .catch(() => setCases([]));
  }, []);

  useEffect(() => { loadReport(); }, [caseId]);

  async function runInvestigation() {
    if (runningRef.current) return;
    runningRef.current = true;
    setLoading(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(`${API}/api/investigate/${encodeURIComponent(caseId)}`, {
        method: "POST",
        headers: { Accept: "application/json" },
      });
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(data?.detail || `API returned ${response.status}`);
      }
      if (
        !data?.case_id ||
        !Array.isArray(data.timeline) ||
        !Array.isArray(data.findings) ||
        !data.evidence_summary
      ) {
        throw new Error("The API response did not contain the expected report.");
      }

      setReport(data);
      setActive("Overview");
      setQuery("");
      setTimelinePage(0);
      setNotice(
        `Analysis complete · ${data.timeline.length} events · ` +
        `${data.findings.length} findings · ${data.evidence_summary.files?.length ?? 0} evidence files`
      );
    } catch (err) {
      setError(`${err.message || "Investigation failed."} Check the Chronicle API.`);
    } finally {
      runningRef.current = false;
      setLoading(false);
    }
  }

  const events = report?.timeline ?? [];
  const findings = report?.findings ?? [];
  const files = report?.evidence_summary?.files ?? [];

  const filteredEvents = useMemo(
    () => events.filter((event) =>
      JSON.stringify(event).toLowerCase().includes(query.toLowerCase())
    ),
    [events, query]
  );
  const pageSize = 50;
  const visibleEvents = filteredEvents.slice(timelinePage * pageSize, (timelinePage + 1) * pageSize);

  const generated = report?.generated_at_utc
    ? new Date(report.generated_at_utc).toLocaleString()
    : "Awaiting analysis";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => setActive("Overview")} aria-label="Chronicle home">
          <span className="brand-mark">C<span>.</span></span>
          <span className="brand-copy">
            <strong>CHRONICLE</strong>
            <small>FORENSIC INTELLIGENCE</small>
          </span>
        </button>

        <div className="workspace-switch">
          <span><small>LOCAL WORKSPACE</small><strong>Registered investigations</strong></span>
        </div>

        {["INVESTIGATION", "CASE OUTPUT"].map((group) => (
          <div className="nav-group" key={group}>
            <div className="nav-label">{group}</div>
            {NAV.filter((item) => item.group === group).map((item) => (
              <button
                key={item.name}
                className={`nav-item ${active === item.name ? "selected" : ""}`}
                onClick={() => setActive(item.name)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span>{item.name}</span>
                {item.name === "Correlation & Findings" && <span className="nav-count">{findings.length}</span>}
              </button>
            ))}
          </div>
        ))}

        <div className="sidebar-spacer" />
        <div className="integrity-card">
          <div className="integrity-icon">⬡</div>
          <div><strong>Evidence fingerprint</strong><small>SHA-256 per investigation run</small></div>
        </div>
        <div className="sidebar-footer">
          <span>CHRONICLE / 1.0</span>
          <span>SIMULATED ENVIRONMENT</span>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="breadcrumb">
            <span>CASES</span><span className="crumb-slash">/</span>
            <strong>{report?.case_id || caseId}</strong>
          </div>
          <div className="top-actions">
            <span className={`environment ${report?.case_kind === "public-sample" ? "environment-sample" : ""}`}><i /> {report?.case_kind === "public-sample" ? "PUBLIC PRACTICE SAMPLE · NOT INCIDENT EVIDENCE" : "SYNTHETIC CASE ENVIRONMENT"}</span>
            <button className="icon-button" onClick={loadReport} title="Refresh report">↻</button>
          </div>
        </header>

        <div className="content">
          <div className="page-heading">
            <div>
              <div className="eyebrow"><span /> CHRONICLE / EVIDENCE WORKBENCH</div>
              <div className="case-select-row">
                <label htmlFor="case-select">ACTIVE CASE</label>
                <select id="case-select" value={caseId} onChange={(event) => { setCaseId(event.target.value); setReport(null); setError(""); }}>
                  {(cases.length ? cases : [{case_id: caseId, name: caseId}]).map((item) => <option key={item.case_id} value={item.case_id}>{item.name}</option>)}
                </select>
              </div>
              <h1>{pageTitle(active)}</h1>
              <p className="subtitle">{pageSubtitle(active)}</p>
            </div>
            <button className="primary-button" onClick={runInvestigation} disabled={loading}>
              <span className={loading ? "button-spinner" : ""}>{loading ? "◌" : "▶"}</span>
              {loading ? "Analysing evidence…" : "Run investigation"}
            </button>
          </div>

          {error && (
            <div className="alert error-banner" role="alert">
              <span>!</span><div><strong>Connection or analysis error</strong><p>{error}</p></div>
              <button onClick={loadReport}>Retry ↗</button>
            </div>
          )}
          {notice && <div className="alert success-banner" role="status"><span>✓</span>{notice}</div>}

          {!report && !error && <section className="panel start-investigation">
            <PanelTitle kicker="CASE READY" title={cases.find(item => item.case_id === caseId)?.name || caseId}
              subtitle="This case has no saved report yet. Run the selected case to create the evidence inventory, timeline, findings, and report from its supplied input." />
            <button className="primary-button" onClick={runInvestigation} disabled={loading}>{loading ? "Analysing evidence…" : "Run investigation"}</button>
          </section>}

          {report && (
            <>
              <section className="case-banner">
                <div className="case-banner-art" aria-hidden="true">
                  <div className="orbit orbit-one" /><div className="orbit orbit-two" />
                  <div className="orbit-center">C<span>.</span></div>
                </div>
                <div className="case-main">
                  <div className="case-label"><span className="live-dot" /> {report.case_kind === "public-sample" ? "PUBLIC SAMPLE EXAMINATION" : "ACTIVE CASE FILE"}</div>
                  <h2>{report.case_id}</h2>
                  <p>{report.case_name} <span>·</span> {report.case_kind === "public-sample" ? "Packet observations linked to supplied capture" : "Evidence-led reconstruction"}</p>
                  <div className="case-pills"><span>CASE OPEN</span><span>SHA-256 / {report.evidence_summary?.integrity_status?.includes("matches") ? "CAPTURE DIGEST MATCHED" : "FINGERPRINTED"}</span><span>{report.case_kind === "public-sample" ? "PUBLIC SAMPLE" : "SYNTHETIC DATASET"}</span></div>
                </div>
                <div className="case-status">
                  <span className="report-ready"><i /> REPORT GENERATED</span>
                  <small>{generated}</small>
                  <span className="case-ref">CASE REF. / {report.case_id}</span>
                </div>
              </section>

              {active === "Overview" && (
                <Overview
                  files={files} events={events} findings={findings}
                  setActive={setActive} report={report} setSelectedObservationId={setSelectedObservationId}
                />
              )}

              {active === "Processing Pipeline" && (
                <ProcessingPipeline report={report} />
              )}

              {active === "Evidence Ledger" && (
                <>
                <section className="panel">
                  <PanelTitle kicker="EVIDENCE LEDGER" title="Received and derived artifacts"
                    subtitle={`${files.length} files fingerprinted this run. A file-level hash is shown with its current-run comparison scope.`} />
                  <EvidenceTable files={files} detailed artifactMetadata={report.evidence_summary?.artifact_metadata} examination={report.examination} />
                </section>
                <section className="panel"><PanelTitle kicker="OBSERVATION SOURCES" title="Registered sources" subtitle={`${report.evidence_summary?.sources?.length || 0} source identifiers appear in the case records.`} />
                  <div className="source-register">{(report.evidence_summary?.sources || []).map(source => <article key={source.source_id}><code>{source.source_id}</code><strong>{source.name}</strong><span>{source.format} · {source.record_count} records · {source.input_file}</span><small>{source.provenance}</small></article>)}</div>
                </section>
                </>
              )}

              {active === "Network Examination" && <NetworkExamination report={report} events={events} selectedId={selectedObservationId} onSelect={setSelectedObservationId} />}

              {active === "Case Dossier" && <CaseDossier caseId={caseId} report={report} onSelectEvent={(id) => { setSelectedObservationId(id); setActive("Network Examination"); }} />}

              {active === "Timeline" && (
                <section className="panel">
                    <PanelTitle kicker="EVENT RECONSTRUCTION" title="Chronological event timeline"
                    subtitle={`${events.length} normalized records · Source timestamps converted to UTC where documented.`} />
                <input className="search" value={query}
                    onChange={(e) => { setQuery(e.target.value); setTimelinePage(0); }}
                    placeholder="Search event IDs, accounts, actions or source references…" />
                  <div className="timeline-list">
                  {visibleEvents.map((event, i) => <Event key={event.event_id || i} event={event} detailed onSelect={() => setSelectedObservationId(event.event_id)} />)}
                    {!filteredEvents.length && <Empty text="No events match this search." />}
                  </div>
                  {filteredEvents.length > pageSize && <div className="pagination"><span>{timelinePage * pageSize + 1}–{Math.min((timelinePage + 1) * pageSize, filteredEvents.length)} of {filteredEvents.length}</span><button disabled={timelinePage === 0} onClick={() => setTimelinePage(page => Math.max(0, page - 1))}>Previous</button><button disabled={(timelinePage + 1) * pageSize >= filteredEvents.length} onClick={() => setTimelinePage(page => page + 1)}>Next</button></div>}
                </section>
              )}

              {active === "Correlation & Findings" && (
                <section className="panel">
                  <PanelTitle kicker="RULE-BASED ANALYSIS" title="Correlation findings"
                    subtitle="Explainable investigative leads generated by the analysis engine." />
                  {findings.map((finding, i) => (
                    <Finding key={finding.rule_id || i} finding={finding} detailed
                      onSelectEvent={(id) => { setQuery(id); setTimelinePage(0); setSelectedObservationId(id); setActive(caseId === "WIRESHARK-PRACTICE-001" ? "Network Examination" : "Timeline"); }} />
                  ))}
                  {!findings.length && <Empty text="No correlation findings in the current report." />}
                </section>
              )}

              {active === "Investigation Report" && (
                <section className="panel">
                  <PanelTitle kicker="CASE DOCUMENTATION" title="Investigation report"
                    subtitle="A readable account of this run, with source references and machine-readable exports." />
                  <div className="report-actions">
                    <span>RUN RECORD / {report.case_id}</span>
                    <button className="secondary-button" onClick={() => downloadReport(report)}>
                      ↓ Export JSON report
                    </button>
                    <button className="secondary-button" onClick={() => downloadMarkdownReport(report)}>
                      ↓ Export Markdown report
                    </button>
                  </div>
                  <ReportDocument report={report} onSelectEvent={(id) => { setQuery(id); setTimelinePage(0); setSelectedObservationId(id); setActive(caseId === "WIRESHARK-PRACTICE-001" ? "Network Examination" : "Timeline"); }} />
                </section>
              )}

              {active === "Evaluation" && <EvaluationPage />}

              <footer>
                <span>CHRONICLE FORENSIC WORKBENCH</span>
                <span>·</span><span>{report.case_kind === "public-sample" ? "PUBLIC SAMPLE / NO INCIDENT LINK" : "SYNTHETIC CASE DATA"}</span>
                <span>·</span><span>CORRELATION IS NOT PROOF OF IDENTITY</span>
              </footer>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

function ReportDocument({ report, onSelectEvent }) {
  const isNetwork = report.case_kind === "public-sample";
  const artifacts = report.evidence_summary?.files || [];
  const artifactsMeta = report.evidence_summary?.artifact_metadata || {};
  const findings = report.findings || [];
  const limitations = [
    ...(report.examination?.limitations || []),
    ...(report.limitations || []),
  ];
  return (
    <article className="report-document">
      <header className="report-document-heading">
        <div><span className="report-kicker">CHRONICLE / INVESTIGATION RECORD</span><h2>{report.case_name || report.case_id}</h2>
          <p>{report.case_id} <span>·</span> {report.case_kind === "synthetic" ? "Synthetic demonstration" : report.case_kind === "public-sample" ? "Public sample examination" : report.case_kind}</p></div>
        <dl><dt>Generated (UTC)</dt><dd>{report.generated_at_utc || "Not recorded"}</dd><dt>Observations</dt><dd>{report.event_count ?? report.timeline?.length ?? 0}</dd><dt>Findings</dt><dd>{findings.length}</dd></dl>
      </header>

      <section className="report-section">
        <span className="report-kicker">01 / SCOPE AND RESULT</span>
        <h3>{isNetwork ? "Ordinary HTTP retrieval and DNS resolution observed" : "Investigation scope"}</h3>
        <p>{report.scenario || "The investigation processes the registered evidence records and reports source-linked observations."}</p>
        {isNetwork && <p className="report-caution">The public practice capture is not linked to C-001 or Operation Glasshouse. The available material establishes no malicious activity, exfiltration, or human attribution.</p>}
      </section>

      <section className="report-section">
        <span className="report-kicker">02 / EVIDENCE INVENTORY</span>
        <div className="report-table-wrap"><table className="report-table"><thead><tr><th>Artifact</th><th>Class / provenance</th><th>Size</th><th>SHA-256</th></tr></thead><tbody>
          {artifacts.map(file => { const meta = artifactsMeta[file.relative_path] || {}; return <tr key={file.relative_path}><td><code>{file.relative_path}</code></td><td>{meta.artifact_type && <strong>{meta.artifact_type}</strong>}<span>{meta.provenance || "Source classification not recorded"}</span></td><td>{formatBytes(file.size_bytes)}</td><td><code>{file.sha256}</code></td></tr>; })}
        </tbody></table></div>
        <p className="report-muted">Integrity: {report.evidence_summary?.integrity_status || "No integrity statement recorded."}</p>
      </section>

      {report.examination && <section className="report-section">
        <span className="report-kicker">03 / EXAMINATION METHOD</span>
        <h3>{report.examination.tool}</h3><p>{report.examination.method}</p>
        <p className="report-muted">Time treatment: {report.examination.timezone_note}</p>
      </section>}

      <section className="report-section">
        <span className="report-kicker">{report.examination ? "04" : "03"} / FINDINGS</span>
        {!findings.length && <p>No correlations were produced in this run.</p>}
        {findings.map((finding, index) => <article className="report-finding" key={`${finding.rule_id}-${index}`}>
          <div className="report-finding-title"><span>{finding.rule_id} · {finding.severity || "lead"}</span><h3>{finding.title}</h3></div>
          <p>{finding.explanation}</p>
          <p><strong>Supporting records</strong></p>
          <ul>{(finding.supporting_records || []).map(record => <li key={`${record.event_id}-${record.source_reference}`}><button className="report-event-link" onClick={() => onSelectEvent(record.event_id)}>{record.event_id}</button> · {record.timestamp} · <code>{record.source_reference}</code></li>)}</ul>
          {finding.alternative_explanations?.length > 0 && <><p><strong>Alternative explanations</strong></p><ul>{finding.alternative_explanations.map((item, i) => <li key={i}>{item}</li>)}</ul></>}
          {finding.limitation && <p className="report-caution">Limitation: {finding.limitation}</p>}
        </article>)}
      </section>

      <section className="report-section">
        <span className="report-kicker">{report.examination ? "05" : "04"} / LIMITATIONS</span>
        <ul>{[...new Set(limitations)].map((item, i) => <li key={i}>{item}</li>)}</ul>
      </section>

      <details className="report-technical-details"><summary>Full timeline and serialized report</summary>
        <h3>Chronological records ({report.timeline?.length || 0})</h3>
        <div className="report-table-wrap"><table className="report-table"><thead><tr><th>Time (UTC)</th><th>Event</th><th>Type / action</th><th>Source record</th></tr></thead><tbody>
          {(report.timeline || []).map(event => <tr key={event.event_id}><td>{event.timestamp}</td><td><code>{event.event_id}</code></td><td>{event.source_type} / {event.action}</td><td><code>{event.source_reference}</code></td></tr>)}
        </tbody></table></div>
        <pre className="json-view">{JSON.stringify(report, null, 2)}</pre>
      </details>
    </article>
  );
}


function EvaluationPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("ALL");

  async function loadEvaluation() {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API}/api/evaluation`);
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(payload?.detail || `API returned ${response.status}`);
      }
      if (!payload || !payload.summary || !Array.isArray(payload.tests)) {
        throw new Error("The evaluation response has an unexpected format.");
      }
      setData(payload);
    } catch (err) {
      setError(err.message || "Could not load evaluation results.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadEvaluation(); }, []);

  const summary = data?.summary ?? {};
  const tests = data?.tests ?? [];
  const moduleMap = new Map();

  for (const test of tests) {
    const parts = String(test.test || "unknown").split(".");
    const moduleName = parts.length > 1 ? parts[0] : "other";
    if (!moduleMap.has(moduleName)) {
      moduleMap.set(moduleName, { name: moduleName, total: 0, passed: 0, failed: 0, errors: 0, skipped: 0 });
    }
    const item = moduleMap.get(moduleName);
    item.total += 1;
    const status = String(test.status || "").toUpperCase();
    if (status === "PASS") item.passed += 1;
    else if (status === "FAIL") item.failed += 1;
    else if (status === "ERROR") item.errors += 1;
    else if (status === "SKIP") item.skipped += 1;
  }

  const modules = [...moduleMap.values()].sort((a, b) => a.name.localeCompare(b.name));
  const visibleTests = tests.filter((test) => filter === "ALL" || String(test.status || "").toUpperCase() === filter);

  return (
    <div className="evaluation-page">
      {loading && <section className="panel"><p>Loading evaluation results from the Chronicle API…</p></section>}

      {!loading && error && (
        <section className="panel">
          <PanelTitle kicker="EVALUATION STATUS" title="Results unavailable"
            subtitle="The API could not provide the generated evaluation artifact." />
          <p className="evaluation-error">{error}</p>
          <button className="secondary-button" onClick={loadEvaluation}>Retry evaluation ↻</button>
          <p className="evaluation-muted">Generate the report with <code>.venv/bin/python evaluation/run_evaluation.py</code>, then retry.</p>
        </section>
      )}

      {!loading && data && (
        <>
          <section className="panel evaluation-hero">
            <PanelTitle kicker="TEST SUITE · CURRENT RUN"
              title="Automated test results"
              subtitle="Results loaded from outputs/evaluation_report.json through the Chronicle API." />
            <div className="evaluation-status-row">
              <span className={`evaluation-status ${data.status === "PASS" ? "is-pass" : "is-fail"}`}>
                {data.status === "PASS" ? "✓" : "!"} {data.status || "UNKNOWN"}
              </span>
              <span className="evaluation-muted">Latest recorded run (UTC)</span>
              <button className="secondary-button" onClick={loadEvaluation}>Refresh ↻</button>
            </div>
          </section>

          <div className="stats-grid evaluation-stats">
            <Stat label="TESTS EXECUTED" value={summary.total ?? tests.length} icon="✓" detail="Discovered by the runner" accent="amber" />
            <Stat label="PASSED" value={summary.passed ?? 0} icon="+" detail="Expected behaviour observed" />
            <Stat label="FAILED" value={summary.failed ?? 0} icon="!" detail="Assertion failures" />
            <Stat label="ERRORS" value={summary.errors ?? 0} icon="×" detail="Execution or import errors" />
          </div>

          <section className="panel">
            <PanelTitle kicker="TEST DISTRIBUTION" title="Results by module"
              subtitle={`${modules.length} test modules represented in this run.`} />
            <div className="evaluation-module-list">
              {modules.map((item) => (
                <div className="evaluation-module" key={item.name}>
                  <div className="evaluation-module-top">
                    <code>{item.name}</code>
                    <strong>{item.passed}/{item.total} passed</strong>
                  </div>
                  <div className="evaluation-track" aria-label={`${item.name}: ${item.passed} of ${item.total} passed`}>
                    <span style={{ width: `${item.total ? item.passed / item.total * 100 : 0}%` }} />
                  </div>
                  <div className="evaluation-module-meta">
                    <span>Passed: {item.passed}</span>
                    <span>Failed: {item.failed}</span>
                    <span>Errors: {item.errors}</span>
                    <span>Skipped: {item.skipped}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <PanelTitle kicker="TRACEABLE RESULTS" title="Individual test cases"
              subtitle={`${visibleTests.length} of ${tests.length} test records shown.`} />
            <div className="evaluation-filters">
              {["ALL", "PASS", "FAIL", "ERROR", "SKIP"].map((status) => (
                <button key={status}
                  className={`evaluation-filter ${filter === status ? "active" : ""}`}
                  onClick={() => setFilter(status)}>
                  {status === "ALL" ? `All (${tests.length})` : `${status} (${tests.filter((t) => String(t.status || "").toUpperCase() === status).length})`}
                </button>
              ))}
            </div>
            <div className="evaluation-test-list">
              {visibleTests.map((test, index) => {
                const status = String(test.status || "UNKNOWN").toUpperCase();
                return (
                  <details className="evaluation-test" key={`${test.test}-${index}`}>
                    <summary>
                      <span className={`evaluation-test-badge ${status === "PASS" ? "is-pass" : "is-fail"}`}>{status}</span>
                      <code>{test.test || "Unnamed test"}</code>
                    </summary>
                    {test.detail && <pre className="evaluation-detail">{test.detail}</pre>}
                  </details>
                );
              })}
              {!visibleTests.length && <p className="evaluation-muted">No tests match this filter.</p>}
            </div>
          </section>

          <section className="panel evaluation-limitations">
            <PanelTitle kicker="INTERPRETATION" title="What these results establish"
              subtitle="Passing tests support the tested software behaviour; they do not prove the system is defect-free." />
            <ul>
              <li>This is a unit-test evaluation of the existing Python test suite, not a benchmark of attribution accuracy against labelled real-world cases.</li>
              <li>It does not independently establish the authenticity or provenance of the supplied evidence or public packet capture.</li>
              <li>It cannot establish a real person's identity, intent or culpability.</li>
                <li>This evaluation screen reports automated tests only; manual browser checks are documented separately in docs/testing-and-evaluation.md.</li>
            </ul>
            <div className="evaluation-run-command">
              <span>REPRODUCE THIS EVALUATION</span>
              <code>.venv/bin/python evaluation/run_evaluation.py</code>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function pageTitle(active) {
  return ({
    "Overview": "Investigation overview",
    "Processing Pipeline": "Processing pipeline",
    "Evidence Ledger": "Evidence ledger",
    "Network Examination": "Packet examination",
    "Case Dossier": "Case dossier & forensic exhibits",
    "Timeline": "Event reconstruction",
    "Correlation & Findings": "Correlation and findings",
    "Investigation Report": "Investigation report",
    "Evaluation": "Automated evaluation",
  })[active] || active;
}

function pageSubtitle(active) {
  return ({
    "Overview": "A consolidated view of evidence integrity, incident activity and analytical leads.",
    "Processing Pipeline": "Inspect the real processing stages, inputs, outputs, and measured durations for this run.",
    "Evidence Ledger": "Inspect artifact identity, provenance, current-run fingerprints, and examination status.",
    "Network Examination": "Review packet-linked observations from the supplied public practice capture.",
    "Case Dossier": "Investigation scope, provenance, recorded observations and supporting exhibits.",
    "Timeline": "Inspect normalised events, timestamps and their original source references.",
    "Correlation & Findings": "Trace each investigative lead to supporting events and source records.",
    "Investigation Report": "Review or export the report generated by the selected investigation run.",
    "Evaluation": "Reproducible unit-test results, module coverage and evaluation limitations.",
  })[active] || "Digital forensic investigation workspace.";
}

function ProcessingPipeline({ report }) {
  const stages = report.pipeline || [];
  return <section className="panel">
    <PanelTitle kicker="LIVE RUN OUTPUT" title="Investigation processing"
      subtitle={`Run ${report.case_id} · ${report.processing_seconds ?? "—"} seconds measured · ${stages.length} recorded stages`} />
    <div className="pipeline-list">
      {stages.map((stage, index) => <details className="pipeline-stage" key={stage.stage_id} open={index === 0}>
        <summary><span className="pipeline-number">{String(index + 1).padStart(2, "0")}</span>
          <span className="pipeline-stage-name"><strong>{stage.name}</strong><small>{stage.status.toUpperCase()} · {stage.duration_seconds}s</small></span>
          <span className="pipeline-stage-count">{stage.output?.event_count ?? stage.output?.file_count ?? stage.output?.match_count ?? stage.output?.format ?? "Ready"}</span>
        </summary>
        <div className="pipeline-detail"><p>{stage.note || "Stage input and output recorded by the investigation engine."}</p>
          <div className="pipeline-io"><div><small>INPUT</small><pre>{JSON.stringify(stage.input, null, 2)}</pre></div>
            <div><small>OUTPUT</small><pre>{JSON.stringify(stage.output, null, 2)}</pre></div></div>
        </div>
      </details>)}
    </div>
    <p className="method-note-text">Durations are measured during this run. Hashes are fingerprints calculated now; they are not historical verification without a trusted reference digest.</p>
  </section>;
}

function Overview({ files, events, findings, setActive, report, setSelectedObservationId }) {
  if (report.case_kind === "public-sample") {
    return <NetworkOverview files={files} events={events} findings={findings} setActive={setActive} setSelectedObservationId={setSelectedObservationId} report={report} />;
  }
  const severityCounts = findings.reduce((counts, finding) => {
    const severity = finding.severity || "unspecified";
    counts[severity] = (counts[severity] || 0) + 1;
    return counts;
  }, {});
  const severitySummary = Object.entries(severityCounts)
    .map(([severity, count]) => `${severity}: ${count}`).join(" · ") || "none";
  const eventTypeSummary = Object.entries(report.event_type_counts || {})
    .map(([type, count]) => `${type}: ${count}`).join(" · ") || "none";
  return (
    <>
      <div className="section-heading"><div><span className="section-index">01</span><strong>INVESTIGATION AT A GLANCE</strong></div><span>CASE SUMMARY / 01</span></div>
      <div className="stats-grid">
        <Stat label="EVIDENCE SOURCES" value={report.evidence_summary?.source_count ?? 0} icon="▤" detail={`${files.length} files fingerprinted`} accent="amber" />
        <Stat label="TIMELINE EVENTS" value={events.length} icon="◷" detail="Normalised records" />
        <Stat label="CORRELATION LEADS" value={findings.length} icon="⌁" detail="Rule-supported findings" />
        <Stat label="INTEGRITY ALGORITHM" value="SHA-256" icon="⬡" detail="Cryptographic hashing" />
      </div>

      <section className="panel overview-brief">
        <PanelTitle kicker={report.case_kind?.toUpperCase() || "CASE BRIEF"} title={report.case_name || report.case_id}
          subtitle={report.scenario || "Scenario description not supplied."} />
        <div className="overview-meta"><span>TIME RANGE <strong>{formatTimestamp(events[0]?.timestamp)} — {formatTimestamp(events.at(-1)?.timestamp)}</strong></span><span>PROCESSING <strong>{report.processing_seconds ?? "—"} s measured</strong></span><span>PIPELINE <strong>{(report.pipeline || []).length} completed stages</strong></span><span>INTEGRITY <strong>{report.evidence_summary?.integrity_status || "Not recorded"}</strong></span><span>EVENT TYPES <strong>{eventTypeSummary}</strong></span><span>FINDINGS BY SEVERITY <strong>{severitySummary}</strong></span></div>
      </section>

      <div className="overview-grid">
        <section className="panel">
          <PanelTitle kicker="RULE MATCHES" title="Forensic intelligence"
            subtitle="Investigative leads identified in this case."
            action={() => setActive("Correlation & Findings")} />
          {findings.length ? findings.map((f, i) => <Finding key={f.rule_id || i} finding={f} />)
            : <Empty text="No findings in this report." />}
        </section>
        <section className="panel">
          <PanelTitle kicker="EVENT STREAM" title="Recent activity"
            subtitle="Latest events in the supplied records."
            action={() => setActive("Timeline")} />
          <div className="mini-timeline">
            {events.slice(-5).reverse().map((event, i) => <Event key={event.event_id || i} event={event} />)}
            {!events.length && <Empty text="No timeline events." />}
          </div>
        </section>
      </div>

      <section className="panel">
        <PanelTitle kicker="EVIDENCE INTEGRITY" title="Evidence manifest"
          subtitle="Recorded file sizes, SHA-256 hashes and collection metadata."
          action={() => setActive("Evidence Ledger")} />
        <EvidenceTable files={files} />
      </section>

      <section className="panel">
        <PanelTitle kicker="INCIDENT RECONSTRUCTION" title="Event relationship map"
          subtitle="A visual sequence of events in the generated timeline."
          action={() => setActive("Processing Pipeline")} />
        <RelationshipMap events={events} findings={findings} />
      </section>

      <div className="method-note">
        <span className="method-icon">i</span>
        <div><strong>Methodological note</strong>
          <p>This interface displays records supplied to Chronicle. Correlation is an investigative lead, not proof of identity, intent, authorisation or causation.</p>
        </div>
      </div>
    </>
  );
}

function NetworkOverview({ files, events, findings, setActive, setSelectedObservationId, report }) {
  const keyEvents = events.filter((event) => event.attributes?.wireshark_annotation || event.action.startsWith("dns_"));
  const observedHttp = events.filter((event) => event.action.startsWith("http_")).length;
  return <div className="forensic-overview">
    <section className="forensic-case-intro">
      <div className="forensic-case-copy"><span className="panel-kicker">PRIMARY INVESTIGATION / PUBLIC TRAINING SAMPLE</span><h2>What does this capture support?</h2><p>{report.scenario}</p></div>
      <div className="forensic-case-action"><span>EXAMINATION RESULT</span><strong>Ordinary HTTP retrieval and DNS resolution observed</strong><small>No malicious activity or user attribution established.</small><button type="button" onClick={() => setActive("Network Examination")}>Inspect packet ledger ↗</button></div>
    </section>

    <section className="forensic-ledger-summary">
      <div><span>REGISTERED ARTIFACTS</span><strong>{files.length}</strong><small>Original capture, export, screenshots, notes</small></div>
      <div><span>CAPTURE FRAMES</span><strong>{events.length}</strong><small>Stable IDs linked to frame references</small></div>
      <div><span>WIRESHARK HTTP FILTER</span><strong>{observedHttp}</strong><small>Annotations attributed to supplied screenshot</small></div>
      <div><span>SUPPORTED CORRELATIONS</span><strong>{findings.length}</strong><small>DNS query and response association</small></div>
    </section>

    <section className="forensic-record-section">
      <header><div><span className="panel-kicker">SELECTED OBSERVATIONS</span><h3>Packet trail</h3><p>Frame numbers and original capture references are preserved.</p></div><button className="text-button" onClick={() => setActive("Network Examination")}>Open full examination ↗</button></header>
      <div className="forensic-record-list">{keyEvents.map((event) => <button className="forensic-record" type="button" key={event.event_id} onClick={() => { setSelectedObservationId(event.event_id); setActive("Network Examination"); }}>
        <span className="forensic-frame">{String(event.attributes.frame_number).padStart(2, "0")}</span><span className="forensic-record-time">{event.timestamp.replace("+00:00", "Z")}</span><strong>{event.attributes.protocol} / {event.action.replaceAll("_", " ")}</strong><span>{event.object_reference || event.attributes.decoded_summary}</span><code>{event.source_reference}</code>
      </button>)}</div>
    </section>

    <div className="forensic-footer-note"><strong>Integrity scope</strong><span>{report.evidence_summary?.integrity_status}</span><button className="text-button" onClick={() => setActive("Evidence Ledger")}>Review evidence ledger ↗</button></div>
    <p className="forensic-method-note">{report.examination?.limitations?.join(" ")}</p>
  </div>;
}

function NetworkExamination({ report, events, selectedId, onSelect }) {
  const [protocol, setProtocol] = useState("ALL");
  const [search, setSearch] = useState("");
  const exam = report.examination || {};
  const rows = useMemo(() => events.filter((event) => {
    const attrs = event.attributes || {};
    const matchesProtocol = protocol === "ALL" || (attrs.protocol || "TCP") === protocol;
    return matchesProtocol && JSON.stringify(event).toLowerCase().includes(search.toLowerCase());
  }), [events, protocol, search]);
  const selected = rows.find((event) => event.event_id === selectedId) || rows[0] || events[0];
  const attrs = selected?.attributes || {};
  const displayEndpoint = (event, side) => {
    const fields = event.attributes || {};
    const ip = fields[`${side}_ip`] || "—";
    const port = fields[`${side}_port`];
    return port == null ? ip : `${ip}:${port}`;
  };

  return <div className="network-workspace">
    <section className="network-case-strip">
      <div><span className="panel-kicker">SOURCE CAPTURE</span><strong>{exam.capture_filename}</strong><small>{exam.frame_count} frames · {exam.tool}</small></div>
      <div><span className="panel-kicker">EXAMINATION SCOPE</span><strong>HTTP and DNS observations</strong><small>Public practice sample · not incident evidence</small></div>
      <a className="secondary-button" href="/evidence/http.cap" download>↓ Download original PCAP</a>
    </section>

    <section className="network-observation-panel">
      <header className="network-panel-head">
        <div><span className="panel-kicker">PACKET OBSERVATION LEDGER / {rows.length} SHOWN</span><h3>Frames linked to source capture</h3><p>Every row retains a frame number, capture timestamp, exporter summary, and capture digest.</p></div>
        <div className="network-filters">
          <label><span>PROTOCOL</span><select value={protocol} onChange={(event) => setProtocol(event.target.value)}><option value="ALL">All observations</option><option value="HTTP">HTTP</option><option value="DNS">DNS</option><option value="TCP">Other TCP</option></select></label>
          <label><span>FIND A FRAME OR FIELD</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Frame, endpoint, action…" /></label>
        </div>
      </header>
      <div className="packet-table-wrap"><table className="packet-table">
        <thead><tr><th>FRAME</th><th>CAPTURE TIME / UTC</th><th>TYPE</th><th>NETWORK ENDPOINTS</th><th>OBSERVATION</th></tr></thead>
        <tbody>{rows.map((event) => {
          const fields = event.attributes || {};
          const active = selected?.event_id === event.event_id;
          return <tr key={event.event_id} className={active ? "packet-selected" : ""}>
            <td><button className="frame-link" type="button" onClick={() => onSelect(event.event_id)}>{String(fields.frame_number).padStart(2, "0")}</button></td>
            <td className="packet-time">{event.timestamp.replace("+00:00", "Z")}</td>
            <td><span className={`protocol-tag protocol-${String(fields.protocol || "TCP").toLowerCase()}`}>{fields.protocol || "TCP"}</span></td>
            <td className="packet-endpoints">{displayEndpoint(event, "source")}<span> → </span>{displayEndpoint(event, "destination")}</td>
            <td>{event.action.replaceAll("_", " ")}<small>{event.object_reference || fields.tcpdump_application_hint || "Packet summary only"}</small></td>
          </tr>;
        })}</tbody>
      </table>{!rows.length && <Empty text="No packet observations match these filters." />}</div>
    </section>

    {selected && <section className="packet-inspector">
      <div className="packet-inspector-heading"><span className="panel-kicker">SELECTED PACKET / {attrs.frame_number}</span><h3>{selected.action.replaceAll("_", " ")}</h3><span className="packet-id">{selected.event_id}</span></div>
      <div className="packet-inspector-main">
        <dl className="packet-fields">
          <div><dt>Source endpoint</dt><dd>{displayEndpoint(selected, "source")}</dd></div>
          <div><dt>Destination endpoint</dt><dd>{displayEndpoint(selected, "destination")}</dd></div>
          <div><dt>Capture time / normalized UTC</dt><dd>{attrs.raw_capture_timestamp_epoch} → {selected.timestamp}</dd></div>
          <div><dt>Capture source</dt><dd>{selected.source_reference}</dd></div>
          <div><dt>Observation export</dt><dd>{attrs.export_record_reference}</dd></div>
          <div><dt>Capture SHA-256</dt><dd className="break-hash">{attrs.capture_sha256}</dd></div>
        </dl>
        <div className="packet-decoding"><span className="panel-kicker">DECODE AND ANNOTATION</span>
          {attrs.wireshark_annotation && <p><strong>Wireshark exhibit:</strong> {attrs.wireshark_annotation} <a href={`/${attrs.annotation_source}`} target="_blank" rel="noreferrer">View exhibit ↗</a></p>}
          {attrs.host && <p><strong>HTTP Host:</strong> {attrs.host}</p>}
          {attrs.user_agent && <p><strong>User-Agent:</strong> {attrs.user_agent}</p>}
          {attrs.paired_query_event_id && <p><strong>Matched query:</strong> {attrs.paired_query_event_id} by DNS transaction ID and reversed endpoints.</p>}
          <details><summary>tcpdump packet summary</summary><pre>{attrs.decoded_summary}</pre></details>
          {attrs.tcpdump_application_hint && <p className="decoder-caveat"><strong>Decoder note:</strong> tcpdump also labels this segment as {attrs.tcpdump_application_hint}. The supplied Wireshark filter exhibits are separately attributed in the export.</p>}
        </div>
      </div>
    </section>}

    <section className="decoder-reconciliation">
      <strong>Decoder reconciliation</strong><p>{exam.decoder_discrepancy} Chronicle stores per-frame tcpdump summaries and imports the supplied Wireshark filter annotations as exhibit-derived observations. It does not claim complete TCP stream reassembly.</p>
    </section>
  </div>;
}

function SOCView({ events, findings, files, setActive }) {
  const failed = events.filter((e) => String(e.action).toLowerCase().includes("failure")).length;
  const successful = events.filter((e) => String(e.action).toLowerCase().includes("success")).length;
  const fileActivity = events.filter((e) => String(e.source_type).toLowerCase().includes("file")).length;

  return (
    <>
      <div className="section-heading"><div><span className="section-index">02</span><strong>SECURITY OPERATIONS / EVENT CORRELATION</strong></div><span>ANALYST VIEW</span></div>
      <div className="soc-banner">
        <div><span className="soc-kicker"><i /> ANALYSIS ENGINE CONNECTED</span>
          <h2>Incident activity map</h2>
          <p>Explore the temporal sequence of supplied authentication and file activity records.</p>
        </div>
        <div className="soc-summary"><span>RULES MATCHED</span><strong>{findings.length.toString().padStart(2, "0")}</strong><small>correlation findings</small></div>
      </div>

      <div className="stats-grid soc-stats">
        <Stat label="FAILED LOGINS" value={failed} icon="×" detail="Authentication events" accent="red" />
        <Stat label="SUCCESSFUL LOGINS" value={successful} icon="✓" detail="Authentication events" accent="green" />
        <Stat label="FILE EVENTS" value={fileActivity} icon="▤" detail="File activity records" />
        <Stat label="EVIDENCE FILES" value={files.length} icon="⬡" detail="Manifest entries" />
      </div>

      <section className="panel">
        <PanelTitle kicker="EVENT GRAPH" title="Connected incident sequence"
          subtitle="Connections represent chronological proximity and matching account identifiers, not proof of causation." />
        <RelationshipMap events={events} findings={findings} large />
      </section>

      <section className="panel">
        <PanelTitle kicker="CORRELATION ENGINE" title="Matched investigative leads"
          subtitle="Select a finding to inspect its supporting event IDs and limitations." />
        {findings.map((f, i) => <Finding key={f.rule_id || i} finding={f} detailed />)}
      </section>

      <section className="panel">
        <PanelTitle kicker="RAW EVENT RECORDS" title="Activity sequence"
          subtitle="Every event retains its source reference."
          action={() => setActive("Timeline")} />
        <div className="timeline-list">
          {events.map((event, i) => <Event key={event.event_id || i} event={event} detailed />)}
        </div>
      </section>
    </>
  );
}


function RelationshipMap({ events, findings, large = false }) {
  const [selectedId, setSelectedId] = useState(null);

  if (!events.length) return <Empty text="No events available to visualise." />;

  const width = 960;
  const height = large ? 350 : 280;
  const left = 62;
  const right = width - 62;
  const y = large ? 150 : 125;

  const displayEvents = events.slice(-12);
  const positions = displayEvents.map((event, i) => ({
    ...event,
    x: displayEvents.length === 1 ? width / 2 : left + (right - left) * i / (displayEvents.length - 1),
    y: y + (i % 2 === 0 ? 0 : 22),
  }));

  const referencedIds = new Set(
    findings.flatMap(f => f.supporting_event_ids || []).map(String)
  );
  const selected =
    positions.find(e => String(e.event_id) === String(selectedId)) || positions[0];

  return (
    <div className={`relationship-map chronicle-map ${large ? "relationship-map-large" : ""}`}>
      <div className="map-toolbar">
        <div className="map-legend">
          <span><i className="legend-auth" /> Authentication</span>
          <span><i className="legend-file" /> File activity</span>
          <span><i className="legend-network" /> Network observation</span>
          <span><i className="legend-correlation" /> Referenced by a finding</span>
        </div>
        <span className="map-interaction-hint">
          <span className="live-dot" /> SELECT A NODE TO INSPECT
        </span>
      </div>

      <div className="graph-scroll">
        <svg viewBox={`0 0 ${width} ${height}`} role="group"
             aria-label="Interactive chronological event sequence">
          <defs>
            <pattern id="graphGrid" width="24" height="24" patternUnits="userSpaceOnUse">
              <path d="M 24 0 L 0 0 0 24" fill="none"
                    stroke="currentColor" strokeOpacity=".08" />
            </pattern>
            <linearGradient id="graphLine" x1="0" x2="1">
              <stop offset="0%" stopColor="#ee8b3a" stopOpacity=".22" />
              <stop offset="100%" stopColor="#ffb35c" stopOpacity=".95" />
            </linearGradient>
          </defs>

          <rect width={width} height={height} fill="url(#graphGrid)" rx="10" />
          <text x="18" y="24" className="svg-label">CHRONOLOGICAL EVENT SEQUENCE</text>
          <text x={right} y="24" textAnchor="end" className="svg-label">
            {String(displayEvents.length).padStart(2, "0")} / {String(events.length).padStart(2, "0")} RECORDS
          </text>

          <path
            d={`M ${left} ${y + 10} ${positions.map(p => `L ${p.x} ${p.y}`).join(" ")}`}
            fill="none" stroke="url(#graphLine)" strokeWidth="2" strokeDasharray="5 6"
          />

          {positions.map((p, i) => {
            const file = String(p.source_type || "").toLowerCase().includes("file");
            const network = String(p.source_type || "").toLowerCase().includes("network");
            const failure = String(p.action || "").toLowerCase().includes("failure");
            const correlated = referencedIds.has(String(p.event_id));
            const active = String(selected.event_id) === String(p.event_id);
            const fill = file ? "#91a4b5" : network ? "#73b8d2" : failure ? "#f07968" : "#ffad55";

            return (
              <g key={p.event_id || i}
                 className={`graph-node ${active ? "graph-node-selected" : ""}`}
                 role="button" tabIndex={0}
                 aria-label={`Inspect ${p.event_id || `event ${i + 1}`}: ${p.action || "event"}`}
                 aria-pressed={active}
                 onClick={() => setSelectedId(p.event_id ?? String(i))}
                 onKeyDown={event => {
                   if (event.key === "Enter" || event.key === " ") {
                     event.preventDefault();
                     setSelectedId(p.event_id ?? String(i));
                   }
                 }}>
                {correlated && (
                  <circle cx={p.x} cy={p.y} r="19" fill="none"
                          stroke="#ffad55" strokeOpacity=".7" strokeWidth="1.5"
                          strokeDasharray="3 4" />
                )}
                {active && (
                  <circle cx={p.x} cy={p.y} r="14" fill={fill} fillOpacity=".13"
                          stroke={fill} strokeOpacity=".8" />
                )}
                <circle cx={p.x} cy={p.y} r={active ? 8 : 6}
                        fill={fill} stroke="#11151a" strokeWidth="3" />
                <text x={p.x} y={p.y - 27} textAnchor="middle" className="svg-event-id">
                  {p.event_id || `E${i + 1}`}
                </text>
                <text x={p.x} y={p.y + 34} textAnchor="middle" className="svg-event-action">
                  {String(p.action || "event").replaceAll("_", " ")}
                </text>
                <text x={p.x} y={p.y + 49} textAnchor="middle" className="svg-event-time">
                  {formatTime(p.timestamp)}
                </text>
                {active && (
                  <text x={p.x} y={p.y + 70} textAnchor="middle" className="svg-selected-label">
                    SELECTED
                  </text>
                )}
              </g>
            );
          })}

          <text x={left} y={height - 15} className="svg-label">EARLIER</text>
          <text x={right} y={height - 15} textAnchor="end" className="svg-label">LATER</text>
        </svg>
      </div>

      <div className="map-caption">
        The line shows chronological display order only. Highlighted rings identify events
        referenced by correlation findings; they do not imply causation.
      </div>

      <section className="selected-event-card" aria-live="polite">
        <div className="selected-event-index">
          <span className="micro-label">SELECTED RECORD</span>
          <strong>{selected.event_id || "EVENT"}</strong>
          <span className="selected-record-type">
            {String(selected.source_type || "SOURCE").toUpperCase()}
          </span>
        </div>
        <div className="selected-event-main">
          <span className="micro-label">OBSERVED ACTION</span>
          <h4>{String(selected.action || "Event").replaceAll("_", " ")}</h4>
          <p>{selected.account_id || "Account not specified"}
            <span> · </span>{selected.object_reference || "No object reference"}</p>
        </div>
        <div className="selected-event-meta">
          <div>
            <span className="micro-label">TIMESTAMP</span>
            <strong>{formatTimestamp(selected.timestamp)}</strong>
          </div>
          <div>
            <span className="micro-label">SOURCE REFERENCE</span>
            <strong>{selected.source_reference || "Not supplied"}</strong>
          </div>
        </div>
      </section>
    </div>
  );
}

function Stat({ label, value, icon, detail, accent = "" }) {
  return (
    <div className={`stat-card ${accent ? `stat-${accent}` : ""}`}>
      <div className="stat-top"><span>{label}</span><i>{icon}</i></div>
      <div className="stat-value">{value}</div>
      <div className="stat-detail">{detail}</div>
      <div className="stat-bottom-line" />
    </div>
  );
}

function PanelTitle({ title, subtitle, action, kicker }) {
  return (
    <div className="panel-heading">
      <div>{kicker && <span className="panel-kicker">{kicker}</span>}<h3>{title}</h3><p>{subtitle}</p></div>
      {action && <button className="text-button" onClick={action}>Explore ↗</button>}
    </div>
  );
}

function Finding({ finding: f, detailed = false, onSelectEvent }) {
  const supporting = f.supporting_event_ids || f.supporting_events || [];
  const severity = String(f.severity || "investigative lead").toLowerCase();

  return (
    <article className={`finding ${detailed ? "finding-detailed" : ""}`}>
      <div className={`finding-symbol ${severity === "high" ? "severity-high" : ""}`}>⌁</div>
      <div className="finding-body">
        <div className="finding-meta">
          <span className="rule-id">{f.rule_id || "CORRELATION"}</span>
          <span className={`confidence ${severity === "high" ? "confidence-high" : ""}`}>{severity.toUpperCase()} / INVESTIGATIVE LEAD</span>
        </div>
        <h4>{f.title || f.name || "Correlation finding"}</h4>
        <p>{f.description || f.explanation || "Rule-supported relationship between source events."}</p>
        {supporting.length > 0 && <div className="event-tags">
                {supporting.map((id, i) => onSelectEvent
                  ? <button key={i} type="button" onClick={() => onSelectEvent(typeof id === "object" ? id.event_id : id)}>{typeof id === "object" ? id.event_id || JSON.stringify(id) : id}</button>
                  : <span key={i}>{typeof id === "object" ? id.event_id || JSON.stringify(id) : id}</span>)}
        </div>}
        {detailed && (
          <div className="finding-detail-grid">
            <div><small>ACCOUNT</small><strong>{f.account_id || "Not specified"}</strong></div>
            <div><small>TIME WINDOW</small><strong>{f.window_minutes != null ? `${f.window_minutes} minutes` : "Not specified"}</strong></div>
            <div><small>SUPPORTING EVENTS</small><strong>{supporting.length}</strong></div>
          </div>
        )}
        {detailed && (f.limitation || f.limitations) && (
          <div className="finding-limitation"><strong>Limitation</strong><p>{Array.isArray(f.limitations) ? f.limitations.join(" ") : f.limitation}</p></div>
        )}
        {detailed && f.alternative_explanations?.length > 0 && <div className="finding-limitation"><strong>Alternative explanations</strong><ul>{f.alternative_explanations.map((text, index) => <li key={index}>{text}</li>)}</ul></div>}
      </div>
    </article>
  );
}

function Event({ event: e, detailed = false }) {
  const file = String(e.source_type || "").toLowerCase().includes("file");
  const failure = String(e.action || "").toLowerCase().includes("failure");
  return (
    <article className={`event-row ${detailed ? "event-detailed" : ""}`}>
      <div className={`event-marker ${file ? "marker-file" : failure ? "marker-failure" : ""}`} />
      <div className="event-content">
        <div className="event-topline"><span>{formatTimestamp(e.timestamp)}</span><strong>{e.event_id || "EVENT"}</strong></div>
        <h4>{String(e.action || "event").replaceAll("_", " ")}</h4>
        <p>{e.account_id || "Unknown account"} <span>·</span> {e.source_type || "source"} <span>·</span> {e.object_reference || "—"}</p>
        {detailed && <div className="event-source">SOURCE REFERENCE <strong>{e.source_reference || "Not supplied"}</strong></div>}
        {detailed && <div className="event-source">SOURCE ID <strong>{e.source_id || "Not supplied"}</strong></div>}
        {detailed && Object.keys(e.attributes || {}).length > 0 && <details className="event-attributes"><summary>Additional source fields</summary><pre>{JSON.stringify(e.attributes, null, 2)}</pre></details>}
      </div>
      {detailed && <span className="event-type">{String(e.source_type || "EVENT").replaceAll("_", " ").toUpperCase()}</span>}
    </article>
  );
}


const DOSSIER_HASH =
  "D8EECC6620DF803F86A31E189A46D3BAD22D04560D8E92C03E69A6E46E75928C";
const PREVIOUS_HASH =
  "A98DF737E6D5A42D8E26F26D848E7A1668C05A61C9F1092CE3270706B63FAF16";
const CAPTURE_HASH =
  "25A72BDF10339F2C29916920C8B9501D294923108DE8F29B19ABA7CC001AB60D";

function DossierSection({ number, kicker, title, children }) {
  return (
    <section className="panel dossier-section">
      <div className="dossier-section-heading">
        <span className="dossier-number">{number}</span>
        <div>
          <span className="panel-kicker">{kicker}</span>
          <h3>{title}</h3>
        </div>
      </div>
      {children}
    </section>
  );
}

function DossierImage({ src, title, caption }) {
  return (
    <figure className="dossier-exhibit">
      <a href={src} target="_blank" rel="noreferrer" aria-label={`Open full-size exhibit: ${title}`}>
        <img src={src} alt={title} loading="lazy" />
      </a>
      <figcaption>
        <strong>{title}</strong>
        <span>{caption}</span>
        <a href={src} target="_blank" rel="noreferrer">Open full size ↗</a>
      </figcaption>
    </figure>
  );
}

function DossierFact({ label, value, mono = false }) {
  return (
    <div className="dossier-fact">
      <span>{label}</span>
      <strong className={mono ? "dossier-mono" : ""}>{value}</strong>
    </div>
  );
}

function CaseDossier({ caseId, report, onSelectEvent }) {
  if (caseId === "WIRESHARK-PRACTICE-001") {
    const observations = report.timeline || [];
    const frame = (number) => observations.find((event) => event.attributes?.frame_number === number);
    const keyFrames = [4, 13, 17, 18, 27, 38].map(frame).filter(Boolean);
    return <div className="network-dossier">
      <section className="dossier-hero network-dossier-hero">
        <div className="dossier-hero-top"><span className="dossier-overline">CASE RECORD / WIRESHARK-PRACTICE-001</span><span className="dossier-status">PUBLIC SAMPLE · NOT INCIDENT EVIDENCE</span></div>
        <div className="dossier-hero-body"><div><div className="dossier-case-label">EXAMINATION OBJECTIVE</div><h2>HTTP capture<br />practice examination</h2><p>Reconstruct the visible HTTP and DNS activity, preserve source frame references, and evaluate what the supplied packet material can and cannot establish.</p></div><div className="dossier-hero-index"><span>PCAP</span><strong>043</strong><i /></div></div>
        <div className="dossier-hero-footer"><span>43 FRAMES / ETHERNET PCAP 2.4</span><span>SHA-256 / {CAPTURE_HASH.slice(0, 16)}…</span><span>HUMAN ATTRIBUTION / NOT ESTABLISHED</span></div>
      </section>

      <div className="dossier-warning"><span className="dossier-warning-icon">!</span><div><strong>Scope and conclusion</strong><p>This is a public practice capture. The examined records show ordinary HTTP page retrieval and DNS resolution. They do not establish malicious activity, unauthorized access, exfiltration, or a human operator.</p></div></div>

      <DossierSection number="01" kicker="EVIDENCE RECEIPT" title="Capture identity and examination method">
        <div className="dossier-integrity-grid"><DossierFact label="ORIGINAL FILE" value="evidence/captures/http.cap" mono /><DossierFact label="SIZE" value="25,803 bytes" /><DossierFact label="SHA-256 / CURRENT RUN" value={CAPTURE_HASH} mono /><DossierFact label="PACKET TOOL" value={report.examination?.tool || "tcpdump (version recorded in export)"} /></div>
        <p className="dossier-copy">The hash calculated during this run matches the digest stored in the derived export. That supports current export-to-capture consistency; it is not comparison against an independently trusted acquisition baseline.</p>
        <a className="dossier-download" href="/evidence/http.cap" download>↓ Download the original practice capture</a>
      </DossierSection>

      <DossierSection number="02" kicker="OBSERVED PACKET RECORDS" title="Wireshark filter exhibits reconciled with packet summaries">
        <p className="dossier-copy">The supplied HTTP screenshot lists frames 4, 18, 27, and 38. The DNS screenshot lists frames 13 and 17. Chronicle retains these as annotations attributed to the screenshots while keeping tcpdump's per-frame summary for all 43 frames.</p>
        <div className="dossier-observation-grid">{keyFrames.map((event) => <article className="dossier-observation" key={event.event_id}>
          <span className="dossier-observation-label">FRAME {String(event.attributes.frame_number).padStart(2, "0")} / {event.attributes.protocol}</span>
          <h4>{event.action.replaceAll("_", " ")}</h4><p>{event.object_reference || event.attributes.decoded_summary}</p>
          <div className="event-source">SOURCE <strong>{event.source_reference}</strong></div>
          {event.attributes.annotation_source && <small>Annotation source: {event.attributes.annotation_source}</small>}
          <button type="button" className="text-button" onClick={() => onSelectEvent?.(event.event_id)}>Inspect this observation ↗</button>
        </article>)}</div>
        <div className="decoder-reconciliation"><strong>Decoder difference recorded</strong><p>tcpdump flags HTTP in adjacent TCP segments that do not appear as HTTP rows in the supplied Wireshark display-filter screenshot. Chronicle preserves that difference instead of silently treating the decoders as identical. Use Wireshark to independently inspect stream reassembly.</p></div>
      </DossierSection>

      <DossierSection number="03" kicker="SUPPORTING EXHIBITS" title="Wireshark analysis records">
        <div className="dossier-exhibit-grid"><DossierImage src="/evidence/screenshots/wireshark-http.png" title="HTTP display filter" caption="Supplied screenshot shows four displayed frames: 4, 18, 27, and 38."/><DossierImage src="/evidence/screenshots/wireshark-dns.png" title="DNS display filter" caption="Supplied screenshot shows query frame 13 and response frame 17."/></div>
      </DossierSection>

      <DossierSection number="04" kicker="OUT-OF-SCOPE EXHIBIT / C-001" title="Autopsy screenshot and missing source image">
        <p className="dossier-copy">The supplied Autopsy screenshot visibly lists `incident-note.txt` as a logical-file-set item and shows synthetic C-001 text. No disk image, Autopsy case database, or structured export was found in the repository. Chronicle has not performed an Autopsy examination; the screenshot is not evidence for this public network-sample case.</p>
        <DossierImage src="/evidence/screenshots/autopsy-evidence.png" title="Separate C-001 Autopsy exhibit" caption="Visual exhibit only · 107,722 bytes · SHA-256 52d4ad309a391ef4d759689c9cfcf9ee8991a002b5387ee499e1e8ce3408a7e4."/>
        <p className="dossier-copy">Structured filesystem analysis would require the original disk image or a validated artifact export, plus acquisition and case context.</p>
      </DossierSection>

      <section className="dossier-final-note"><span className="dossier-overline">SUPPORTED CONCLUSION</span><h3>Routine web and DNS activity is visible; incident attribution is not.</h3><p>The capture shows a client request for an Ethereal download page, DNS resolution, and HTTP responses. The available material does not support a claim of malicious intent or exfiltration. The client-reported User-Agent string does not independently identify the operating system or person.</p></section>
    </div>;
  }
  if (caseId === "OPERATION-GLASSHOUSE") {
    return <div className="dossier">
      <section className="panel dossier-section"><span className="panel-kicker">SYNTHETIC CASE BRIEF</span>
        <h3>Operation Glasshouse</h3><p>{report?.scenario || "Synthetic scenario of suspected account access and possible file staging and transfer."}</p>
        <p className="method-note-text">All identities, systems, records, and observations in this case are generated for academic demonstration. The dataset cannot identify a real person or establish unauthorized access.</p>
        <div className="dossier-question-grid"><div className="dossier-question"><span>01</span><strong>Scope</strong><p>240 synthetic events across authentication, endpoint activity, and network observations.</p></div><div className="dossier-question"><span>02</span><strong>Alternative</strong><p>A scheduled service-account backup is included as a competing benign sequence.</p></div><div className="dossier-question"><span>03</span><strong>Limits</strong><p>Network rows are synthetic log observations; Chronicle does not inspect packet payloads.</p></div></div>
      </section>
      <section className="panel dossier-section"><span className="panel-kicker">SEPARATE TEAM MATERIALS</span><h3>Shreya's Wireshark practice workflow</h3><p>The project includes a public Wireshark sample capture, analysis notes, and HTTP/DNS screenshots contributed by Shreya. Those materials are separate from Operation Glasshouse and C-001.</p><p><strong>Capture digest:</strong> <code>{CAPTURE_HASH}</code></p>
        <div className="dossier-exhibit-grid"><DossierImage src="/evidence/screenshots/wireshark-http.png" title="Wireshark HTTP view" caption="Supplied practice-capture screenshot."/><DossierImage src="/evidence/screenshots/wireshark-dns.png" title="Wireshark DNS view" caption="Supplied practice-capture screenshot."/><DossierImage src="/evidence/screenshots/autopsy-evidence.png" title="Autopsy exhibit" caption="Supplied C-001 synthetic note exhibit; separate case material."/></div>
      </section>
    </div>;
  }
  return (
    <div className="dossier">
      {caseId === "CHRONICLE-DEMO-001" && <div className="dossier-warning"><span className="dossier-warning-icon">!</span><div><strong>Separate reference dossier</strong><p>This page documents C-001 and Shreya’s public practice capture. Neither is evidence for the currently selected CHRONICLE-DEMO-001 case.</p></div></div>}
      <section className="dossier-hero">
        <div className="dossier-hero-top">
          <span className="dossier-overline">CHRONICLE / INVESTIGATION RECORD</span>
          <span className="dossier-status"><i /> SIMULATED CASE</span>
        </div>
        <div className="dossier-hero-body">
          <div>
            <div className="dossier-case-label">CASE FILE / C-001</div>
            <h2>Digital Forensic<br />Case Dossier</h2>
            <p>
              Controlled evidence, recorded observations and explicit limits
              on what the available material can establish.
            </p>
          </div>
          <div className="dossier-hero-index" aria-hidden="true">
            <span>CF</span><strong>001</strong><i />
          </div>
        </div>
        <div className="dossier-hero-footer">
          <span>SHA-256 / DOCUMENTED</span>
          <span>PROVENANCE / DISCLOSED</span>
          <span>ATTRIBUTION / NOT ESTABLISHED</span>
        </div>
      </section>

      <div className="dossier-warning">
        <span className="dossier-warning-icon">!</span>
        <div>
          <strong>Scope boundary</strong>
          <p>
            C-001 is a fictional test scenario. The included HTTP capture is
            a public practice sample and is not established as evidence from
            C-001. The exhibits below document supplied materials; they do
            not independently prove a real incident or identify a person.
          </p>
        </div>
      </div>

      <DossierSection number="01" kicker="CASE BRIEF" title="Purpose & investigation questions">
        <p className="dossier-copy">
          Chronicle demonstrates how controlled synthetic records can be
          inventoried, checked using SHA-256, placed on a chronological
          timeline and correlated using explainable rules.
        </p>
        <div className="dossier-question-grid">
          {[
            ["01", "Evidence inventory", "What records are available, and where did they originate?"],
            ["02", "Integrity", "Can a file's current content be compared with a recorded SHA-256 value?"],
            ["03", "Timeline", "What sequence can be reconstructed from the supplied timestamps?"],
            ["04", "Correlation", "Which events are linked by documented rules and supporting records?"],
          ].map(([n, title, text]) => (
            <div className="dossier-question" key={n}>
              <span>{n}</span><strong>{title}</strong><p>{text}</p>
            </div>
          ))}
        </div>
      </DossierSection>

      <DossierSection number="02" kicker="INTEGRITY RECORD" title="Hash review & audit note">
        <div className="dossier-integrity-grid">
          <DossierFact label="EVIDENCE FILE" value="evidence/synthetic/incident-note.txt" mono />
          <DossierFact label="EVIDENCE TYPE" value="Synthetic text fixture" />
          <DossierFact label="ALGORITHM" value="SHA-256" />
          <DossierFact label="REVIEW VALUE" value={DOSSIER_HASH} mono />
        </div>
        <div className="dossier-hash-block">
          <span className="dossier-overline">CURRENTLY RECORDED SHA-256</span>
          <code>{DOSSIER_HASH}</code>
          <button type="button" onClick={() => navigator.clipboard?.writeText(DOSSIER_HASH)}>
            Copy hash
          </button>
        </div>
        <div className="dossier-audit-note">
          <strong>Recorded discrepancy — cause unknown</strong>
          <p>The earlier manifest value was:</p>
          <code>{PREVIOUS_HASH}</code>
          <p>
            During review, that value did not match the independently
            calculated value shown above. The investigation notes state that
            the evidence file was not modified; the reason for the discrepancy
            has not been established. The current hash records the file's
            content at review time and does not establish its historical integrity.
          </p>
        </div>
      </DossierSection>

      <DossierSection number="03" kicker="NETWORK EXAMINATION NOTES" title="Public Wireshark practice capture">
        <div className="dossier-provenance">
          <span className="dossier-sample-label">PUBLIC SAMPLE / NOT C-001 EVIDENCE</span>
          <p>
            <strong>File:</strong> evidence/captures/http.cap<br />
            <strong>Recorded tool version:</strong> Wireshark 4.6.9<br />
            <strong>Packets:</strong> 43 total; 4 shown with the HTTP filter and
            2 with the DNS filter, according to the supplied analysis notes.
          </p>
          <p>
            <strong>Recorded capture SHA-256:</strong>
            <code>{CAPTURE_HASH}</code>
          </p>
            <a className="dossier-download" href="/evidence/http.cap" download>
            ↓ Download public practice capture
          </a>
        </div>

        <div className="dossier-observation-grid">
          <article className="dossier-observation">
            <span className="dossier-observation-label">OBSERVATION / HTTP</span>
            <h4>Request & response records</h4>
            <ul>
              <li>Packet 4 contains a GET request for <code>/download.html</code>.</li>
              <li>Recorded source: <code>145.254.160.237:3372</code>.</li>
              <li>Recorded destination: <code>65.208.228.223:80</code>.</li>
              <li>Host header: <code>www.ethereal.com</code>.</li>
              <li>The request's User-Agent reports Windows NT 5.1.</li>
              <li>Packets 27 and 38 display HTTP 200 OK responses.</li>
            </ul>
          </article>
          <article className="dossier-observation">
            <span className="dossier-observation-label">OBSERVATION / DNS</span>
            <h4>Query & response records</h4>
            <ul>
              <li>Packet 13 queries for <code>pagead2.googlesyndication.com</code>.</li>
              <li>Recorded DNS server: <code>145.253.2.203</code>.</li>
              <li>Packet 17 contains CNAME records for <code>pagead2.google.com.</code> and <code>pagead.google.akadns.net.</code>.</li>
              <li>Recorded IPv4 addresses: <code>216.239.59.104</code> and <code>216.239.59.99</code>.</li>
              <li>Recorded query and response times from capture start: 2.553672 s and 2.914190 s.</li>
            </ul>
          </article>
        </div>
        <div className="dossier-caveat">
          These are observations recorded in the supplied analysis notes.
          They do not independently establish malicious activity, user identity,
          or any relationship to C-001. A User-Agent is client-reported and
          does not independently verify the actual operating system.
        </div>
      </DossierSection>

      <DossierSection number="04" kicker="EXHIBIT REGISTER" title="Supporting screenshots">
        <p className="dossier-copy">
          Supplied screenshots are presented as exhibits from the project
          materials. Their presence in this interface is not an independent
          validation of the underlying tool output.
        </p>
        <div className="dossier-exhibit-grid">
          <DossierImage
            src="/evidence/screenshots/autopsy-evidence.png"
            title="Exhibit A / Autopsy"
            caption="Supplied screenshot labelled as Autopsy evidence."
          />
          <DossierImage
            src="/evidence/screenshots/wireshark-http.png"
            title="Exhibit B / HTTP"
            caption="Supplied screenshot associated with the HTTP capture notes."
          />
          <DossierImage
            src="/evidence/screenshots/wireshark-dns.png"
            title="Exhibit C / DNS"
            caption="Supplied screenshot associated with the DNS capture notes."
          />
        </div>
      </DossierSection>

      <DossierSection number="05" kicker="REPRODUCIBLE METHOD" title="Investigation workflow">
        <div className="dossier-method-list">
          {[
            ["01", "Preserve", "Keep original evidence files intact and document their provenance."],
            ["02", "Fingerprint", "Calculate SHA-256 and record file details and discrepancies."],
            ["03", "Examine", "Inspect suitable artefacts with appropriate forensic tools and record actual steps."],
            ["04", "Normalise", "Build a timeline while documenting timestamp and timezone assumptions."],
            ["05", "Correlate", "Apply explainable rules and link each finding to supporting records."],
            ["06", "Report", "State uncertainties, limitations and what the evidence cannot establish."],
          ].map(([n, title, description]) => (
            <div className="dossier-method-step" key={n}>
              <span>{n}</span><div><strong>{title}</strong><p>{description}</p></div>
            </div>
          ))}
        </div>
      </DossierSection>

      <section className="dossier-final-note">
        <span className="dossier-overline">FORENSIC INTERPRETATION</span>
        <h3>Correlation is a lead, not a verdict.</h3>
        <p>
          A matching timestamp or account identifier does not by itself prove
          identity, intent, authorisation or causation. A hash can help detect
          content changes relative to a known value, but does not independently
          prove authenticity. The case narrative records findings as pending
          examination; this dossier does not invent additional findings.
        </p>
      </section>
    </div>
  );
}


function EvidenceTable({ files, detailed = false, artifactMetadata = {}, examination = null }) {
  if (!files.length) return <Empty text="No evidence files are present in the report." />;
  return (
    <div className="table-wrap"><table className="evidence-table">
      <thead><tr><th>ARTIFACT</th>{detailed && <th>CLASS / PROVENANCE</th>}<th>SIZE</th><th>SHA-256 FINGERPRINT</th>{detailed && <th>RUN / DETAILS</th>}</tr></thead>
      <tbody>{files.map((file, i) => (
        <tr key={`${file.relative_path}-${i}`}>
          <td><span className="file-icon">▤</span><strong>{file.relative_path || file.path || "Evidence file"}</strong>{detailed && <small className="artifact-identity">{artifactMetadata[file.relative_path]?.artifact_type || "Evidence file"}</small>}</td>
          {detailed && <td className="artifact-provenance">{artifactMetadata[file.relative_path]?.provenance || "Provenance not recorded"}</td>}
          <td className="mono">{formatBytes(file.size_bytes)}</td>
          <td><code className="hash">{file.sha256 || "Not provided"}</code></td>
          {detailed && <td className="mono">{file.relative_path === examination?.capture_path && examination?.capture_sha256 === file.sha256 ? <span className="integrity-match">● DIGEST MATCHED TO EXPORT</span> : <>HASHED THIS RUN<br />{formatTimestamp(file.collected_at_utc)}</>}</td>}
        </tr>
      ))}</tbody>
    </table></div>
  );
}

function Empty({ text }) {
  return <div className="empty-state">{text}</div>;
}

function formatTimestamp(value) {
  if (!value) return "Timestamp unavailable";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
}

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
}

function formatBytes(value) {
  if (value == null || value === "") return "—";
  const bytes = Number(value);
  if (!Number.isFinite(bytes)) return String(value);
  return bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KB`;
}

function downloadReport(report) {
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${report.case_id}_report.json`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function downloadMarkdownReport(report) {
  const artifactMetadata = report.evidence_summary?.artifact_metadata || {};
  const lines = [
    `# Chronicle Investigation Report — ${report.case_id}`,
    "", `**Case:** ${report.case_name || report.case_id}`, `**Case type:** ${report.case_kind || "not recorded"}`,
    `**Generated (UTC):** ${report.generated_at_utc}`,
    "", "## Scope", report.scenario || "",
    "", "## Integrity statement", report.evidence_summary?.integrity_status || "No integrity statement recorded.",
    "", "## Evidence inventory",
    ...(report.evidence_summary?.files || []).map(file => { const meta = artifactMetadata[file.relative_path] || {}; return `- **${file.relative_path}** — ${meta.artifact_type || "artifact type not recorded"}; ${file.size_bytes} bytes; SHA-256 ${file.sha256}. ${meta.provenance || "Provenance not recorded."}`; }),
    ...(report.examination ? ["", "## Examination method", report.examination.method || "", `Tool: ${report.examination.tool || "not recorded"}`, `Time treatment: ${report.examination.timezone_note || "not recorded"}`, `Capture digest: ${report.examination.capture_sha256 || "not recorded"}`] : []),
    "", `## Timeline (${report.timeline?.length || 0} events)`,
    ...(report.timeline || []).map(event => `- ${event.timestamp} | ${event.event_id} | ${event.source_id || ""} | ${event.action} | ${event.source_reference}`),
    "", `## Findings (${report.findings?.length || 0})`,
    ...(report.findings || []).flatMap(finding => [`### ${finding.rule_id}: ${finding.title}`, "", finding.explanation || "", "Supporting records:", ...(finding.supporting_records || []).map(record => `- ${record.event_id} | ${record.timestamp} | ${record.source_reference}`), "Alternative explanations:", ...(finding.alternative_explanations || []).map(item => `- ${item}`), `Limitation: ${finding.limitation || "Not separately recorded."}`, ""]),
    "## Limitations", ...(report.limitations || []).map(text => `- ${text}`), "",
  ];
  const blob = new Blob([lines.join("\n")], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = `${report.case_id}_report.md`; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export default App;
