"""Format merged status reports."""

from __future__ import annotations

import json

from stubborn_status.models import StatusReport


def format_text(report: StatusReport) -> str:
    lines = [f"stubborn-status — {report.cwd}", ""]
    for entry in report.doctors:
        lines.append(f"[{entry.package}] state={entry.state}")
        if entry.error:
            lines.append(f"  ✗ {entry.error}")
            lines.append("")
            continue
        if entry.state == "not_installed":
            lines.append("  · CLI not on PATH")
            lines.append("")
            continue
        if entry.state == "skipped":
            lines.append("  · skipped")
            lines.append("")
            continue
        if entry.report is None:
            lines.append("")
            continue

        for check in entry.report.get("checks", []):
            prefix = _status_prefix(str(check.get("status", "info")))
            check_id = check.get("id", "unknown")
            message = check.get("message", "")
            lines.append(f"  {prefix} {check_id}: {message}")
        lines.append("")

    lines.append(f"Exit {report.exit_code()}")
    return "\n".join(lines)


def format_json(report: StatusReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def _status_prefix(status: str) -> str:
    return {"pass": "✓", "warn": "⚠", "fail": "✗", "skip": "·", "info": "·"}.get(status, "·")
