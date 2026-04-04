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
- **Policy-aware diagnostics** — each diagnostic compares the extracted architecture
  against a declared target specification, reflecting the project's own intent rather
  than universal assumptions.
- **Confidence annotations** — every extracted relation carries a confidence level, and
  diagnostics are classified as either hard violations (deterministic) or soft
  suspicions (probabilistic).
- **Refactoring-oriented patterns** — design patterns are treated as conditional
  refactoring hypotheses for diagnosed defects, not as taxonomic labels.

### Theoretical Foundations

The analysis framework draws on Robert C. Martin's package metrics (afferent/efferent
coupling, instability, abstractness), the connascence taxonomy (Page-Jones), and
graph-theoretic structural analysis.

---

## Features

### Dependency Graph Analysis

- [ ] **Cycle detection**: Detect strongly connected components in import and call
  subgraphs, particularly across bounded-context boundaries.
- [ ] **Layer violations**: Flag dependency edges directed against the declared layer
  order.
- [ ] **Instability inversions**: Identify stable components with high efferent coupling
  to volatile components.
- [ ] **Composition root violations**: Flag infrastructure services constructed outside
  designated assembly zones.
- [ ] **Cross-layer shortcuts**: Detect direct dependencies that bypass intermediate
  interface layers.

### Responsibility and Cohesion Analysis

- [ ] **Mixed concerns**: Detect components combining orchestration, business logic,
  persistence, and presentation roles.
- [ ] **Structural cohesion**: Measure method–field bipartite graph connectivity (LCOM
  family).
- [ ] **Disjoint collaborator neighborhoods**: Detect service objects whose call graph
  decomposes into unrelated clusters.

### Contract and Interface Analysis

- [ ] **Concrete-to-abstract violations**: Flag direct dependencies on implementations
  where an interface is expected.
- [ ] **Leaky interfaces**: Detect public boundary signatures that reference
  infrastructure-layer types.
- [ ] **Interface segregation violations**: Identify over-broad contracts with unrelated
  client groups.

### Configuration and Variability Analysis

- [ ] **Magic strings**: Detect string literals used as routing keys, event names, or
  service selectors outside their definition site.
- [ ] **Scattered configuration access**: Flag configuration reads distributed across
  layers rather than isolated in a composition root.
- [ ] **Hardcoded infrastructure details**: Detect literal connection strings, file
  paths, or service addresses inside domain-layer code.

### Architectural Smell Detection

- [ ] **God module / God service**: Identify components with anomalously high fan-in
  and heterogeneous collaborator sets.
- [ ] **Shotgun surgery risk**: Detect a single logical concern requiring modifications
  distributed across many unrelated components.
- [ ] **Framework leakage**: Flag framework types appearing in domain-layer signatures
  or dependencies.
- [ ] **Policy–mechanism conflation**: Detect components combining decision rules with
  execution machinery.
- [ ] **Hidden temporal coupling**: Identify execution-order dependencies not expressed
  in the type or interface system.

### Design Pattern Reasoning

- [ ] **Structural motif detection**: Recognize creational, structural, and behavioral
  pattern skeletons with confidence scores.
- [ ] **Defect-to-pattern mapping**: Recommend candidate patterns as solutions to
  diagnosed structural problems.
- [ ] **Pattern composition analysis**: Reason over motif chains (e.g.,
  Strategy-via-AbstractFactory) as distinct architectural commitments.

### Conformance Checking

- [ ] **Declared architecture specification**: Define allowed dependencies, layer
  policies, composition root zones, and public boundary declarations in a versioned
  YAML format.
- [ ] **Drift detection**: Compare the extracted model against the declared target and
  report divergences as policy violations.

### Scoring and Reporting

- [ ] **Hard/soft diagnostic separation**: Distinguish confirmed invariant violations
  from probabilistic risk signals.
- [ ] **Martin's metrics**: Compute instability, abstractness, and distance from the
  main sequence per component.
- [ ] **Connascence classification**: Characterize coupling between components by
  connascence class (identity, type, meaning, algorithm, execution).

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
