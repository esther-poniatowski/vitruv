# Modeling Principles

Architectural rules governing the adequacy of the code's domain model.
Authoritative source for modeling standards enforced by the
[model audit prompt](../audits/audit-model.md).

Where the [design principles](design-principles.md) govern whether components
are well-built and the [interaction principles](interaction-principles.md)
govern whether components coordinate correctly, these principles govern whether
the components represent the right concepts.

---

## 1. Concept Coverage

Every load-bearing domain concept must have an explicit code counterpart.

### 1.1 Explicit Representation Rule

A domain concept is **load-bearing** if multiple components depend on it — by
computing it, consuming it, or making decisions based on it. Load-bearing
concepts must be represented as named types (dataclasses, protocols, enums),
not derived ad-hoc at each point of use.

### 1.2 Ad-Hoc Derivation

A domain concept that is derived at runtime by one or more functions — rather
than existing as a named type — is **ad-hoc**. Ad-hoc representation is a
modeling defect when:

- multiple consumers derive the same concept independently (redundant
  derivation)
- the concept's derivation logic changes, requiring updates in multiple
  locations
- the concept cannot be inspected, logged, or tested in isolation because it
  exists only transiently during computation

### 1.3 Acceptable Absence

A domain concept may lack a code counterpart when:

- it is genuinely out of scope for the system's purpose
- it is used by a single consumer at a single site, making extraction premature
- it maps directly to a primitive type with no additional semantics (e.g.,
  a file path represented as `str` when no path-specific operations are needed)

### 1.4 Violation Indicators

- a computation that produces a meaningful intermediate result which is
  immediately decomposed and discarded, never stored as a named object
- multiple functions that extract the same subset or derived property from a
  shared input type, each re-implementing the extraction
- a concept that appears in the project's documentation, user interface, or
  configuration but has no corresponding type in the code

---

## 2. Relationship Coverage

Every load-bearing relationship between domain concepts must have an explicit
representation, not be derived ad-hoc by consumers.

### 2.1 Explicit Relationship Rule

A relationship is **load-bearing** if it carries information that multiple
consumers need. Load-bearing relationships must be pre-computed and stored in a
named type, not re-derived at each consumption site.

### 2.2 Relationship Types

Domain relationships include:

- **Alignment**: the correspondence between two parallel structures (e.g.,
  function parameters and their documentation entries)
- **Derivation**: a value computed from two or more inputs (e.g., the set of
  undocumented parameters, derived from the signature and the docstring)
- **Classification**: the assignment of an entity to a category based on
  multiple attributes
- **Aggregation**: a summary computed from a collection of entities (e.g.,
  documentation coverage of a module)

### 2.3 Cost of Ad-Hoc Relationship Derivation

When relationships are derived ad-hoc:

- multiple consumers may compute slightly different versions of the same
  relationship (divergent derivation)
- the relationship cannot be tested in isolation — it exists only as a
  by-product of a consumer's logic
- adding a new consumer that needs the relationship requires re-implementing
  the derivation
- the relationship's semantics are implicit in the code rather than declared
  in a type

### 2.4 Violation Indicators

- two or more functions that take the same pair of inputs and compute a
  cross-reference between them
- a consumer that receives two inputs and spends its first several lines
  aligning them before performing its actual logic
- a utility module whose sole purpose is to factor out a cross-referencing
  computation used by multiple consumers — the utility addresses code
  duplication but not model duplication

---

## 3. Abstraction Fidelity

Code constructs that represent domain concepts must capture the concept's
essential attributes and relationships, not a partial or distorted subset.

### 3.1 Fidelity Rule

A code construct that claims to represent a domain concept must:

- include all attributes that consumers need
- model the concept at the right granularity (not too coarse, not too fine)
- represent the concept's relationships to other concepts through typed fields
  or protocol methods, not through external computation

### 3.2 Partial Representation

A code construct that captures only a subset of a domain concept's attributes
forces consumers to supplement it with additional data from other sources. This
is a fidelity defect when:

- the missing attributes are needed by most consumers (the type is
  systematically incomplete)
- the supplementation pattern is repeated across consumers
- the missing attributes are available at construction time but are not stored

### 3.3 Granularity Mismatch

- **Too coarse**: a single type conflates two distinct domain concepts that have
  different lifecycles, different consumers, or different update frequencies.
  Consumers must filter or decompose the type to reach the concept they need.
- **Too fine**: a domain concept is split across multiple types that are always
  used together. Consumers must reassemble the concept from its fragments.

### 3.4 Violation Indicators

- a type that requires a companion helper function to be usable (the helper
  compensates for the type's missing attributes)
- a consumer that receives a typed argument and immediately accesses a second
  data source to supplement it with information that should have been on the
  type
- a type that has a field named `extra`, `metadata`, or `context` used as an
  escape hatch for attributes that don't fit the declared schema

---

## 4. Abstraction Economy

The code must not contain named abstractions that do not correspond to domain
concepts and are not required by the implementation platform.

### 4.1 Economy Rule

Every named type, module, or protocol in the codebase must be justified by one
of two grounds:

- it represents a domain concept (covered by Concept Coverage)
- it is a technical necessity of the implementation platform (framework
  requirement, serialization adapter, protocol for dependency inversion)

Types that satisfy neither criterion are **phantom abstractions**: they model
nothing in the domain and serve no technical purpose.

### 4.2 Phantom Abstraction Indicators

- a type that wraps another type with no additional attributes or behavior
  beyond delegation
- a module that exists because "it might be needed later" but has no current
  consumer
- a protocol or interface with a single implementation that is not expected to
  gain additional implementations
- a type whose name cannot be explained in domain terms without referring to
  the code's internal structure

### 4.3 Acceptable Technical Abstractions

The following are not phantom abstractions:

- protocols that invert dependencies across layer boundaries (even with a
  single implementation)
- adapter types that translate between the domain model and an external system
- configuration types that structure runtime parameters
- result types that make error paths explicit

### 4.4 Distinction from Premature Abstraction

A phantom abstraction models nothing. A premature abstraction models something
real but introduces the model before it is needed, adding complexity without
current benefit. Both are defects, but with different remediations:

- phantom abstractions should be removed
- premature abstractions should be inlined and reintroduced when the second
  use case materializes
