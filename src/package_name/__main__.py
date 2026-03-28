"""
Entry point for the `vitruv` package, invoked as a module.

Usage
-----
To launch the command-line interface, execute::

    python -m vitruv


See Also
--------
vitruv.cli: Module implementing the application's command-line interface.
"""
from .cli import app

app()
