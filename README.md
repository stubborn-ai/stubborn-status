# stubborn-status

**Beta `0.10.0b2`** — aggregate federated `doctor --json` reports from Stubborn ecosystem packages.

[![PyPI](https://img.shields.io/pypi/v/stubborn-status)](https://pypi.org/project/stubborn-status/)

Part of [stubborn-ai](https://github.com/stubborn-ai). Spec: [ADR-016](https://github.com/stubborn-ai/stubborn/blob/main/docs/adr/ADR-016-doctor-status-aggregation.md).

## Install

```bash
pip install stubborn-status
```

Requires sibling CLIs on `PATH` (`stubborn`, `stubborn-mcp`, `stubborn-watch`, …).

## Usage

```bash
# Human-readable merged report
stubborn-status

# Machine-readable for CI / IDE bridges
stubborn-status --json

# Require optional doctors in the aggregate exit code
stubborn-status --require stubborn-mcp,stubborn-watch

# Forward DB path to doctors that accept --db
stubborn-status --db metadata/symbols.db
```

## Design

- **Subprocess only** — never imports `stubborn_mcp` or other sibling packages
- **Graceful degradation** — missing optional packages appear as `not_installed`
- **Source attribution** — every check keeps its owning package label
- **Read-only** — doctors are invoked with `--json`; no ingest, merge, or schema migration

## Development

```bash
pip install -e '.[dev]'
pytest
```

See [CHANGELOG](CHANGELOG.md) and [docs/RELEASE.md](docs/RELEASE.md).
