"""
The rules that keep the boundaries between tools, and their check against a boundary table.

The rules restate three drivers of the decision on tool roles. Under *declared reads*, a tool reads
only its own files, files fixed by a widely accepted convention, and the published contracts of the
tools that it declares as dependencies. Under *owner implementations*, a tool parses, validates or
serializes a format of another tool only through an implementation published by the owner. Under
*agnostic tools*, no output, schema, message or test of a tool names a tool that depends on it, a
renderer, a consumer, or an internal module of another tool. The specification is
`docs/guide/boundaries.md`.

Functions
---------
check_tools(table, workspace, only=None) -> list[Finding]
    Check the rules on the tools of a table, or on one of them.

Classes
-------
Rule, Finding
    A rule of boundaries, and one of its violations.
BoundaryInputError
    A tool folder or a published file that the table names and the workspace lacks.
"""

import ast
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Mapping

import yaml

from .scan import SourceFile, scan
from .table import OwnedFormat, Table, Tool


class BoundaryInputError(Exception):
    """A folder or a file named by the table that the workspace does not hold."""


@dataclass(frozen=True)
class Rule:
    """A rule of boundaries: its identifier, the driver that it states, and its description."""

    identifier: str
    driver: str
    description: str


UNDECLARED_FORMAT = Rule(
    "reads/undeclared-format",
    "declared reads",
    "A tool holds a marker of a format of another tool, without declaring that it uses the format.",
)
SIBLING_PATH = Rule(
    "reads/sibling-path",
    "declared reads",
    "A tool reaches the folder of another tool by a relative path, as a sibling clone.",
)
UNDECLARED_DEPENDENCY = Rule(
    "reads/undeclared-dependency",
    "declared reads",
    "A tool imports a package of another tool that it does not declare as a dependency.",
)
UNDECLARED_OWNER = Rule(
    "implementations/undeclared-owner",
    "owner implementations",
    "A tool uses a format through an implementation that is not the published interface of a "
    "declared owner.",
)
UNUSED_OWNER_IMPLEMENTATION = Rule(
    "implementations/unused-owner-implementation",
    "owner implementations",
    "A tool declares that it uses a format through an implementation of its owner, and never "
    "imports or names that implementation.",
)
COPIED_FILE = Rule(
    "implementations/copied-file",
    "owner implementations",
    "A tool holds a copy of a file that another tool publishes, or a schema under its $id.",
)
FOREIGN_NAMESPACE = Rule(
    "implementations/foreign-namespace",
    "owner implementations",
    "A tool names a contract in the namespace of another tool, which that tool does not own.",
)
DEPENDENT_NAME = Rule(
    "agnostic/dependent-name",
    "agnostic tools",
    "A tool names a tool that depends on it.",
)
ENTITY_NAME = Rule(
    "agnostic/entity-name",
    "agnostic tools",
    "A tool names a consumer, a renderer or a layout that it may not know.",
)
INTERNAL_IMPORT = Rule(
    "agnostic/internal-import",
    "agnostic tools",
    "A tool imports a module of another tool outside its public interface.",
)

RULES = (
    UNDECLARED_FORMAT,
    SIBLING_PATH,
    UNDECLARED_DEPENDENCY,
    UNDECLARED_OWNER,
    UNUSED_OWNER_IMPLEMENTATION,
    COPIED_FILE,
    FOREIGN_NAMESPACE,
    DEPENDENT_NAME,
    ENTITY_NAME,
    INTERNAL_IMPORT,
)
"""Every rule of boundaries, in the order of the specification."""

_WORD = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"
CONTRACT = re.compile(rf"(?<![\w.:/-])({_WORD}):({_WORD}(?:\.{_WORD})*)@([1-9][0-9]*)(?![\w.])")
"""A contract identifier `<namespace>:<name>@<version>` standing as a token of a text."""

_TS_IMPORT = re.compile(
    r"""(?:\bfrom\s*|\bimport\s*\(\s*|\brequire\s*\(\s*|\bimport\s+)["']([^"']+)["']"""
)
"""The module specifier of an import in TypeScript or JavaScript."""

_SCRIPT_SUFFIXES = (".ts", ".tsx", ".js", ".mjs", ".cjs", ".mts", ".cts")


@dataclass(frozen=True)
class Finding:
    """
    One violation of a rule of boundaries.

    Attributes
    ----------
    rule : Rule
        The rule broken.
    tool : str
        The tool that breaks it.
    path : str
        The path of the file, relative to the workspace, or the folder of the tool ending with `/`.
    discriminator : str
        The offending content: a marker, a path, a module or a format.
    message : str
        The explanation.
    position : tuple[int, int] | None
        The line and the column of the offending text, None for a whole file or folder.
    """

    rule: Rule
    tool: str
    path: str
    discriminator: str
    message: str
    position: tuple[int, int] | None = None


def _occurrences(source: SourceFile, literal: str) -> Iterator[tuple[int, int]]:
    """Yield the position of each occurrence of a literal in a file."""
    start = source.text.find(literal)
    while start != -1:
        yield source.position(start)
        start = source.text.find(literal, start + len(literal))


def _matches(source: SourceFile, pattern: re.Pattern[str]) -> Iterator[re.Match[str]]:
    yield from pattern.finditer(source.text)


def _read_structured(path: Path) -> object:
    """Read a JSON or YAML file, None when it cannot be read."""
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError):
        return None


@dataclass(frozen=True)
class _Published:
    """A file published by an owner: its digest and the `$id` that it declares, if any."""

    owner: str
    format: str
    path: str
    digest: str
    identifier: str | None


def _published(table: Table, workspace: Path) -> list[_Published]:
    """Read every file that an owner publishes, or raise `BoundaryInputError` for an absent one."""
    found: list[_Published] = []
    for owned in table.formats.values():
        tool = table.tools[owned.owner]
        for rel in owned.files:
            path = workspace / tool.path / rel
            try:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError as error:
                raise BoundaryInputError(
                    f"{tool.path / rel}: the file published by {owned.owner} for "
                    f"{owned.identifier} cannot be read: {error}"
                ) from error
            content = _read_structured(path)
            identifier = content.get("$id") if isinstance(content, dict) else None
            found.append(
                _Published(
                    owned.owner,
                    owned.identifier,
                    str(tool.path / rel),
                    digest,
                    identifier if isinstance(identifier, str) else None,
                )
            )
    return found


def _python_imports(source: SourceFile) -> Iterator[tuple[str, tuple[int, int]]]:
    """Yield each absolute module that a Python file imports, with its position; for `from M
    import N`, both `M` and `M.N`, since `N` may be a module."""
    try:
        tree = ast.parse(source.text)
    except (SyntaxError, ValueError):
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, (node.lineno, node.col_offset + 1)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            yield node.module, (node.lineno, node.col_offset + 1)
            for alias in node.names:
                yield f"{node.module}.{alias.name}", (node.lineno, node.col_offset + 1)


def _script_imports(source: SourceFile) -> Iterator[tuple[str, tuple[int, int]]]:
    """Yield each package specifier that a TypeScript or JavaScript file imports."""
    for match in _matches(source, _TS_IMPORT):
        specifier = match.group(1)
        if not specifier.startswith("."):
            yield specifier, source.position(match.start(1))


class _Checker:
    """The rules of boundaries, checked on the scanned files of the tools of one table."""

    def __init__(self, table: Table, workspace: Path) -> None:
        self.table = table
        self.workspace = workspace
        self.published = _published(table, workspace)
        self.roots = {
            package: tool.name for tool in table.tools.values() for package in tool.packages
        }

    def owner_of(self, module: str) -> str | None:
        """Return the tool whose import roots hold a module or a package specifier."""
        if module.startswith("@"):
            scope = "/".join(module.split("/")[:2])
            return self.roots.get(scope) or self.roots.get(module.split("/")[0])
        return self.roots.get(module.split(".")[0]) or self.roots.get(module.split("/")[0])

    def admitted(self, owner: Tool, module: str) -> bool:
        """Whether a module belongs to the public interface of its owner."""
        for interface in owner.interfaces:
            if module == interface:
                return True
            rest = module.removeprefix(interface)
            if rest != module and rest[:1] in (".", "/"):
                parts = re.split(r"[./]", rest[1:])
                if not any(part.startswith("_") for part in parts):
                    return True
        return False

    def check(self, tool: Tool) -> list[Finding]:
        """Return the findings of one tool."""
        sources = list(scan(self.workspace, tool.path, tool.exclude, tool.include))
        findings = list(self._table_findings(tool, sources))
        for source in sources:
            findings += self._file_findings(tool, source)
        return findings

    # --- Rules on the declarations of a tool -----------------------------------------------------

    def _table_findings(self, tool: Tool, sources: list[SourceFile]) -> Iterator[Finding]:
        """Check each format that the tool uses against its owner, its interface and its imports."""
        folder = f"{tool.path}/"
        for identifier, through in tool.uses.items():
            owner = self.table.tools[self.table.formats[identifier].owner]
            published_ids = {item.identifier for item in self.published if item.owner == owner.name}
            if owner.name not in tool.depends_on:
                yield Finding(
                    UNDECLARED_OWNER,
                    tool.name,
                    folder,
                    identifier,
                    f"{tool.name} uses {identifier}, but does not declare its owner "
                    f"{owner.name} as a dependency",
                )
            elif through == owner.name:
                continue
            elif through not in owner.interfaces and through not in published_ids:
                yield Finding(
                    UNDECLARED_OWNER,
                    tool.name,
                    folder,
                    identifier,
                    f"{tool.name} uses {identifier} through {through}, which is neither an "
                    f"interface nor a published schema of {owner.name}",
                )
            elif not any(self._names_implementation(source, through) for source in sources):
                yield Finding(
                    UNUSED_OWNER_IMPLEMENTATION,
                    tool.name,
                    folder,
                    identifier,
                    f"{tool.name} declares that it uses {identifier} through {through}, and "
                    "never imports or names it",
                )

    def _names_implementation(self, source: SourceFile, through: str) -> bool:
        """Whether a file imports an interface module, or names a published schema."""
        if through.startswith(("http://", "https://")):
            return through in source.text
        imports = (
            _python_imports(source)
            if source.path.suffix == ".py"
            else _script_imports(source) if source.path.suffix in _SCRIPT_SUFFIXES else iter(())
        )
        return any(
            module == through
            or module.startswith(f"{through}.")
            or module.startswith(f"{through}/")
            for module, _ in imports
        )

    # --- Rules on the files of a tool ------------------------------------------------------------

    def _file_findings(self, tool: Tool, source: SourceFile) -> list[Finding]:
        """Check every rule on the text of one file of the tool."""
        findings: list[Finding] = []
        findings += self._formats(tool, source)
        findings += self._siblings(tool, source)
        findings += self._copies(tool, source)
        findings += self._namespaces(tool, source)
        findings += self._names(tool, source)
        findings += self._imports(tool, source)
        return findings

    def _formats(self, tool: Tool, source: SourceFile) -> Iterator[Finding]:
        """Report each marker of a format of another tool that the tool does not use."""
        for owned in self._foreign_formats(tool):
            if owned.identifier in tool.uses:
                continue
            for marker in owned.markers:
                for position in _occurrences(source, marker):
                    yield Finding(
                        UNDECLARED_FORMAT,
                        tool.name,
                        str(source.path),
                        marker,
                        f"{marker!r} marks the format {owned.identifier} of {owned.owner}, "
                        f"which {tool.name} does not declare that it uses",
                        position,
                    )

    def _foreign_formats(self, tool: Tool) -> Iterable[OwnedFormat]:
        return (owned for owned in self.table.formats.values() if owned.owner != tool.name)

    def _siblings(self, tool: Tool, source: SourceFile) -> Iterator[Finding]:
        """Report each relative path that enters the folder of another tool."""
        for other in self.table.tools.values():
            if other.name == tool.name:
                continue
            for match in _matches(source, _sibling_pattern(other.path.name)):
                yield Finding(
                    SIBLING_PATH,
                    tool.name,
                    str(source.path),
                    match.group(0),
                    f"{tool.name} reaches the folder of {other.name} by {match.group(0)!r}",
                    source.position(match.start()),
                )

    def _copies(self, tool: Tool, source: SourceFile) -> Iterator[Finding]:
        """Report a file copying a published file of another tool, or declaring its `$id`."""
        digest = hashlib.sha256(source.text.encode("utf-8")).hexdigest()
        for owned in self._foreign_formats(tool):
            for marker in owned.markers:
                if marker.startswith(("http://", "https://")) and _declares_id(source.text, marker):
                    yield Finding(
                        COPIED_FILE,
                        tool.name,
                        str(source.path),
                        marker,
                        f"{source.path} declares the $id {marker} of {owned.identifier}, owned by "
                        f"{owned.owner}",
                    )
        for item in self.published:
            if item.owner == tool.name:
                continue
            if digest == item.digest:
                yield Finding(
                    COPIED_FILE,
                    tool.name,
                    str(source.path),
                    item.path,
                    f"{source.path} copies {item.path}, published by {item.owner} for "
                    f"{item.format}",
                )
            elif (
                item.identifier is not None
                and _declares_id(source.text, item.identifier)
                and not self._id_marker(item.identifier)
            ):
                yield Finding(
                    COPIED_FILE,
                    tool.name,
                    str(source.path),
                    item.identifier,
                    f"{source.path} declares the $id {item.identifier} of {item.path}, published "
                    f"by {item.owner}",
                )

    def _id_marker(self, identifier: str) -> bool:
        """Whether an `$id` is also the marker of a format, which reports its copies already."""
        return any(identifier in owned.markers for owned in self.table.formats.values())

    def _namespaces(self, tool: Tool, source: SourceFile) -> Iterator[Finding]:
        """Report each contract identifier invented in the namespace of another tool."""
        for match in _matches(source, CONTRACT):
            namespace = match.group(1)
            if namespace == tool.name or namespace not in self.table.tools:
                continue
            if self._owned(namespace, match.group(0)):
                continue
            yield Finding(
                FOREIGN_NAMESPACE,
                tool.name,
                str(source.path),
                match.group(0),
                f"{match.group(0)} lies in the namespace of {namespace}, which owns no such "
                "contract",
                source.position(match.start()),
            )

    def _owned(self, owner: str, identifier: str) -> bool:
        """Whether the table gives `owner` a format named by a contract identifier: the identifier
        itself, its name without version, or a format whose marker opens the identifier."""
        family = identifier.rsplit("@", 1)[0]
        return any(
            owned.identifier in (identifier, family)
            or any(identifier.startswith(marker) for marker in owned.markers)
            for owned in self.table.formats.values()
            if owned.owner == owner
        )

    def _names(self, tool: Tool, source: SourceFile) -> Iterator[Finding]:
        """Report each name of a dependent, and each marker of an entity unknown to the tool."""
        for dependent in self.table.dependents(tool.name):
            for word in self.table.tools[dependent].names:
                pattern = re.compile(rf"(?<![\w-]){re.escape(word)}(?![\w-])", re.IGNORECASE)
                for match in _matches(source, pattern):
                    yield Finding(
                        DEPENDENT_NAME,
                        tool.name,
                        str(source.path),
                        word,
                        f"{tool.name} names {dependent}, which depends on it",
                        source.position(match.start()),
                    )
        for entity in self.table.entities:
            if tool.name in entity.known_by:
                continue
            for marker in entity.markers:
                for position in _occurrences(source, marker):
                    yield Finding(
                        ENTITY_NAME,
                        tool.name,
                        str(source.path),
                        marker,
                        f"{tool.name} names {entity.name} by {marker!r}",
                        position,
                    )

    def _imports(self, tool: Tool, source: SourceFile) -> Iterator[Finding]:
        """Report each import of an undeclared dependency, or of an internal module."""
        if source.path.suffix == ".py":
            imports = _python_imports(source)
        elif source.path.suffix in _SCRIPT_SUFFIXES:
            imports = _script_imports(source)
        else:
            return
        seen: set[tuple[str, str]] = set()
        for module, position in imports:
            owner_name = self.owner_of(module)
            if owner_name is None or owner_name == tool.name:
                continue
            owner = self.table.tools[owner_name]
            if owner_name not in tool.depends_on and (owner_name, str(position)) not in seen:
                seen.add((owner_name, str(position)))
                yield Finding(
                    UNDECLARED_DEPENDENCY,
                    tool.name,
                    str(source.path),
                    owner_name,
                    f"{tool.name} imports {module} of {owner_name}, which it does not declare as "
                    "a dependency",
                    position,
                )
            if not self.admitted(owner, module) and not self._parent_admitted(owner, module):
                yield Finding(
                    INTERNAL_IMPORT,
                    tool.name,
                    str(source.path),
                    module,
                    f"{module} is not part of the public interface of {owner_name}",
                    position,
                )

    def _parent_admitted(self, owner: Tool, module: str) -> bool:
        """Whether `module` is a name imported from an admitted module, as in `from M import N`."""
        parent = module.rsplit(".", 1)[0]
        return (
            parent != module
            and self.admitted(owner, parent)
            and not module.rsplit(".", 1)[1].startswith("_")
        )


def _sibling_pattern(folder: str) -> re.Pattern[str]:
    """
    Return the pattern of a relative path that climbs out of a tool and enters `folder`.

    Three forms climb: a path `../<folder>`, a Python traversal `parents[n]` or `.parent`
    joined by `/` to the name of the folder, and a JavaScript `join` of `".."` with the name.

    Examples
    --------
    >>> pattern = _sibling_pattern("other")
    >>> [bool(pattern.search(text)) for text in (
    ...     '"../other/specs"', 'Path(__file__).parents[3] / "other" / "specs"',
    ...     'path.join(root, "..", "other")', '"other"', '"../other-data"')]
    [True, True, True, False, False]
    """
    name = re.escape(folder)
    return re.compile(
        rf"(?:\.\./)+{name}(?![\w.-])"
        rf"|(?:\bparents\[\d+\]|\.parent)\s*/\s*[\"']{name}[\"']"
        rf"|[\"']\.\.[\"']\s*,\s*[\"']{name}[\"']"
    )


def _declares_id(text: str, identifier: str) -> bool:
    """Whether a text declares a schema under `identifier`, as `"$id": ...` or `$id: ...`."""
    pattern = rf"""["']?\$id["']?\s*:\s*["']?{re.escape(identifier)}["']?"""
    return re.search(pattern, text) is not None


def check_tools(table: Table, workspace: Path, only: str | None = None) -> list[Finding]:
    """
    Check the rules of boundaries on the tools of a table, or on one of them.

    Parameters
    ----------
    table : Table
        The boundary table of the set of tools.
    workspace : Path
        The folder holding every tool, against which the paths of the table resolve.
    only : str, optional
        The name of the one tool to check; every tool of the table by default.

    Returns
    -------
    list[Finding]
        The findings, tool by tool in the order of the table, then file by file.

    Raises
    ------
    BoundaryInputError
        If a checked tool has no folder in the workspace, or a published file cannot be read.
    """
    if only is not None and only not in table.tools:
        raise BoundaryInputError(f"the table holds no tool {only}")
    checker = _Checker(table, workspace)
    findings: list[Finding] = []
    for tool in table.tools.values():
        if only is not None and tool.name != only:
            continue
        if not (workspace / tool.path).is_dir():
            raise BoundaryInputError(f"{tool.path}: the folder of {tool.name} is absent")
        findings += checker.check(tool)
    return findings


def rules_of(findings: Iterable[Finding]) -> Mapping[str, int]:
    """Count the findings of each rule, in the order of `RULES`."""
    counts = {rule.identifier: 0 for rule in RULES}
    for finding in findings:
        counts[finding.rule.identifier] += 1
    return counts


__all__ = [
    "BoundaryInputError",
    "Finding",
    "RULES",
    "Rule",
    "check_tools",
    "rules_of",
]
