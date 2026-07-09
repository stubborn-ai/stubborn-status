"""Doctor CLI registry for stubborn-status."""

from __future__ import annotations

from stubborn_status.models import DoctorSpec

DOCTOR_REGISTRY: tuple[DoctorSpec, ...] = (
    DoctorSpec(package="stubborn-stub", argv=("stubborn", "doctor"), required=True),
    DoctorSpec(package="stubborn-mcp", argv=("stubborn-mcp", "doctor")),
    DoctorSpec(package="stubborn-watch", argv=("stubborn-watch", "doctor")),
    DoctorSpec(package="stubborn-indexer", argv=("stubborn-indexer", "doctor")),
)


def registry_by_package() -> dict[str, DoctorSpec]:
    return {spec.package: spec for spec in DOCTOR_REGISTRY}
