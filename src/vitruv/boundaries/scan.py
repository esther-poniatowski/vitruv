"""
The files of a tool that the rules of boundaries read, with their text.

The scan takes the files that Git tracks in the folder of the tool, or every file when the folder
is no Git working tree, such as an exported state of a past commit. It leaves out the files that
the table excludes, binary files, and files larger than `MAX_BYTES`.
"""

import re
import subprocess
from bisect import bisect_right
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path, PurePosixPath
from typing import Iterator, Sequence

MAX_BYTES = 2_000_000
"""Size above which a file is not read; a generated or vendored file is that large."""


@cache
def glob_pattern(glob: str) -> re.Pattern[str]:
    """
    Return the regular expression of a glob over POSIX paths relative to the folder of a tool.

    `**/` matches any number of folders, `**` any text, `*` any text without `/`, and `?` one
    character other than `/`. A glob without `/` matches a name in any folder.

    Examples
    --------
    >>> bool(glob_pattern("docs/**").fullmatch("docs/a/b.md"))
    True
    >>> bool(glob_pattern("**/*.md").fullmatch("README.md"))
    True
    >>> bool(glob_pattern("*.md").fullmatch("a/b.md"))
    True
    """
    if "/" not in glob:
        glob = f"**/{glob}"
    parts = re.split(r"(\*\*/|\*\*|\*|\?)", glob)
    tokens = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}
    return re.compile("".join(tokens.get(part, re.escape(part)) for part in parts))


@dataclass
class SourceFile:
    """One scanned file: its path relative to the workspace, and its text."""

    path: PurePosixPath
    text: str
    _starts: list[int] = field(default_factory=list, repr=False)

    def position(self, offset: int) -> tuple[int, int]:
        """Return the line and the column, from 1, of a character offset of the text."""
        if not self._starts:
            self._starts = [0] + [match.end() for match in re.finditer("\n", self.text)]
        line = bisect_right(self._starts, offset)
        return line, offset - self._starts[line - 1] + 1


def _listed(folder: Path) -> list[str]:
    """Return the files of a folder, relative to it: those that Git tracks, or every file."""
    if (folder / ".git").exists():
        completed = subprocess.run(
            ["git", "ls-files", "-z"], cwd=folder, capture_output=True, check=False
        )
        if not completed.returncode:
            return [name for name in completed.stdout.decode("utf-8").split("\0") if name]
    return sorted(
        path.relative_to(folder).as_posix()
        for path in folder.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(folder).parts
    )


def scan(
    workspace: Path,
    folder: PurePosixPath,
    exclude: Sequence[str],
    include: Sequence[str] = (),
) -> Iterator[SourceFile]:
    """
    Yield the text files of the tool at `folder`, below the workspace, in sorted order.

    Parameters
    ----------
    workspace : Path
        The folder holding every tool of the table.
    folder : PurePosixPath
        The folder of the tool, relative to the workspace.
    exclude : Sequence[str]
        Globs of the files left out, relative to the folder of the tool.
    include : Sequence[str], default ()
        Globs of the files kept, relative to the folder of the tool; every file when empty.
    """
    root = workspace / folder
    patterns = [glob_pattern(glob) for glob in exclude]
    kept = [glob_pattern(glob) for glob in include]
    for name in sorted(_listed(root)):
        if any(pattern.fullmatch(name) for pattern in patterns):
            continue
        if kept and not any(pattern.fullmatch(name) for pattern in kept):
            continue
        path = root / name
        try:
            if not path.is_file() or path.stat().st_size > MAX_BYTES:
                continue
            text = path.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "\0" in text:
            continue
        yield SourceFile(folder / name, text)
