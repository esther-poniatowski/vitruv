# vitruv

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/vitruv)](https://github.com/esther-poniatowski/vitruv/commits/main)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Analyzes the structural quality of software projects across programming languages.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Support](#support)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

Vitruv is a static architecture analysis system. It extracts the structural organization of a codebase — subsystem boundaries, dependency directions, responsibility assignments, extension points — and evaluates it against declared quality criteria and architectural policies. The output is a set of diagnostics: confirmed invariant violations, calibrated risk signals, and refactoring recommendations.

### Motivation

Standard linters, type checkers, and code quality tools operate at the token, expression, or file level. They detect type errors, unused variables, formatting violations, and function-level complexity. They are structurally incapable of addressing the architectural dimension of code quality — the properties that live in dependency graphs, module partitions, interface contracts, and cross-component invariants.

In practice, developers seeking architectural feedback from automated agents observe a consistent failure: agents collapse toward low-level feature detection, because low-level features are directly localizable and weakly dependent on design intent. Architectural evaluation requires reconstructing abstract structural objects that are distributed across many files and can only be apprehended at the system level.

Vitruv addresses this gap. Architecture, though a high-level design concept, leaves observable structural traces in implementation artifacts. These traces are amenable to formal extraction and evaluation — provided the analysis operates on an appropriate intermediate representation rather than directly on source code.

### Advantages

- **Language-independent**: language-specific extraction feeds a shared canonical model; the same evaluation rules apply identically to Python, Java, or TypeScript codebases once their models share the same schema.
- **Formally grounded**: evaluation criteria derive from graph theory, Robert C. Martin's stability/abstractness metrics, and the connascence taxonomy — not ad hoc heuristics.
- **Policy-aware**: the system checks the extracted architecture against a declared target specification, so diagnostics reflect the project's own architectural intent rather than universal assumptions.
- **Honest about confidence**: every extracted relation carries a confidence annotation, and diagnostics are strictly classified as either hard violations (deterministic, unambiguous) or soft suspicions (probabilistic, requiring human verification).
- **Refactoring-oriented**: design patterns are treated as conditional refactoring hypotheses for diagnosed defects, not as taxonomic labels on existing code.

---

## Features

### Dependency Graph Analysis

- [ ] **Cycle detection**: strongly connected components in import and call subgraphs, particularly across component or bounded-context boundaries.
- [ ] **Layer violation detection**: dependency edges directed against the declared layer order.
- [ ] **Instability inversions**: stable components with high efferent coupling to volatile components.
- [ ] **Composition root violations**: construction of infrastructure services outside designated assembly zones.
- [ ] **Cross-layer shortcuts**: direct dependencies bypassing intermediate interface layers.

### Responsibility and Cohesion Analysis

- [ ] **Mixed-concern detection**: components combining orchestration, business logic, persistence, and presentation roles.
- [ ] **Structural cohesion measurement**: method–field bipartite graph connectivity (LCOM family).
- [ ] **Disjoint collaborator neighborhoods**: service objects whose call graph decomposes into unrelated clusters.

### Contract and Interface Analysis

- [ ] **Concrete-to-abstract violations**: direct dependency on implementations where an interface is expected.
- [ ] **Leaky interfaces**: public boundary signatures referencing infrastructure-layer types.
- [ ] **Interface segregation violations**: over-broad contracts with unrelated client groups.

### Configuration and Variability Analysis

- [ ] **Magic string detection**: string literals used as routing keys, event names, or service selectors outside their definition site.
- [ ] **Scattered configuration access**: configuration reads distributed across layers rather than isolated in a composition root.
- [ ] **Hardcoded infrastructure details**: literal connection strings, file paths, or service addresses inside domain-layer code.

### Architectural Smell Detection

- [ ] **God module / God service**: anomalously high fan-in with heterogeneous collaborator sets.
- [ ] **Shotgun surgery risk**: a single logical concern requiring modifications distributed across many unrelated components.
- [ ] **Framework leakage**: framework types appearing in domain-layer signatures or dependencies.
- [ ] **Policy–mechanism conflation**: components combining decision rules with execution machinery.
- [ ] **Hidden temporal coupling**: execution-order dependencies not expressed in the type or interface system.

### Design Pattern Reasoning

- [ ] **Structural motif detection**: confidence-scored recognition of creational, structural, and behavioral pattern skeletons.
- [ ] **Defect-to-pattern mapping**: recommendation of candidate patterns as solutions to diagnosed structural problems.
- [ ] **Pattern composition analysis**: reasoning over motif chains (e.g., Strategy-via-AbstractFactory) as distinct architectural commitments.

### Conformance Checking

- [ ] **Declared architecture specification**: a versioned YAML format encoding allowed dependencies, layer policies, composition root zones, and public boundary declarations.
- [ ] **Drift detection**: comparison of the extracted model against the declared target, reporting divergences as policy violations.

### Scoring and Reporting

- [ ] **Hard/soft diagnostic separation**: confirmed invariant violations are clearly distinguished from probabilistic risk signals.
- [ ] **Martin's metrics**: instability, abstractness, and distance from the main sequence computed per component.
- [ ] **Connascence classification**: coupling between components characterized by connascence class (identity, type, meaning, algorithm, execution).

---

## Installation

### Using pip

Install from the GitHub repository:

```bash
pip install git+https://github.com/esther-poniatowski/vitruv.git
```

### Using conda

Install from the eresthanaconda channel:

```bash
conda install vitruv -c eresthanaconda
```

### From source

1. Clone the repository:

      ```bash
      git clone https://github.com/esther-poniatowski/vitruv.git
      ```

2. Create a dedicated virtual environment and install:

      ```bash
      cd vitruv
      conda env create -f environment.yml
      conda activate vitruv
      ```

---

## Quick Start

### CLI

```sh
vitruv --help
```

### Python

```python
import vitruv

vitruv.info()
```

---

## Documentation

- [User Guide](https://esther-poniatowski.github.io/vitruv/guide/)
- [API Documentation](https://esther-poniatowski.github.io/vitruv/api/)
- [Project Proposal](docs/proposal.md)

> [!NOTE]
> Documentation can also be browsed locally from the [`docs/`](docs/) directory.

---

## Support

**Issues**: [GitHub Issues](https://github.com/esther-poniatowski/vitruv/issues)

**Email**: `esther.poniatowski@ens.psl.eu`

---

## Contributing

Please refer to the [contribution guidelines](CONTRIBUTING.md).

---

## Acknowledgments

### Authors & Contributors

**Author**: @esther-poniatowski

**Contact**: `esther.poniatowski@ens.psl.eu`

For academic use, please cite using the GitHub "Cite this repository" feature to
generate a citation in various formats.

Alternatively, refer to the [citation metadata](CITATION.cff).

### Theoretical Foundations

Vitruv's evaluation criteria are grounded in the following frameworks:

- **Robert C. Martin's package metrics** — instability, abstractness, and the main sequence as quantitative measures of component health
- **Connascence taxonomy** (Meilir Page-Jones) — a refined coupling vocabulary characterizing what two components must agree on for correctness
- **Graph-theoretic dependency analysis** — cycle detection, reachability, and typed path predicates over architectural models
- **Design pattern theory** (Gamma et al.) — structural motifs treated as conditional refactoring hypotheses, not taxonomic labels

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
