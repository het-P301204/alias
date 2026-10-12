"""Report generation: JSON, CSV, and HTML formats for ExperimentResult objects."""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alias_core.experiments.models import ExperimentResult

APP_VERSION = "0.1.0"
DISCLAIMER = (
    "Findings are from a synthetic local lab environment for educational research only. "
    "Results do not indicate real-world vulnerabilities. "
    "Do not use this tooling against production or third-party systems."
)

_REMEDIATION: dict[str, str] = {
    "introspection": (
        "Disable introspection in production. Implement field-level authorization "
        "instead of relying on schema obscurity."
    ),
    "alias-authorization": (
        "Verify object ownership in every resolver. "
        "Check record.user_id == authenticated_user.id before returning data."
    ),
    "batching": (
        "Enforce operation count limits at the GraphQL layer, not just HTTP rate limiting."
    ),
    "query-complexity": (
        "Implement query depth and complexity analysis. "
        "Reject queries exceeding configured budgets before execution."
    ),
    "blind-recovery": (
        "Suppress verbose validation suggestions in production. "
        "Return generic error messages that do not hint at valid field names or entity IDs."
    ),
    "field-authorization": (
        "Apply permission checks consistently in every sensitive field resolver. "
        "Never rely on UI-level visibility to protect data."
    ),
}


def _get_remediation(scenario_id: str) -> str:
    return _REMEDIATION.get(scenario_id, "Follow GraphQL security best practices.")


def _build_summary(result: "ExperimentResult") -> str:
    status_phrase = {
        "completed": "completed successfully",
        "failed": "failed",
        "timeout": "timed out",
        "cancelled": "was cancelled",
    }.get(result.status.value, result.status.value)

    return (
        f"Experiment {result.id} ran scenario '{result.scenario_id.value}' "
        f"in {result.mode.value} mode and {status_phrase}. "
        f"{len(result.evidence)} evidence item(s) were collected "
        f"over {result.duration_ms or 0} ms."
    )


def generate_json(result: "ExperimentResult") -> str:
    """Return a pretty-printed JSON security research report."""
    report = {
        "report_type": "ALIAS Security Research Report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "app_version": APP_VERSION,
        "disclaimer": DISCLAIMER,
        "executive_summary": _build_summary(result),
        "environment": {
            "scenario_id": result.scenario_id.value,
            "mode": result.mode.value,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "duration_ms": result.duration_ms,
        },
        "methodology": (
            "Execute GraphQL queries against a local synthetic lab endpoint; "
            "compare responses to expected outcomes; collect evidence of the vulnerability."
        ),
        "findings": {
            "expected": result.expected_outcome,
            "actual": result.actual_outcome,
            "status": result.status.value,
            "error": result.error,
        },
        "evidence": [e.model_dump() for e in result.evidence],
        "defense_status": (
            result.defensive_control_result.model_dump()
            if result.defensive_control_result
            else None
        ),
        "remediation": _get_remediation(result.scenario_id.value),
        "reproducibility": result.reproducibility_metadata,
        "limitations": DISCLAIMER,
    }
    return json.dumps(report, indent=2, default=str)


def generate_csv(result: "ExperimentResult") -> str:
    """Return evidence items as CSV rows, one row per item."""
    output = io.StringIO()
    fieldnames = ["type", "label", "timestamp", "data"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    if result.evidence:
        for ev in result.evidence:
            writer.writerow({
                "type": ev.type,
                "label": ev.label,
                "timestamp": ev.timestamp,
                "data": json.dumps(ev.data, default=str),
            })
    else:
        # Emit a summary row when there is no evidence
        writer.writerow({
            "type": "summary",
            "label": f"{result.scenario_id.value} ({result.mode.value})",
            "timestamp": result.completed_at or result.started_at,
            "data": json.dumps({
                "status": result.status.value,
                "expected": result.expected_outcome,
                "actual": result.actual_outcome,
            }),
        })

    return output.getvalue()


def generate_html(result: "ExperimentResult") -> str:
    """Return a self-contained HTML security report with embedded CSS."""
    evidence_rows = "".join(
        f"""
        <tr>
          <td>{ev.type}</td>
          <td>{ev.label}</td>
          <td><code>{ev.timestamp}</code></td>
          <td><pre class="data">{json.dumps(ev.data, indent=2, default=str)}</pre></td>
        </tr>"""
        for ev in result.evidence
    ) or "<tr><td colspan='4'>No evidence recorded.</td></tr>"

    defense_html = ""
    if result.defensive_control_result:
        d = result.defensive_control_result
        badge = "✅ Verified" if d.verified else "❌ Not Verified"
        defense_html = f"""
        <section>
          <h2>Defensive Control</h2>
          <p><strong>{d.control_id}</strong> — {badge}</p>
          <p>{d.description}</p>
          <pre class="data">{json.dumps(d.details, indent=2, default=str)}</pre>
        </section>"""

    mode_class = "badge-hardened" if result.mode.value == "hardened" else "badge-vulnerable"
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ALIAS Report — {result.id[:8]}</title>
  <style>
    :root {{
      --bg: #171615;
      --surface: #211f1e;
      --border: #3a3633;
      --text: #f5f0e8;
      --muted: #a09080;
      --accent: #d5a45b;
      --danger: #b84d43;
      --success: #8eaa91;
      --mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: Inter, system-ui, sans-serif;
      font-size: 15px;
      line-height: 1.6;
      padding: 2rem 1rem;
    }}
    .container {{ max-width: 960px; margin: auto; }}
    h1 {{ color: var(--accent); font-size: 1.8rem; margin-bottom: 0.25rem; }}
    h2 {{ color: var(--accent); font-size: 1.1rem; margin: 1.5rem 0 0.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.25rem; }}
    p {{ margin: 0.5rem 0; }}
    section {{ margin: 1.5rem 0; }}
    .meta {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 1.5rem; }}
    .badge-vulnerable {{ display: inline-block; background: var(--danger); color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }}
    .badge-hardened {{ display: inline-block; background: var(--success); color: #111; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }}
    table {{ border-collapse: collapse; width: 100%; margin: 0.75rem 0; font-size: 0.9rem; }}
    th, td {{ border: 1px solid var(--border); padding: 8px 12px; text-align: left; vertical-align: top; }}
    th {{ background: var(--surface); color: var(--accent); }}
    pre.data {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 8px;
      font-family: var(--mono);
      font-size: 0.78rem;
      white-space: pre-wrap;
      word-break: break-word;
      max-height: 200px;
      overflow-y: auto;
      margin: 0;
    }}
    code {{ font-family: var(--mono); background: var(--surface); padding: 1px 5px; border-radius: 3px; font-size: 0.85em; }}
    .disclaimer {{
      background: var(--surface);
      border-left: 3px solid var(--accent);
      padding: 0.75rem 1rem;
      font-size: 0.85rem;
      color: var(--muted);
      border-radius: 0 4px 4px 0;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>ALIAS Security Research Report</h1>
    <p class="meta">
      Generated {generated} · Version {APP_VERSION} ·
      Experiment <code>{result.id}</code>
    </p>

    <section>
      <h2>Executive Summary</h2>
      <p>{_build_summary(result)}</p>
    </section>

    <section>
      <h2>Environment</h2>
      <table>
        <tr><th>Scenario</th><td>{result.scenario_id.value}</td></tr>
        <tr><th>Mode</th><td><span class="{mode_class}">{result.mode.value}</span></td></tr>
        <tr><th>Status</th><td>{result.status.value}</td></tr>
        <tr><th>Duration</th><td>{result.duration_ms or 0} ms</td></tr>
        <tr><th>Started</th><td>{result.started_at or '—'}</td></tr>
        <tr><th>Completed</th><td>{result.completed_at or '—'}</td></tr>
      </table>
    </section>

    <section>
      <h2>Methodology</h2>
      <p>Execute GraphQL queries against a local synthetic lab endpoint; compare responses to expected outcomes; collect evidence of the vulnerability.</p>
    </section>

    <section>
      <h2>Expected vs Observed</h2>
      <table>
        <tr><th>Expected</th><td>{result.expected_outcome or '—'}</td></tr>
        <tr><th>Observed</th><td>{result.actual_outcome or '—'}</td></tr>
        {f'<tr><th>Error</th><td style="color:var(--danger)">{result.error}</td></tr>' if result.error else ''}
      </table>
    </section>

    <section>
      <h2>Evidence ({len(result.evidence)} items)</h2>
      <table>
        <tr><th>Type</th><th>Label</th><th>Timestamp</th><th>Data</th></tr>
        {evidence_rows}
      </table>
    </section>

    {defense_html}

    <section>
      <h2>Remediation</h2>
      <p>{_get_remediation(result.scenario_id.value)}</p>
    </section>

    <section>
      <h2>Limitations</h2>
      <div class="disclaimer">{DISCLAIMER}</div>
    </section>
  </div>
</body>
</html>"""
