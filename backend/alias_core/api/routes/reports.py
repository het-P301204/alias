"""Report generation endpoint — JSON, CSV, HTML formats."""
import csv
import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from alias_core.database.init_db import get_db
from alias_core.database.queries import get_experiment
from alias_core.config.settings import settings

router = APIRouter()


def _build_json_report(result) -> dict:
    return {
        "report_format": "json",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "application_version": settings.app_version,
        "executive_summary": (
            f"Experiment {result.id} ran scenario '{result.scenario_id.value}' "
            f"in {result.mode.value} mode and completed with status '{result.status.value}'."
        ),
        "environment": {
            "python_version": "3.12",
            "schema_version": "0.1.0",
            "timestamp": result.started_at,
        },
        "scenario": result.scenario_id.value,
        "mode": result.mode.value,
        "methodology": "Execute GraphQL query against lab endpoint; compare response to expected outcome.",
        "expected_outcome": result.expected_outcome,
        "actual_outcome": result.actual_outcome,
        "evidence": [e.model_dump() for e in result.evidence],
        "defensive_control_result": result.defensive_control_result.model_dump() if result.defensive_control_result else None,
        "error": result.error,
        "duration_ms": result.duration_ms,
        "reproducibility": result.reproducibility_metadata,
        "limitations": "All results are based on intentionally vulnerable synthetic lab fixtures for educational purposes only.",
        "remediation": _remediation(result.scenario_id.value),
    }


def _build_csv_report(result) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Field", "Value"])
    writer.writerow(["experiment_id", result.id])
    writer.writerow(["scenario", result.scenario_id.value])
    writer.writerow(["mode", result.mode.value])
    writer.writerow(["status", result.status.value])
    writer.writerow(["started_at", result.started_at])
    writer.writerow(["completed_at", result.completed_at or ""])
    writer.writerow(["duration_ms", result.duration_ms or ""])
    writer.writerow(["expected_outcome", result.expected_outcome])
    writer.writerow(["actual_outcome", result.actual_outcome or ""])
    writer.writerow(["evidence_count", len(result.evidence)])
    writer.writerow(["error", result.error or ""])
    writer.writerow(["remediation", _remediation(result.scenario_id.value)])
    return buf.getvalue()


def _build_html_report(result) -> str:
    evidence_html = "".join(
        f"<li><strong>{e.label}</strong> ({e.type}): <code>{json.dumps(e.data)}</code></li>"
        for e in result.evidence
    )
    defense_html = ""
    if result.defensive_control_result:
        d = result.defensive_control_result
        verified_badge = "✅ Verified" if d.verified else "❌ Not Verified"
        defense_html = f"<p>{verified_badge} — {d.description}</p>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ALIAS Report — {result.id[:8]}</title>
<style>
  body {{ font-family: Inter, sans-serif; background: #171615; color: #F5F0E8; padding: 2rem; max-width: 900px; margin: auto; }}
  h1, h2 {{ color: #D5A45B; }}
  code {{ background: #282624; padding: 2px 6px; border-radius: 3px; font-family: 'JetBrains Mono', monospace; }}
  .badge-vuln {{ color: #B84D43; }} .badge-hard {{ color: #8EAA91; }}
  table {{ border-collapse: collapse; width: 100%; }} td, th {{ border: 1px solid #444; padding: 8px; }}
  ul {{ line-height: 1.8; }}
</style>
</head>
<body>
<h1>ALIAS Security Research Report</h1>
<p><em>Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} · Version {settings.app_version}</em></p>

<h2>Executive Summary</h2>
<p>Experiment <code>{result.id}</code> ran scenario <strong>{result.scenario_id.value}</strong>
in <span class="{'badge-hard' if result.mode.value == 'hardened' else 'badge-vuln'}">{result.mode.value}</span> mode.
Status: <strong>{result.status.value}</strong>. Duration: {result.duration_ms or 'N/A'} ms.</p>

<h2>Methodology</h2>
<p>Execute GraphQL query against lab endpoint; compare response to expected outcome.</p>

<h2>Expected vs Observed</h2>
<table>
<tr><th>Expected</th><th>Observed</th></tr>
<tr><td>{result.expected_outcome}</td><td>{result.actual_outcome or '—'}</td></tr>
</table>

<h2>Evidence</h2>
<ul>{evidence_html or '<li>No evidence recorded.</li>'}</ul>

<h2>Defensive Control</h2>
{defense_html or '<p>No defensive control result recorded.</p>'}

<h2>Remediation</h2>
<p>{_remediation(result.scenario_id.value)}</p>

<h2>Limitations</h2>
<p>All results are based on intentionally vulnerable synthetic lab fixtures for educational purposes only.
Do not use this tooling against real or production systems.</p>
</body>
</html>"""


def _remediation(scenario_id: str) -> str:
    _MAP = {
        "introspection": "Disable introspection in production. Use allowlist-based schema exposure for tooling.",
        "alias-authorization": "Verify record ownership inside each resolver, not just at authentication boundaries.",
        "batching": "Enforce per-request operation count limits server-side, independent of HTTP rate limiting.",
        "query-complexity": "Apply depth and complexity limits using schema extensions. Reject over-budget queries before execution.",
        "blind-recovery": "Return generic error messages; log verbose errors server-side only.",
        "field-authorization": "Check caller permissions in every resolver for sensitive fields; never trust client-side filtering.",
    }
    return _MAP.get(scenario_id, "Follow GraphQL security best practices.")


@router.get("/reports/{experiment_id}")
async def get_report(experiment_id: str, format: str = Query("json", pattern="^(json|csv|html)$")):
    async with get_db() as db:
        result = await get_experiment(db, experiment_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id!r} not found")

    if format == "json":
        return Response(
            content=json.dumps(_build_json_report(result), indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="alias-report-{experiment_id[:8]}.json"'},
        )
    elif format == "csv":
        return Response(
            content=_build_csv_report(result),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="alias-report-{experiment_id[:8]}.csv"'},
        )
    else:
        return Response(
            content=_build_html_report(result),
            media_type="text/html",
        )
