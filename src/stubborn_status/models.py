"""Status report models (ADR-016)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

STATUS_REPORT_SCHEMA = "stubborn.status-report/v1"
AGGREGATOR_ID = "stubborn-status"
DOCTOR_REPORT_SCHEMA = "stubborn.doctor-report/v1"

DoctorState = Literal["ran", "not_installed", "skipped", "failed_to_run"]


@dataclass(frozen=True)
class DoctorSpec:
    package: str
    argv: tuple[str, ...]
    required: bool = False


@dataclass
class DoctorEntry:
    package: str
    state: DoctorState
    report: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "package": self.package,
            "state": self.state,
            "report": self.report,
            "error": self.error,
        }


@dataclass
class StatusReport:
    version: str
    cwd: str
    doctors: list[DoctorEntry] = field(default_factory=list)
    required_packages: tuple[str, ...] = ("stubborn-stub",)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": STATUS_REPORT_SCHEMA,
            "aggregator": AGGREGATOR_ID,
            "version": self.version,
            "cwd": self.cwd,
            "exit": self.exit_code(),
            "doctors": [entry.to_dict() for entry in self.doctors],
        }

    def exit_code(self) -> int:
        blocking = False
        warning = False
        required = set(self.required_packages)

        for entry in self.doctors:
            if entry.state == "skipped":
                continue
            if entry.package in required and entry.state in {"not_installed", "failed_to_run"}:
                blocking = True
            if entry.state == "failed_to_run":
                blocking = True
            if entry.report is None:
                continue
            child_exit = int(entry.report.get("exit", 0))
            if entry.package in required and child_exit == 1:
                blocking = True
            if child_exit == 2:
                warning = True
            for check in entry.report.get("checks", []):
                if check.get("status") == "warn":
                    warning = True
                if check.get("status") == "fail" and entry.package in required:
                    blocking = True

        if blocking:
            return 1
        if warning:
            return 2
        return 0
