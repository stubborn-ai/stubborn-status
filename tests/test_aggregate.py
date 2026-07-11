"""Tests for stubborn-status aggregation."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from stubborn_status.aggregate import run_status
from stubborn_status.cli import app
from stubborn_status.models import DOCTOR_REPORT_SCHEMA, STATUS_REPORT_SCHEMA
from stubborn_status.registry import DOCTOR_REGISTRY

SAMPLE_REPORT = {
    "schema": DOCTOR_REPORT_SCHEMA,
    "package": "stubborn-stub",
    "command": "stubborn doctor",
    "version": "0.9.0b6",
    "cwd": "/tmp",
    "exit": 0,
    "checks": [{"id": "core.import", "status": "pass", "message": "ok", "hint": None}],
}


@pytest.fixture()
def mock_subprocess(monkeypatch: pytest.MonkeyPatch) -> dict[str, MagicMock]:
    calls: dict[str, MagicMock] = {}

    def fake_run(cmd, **kwargs):
        executable = cmd[0]
        mock = MagicMock()
        mock.stdout = json.dumps(SAMPLE_REPORT | {"package": _package_for(executable)})
        mock.stderr = ""
        mock.returncode = 0
        calls[executable] = mock
        return mock

    monkeypatch.setattr("stubborn_status.aggregate.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr("stubborn_status.aggregate.subprocess.run", fake_run)
    return calls


def _package_for(executable: str) -> str:
    mapping = {spec.argv[0]: spec.package for spec in DOCTOR_REGISTRY}
    return mapping[executable]


def test_status_report_schema(tmp_path: Path, mock_subprocess) -> None:
    report = run_status(tmp_path, only={"stubborn-stub"})
    payload = report.to_dict()
    assert payload["schema"] == STATUS_REPORT_SCHEMA
    assert payload["exit"] == 0
    assert payload["doctors"][0]["state"] == "ran"


def test_not_installed_is_non_blocking_for_optional(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("stubborn_status.aggregate.shutil.which", lambda name: None)
    report = run_status(tmp_path)
    states = {entry.package: entry.state for entry in report.doctors}
    assert states["stubborn-stub"] == "not_installed"
    assert report.exit_code() == 1


def test_required_mcp_affects_exit(tmp_path: Path, mock_subprocess) -> None:
    report = run_status(
        tmp_path,
        only={"stubborn-stub", "stubborn-mcp"},
        require={"stubborn-mcp"},
    )
    assert report.exit_code() == 0


def test_failed_to_run_blocks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("stubborn_status.aggregate.shutil.which", lambda name: f"/usr/bin/{name}")

    def bad_run(cmd, **kwargs):
        mock = MagicMock(stdout="not-json", stderr="", returncode=1)
        return mock

    monkeypatch.setattr("stubborn_status.aggregate.subprocess.run", bad_run)
    report = run_status(tmp_path, only={"stubborn-stub"})
    assert report.doctors[0].state == "failed_to_run"
    assert report.exit_code() == 1


def test_cli_json(tmp_path: Path, mock_subprocess) -> None:
    from typer.testing import CliRunner

    result = CliRunner().invoke(
        app,
        ["--json", "--only", "stubborn-stub", str(tmp_path)],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema"] == STATUS_REPORT_SCHEMA
