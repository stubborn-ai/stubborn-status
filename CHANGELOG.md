# Changelog

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.10.0b2] - 2026-07-12

### Changed

- Coordinated program release **0.10.0b2** (Layer 1 external-user hardening milestone).

## [0.10.0b1] - 2026-07-12

### Changed

- Align program-wide PyPI version line to **0.10.0b1** (unified release matrix across core and satellite packages).

## [0.1.0b1] - 2026-07-09

### Added

- **`stubborn-status` CLI** — aggregate federated `doctor --json` via subprocess per [ADR-016](https://github.com/stubborn-ai/stubborn/blob/main/docs/adr/ADR-016-doctor-status-aggregation.md).
- Static doctor registry for `stubborn-stub`, `stubborn-mcp`, `stubborn-watch` (optional), and future `stubborn-indexer`.
- Status Report v1 (`stubborn.status-report/v1`) with aggregate exit codes and graceful `not_installed` handling.
- Unit tests with mocked subprocess output.

[0.10.0b2]: https://github.com/stubborn-ai/stubborn-status/compare/v0.10.0b1...v0.10.0b2
[0.10.0b1]: https://github.com/stubborn-ai/stubborn-status/compare/v0.1.0b1...v0.10.0b1
[0.1.0b1]: https://github.com/stubborn-ai/stubborn-status/releases/tag/v0.1.0b1
