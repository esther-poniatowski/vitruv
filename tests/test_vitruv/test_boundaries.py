"""Tests of the check of boundaries on a workspace where each rule is broken once."""

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from vitruv.boundaries import BoundaryInputError, TableError, check_tools, load_table, sarif_log
from vitruv.cli import app

REGISTRY_SCHEMA = {"$id": "https://example.org/regis/registry.schema.json", "type": "object"}

TABLE = {
    "_schema": "vitruv:boundaries@1",
    "defaults": {"folder": "tools"},
    "tools": {
        "regis": {
            "interfaces": ["regis.api"],
            "formats": {
                "regis:registry@1": {
                    "markers": ["regis:registry@1", "registry.lock"],
                    "files": ["specs/registry.schema.json"],
                }
            },
        },
        "user": {
            "depends_on": ["regis"],
            "uses": {"regis:registry@1": {"through": "regis.api"}},
        },
        "lone": {"include": ["src/**"]},
        "lazy": {
            "depends_on": ["regis"],
            "uses": {"regis:registry@1": {"through": "regis.api"}},
        },
        "wrong": {
            "depends_on": ["regis"],
            "uses": {"regis:registry@1": {"through": "regis.core"}},
        },
    },
    "entities": {"renderer": {"markers": ["viewer://"], "known_by": ["lone"]}},
}

FILES = {
    "tools/regis/specs/registry.schema.json": json.dumps(REGISTRY_SCHEMA),
    "tools/regis/src/regis/api.py": '"""Reader of registries, for user tools."""\n',
    "tools/regis/README.md": "The tool `user` reads registries through this package.\n",
    "tools/user/src/user/read.py": (
        "from regis.api import read\n"
        "from regis._core import parse\n"
        'FORMAT = "regis:registry@1"\n'
        'OTHER = "regis:other@1"\n'
        'VECTORS = "../regis/specs"\n'
        'CASES = Path(__file__).parents[2] / "regis" / "specs"\n'
        'LINK = "viewer://open"\n'
    ),
    "tools/user/tests/registry.schema.json": json.dumps(REGISTRY_SCHEMA),
    "tools/user/tests/drifted.schema.json": json.dumps({**REGISTRY_SCHEMA, "type": "array"}),
    "tools/lone/notes/ignored.py": 'NAME = "registry.lock"\n',
    "tools/lone/src/lone/main.py": (
        "from regis.api import read\n" 'NAME = "registry.lock"\n' 'LINK = "viewer://open"\n'
    ),
    "tools/lazy/src/lazy/main.py": "VALUE = 1\n",
    "tools/wrong/src/wrong/main.py": "from regis.core import read\n",
}


def workspace(root: Path, table: dict = TABLE) -> Path:
    """Write the table and the tools below `root`, and return the path of the table."""
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    path = root / "boundaries.yml"
    path.write_text(yaml.safe_dump(table, sort_keys=False), encoding="utf-8")
    return path


def found(root: Path, only: str | None = None) -> set[tuple[str, str, str, str]]:
    """The tool, rule, path and discriminator of every finding."""
    table = load_table(workspace(root))
    return {
        (finding.tool, finding.rule.identifier, finding.path, finding.discriminator)
        for finding in check_tools(table, root, only)
    }


def test_each_rule_reports_its_planted_instance(tmp_path: Path) -> None:
    """Every planted crossing is reported, and nothing else."""
    assert found(tmp_path) == {
        ("regis", "agnostic/dependent-name", "tools/regis/src/regis/api.py", "user"),
        ("user", "agnostic/internal-import", "tools/user/src/user/read.py", "regis._core"),
        ("user", "agnostic/internal-import", "tools/user/src/user/read.py", "regis._core.parse"),
        (
            "user",
            "implementations/foreign-namespace",
            "tools/user/src/user/read.py",
            "regis:other@1",
        ),
        ("user", "reads/sibling-path", "tools/user/src/user/read.py", "../regis"),
        ("user", "reads/sibling-path", "tools/user/src/user/read.py", 'parents[2] / "regis"'),
        ("user", "agnostic/entity-name", "tools/user/src/user/read.py", "viewer://"),
        (
            "user",
            "implementations/copied-file",
            "tools/user/tests/registry.schema.json",
            "tools/regis/specs/registry.schema.json",
        ),
        (
            "user",
            "implementations/copied-file",
            "tools/user/tests/drifted.schema.json",
            "https://example.org/regis/registry.schema.json",
        ),
        ("lone", "reads/undeclared-dependency", "tools/lone/src/lone/main.py", "regis"),
        ("lone", "reads/undeclared-format", "tools/lone/src/lone/main.py", "registry.lock"),
        ("lazy", "implementations/unused-owner-implementation", "tools/lazy/", "regis:registry@1"),
        ("wrong", "implementations/undeclared-owner", "tools/wrong/", "regis:registry@1"),
        ("wrong", "agnostic/internal-import", "tools/wrong/src/wrong/main.py", "regis.core"),
        ("wrong", "agnostic/internal-import", "tools/wrong/src/wrong/main.py", "regis.core.read"),
    }


def test_one_tool_is_checked_with_the_whole_table(tmp_path: Path) -> None:
    """A check of one tool still knows its dependents, which the table declares."""
    assert found(tmp_path, "regis") == {
        ("regis", "agnostic/dependent-name", "tools/regis/src/regis/api.py", "user")
    }


def test_a_marker_is_located_at_its_line(tmp_path: Path) -> None:
    table = load_table(workspace(tmp_path))
    finding = next(
        item
        for item in check_tools(table, tmp_path, "user")
        if item.rule.identifier == "reads/sibling-path"
    )
    assert finding.position == (5, 12)


def test_the_log_conforms_to_the_findings_profile(tmp_path: Path) -> None:
    """The log is a producer log of the profile of Elenchos, which yields one identity each."""
    profile = pytest.importorskip("elenchos.profile")
    table = load_table(workspace(tmp_path))
    log = sarif_log(check_tools(table, tmp_path))
    assert profile.violations(log) == []
    assert len(set(profile.identities(log))) == len(log["runs"][0]["results"])
    stopped = sarif_log([], "the table cannot be read")
    assert profile.violations(stopped) == []


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda table: table["tools"]["user"].update(depends_on=["ghost"]), "ghost"),
        (lambda table: table["tools"]["lone"].update(uses={"x:y@1": {"through": "x"}}), "x:y@1"),
        (lambda table: table["tools"]["lone"].update(unknown=1), "unknown"),
    ],
    ids=["unknown-dependency", "unowned-format", "unknown-key"],
)
def test_an_invalid_table_is_refused(tmp_path: Path, edit, message: str) -> None:
    table = json.loads(json.dumps(TABLE))
    edit(table)
    with pytest.raises(TableError, match=message):
        load_table(workspace(tmp_path, table))


def test_an_absent_tool_folder_stops_the_check(tmp_path: Path) -> None:
    table = load_table(workspace(tmp_path))
    with pytest.raises(BoundaryInputError, match="absent"):
        check_tools(table, tmp_path / "elsewhere")


@pytest.mark.parametrize(("only", "status"), [("regis", 1), ("lone", 1)])
def test_exit_status(tmp_path: Path, only: str, status: int) -> None:
    path = workspace(tmp_path)
    result = CliRunner().invoke(
        app,
        ["boundaries", "check", "--table", str(path), "--workspace", str(tmp_path), "--tool", only],
    )
    assert result.exit_code == status, result.output


def test_a_clean_tool_passes_and_an_unknown_tool_stops(tmp_path: Path) -> None:
    path = workspace(tmp_path)
    arguments = ["boundaries", "check", "--table", str(path), "--workspace", str(tmp_path)]
    assert CliRunner().invoke(app, [*arguments, "--tool", "lazy"]).exit_code == 1
    assert CliRunner().invoke(app, [*arguments, "--tool", "ghost"]).exit_code == 2


def test_a_versioned_family_and_the_owner_command_are_admitted(tmp_path: Path) -> None:
    """A contract of a family that its owner declares is no foreign namespace, and a tool may hold
    a document that the command of its owner reads."""
    table = json.loads(json.dumps(TABLE))
    table["tools"]["regis"]["formats"]["regis:config"] = {"markers": ["regis:config@"]}
    table["tools"]["lazy"]["uses"]["regis:config"] = {"through": "regis"}
    path = workspace(tmp_path, table)
    (tmp_path / "tools/lazy/regis.yml").write_text("_schema: regis:config@4\n", encoding="utf-8")
    findings = check_tools(load_table(path), tmp_path, "lazy")
    assert {(item.rule.identifier, item.discriminator) for item in findings} == {
        ("implementations/unused-owner-implementation", "regis:registry@1")
    }


def test_a_schema_under_the_id_marker_of_an_owner_is_a_copy(tmp_path: Path) -> None:
    """A file declaring the $id that the table gives as a marker copies the schema of its owner,
    although the owner lists no published file."""
    table = json.loads(json.dumps(TABLE))
    table["tools"]["regis"]["formats"]["regis:addressing"] = {
        "markers": ["https://example.org/regis/addressing.schema.yml"]
    }
    path = workspace(tmp_path, table)
    copy = tmp_path / "tools/lazy/data/addressing.schema.yml"
    copy.parent.mkdir(parents=True)
    copy.write_text("$id: https://example.org/regis/addressing.schema.yml\n", encoding="utf-8")
    findings = check_tools(load_table(path), tmp_path, "lazy")
    assert ("implementations/copied-file", "tools/lazy/data/addressing.schema.yml") in {
        (item.rule.identifier, item.path) for item in findings
    }


def test_the_packaged_template_is_a_valid_table() -> None:
    """The template that the analyst fills is itself a valid table."""
    from importlib.resources import files

    template = Path(str(files("vitruv").joinpath("templates/boundaries.yml")))
    assert set(load_table(template).tools) == {"owner-tool", "consumer-tool"}
