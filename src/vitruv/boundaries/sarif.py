"""
The report of a check of boundaries: a findings log in the profile of Elenchos, or text lines.

Each finding is located at a file of a tool, relative to the workspace, with the line and the
column of its offending text, or at the folder of a tool when it concerns the declarations of the
tool. The discriminator is the offending content, so that two findings of one rule in one file
keep distinct identities.
"""

from typing import Any, Sequence
from urllib.parse import quote

from .. import __version__
from .checks import RULES, Finding

TOOL = "vitruv"
"""Driver name of the log."""

SARIF_SCHEMA = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json"
)


def _name(path: str) -> str:
    """Return the logical name of the resource `path:<path>`, with % and # escaped."""
    return "path:" + path.replace("%", "%25").replace("#", "%23")


def _result(finding: Finding) -> dict[str, Any]:
    """Write one finding as a SARIF result of the profile."""
    physical: dict[str, Any] = {
        "artifactLocation": {"uri": quote(finding.path), "uriBaseId": "SRCROOT"}
    }
    if finding.position is not None:
        physical["region"] = {"startLine": finding.position[0], "startColumn": finding.position[1]}
    return {
        "ruleId": finding.rule.identifier,
        "level": "error",
        "message": {"text": finding.message},
        "locations": [
            {"physicalLocation": physical, "logicalLocations": [{"name": _name(finding.path)}]}
        ],
        "partialFingerprints": {"discriminator/v1": finding.discriminator},
        "properties": {"vitruv/tool": finding.tool},
    }


def sarif_log(findings: Sequence[Finding], stopped: str | None = None) -> dict[str, Any]:
    """
    Write the findings log of a check of boundaries.

    Parameters
    ----------
    findings : Sequence[Finding]
        The findings of the check.
    stopped : str, optional
        Why the check could not run; the log then holds a failed run without results.
    """
    run: dict[str, Any] = {
        "tool": {
            "driver": {
                "name": TOOL,
                "version": __version__,
                "isComprehensive": True,
                "rules": [
                    {
                        "id": rule.identifier,
                        "shortDescription": {"text": rule.description},
                        "defaultConfiguration": {"level": "error"},
                        "properties": {"vitruv/driver": rule.driver},
                    }
                    for rule in RULES
                ],
            }
        },
        "columnKind": "unicodeCodePoints",
    }
    if stopped is not None:
        run["invocations"] = [
            {
                "executionSuccessful": False,
                "toolExecutionNotifications": [{"level": "error", "message": {"text": stopped}}],
            }
        ]
    else:
        run["results"] = [_result(finding) for finding in findings]
    return {"version": "2.1.0", "$schema": SARIF_SCHEMA, "runs": [run]}


def text_lines(findings: Sequence[Finding]) -> list[str]:
    """
    Write one line per finding, then the count of findings.

    Examples
    --------
    >>> from .checks import SIBLING_PATH
    >>> text_lines([Finding(SIBLING_PATH, "a", "a/t.py", "../b", "a reaches b", (3, 5))])
    ['a/t.py:3:5: reads/sibling-path: a reaches b', '1 findings']
    """
    lines = []
    for finding in findings:
        place = f":{finding.position[0]}:{finding.position[1]}" if finding.position else ""
        lines.append(f"{finding.path}{place}: {finding.rule.identifier}: {finding.message}")
    lines.append(f"{len(findings)} findings")
    return lines
