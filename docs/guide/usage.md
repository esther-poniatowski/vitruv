# Usage

Vitruv analyzes the structural quality of software projects by extracting
dependency graphs, measuring architectural metrics, and detecting structural
smells. The tool operates on import graphs extracted from any language.

For the full command registry, refer to [CLI Reference](cli-reference.md). For
audit profiles and rule selection, refer to [Configuration](configuration.md).

## Analyzing a Project

The `analyze` command extracts the dependency graph and reports structural
metrics:

```sh
vitruv analyze src/
```

## Running an Architectural Audit

Audits evaluate specific structural dimensions. The `--profile` flag selects
among predefined audit profiles:

```sh
vitruv audit src/ --profile component
vitruv audit src/ --profile interaction
vitruv audit src/ --profile model
```

Each profile targets a distinct dimension:

- **component** — module cohesion, responsibility boundaries, and internal
  coupling.
- **interaction** — dependency direction, interface segregation, and protocol
  conformance.
- **model** — data model consistency, abstraction levels, and domain
  alignment.

## Detecting Architectural Smells

The `smells` command identifies common structural anti-patterns:

```sh
vitruv smells src/
```

Detected smells include cyclic dependencies, god modules, unstable
dependencies, shotgun surgery, and layer violations.

## Measuring Package Metrics

Quantitative metrics follow Robert C. Martin's package principles:

```sh
vitruv metrics src/
```

Reported metrics include afferent coupling (Ca), efferent coupling (Ce),
instability (I), abstractness (A), and distance from the main sequence (D).

## Checking Conformance

Verify that a codebase conforms to a declared architecture:

```sh
vitruv conform src/ --architecture architecture.yaml
```

The architecture file declares allowed and forbidden dependency directions
between modules or layers.

## Programmatic API

The same analysis is accessible from Python:

```python
from vitruv.api import analyze

report = analyze("src/")
for module in report.modules:
    print(f"{module.name}: I={module.instability:.2f} A={module.abstractness:.2f}")
```

## Next Steps

- [CLI Reference](cli-reference.md) — Full command registry and options.
- [Configuration](configuration.md) — Audit profiles, rule selection.
- [Design Principles](../standards/design-principles.md) — Software design standards.
- [Audit Taxonomy](../design/audit-taxonomy.md) — Audit dimensions and categories.
