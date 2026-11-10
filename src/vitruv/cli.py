"""
Command-line interface for the `vitruv` package.

Defines commands available via `python -m vitruv` or `vitruv` if installed as a script.

Commands
--------
info : Display diagnostic information.

See Also
--------
typer.Typer
    Library for building CLI applications: https://typer.tiangolo.com/
"""

import typer
from . import info, __version__

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command("info")
def cli_info() -> None:
    """Display version and platform diagnostics."""
    typer.echo(info())


def _print_version(value: bool) -> None:
    """Print the package version and exit, before any command is required."""
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=_print_version,
        is_eager=True,
        help="Show the package version and exit.",
    )
) -> None:
    """Root command for the package command-line interface."""
