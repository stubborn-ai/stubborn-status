"""CLI for stubborn-status."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from stubborn_status.aggregate import run_status
from stubborn_status.registry import registry_by_package
from stubborn_status.report import format_json, format_text

app = typer.Typer(
    name="stubborn-status",
    help="Aggregate federated Stubborn doctor reports (ADR-016).",
    invoke_without_command=True,
    no_args_is_help=False,
)


def _parse_package_list(value: str | None) -> set[str] | None:
    if value is None:
        return None
    packages = {part.strip() for part in value.split(",") if part.strip()}
    known = registry_by_package()
    unknown = sorted(package for package in packages if package not in known)
    if unknown:
        raise typer.BadParameter(f"unknown package(s): {', '.join(unknown)}")
    return packages


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    path: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Project root passed to each doctor",
    ),
    db: Optional[Path] = typer.Option(
        None,
        "--db",
        help="Forward --db to doctors that accept it",
    ),
    workspace: Optional[str] = typer.Option(
        None,
        "--workspace",
        help="Forward --workspace to stubborn doctor",
    ),
    require: Optional[str] = typer.Option(
        None,
        "--require",
        help="Comma-separated packages that affect aggregate exit code (default: stubborn-stub only)",
    ),
    only: Optional[str] = typer.Option(
        None,
        "--only",
        help="Comma-separated subset of packages to run",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit Status Report v1 JSON"),
    quiet: bool = typer.Option(False, "-q", "--quiet", help="Suppress output; exit code only"),
) -> None:
    """Run registered doctor CLIs and merge their JSON reports."""
    if ctx.invoked_subcommand is not None:
        return

    report = run_status(
        path,
        db_path=db,
        workspace=workspace,
        require=_parse_package_list(require),
        only=_parse_package_list(only),
    )
    if not quiet:
        typer.echo(format_json(report) if json_output else format_text(report))
    raise typer.Exit(code=report.exit_code())


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
