"""
Command-line interface for the `vitruv` package.

Defines commands available via `python -m vitruv` or `vitruv` if installed as a script.

Commands
--------
info : Display diagnostic information.
boundaries check : Check the boundaries between the tools of a boundary table.

See Also
--------
typer.Typer
    Library for building CLI applications: https://typer.tiangolo.com/
"""

import json
from pathlib import Path
from typing import Optional

import typer

from . import __version__, info
from .boundaries import (
    BoundaryInputError,
    TableError,
    check_tools,
    load_table,
    sarif_log,
    text_lines,
)

app = typer.Typer(add_completion=False, no_args_is_help=True)
boundaries_app = typer.Typer(no_args_is_help=True, help="Check the boundaries between tools.")
app.add_typer(boundaries_app, name="boundaries")

EXIT_PASS = 0
"""Exit status when no finding is reported."""

EXIT_FINDINGS = 1
"""Exit status when at least one finding is reported."""

EXIT_ERROR = 2
"""Exit status when the check cannot run."""


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


@boundaries_app.command("check")
def cli_boundaries_check(
    table: Path = typer.Option(..., "--table", "-t", help="The boundary table to check against."),
    workspace: Path = typer.Option(
        ..., "--workspace", "-w", help="The folder holding every tool of the table."
    ),
    tool: Optional[str] = typer.Option(
        None, "--tool", help="Check one tool of the table; every tool by default."
    ),
    output_format: str = typer.Option(
        "text", "--format", help="Report format: `text`, or `sarif` for a findings log."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="File of the report; standard output by default."
    ),
) -> None:
    """
    Check the boundaries between the tools of a boundary table.

    The exit status is 0 when no finding is reported, 1 when one is, and 2 when the check cannot
    run: an unreadable or invalid table, a tool absent from the table or from the workspace, or an
    unreadable published file.
    """
    if output_format not in ("text", "sarif"):
        typer.echo(f"vitruv: --format takes text or sarif, not {output_format}", err=True)
        raise typer.Exit(EXIT_ERROR)
    stopped: str | None = None
    findings = []
    try:
        findings = check_tools(load_table(table), workspace.resolve(), tool)
    except (TableError, BoundaryInputError) as error:
        stopped = str(error)
    if output_format == "sarif":
        report = json.dumps(sarif_log(findings, stopped), indent=2, ensure_ascii=False) + "\n"
    else:
        report = "\n".join([f"vitruv: {stopped}"] if stopped else text_lines(findings)) + "\n"
    try:
        if output is None:
            typer.echo(report, nl=False)
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(report, encoding="utf-8")
    except OSError as error:
        typer.echo(f"vitruv: cannot write {output}: {error}", err=True)
        raise typer.Exit(EXIT_ERROR) from error
    if stopped is not None:
        if output is not None or output_format == "sarif":
            typer.echo(f"vitruv: {stopped}", err=True)
        raise typer.Exit(EXIT_ERROR)
    raise typer.Exit(EXIT_FINDINGS if findings else EXIT_PASS)


def _print_version(value: bool) -> None:
    """Print the package version and exit, before any command is required."""
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(  # pylint: disable=unused-argument
        False,
        "--version",
        "-v",
        callback=_print_version,
        is_eager=True,
        help="Show the package version and exit.",
    )
) -> None:
    """Root command for the package command-line interface."""
