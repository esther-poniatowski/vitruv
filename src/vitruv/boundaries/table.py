"""
Reading of a boundary table, the format `vitruv:boundaries@1`.

The analyst who checks a set of tools writes the table: each tool with its folder in the workspace,
its names, its dependencies, its public interface, the formats that it owns and the formats of other
tools that it uses, and the entities that no tool may name. The tools themselves declare nothing for
Vitruv. The schema of the table is `vitruv/schemas/boundaries.schema.json`.

Functions
---------
load_table(path) -> Table
    Read and check a boundary table.

Classes
-------
Table, Tool, OwnedFormat, Entity
    The checked content of a table.
TableError
    A table that breaks its schema, or names a tool, a format or an entity that it lacks.
"""

import json
from dataclasses import dataclass, field
from functools import cache
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

TABLE_FORMAT = "vitruv:boundaries@1"
"""Contract identifier of a boundary table."""

DEFAULT_EXCLUDE = (
    "docs/**",
    "**/*.md",
    "**/*.rst",
    "LICENSE*",
    "CITATION.cff",
    ".github/**",
    ".vscode/**",
    "*.code-workspace",
    "**/pyproject.toml",
    "**/package.json",
    "**/tsconfig*.json",
    "environment.yml",
    "conda.recipe/**",
    ".gitignore",
    ".gitattributes",
    ".gitmessage",
)
"""The files of a tool outside the scan by default: its documentation and its development
configuration, which hold no output, schema, message or test of the tool."""


class TableError(Exception):
    """A boundary table that cannot be read, breaks its schema, or names what it lacks."""


@dataclass(frozen=True)
class OwnedFormat:
    """A format owned by one tool: the literals that reveal it, and the files that publish it."""

    identifier: str
    owner: str
    markers: tuple[str, ...] = ()
    files: tuple[str, ...] = ()


# A tool carries one field per key of its declaration in the table.
@dataclass(frozen=True)
class Tool:  # pylint: disable=too-many-instance-attributes
    """One tool of the set, as the table declares it."""

    name: str
    path: PurePosixPath
    names: tuple[str, ...]
    depends_on: tuple[str, ...]
    packages: tuple[str, ...]
    interfaces: tuple[str, ...]
    formats: tuple[OwnedFormat, ...]
    uses: Mapping[str, str]
    exclude: tuple[str, ...]
    include: tuple[str, ...] = ()


@dataclass(frozen=True)
class Entity:
    """A consumer, renderer or layout that no tool may name, except the tools that know it."""

    name: str
    markers: tuple[str, ...]
    known_by: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Table:
    """A checked boundary table."""

    tools: Mapping[str, Tool]
    entities: tuple[Entity, ...] = ()
    formats: Mapping[str, OwnedFormat] = field(default_factory=dict)

    def dependents(self, name: str) -> tuple[str, ...]:
        """Return the tools that declare the tool `name` as a dependency, in the order of the table,
        except those that it declares as dependencies itself, which it may name."""
        own = self.tools[name].depends_on
        return tuple(
            tool.name
            for tool in self.tools.values()
            if name in tool.depends_on and tool.name not in own
        )


@cache
def _schema() -> dict[str, Any]:
    """Return the packaged schema of a boundary table, read once."""
    text = files("vitruv").joinpath("schemas/boundaries.schema.json").read_text("utf-8")
    schema: dict[str, Any] = json.loads(text)
    return schema


def _tool(name: str, raw: Mapping[str, Any], defaults: Mapping[str, Any]) -> Tool:
    """Return a tool of the table, its omitted keys taken from the defaults."""
    folder = defaults.get("folder")
    path = PurePosixPath(raw.get("path") or (f"{folder}/{name}" if folder else name))
    exclude = tuple(defaults.get("exclude", DEFAULT_EXCLUDE)) + tuple(raw.get("exclude", ()))
    return Tool(
        name=name,
        path=path,
        names=tuple(raw.get("names", (name,))),
        depends_on=tuple(raw.get("depends_on", ())),
        packages=tuple(raw.get("packages", (name,))),
        interfaces=tuple(raw.get("interfaces", ())),
        formats=tuple(
            OwnedFormat(
                identifier,
                name,
                tuple(spec.get("markers", ())),
                tuple(spec.get("files", ())),
            )
            for identifier, spec in raw.get("formats", {}).items()
        ),
        uses={identifier: spec["through"] for identifier, spec in raw.get("uses", {}).items()},
        exclude=exclude,
        include=tuple(raw.get("include", ())),
    )


def _check_references(table: Table) -> None:
    """Raise `TableError` when the table names a tool or a format that it does not declare."""
    for tool in table.tools.values():
        for dependency in tool.depends_on:
            if dependency not in table.tools:
                raise TableError(f"tool {tool.name} depends on {dependency}, absent from the table")
        for identifier in tool.uses:
            if identifier not in table.formats:
                raise TableError(f"tool {tool.name} uses {identifier}, which no tool owns")
            if table.formats[identifier].owner == tool.name:
                raise TableError(f"tool {tool.name} uses {identifier}, which it owns")
    for entity in table.entities:
        for name in entity.known_by:
            if name not in table.tools:
                raise TableError(f"entity {entity.name} is known by {name}, absent from the table")


def load_table(path: Path) -> Table:
    """
    Read and check a boundary table.

    Parameters
    ----------
    path : Path
        The YAML file of the table.

    Returns
    -------
    Table
        The tools, their formats and the entities of the table.

    Raises
    ------
    TableError
        If the file cannot be read, breaks the schema `vitruv:boundaries@1`, declares one format
        under two owners, or names a tool or a format that it does not declare.
    """
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise TableError(f"{path}: the table cannot be read: {error}") from error
    errors = sorted(Draft202012Validator(_schema()).iter_errors(raw), key=lambda e: list(e.path))
    if errors:
        where = "/".join(str(step) for step in errors[0].absolute_path)
        raise TableError(f"{path}: /{where}: {errors[0].message}")
    defaults = raw.get("defaults", {})
    tools = {name: _tool(name, spec or {}, defaults) for name, spec in raw["tools"].items()}
    formats: dict[str, OwnedFormat] = {}
    for tool in tools.values():
        for owned in tool.formats:
            if owned.identifier in formats:
                raise TableError(
                    f"{path}: format {owned.identifier} is owned by both "
                    f"{formats[owned.identifier].owner} and {tool.name}"
                )
            formats[owned.identifier] = owned
    entities = tuple(
        Entity(name, tuple(spec["markers"]), frozenset(spec.get("known_by", ())))
        for name, spec in raw.get("entities", {}).items()
    )
    table = Table(tools, entities, formats)
    try:
        _check_references(table)
    except TableError as error:
        raise TableError(f"{path}: {error}") from error
    return table
