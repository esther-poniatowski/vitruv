"""
The check of the boundaries between tools, against a boundary table written by the analyst.

The table `vitruv:boundaries@1` declares a set of tools; `check_tools` reports each crossing of a
boundary that the rules of `checks` define, and `sarif` writes the report.
"""

from .checks import RULES, BoundaryInputError, Finding, Rule, check_tools
from .sarif import sarif_log, text_lines
from .table import Table, TableError, load_table

__all__ = [
    "RULES",
    "BoundaryInputError",
    "Finding",
    "Rule",
    "Table",
    "TableError",
    "check_tools",
    "load_table",
    "sarif_log",
    "text_lines",
]
