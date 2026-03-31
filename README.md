# vitruv

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](docs/guide/installation.md)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/vitruv)](https://github.com/esther-poniatowski/vitruv/commits/main)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Analyzes the structural quality of software projects across programming languages.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

### Motivation

Software architecture degrades over time as projects accumulate coupling, unclear
responsibilities, and inconsistent patterns. Existing linters check code style and
surface-level issues but do not evaluate structural properties: dependency direction,
cohesion, contract conformance, or architectural smell patterns.

### Advantages

- **Multi-language analysis** — operates on dependency graphs extracted from any
  language, not limited to Python AST.
- **Quantitative metrics** — measures coupling, cohesion, instability, and
  abstractness using Robert C. Martin's package metrics and connascence taxonomy.
- **Architectural smell detection** — identifies cyclic dependencies, god modules,
  unstable dependencies, and layer violations.
- **Design pattern reasoning** — evaluates whether observed patterns align with
  declared architectural intent.

### Theoretical Foundations

The analysis framework draws on Robert C. Martin's package metrics (afferent/efferent
coupling, instability, abstractness), the connascence taxonomy (Page-Jones), and
graph-theoretic structural analysis.

---

## Features

- [ ] **Dependency graph analysis**: Extract and analyze import graphs, detect cycles,
  measure coupling metrics.
- [ ] **Responsibility and cohesion analysis**: Evaluate module cohesion through
  structural and semantic indicators.
- [ ] **Contract and interface analysis**: Check interface segregation, dependency
  inversion, and protocol conformance.
- [ ] **Architectural smell detection**: Identify god modules, unstable dependencies,
  shotgun surgery, and layer violations.
- [ ] **Design pattern reasoning**: Evaluate pattern usage against declared
  architectural intent.
- [ ] **Conformance checking**: Verify that a codebase conforms to its declared
  architecture.

---

## Quick Start

Analyze a project:

```sh
vitruv analyze src/
```

Run a specific audit:

```sh
vitruv audit src/ --profile component
```

---

## Documentation

| Guide | Content |
| ----- | ------- |
| [Installation](docs/guide/installation.md) | Prerequisites, pip/conda/source setup |
| [Usage](docs/guide/usage.md) | Workflows and detailed examples |
| [CLI Reference](docs/guide/cli-reference.md) | Full command registry and options |
| [Configuration](docs/guide/configuration.md) | Audit profiles, rule selection |
| [Design Principles](docs/standards/design-principles.md) | Software design standards |
| [Audit Taxonomy](docs/design/audit-taxonomy.md) | Audit dimensions and categories |

Full API documentation and rendered guides are also available at
[esther-poniatowski.github.io/vitruv](https://esther-poniatowski.github.io/vitruv/).

---

## Contributing

Contribution guidelines are described in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Acknowledgments

### Authors

**Author**: @esther-poniatowski

For academic use, the GitHub "Cite this repository" feature generates citations in
various formats. The [citation metadata](CITATION.cff) file is also available.

---

## License

This project is licensed under the terms of the
[GNU General Public License v3.0](LICENSE).
