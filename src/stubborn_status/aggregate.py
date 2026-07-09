"""Invoke federated doctors via subprocess and merge reports."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

from stubborn_status import __version__
from stubborn_status.models import (
    DOCTOR_REPORT_SCHEMA,
    DoctorEntry,
    DoctorSpec,
    StatusReport,
)
from stubborn_status.registry import DOCTOR_REGISTRY


def run_status(
    project_root: Path,
    *,
    db_path: Path | None = None,
    workspace: str | None = None,
    require: set[str] | None = None,
    only: set[str] | None = None,
    timeout_seconds: float = 60.0,
) -> StatusReport:
    root = project_root.resolve()
    required = {"stubborn-stub"}
    if require:
        required.update(require)

    selected = _selected_specs(only)
    report = StatusReport(
        version=__version__,
        cwd=str(root),
        required_packages=tuple(sorted(required)),
    )

    forward_args = _forward_args(db_path=db_path, workspace=workspace)
    for spec in DOCTOR_REGISTRY:
        if spec.package not in selected:
            report.doctors.append(DoctorEntry(package=spec.package, state="skipped"))
            continue
        report.doctors.append(
            _run_doctor(spec, root, forward_args=forward_args, timeout_seconds=timeout_seconds),
        )
    return report


def _selected_specs(only: set[str] | None) -> set[str]:
    if only is None:
        return {spec.package for spec in DOCTOR_REGISTRY}
    return only


def _forward_args(*, db_path: Path | None, workspace: str | None) -> list[str]:
    args: list[str] = []
    if db_path is not None:
        args.extend(["--db", str(db_path)])
    if workspace is not None:
        args.extend(["--workspace", workspace])
    return args


def _run_doctor(
    spec: DoctorSpec,
    cwd: Path,
    *,
    forward_args: list[str],
    timeout_seconds: float,
) -> DoctorEntry:
    executable = spec.argv[0]
    if shutil.which(executable) is None:
        return DoctorEntry(package=spec.package, state="not_installed")

    cmd = [
        *spec.argv,
        str(cwd),
        "--json",
        "--no-fix-hint",
        "-q",
        *forward_args,
    ]
    try:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return DoctorEntry(
            package=spec.package,
            state="failed_to_run",
            error=f"timeout after {timeout_seconds}s: {shlex.join(cmd)}",
        )
    except OSError as exc:
        return DoctorEntry(
            package=spec.package,
            state="failed_to_run",
            error=str(exc),
        )

    stdout = (completed.stdout or "").strip()
    if not stdout:
        stderr = (completed.stderr or "").strip()
        return DoctorEntry(
            package=spec.package,
            state="failed_to_run",
            error=stderr or f"empty stdout from {shlex.join(cmd)}",
        )

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return DoctorEntry(
            package=spec.package,
            state="failed_to_run",
            error=f"invalid JSON from {executable}: {exc}",
        )

    if payload.get("schema") != DOCTOR_REPORT_SCHEMA:
        return DoctorEntry(
            package=spec.package,
            state="failed_to_run",
            error=f"unexpected schema from {executable}: {payload.get('schema')!r}",
        )

    if int(payload.get("exit", 0)) != completed.returncode:
        payload = dict(payload)
        payload["exit"] = completed.returncode

    return DoctorEntry(package=spec.package, state="ran", report=payload)
