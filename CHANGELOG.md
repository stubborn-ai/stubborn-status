# Changelog

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0b1] - 2026-07-09

### Added

- **`stubborn-status` CLI** — aggregate federated `doctor --json` via subprocess per [ADR-016](https://github.com/stubborn-ai/stubborn/blob/main/docs/adr/ADR-016-doctor-status-aggregation.md).
- Static doctor registry for `stubborn-stub`, `stubborn-mcp`, `stubborn-watch` (optional), and future `stubborn-indexer`.
- Status Report v1 (`stubborn.status-report/v1`) with aggregate exit codes and graceful `not_installed` handling.
- Unit tests with mocked subprocess output.

[0.1.0b1]: https://github.com/stubborn-ai/stubborn-status/releases/tag/v0.1.0b1
