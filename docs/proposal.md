# Static Architecture Analysis System: A Formal Proposal

---

## Table of Contents

- [Static Architecture Analysis System: A Formal Proposal](#static-architecture-analysis-system-a-formal-proposal)
  - [Table of Contents](#table-of-contents)
  - [1. Problem Statement](#1-problem-statement)
  - [2. Project Goal](#2-project-goal)
  - [3. Foundational Thesis](#3-foundational-thesis)
  - [4. System Architecture](#4-system-architecture)
    - [4.1 Extraction Layer](#41-extraction-layer)
    - [4.2 Canonical Architectural Model](#42-canonical-architectural-model)
      - [Node types](#node-types)
      - [Edge types](#edge-types)
      - [Node annotations](#node-annotations)
      - [Formal properties](#formal-properties)
    - [4.3 Evaluation Layer](#43-evaluation-layer)
      - [Rule specification language](#rule-specification-language)
      - [Cross-cutting concern exemptions](#cross-cutting-concern-exemptions)
    - [4.4 Recommendation Engine](#44-recommendation-engine)
    - [4.5 Intent Alignment Module](#45-intent-alignment-module)
  - [5. Evaluation Criteria Taxonomy](#5-evaluation-criteria-taxonomy)
    - [5.1 Dependency-Graph Criteria](#51-dependency-graph-criteria)
    - [5.2 Responsibility and Cohesion Criteria](#52-responsibility-and-cohesion-criteria)
    - [5.3 Contract and Interface Criteria](#53-contract-and-interface-criteria)
    - [5.4 Configuration and Variability Criteria](#54-configuration-and-variability-criteria)
    - [5.5 Metric Frameworks](#55-metric-frameworks)
      - [Martin's stability and abstractness metrics](#martins-stability-and-abstractness-metrics)
      - [Connascence taxonomy](#connascence-taxonomy)
    - [5.6 Design Pattern Detection and Prescription](#56-design-pattern-detection-and-prescription)
      - [Detectable pattern families](#detectable-pattern-families)
      - [Detection methodology](#detection-methodology)
      - [Pattern composition](#pattern-composition)
    - [5.7 Architectural Code Smells](#57-architectural-code-smells)
  - [6. Diagnostic Classification](#6-diagnostic-classification)
    - [Hard diagnostics](#hard-diagnostics)
    - [Soft diagnostics](#soft-diagnostics)
  - [7. Epistemic Limitations](#7-epistemic-limitations)
  - [8. Principal Technical Challenges](#8-principal-technical-challenges)
    - [8.1 Semantic recovery under dynamic dispatch](#81-semantic-recovery-under-dynamic-dispatch)
    - [8.2 Edge type semantics](#82-edge-type-semantics)
    - [8.3 Framework distortion](#83-framework-distortion)
    - [8.4 False positives in pattern detection](#84-false-positives-in-pattern-detection)
    - [8.5 Cross-cutting concern misclassification](#85-cross-cutting-concern-misclassification)
    - [8.6 Incremental analysis](#86-incremental-analysis)
  - [9. Implementation Strategy](#9-implementation-strategy)
    - [Phase 1 — Core extraction and model foundation](#phase-1--core-extraction-and-model-foundation)
    - [Phase 2 — Dependency graph and layering evaluation](#phase-2--dependency-graph-and-layering-evaluation)
    - [Phase 3 — Policy declaration and conformance checking](#phase-3--policy-declaration-and-conformance-checking)
    - [Phase 4 — Heuristic smell and pattern detection](#phase-4--heuristic-smell-and-pattern-detection)
    - [Phase 5 — Incremental analysis and additional language front-ends](#phase-5--incremental-analysis-and-additional-language-front-ends)
  - [10. Summary](#10-summary)

---

## 1. Problem Statement

Software architects and senior developers routinely audit codebases for structural deficiencies that conventional static analysis tools are unable to detect. Standard linters, type checkers, and code quality tools operate at the token, expression, or at best file level. Their diagnostic scope is confined to: type errors, unused variables, formatting violations, cyclomatic complexity within functions, and similar low-level signals. These tools are structurally incapable of addressing the architectural dimension of code quality.

Architectural quality concerns a different class of objects entirely: subsystem boundaries, dependency directions, ownership of responsibilities, lifecycle orchestration, interaction protocols, variability points, extension mechanisms, coupling modes, and the separation of domain logic from infrastructure. These are properties of **graphs, partitions, contracts, and invariants**, not of isolated lines or files.

In practice, developers seeking architectural feedback from automated agents observe a systematic failure: agents consistently collapse toward low-level feature detection. This failure is unsurprising. Low-level features are directly localizable, easy to verify, language-tooling friendly, and weakly dependent on domain intent. Architectural evaluation, by contrast, requires the reconstruction of abstract structural objects that are distributed across many files and modules, and that can only be apprehended at the system level.

This systematic gap motivates the present project. Architecture, though a high-level intellectual design concept, leaves observable structural traces in implementation artifacts. The project's core premise is that these traces are, at least partially, amenable to formal extraction and evaluation — provided the analysis operates on an appropriate intermediate representation rather than directly on raw source code.

---

## 2. Project Goal

The goal is to design and implement a **Static Architecture Analysis System (SAAS)**: a multi-layer analysis pipeline capable of evaluating the architectural quality of a software system from its implementation artifacts, across multiple programming languages, through the following capabilities:

- **Dependency graph analysis**: detection of cycles, forbidden dependency directions, coupling anomalies, and layering violations.
- **Responsibility and cohesion analysis**: identification of over-loaded components, mixed-concern structures, and semantic incoherence.
- **Contract and interface analysis**: detection of abstraction failures, interface segregation violations, and stability mismatches.
- **Configuration and variability analysis**: identification of scattered configuration, magic strings, hidden coupling, and missing composition roots.
- **Design pattern detection**: structural motif recognition for creational, structural, and behavioral patterns, treated as refactoring hypotheses rather than taxonomic badges.
- **Architectural code smell detection**: identification of god objects, shotgun surgery risk, framework leakage, policy-mechanism conflation, and related large-scale structural pathologies.
- **Conformance checking**: optional comparison of the extracted architectural model against a declared target architecture.

The system is explicitly not designed to replace human architectural review. Its output is a set of structural signals, measurable invariants, and probabilistic risk indicators — the diagnostics most suitable for supporting, not substituting, expert judgment.

---

## 3. Foundational Thesis

The project rests on the following architectural thesis:

> Architecture as a design intention is partly semantic and contextual. Architecture as an implemented system leaves **observable structural traces** in implementation artifacts. A static analysis system can only assess the second level directly. Its validity rests on the precision of the mapping between architectural concepts and observable structural properties.

This entails a strict methodological constraint: the system must not claim to evaluate "architectural quality in general." It evaluates a rigorously defined set of **operationalized structural properties**, extracted from code and configuration artifacts, organized into a canonical intermediate model, and assessed through a combination of formal rules and calibrated heuristics.

The key architectural insight enabling language independence is the following:

> The language-specific properties of a codebase — import semantics, type resolution, inheritance mechanics, visibility rules, metaprogramming conventions — are concerns of the **extraction front-end**. Once abstracted into a canonical architectural model, the evaluation rules become **language-agnostic**. The same cycle detection, layer violation check, or god-object heuristic applies identically to a Python, Java, or TypeScript codebase once their architectural models share the same schema.

This motivates the fundamental design: **language-specific front-ends feeding a shared intermediate model evaluated by a shared rule and heuristic engine**.

---

## 4. System Architecture

The system is organized as a five-layer pipeline.

```
┌────────────────────────────────────────────────────────────────────┐
│  SOURCE ARTIFACTS  (source files, configuration, build descriptors) │
└───────────────────────────────┬────────────────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   1. EXTRACTION LAYER  │  (language-specific)
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  2. CANONICAL MODEL    │  (language-agnostic)
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   3. EVALUATION LAYER  │  (rules + heuristics)
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  4. RECOMMENDATION     │  (defect → refactoring)
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  5. INTENT ALIGNMENT   │  (optional conformance)
                    └────────────────────────┘
```

---

### 4.1 Extraction Layer

The extraction layer is language-specific. Its responsibility is to parse implementation artifacts and reconstruct a raw structural description of the system from which the canonical model is assembled.

Extracted objects include:

- **Structural units**: modules, packages, namespaces, classes, interfaces, protocols, traits, functions, methods.
- **Dependency relations**: import edges, call edges, inheritance edges, composition edges, construction edges.
- **Configuration sources**: environment variable accesses, configuration file readers, feature flag evaluations.
- **Infrastructure access points**: database access sites, external service clients, file system access, network calls.
- **Communication infrastructure**: event channels, message buses, service registries, pub/sub subscriptions.
- **Data model definitions**: schema declarations, DTO definitions, serialization boundaries.
- **Side-effect boundaries**: mutation sites, I/O sites, observable state transitions.
- **Extension points**: plugin registries, abstract factories, strategy injection sites, hook declarations.
- **Symbolic identifiers**: string literals used as routing keys, event names, service identifiers, registry keys.

**Critical constraint**: for dynamic languages such as Python and JavaScript, exact static extraction is an undecidable problem in general. Dynamic attribute assignment, runtime module loading, metaclasses, decorator-based wiring, and dependency injection containers mean that any extraction is an approximation. The extraction layer must therefore:

1. operate as an approximation engine with explicit soundness/completeness trade-offs,
2. attach **confidence annotations** to every extracted relation,
3. propagate these annotations into the canonical model so that downstream rule evaluation can condition diagnostic severity on evidentiary confidence.

This is not an implementation inconvenience but a **first-class architectural constraint** on the entire system. An evaluation layer that treats the intermediate model as exact will systematically produce both false positives and false negatives on dynamically wired codebases.

---

### 4.2 Canonical Architectural Model

The canonical architectural model is the central theoretical object of the system. It is the primary design investment and the condition for language independence. It must not be a repackaged AST. It is a **typed attributed multigraph** whose schema is defined independently of any source language.

#### Node types

| Node type | Semantic role |
|---|---|
| `Component` | Deployable or logical unit with a defined boundary |
| `Interface` | Abstract contract exposed at a boundary |
| `Implementation` | Concrete realization of an interface or role |
| `Orchestrator` | Unit responsible for coordinating other components |
| `PolicyObject` | Unit encoding a decision rule or business invariant |
| `InfrastructureService` | Adapter to an external or volatile resource |
| `ConfigurationSource` | Provider of runtime-variable parameters |
| `DataSchema` | Definition of a data structure exchanged across boundaries |
| `ExternalAdapter` | Translation layer between domain and external protocol |
| `ExtensionPoint` | Declared variability seam |

#### Edge types

| Edge type | Semantic role |
|---|---|
| `imports` | Static module dependency |
| `calls` | Runtime invocation |
| `constructs` | Instantiation responsibility |
| `implements` | Interface realization |
| `inherits` | Supertype relation |
| `owns` | Lifecycle ownership |
| `reads_config_from` | Configuration dependency |
| `publishes_event_to` | Outbound event emission |
| `subscribes_to` | Inbound event consumption |
| `persists_to` | Persistence coupling |
| `serializes_to` | Data exchange coupling |

#### Node annotations

Each node carries a set of typed annotations:

- `layer`: the architectural layer to which the node is assigned (e.g., `domain`, `application`, `infrastructure`, `presentation`)
- `bounded_context`: the domain subdomain owning this node
- `stability`: estimated stability level (`stable`, `volatile`, `external`)
- `side_effect_class`: classification of observable effects (`pure`, `io`, `mutation`, `external_call`)
- `framework_dependent`: boolean flag indicating tight coupling to a framework
- `public_boundary`: boolean flag indicating exposure across subsystem boundaries
- `confidence`: extraction confidence score in $[0, 1]$

#### Formal properties

Beyond the schema, the model must satisfy three formal properties to support sound evaluation:

**Completeness semantics**: Every fact in the model carries a confidence annotation. Rules that fire on low-confidence facts produce warnings annotated as `probable` rather than `certain`. Aggregated confidence over a rule's evidentiary basis is propagated to the diagnostic.

**Edge compositionality**: The model supports derived relations through transitive closure and path predicates. Crucially, a `calls` edge followed by an `imports` edge crossing a layer boundary is a structurally distinct fact from a direct `imports` edge crossing that boundary. The evaluation layer must be able to reason over typed paths, not merely individual edges.

**Versioned instantiation**: The model optionally supports multiple timestamped instances to enable delta-based analysis. Architectural decay is a process; the detection of incremental boundary erosion, growing god objects, and progressive layering violations requires diachronic comparison.

---

### 4.3 Evaluation Layer

The evaluation layer applies formal rules and calibrated heuristics to the canonical model. The choice of rule specification language is a first-class design decision.

#### Rule specification language

The evaluation layer requires a formal language for expressing architectural constraints as predicates over the canonical model. The expressivity/decidability trade-off for candidate language classes is as follows:

| Language class | Example | Decidability | Expressivity |
|---|---|---|---|
| Threshold predicates | Fan-out $> k$ | Decidable, $O(n)$ | Low |
| First-order graph logic | $\exists$ path from domain node to infrastructure node | Decidable | Moderate |
| Datalog over typed graph | Transitive reachability under typed edge composition | Decidable, polynomial | High |
| Second-order partition logic | Layering invariants over arbitrary partitions | Generally undecidable | Very high |

**Recommendation**: a Datalog-class DSL, analogous in spirit to CodeQL/QL or Soufflé, is the appropriate target formalism. It provides sufficient expressivity for all criteria families enumerated in §5, tractable evaluation over realistic codebases, and composable rule libraries that can be maintained and extended independently of the extraction layer.

#### Cross-cutting concern exemptions

A critical source of false positives that naive evaluation layers produce is the conflation of **accidental coupling** with **mandated cross-cutting structure**. Logging instrumentation, security enforcement, transaction demarcation, and observability pipelines produce coupling patterns that structurally resemble violations but are legitimate by design. The evaluation layer must support an exemption mechanism — either through explicit cross-cutting annotations on the canonical model, or through a policy-layer exemption declaration — to distinguish framework leakage (a defect) from centralized observability instrumentation (a design choice).

---

### 4.4 Recommendation Engine

The recommendation engine maps diagnosed structural defects to structured refactoring hypotheses. Its function is distinct from diagnosis: where the evaluation layer identifies *what* is structurally wrong, the recommendation engine characterizes *how* it could be corrected and *which* design patterns constitute candidate solution schemas.

The correct order of reasoning is:

1. Detect a structural problem (e.g., excessive conditional dispatch over an algorithm family)
2. Characterize its structural form (e.g., branching over type tags without polymorphic dispatch)
3. Infer candidate refactorings (e.g., extract strategy objects, introduce polymorphic interface)
4. Name the pattern as a solution schema (e.g., Strategy pattern)

This ordering prevents the classical failure mode of badge-based pattern detection ("this class is a Strategy") and correctly positions patterns as **conditional refactoring hypotheses**, not taxonomic labels.

The recommendation engine must also reason over **pattern compositions**, not merely individual motifs. A Strategy instantiated through an Abstract Factory is a different architectural commitment than one wired through direct construction. A Decorator chain over a Facade implies different coupling topology than a Decorator directly wrapping a domain object. Compositional motif paths must be expressible as recommendation targets.

---

### 4.5 Intent Alignment Module

The intent alignment module provides the **conformance checking** use case: comparison of the extracted architectural model against a declared target architecture. This use case is significantly more reliable than architecture discovery alone because the declared architecture provides ground truth against which extraction results are evaluated, rather than requiring the system to infer intended structure from implementation alone.

The module requires its own **declarative specification format**, versioned alongside the codebase. This format must be expressive enough to encode:

- allowed and forbidden dependency edges between layers or bounded contexts
- composition root declarations (specifying which zones are authorized to construct infrastructure services)
- public boundary declarations (specifying which interfaces are exposed across subsystem boundaries)
- extension point declarations
- naming and placement conventions for interfaces and adapters
- stability and volatility assignments

The specification format should be language-neutral (YAML or TOML are appropriate bases), parsed by a dedicated module strictly separated from the extraction and evaluation layers, and validated against a published schema. It is the primary input to the conformance rule engine and should be treated as a first-class project artifact, not a configuration afterthought.

---

## 5. Evaluation Criteria Taxonomy

### 5.1 Dependency-Graph Criteria

Dependency graph criteria form the most formally tractable family. The canonical model provides the graph-theoretic substrate on which these criteria are expressed as predicates.

**Formal structure**: let $G = (V, E, \lambda, \mu)$ be the canonical model where $V$ is the node set, $E \subseteq V \times V \times T$ is the typed edge set over edge type vocabulary $T$, $\lambda: V \to \mathcal{A}$ assigns annotation tuples to nodes, and $\mu: E \to [0,1]$ assigns confidence weights to edges.

Let $\Pi: V \to L$ be the layer assignment of nodes to a total order of layers $L = (l_1 \prec l_2 \prec \cdots \prec l_k)$. A **layering violation** exists whenever there is an edge $(u, v, \tau) \in E$ such that $\Pi(u) \prec \Pi(v)$ and the edge direction is forbidden by the declared layer policy — equivalently, when a lower-layer component depends upon a higher-layer component.

Detectable criteria in this family include:

- **Dependency cycles**: strongly connected components of size $> 1$ in the import or call subgraphs, particularly those crossing component or bounded-context boundaries
- **Layer violations**: edges directed against the declared layer order
- **Instability inversions**: stable components with high efferent coupling to volatile components (see §5.5)
- **Dependency concentration**: components with anomalously high fan-in (god modules) or fan-out
- **Bidirectional coupling**: pairs of components with edges in both directions across a declared boundary
- **Infrastructure-to-domain inversion**: infrastructure layer components depending on domain layer components in a direction violating the Dependency Inversion Principle
- **Composition root violations**: construction of infrastructure services outside declared composition root zones
- **Cross-layer shortcuts**: direct dependencies bypassing intermediate interface layers

### 5.2 Responsibility and Cohesion Criteria

Cohesion analysis requires a strict separation of two structurally distinct concepts, the conflation of which produces both false positives and theoretical confusion.

**Structural cohesion** is directly measurable from the canonical model. The LCOM (Lack of Cohesion in Methods) family of metrics quantifies whether the methods of a class operate on overlapping subsets of its fields. In its graph-theoretic formulation, a class is structurally cohesive if its method–field bipartite graph is connected; LCOM measures the number of connected components of that bipartite graph. This is computable from the canonical model without any semantic interpretation.

**Semantic cohesion** refers to whether the operations of a component belong to the same conceptual domain. This is only partially analyzable through naming heuristics and embedding-based similarity. A tool cannot decide semantic cohesion from structure alone. Diagnostics in this dimension must be classified as heuristic suspicions with explicitly bounded confidence, not rule violations.

Structural signals of low cohesion or mixed responsibility include:

- Components combining orchestration, business logic, persistence, and presentation roles as evidenced by heterogeneous edge neighborhoods (calls to infrastructure, domain, and presentation nodes simultaneously)
- Components whose collaborator sets decompose into two or more structurally disjoint neighborhoods in the call graph
- Methods operating exclusively on disjoint field subsets (high LCOM)
- Service objects that both construct dependencies and execute policies (construction edge co-occurring with policy execution in the same node)

### 5.3 Contract and Interface Criteria

Contract and interface criteria address the stability and correctness of the boundaries through which components interact.

Detectable criteria include:

- **Concrete-to-abstract violations**: direct dependency on concrete implementations where the dependency inversion principle mandates an abstract interface, detectable from the absence of an `implements` or `Interface` node on the dependency path
- **Interface stability mismatches**: volatile interfaces (high efferent coupling, low abstractness) exposed across stable subsystem boundaries
- **Leaky interfaces**: public boundary interfaces whose signatures reference infrastructure-layer types, detectable from type annotations crossing layer boundaries in the canonical model
- **Interface segregation violations**: interfaces with excessively high fan-out among unrelated clients, suggesting over-broad contract definitions
- **Substitutability violations**: structural evidence that concrete implementations diverge from the behavioral contract implied by their interface (partially detectable from method signature mismatches and override patterns)
- **Protocol inconsistency**: heterogeneous error-handling or result-encoding patterns across components declared as interchangeable

### 5.4 Configuration and Variability Criteria

Configuration and variability criteria target the class of architectural defects that arise when runtime-variable parameters are hardcoded, scattered, or accessed through inconsistent paths.

Detectable criteria include:

- **Magic strings**: string literals used as routing keys, event names, registry identifiers, or service selectors outside their canonical definition site, detectable from the `symbolic_identifier` extraction category
- **Hardcoded infrastructure details**: literal values encoding infrastructure configuration (connection strings, file paths, service addresses) inside domain or application layer nodes
- **Scattered configuration access**: `reads_config_from` edges distributed across multiple layers rather than isolated in a composition root or configuration module
- **Feature toggle fragmentation**: conditional branches keyed on feature flags without centralized ownership
- **Duplicated configuration logic**: structurally isomorphic configuration assembly code distributed across multiple modules
- **Stringly-typed architecture**: systematic use of string literals as identifiers in place of typed symbolic constants across inter-component communication

### 5.5 Metric Frameworks

Two established metric frameworks are directly computable from the canonical model and should be first-class outputs of the evaluation layer.

#### Martin's stability and abstractness metrics

For a component $C$, let $C_a$ denote afferent coupling (number of components depending on $C$) and $C_e$ denote efferent coupling (number of components $C$ depends on). The **instability** of $C$ is:

$$I(C) = \frac{C_e}{C_a + C_e} \in [0, 1]$$

Let $N_a$ denote the number of abstract types (interfaces, abstract classes) in $C$ and $N_c$ the total number of types. The **abstractness** of $C$ is:

$$A(C) = \frac{N_a}{N_c} \in [0, 1]$$

The **distance from the main sequence** measures deviation from the desirable trade-off between stability and abstraction:

$$D(C) = |A(C) + I(C) - 1|$$

Components in the **zone of pain** ($A \approx 0$, $I \approx 0$: stable and concrete) are rigid and hard to extend. Components in the **zone of uselessness** ($A \approx 1$, $I \approx 1$: abstract and unstable) impose abstraction overhead without stability benefit. Both extremes are diagnosable from the canonical model.

#### Connascence taxonomy

The connascence taxonomy provides a more refined coupling vocabulary than simple edge types. Connascence characterizes the nature of the dependency between two components — what they must agree on for the system to remain correct:

| Connascence class | Description | Architectural impact |
|---|---|---|
| Identity | Must reference the same object | High (object coupling) |
| Type | Must agree on a type | Moderate |
| Meaning | Must agree on interpretation of a value | High (magic constants) |
| Position | Must agree on argument order | Moderate |
| Algorithm | Must use the same algorithm | Very high |
| Execution | Must execute in a specific order | High (temporal coupling) |
| Timing | Must execute within a time window | Very high |
| Value | Must agree on constrained value sets | Moderate |

Connascence of meaning is of particular relevance to architectural analysis: it is the precise formal characterization of the defect underlying magic strings, magic integers, and stringly-typed architectures. The smell detector should report connascence class alongside smell identification.

### 5.6 Design Pattern Detection and Prescription

Pattern detection must be treated with the following methodological constraints:

1. **Presence is not quality**: the presence of a pattern is not evidence of architectural merit. The absence of a pattern in a context where it would resolve a structural defect is a stronger signal.
2. **Patterns are partial and hybrid**: real code frequently implements degenerate, partial, or hybrid forms of textbook patterns. Detection must estimate confidence, not assert identity.
3. **Prescription precedes identification**: the primary function of pattern reasoning is not to label existing structures but to identify candidate patterns that would resolve diagnosed structural defects.

#### Detectable pattern families

**Creational**: Factory Method, Abstract Factory, Builder, Prototype, Singleton, Dependency Injection Container, Service Locator (as an anti-pattern signal).

**Structural**: Adapter, Facade, Composite, Proxy, Decorator, Bridge, Flyweight.

**Behavioral**: Strategy, Observer, Command, Template Method, Chain of Responsibility, State, Mediator, Iterator, Visitor, Interpreter.

#### Detection methodology

Pattern detection operates on **structural motifs** in the canonical model — typed subgraph patterns that correspond to the structural skeleton of a design pattern. The detector:

1. extracts typed subgraph candidates matching the motif schema,
2. scores each candidate on a set of structural evidence criteria,
3. returns a confidence-annotated match with an evidence summary,
4. distinguishes beneficial from accidental structural alignments using the surrounding context.

#### Pattern composition

The recommendation engine must reason over pattern compositions. Structural motif chains — such as Strategy-via-AbstractFactory, Decorator-over-Facade, or Command-in-ChainOfResponsibility — constitute different architectural commitments than their component patterns in isolation. Compositional motif paths must be expressible as recommendation targets and diagnosable as either beneficial compositions or over-engineered structures.

### 5.7 Architectural Code Smells

Architectural code smells are large-scale structural pathologies that differ from ordinary code smells in that they are properties of inter-component structure, not of individual methods or classes.

| Smell | Structural signature |
|---|---|
| God module / God service | Single node with anomalously high fan-in, heterogeneous collaborator set, and mixed responsibility signals |
| Shotgun surgery risk | Change to a single logical concern requires modifications distributed across many unrelated nodes |
| Inappropriate intimacy | Two components with bidirectional high-frequency call edges across a declared boundary |
| Feature envy | Component with higher call density into a foreign bounded context than its own |
| Redundant orchestration | Multiple nodes with structurally isomorphic orchestration logic over the same collaborator set |
| Policy–mechanism conflation | Nodes combining decision rules (policy) with execution machinery (mechanism) as evidenced by mixed edge neighborhoods |
| Parallel inheritance hierarchies | Two inheritance hierarchies with isomorphic structure forced to evolve in synchrony |
| Framework leakage | Infrastructure or framework types appearing in domain-layer node signatures or dependencies |
| Over-centralized registry | Single registry node with unbounded fan-in, creating a hidden global dependency |
| Hidden temporal coupling | Execution-order dependencies not expressed in the type or interface system, detectable from sequencing annotations |
| Uncontrolled shared mutable state | Mutation edges from multiple unrelated components into a shared mutable node without synchronization structure |
| Stringly-typed architecture | Systematic use of `symbolic_identifier` string literals across component boundaries in place of typed contracts |
| Composition root violation | Construction of volatile or infrastructure components outside designated assembly zones |

---

## 6. Diagnostic Classification

The strict separation between hard and soft diagnostics is not a presentational choice; it is the **epistemic contract** the system establishes with its users. Conflating the two categories destroys diagnostic trust.

### Hard diagnostics

Hard diagnostics are rule violations with unambiguous semantics, computable deterministically from the canonical model under the declared architectural policy. They are either present or absent. Examples:

- A cycle exists between nodes in distinct bounded contexts
- A direct import edge crosses from an infrastructure node to a domain node against the declared layer policy
- A string literal is used as an event name outside the event-definition module, violating the declared symbolic-constant policy
- A construction edge from an application-layer node reaches an infrastructure service outside any declared composition root zone
- A duplicate registry key is assigned by two distinct construction sites

### Soft diagnostics

Soft diagnostics are probabilistic suspicions — calibrated structural risk signals produced by heuristics operating on the canonical model. They carry a confidence score and an evidence summary. Examples:

- Probable god class: node with fan-in $> \theta_1$, collaborator heterogeneity $> \theta_2$, and LCOM $> \theta_3$
- Likely missing Strategy pattern: branching structure over an algorithm-selection variable without polymorphic dispatch
- Probable composition root violation: construction edge in a non-designated zone with confidence 0.7
- Possible service locator anti-pattern: dynamic lookup pattern in a node annotated as domain layer

The system must clearly label the diagnostic class in all output. A hard diagnostic represents a confirmed invariant violation. A soft diagnostic represents a structural risk signal requiring human verification.

---

## 7. Epistemic Limitations

The following limitations are intrinsic to the approach and must be explicitly acknowledged in system documentation.

**Semantic adequacy is not mechanically decidable.** The system can detect low cohesion, excessive coupling, missing abstraction boundaries, and poor extension design. It cannot, from structure alone, determine whether a decomposition correctly models the domain, whether an abstraction is premature relative to actual variability requirements, or whether a deliberately simple design was the correct architectural choice in context.

**Extraction is approximate.** For all languages with dynamic features, the canonical model is an approximation of the true runtime dependency structure. Confidence annotations mitigate but do not eliminate this limitation.

**Architectural adequacy is context-dependent.** Some rules are universal; many are project-specific. The system must support project-specific policy declarations precisely because no universal policy set is complete.

**Pattern presence is not architectural quality.** The detection of pattern structures does not indicate that those structures are beneficial in context. The recommendation engine's value lies in identifying missing patterns as solutions to diagnosed defects, not in cataloguing present ones.

The system is correctly characterized as:

- a detector of structural signals
- a checker of architectural invariants against declared policy
- a recommender of likely design improvements
- a support system for human architectural review

It is not a universal architectural judge.

---

## 8. Principal Technical Challenges

### 8.1 Semantic recovery under dynamic dispatch

Static imports are insufficient for recovering the true runtime interaction structure. Dependency injection containers, decorators, metaclass-based registration, event bus wiring, and reflection-based assembly require dedicated extraction strategies beyond import graph analysis. The extraction layer must model these patterns explicitly and attach appropriate confidence annotations rather than silently omitting the corresponding edges.

### 8.2 Edge type semantics

A call edge, an import edge, and a construction edge do not represent the same architectural coupling. The canonical model's edge type vocabulary must be sufficiently fine-grained to support rules that distinguish, for instance, "component A calls component B" from "component A constructs and owns component B." Collapsing these into a single edge type defeats the purpose of the intermediate representation.

### 8.3 Framework distortion

Framework-heavy codebases can produce severely misleading architectural impressions. Inversion-of-control containers, ORM frameworks, and plugin architectures obscure the actual interaction structure behind framework-managed wiring. The extraction layer requires framework-specific analysis modules to recover the latent architectural structure from framework-mediated dependencies.

### 8.4 False positives in pattern detection

Structural motifs resembling design patterns are extremely common in well-structured code without corresponding to intentional pattern use. The detection engine must condition confidence scores on contextual evidence — naming conventions, collaborator roles, usage patterns — rather than motif structure alone.

### 8.5 Cross-cutting concern misclassification

Cross-cutting concerns (logging, security, observability, transaction management) produce coupling signatures that structurally resemble violations. Without explicit cross-cutting annotations in the canonical model, the evaluation layer will produce systematic false positives on any well-structured enterprise codebase. The exemption mechanism described in §4.3 is a prerequisite for production-quality diagnostic precision.

### 8.6 Incremental analysis

A system requiring full re-extraction and re-evaluation on every code change is unsuitable for integration into a development workflow. An incremental analysis architecture must specify which subsets of the canonical model are invalidated by a given changeset, which rules require re-evaluation given those invalidations, and how to propagate partial updates through the evaluation layer. This determines whether the system operates as a CI pipeline tool or only as a periodic audit instrument.

---

## 9. Implementation Strategy

The implementation should proceed in five phases ordered by dependency and yield.

### Phase 1 — Core extraction and model foundation

Implement extraction front-ends for one or two target languages. Define and stabilize the canonical model schema. This phase is the highest-leverage investment: an unstable model schema will invalidate all subsequent evaluation work. Output: validated canonical model instances for representative codebases.

### Phase 2 — Dependency graph and layering evaluation

Implement the Datalog-class rule engine. Implement the highest-yield evaluation criteria: dependency cycles, layer violations, instability/abstractness metrics, composition root violations, and magic string detection. Implement the hard/soft diagnostic classification infrastructure. Output: a working evaluation pipeline with high-confidence hard diagnostics.

### Phase 3 — Policy declaration and conformance checking

Define and implement the declarative architectural specification format. Implement the intent alignment module. Implement the policy-conditioned rule evaluation and cross-cutting exemption mechanism. Output: conformance checking against declared architectures.

### Phase 4 — Heuristic smell and pattern detection

Implement the architectural code smell detectors. Implement the structural motif detector for the design pattern families. Implement the recommendation engine mapping defects to pattern hypotheses. Output: soft diagnostics with calibrated confidence scores.

### Phase 5 — Incremental analysis and additional language front-ends

Implement the change-impact model for incremental evaluation. Add extraction front-ends for additional target languages, validating language independence through shared rule and heuristic evaluation. Output: CI-integrable incremental analysis pipeline with multi-language support.

---

## 10. Summary

The Static Architecture Analysis System proposed here is grounded in a single foundational insight: architectural quality, while partly semantic and contextual, leaves observable structural traces that are amenable to formal extraction and rule-based evaluation, provided the analysis operates on an appropriate intermediate representation rather than on raw source code.

The system's validity rests on three architectural decisions: the strict three-layer pipeline separating language-specific extraction, language-agnostic canonical modeling, and formal evaluation; the use of a Datalog-class rule language for expressing architectural constraints over the canonical model; and the strict separation of hard diagnostic violations from soft probabilistic suspicions.

Its primary contributions are:

- a reusable canonical architectural model that enables language-independent evaluation,
- a formal taxonomy of operationalized architectural criteria grounded in graph theory, metric frameworks, and connascence theory,
- a pattern reasoning framework that treats patterns as refactoring hypotheses rather than taxonomic labels,
- a conformance checking mechanism anchored to a versioned declarative architectural specification.

Its explicitly acknowledged limitation is that structural analysis cannot substitute for domain-level architectural judgment. The system is designed as a high-precision support instrument for human architectural review, not as an autonomous arbiter of architectural quality.