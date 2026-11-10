"""Tests for the reserved option `-v`/`--version` of the command line."""

import pytest
from typer.testing import CliRunner

from vitruv import __version__
from vitruv.cli import app


@pytest.mark.parametrize("flag", ["-v", "--version"])
def test_version_option_prints_the_version_without_a_command(flag: str) -> None:
    result = CliRunner().invoke(app, [flag])

    assert result.exit_code == 0, result.output
    assert result.output.strip() == __version__
