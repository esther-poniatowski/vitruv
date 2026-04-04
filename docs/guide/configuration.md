# Configuration

Vitruv has no project-specific configuration yet. No YAML schema, environment
variables, or runtime settings exist.

## Third-Party Tool Configs

The `config/` directory contains configuration files for third-party
development tools, organized into two subdirectories.

### `config/tools/`

Linter, formatter, and type-checker settings used during development:

| File | Tool |
| ---- | ---- |
| `black.toml` | Black (formatter) |
| `mypy.ini` | Mypy (type checker) |
| `pylintrc.ini` | Pylint (linter, production code) |
| `pylintrc_tests.ini` | Pylint (linter, test code) |
| `pyrightconfig.json` | Pyright (type checker) |
| `releaserc.toml` | semantic-release (versioning) |

### `config/dictionaries/`

Spelling dictionaries for CSpell or similar spell-checking tools:

| File | Scope |
| ---- | ----- |
| `project.txt` | Project-specific terms |
| `python.txt` | Python ecosystem terms |
| `tools.txt` | Tool and library names |
