# Audit Taxonomy

> [!INFO] See also
> Related: [component audit](../audits/audit-component.md) —
> [interaction audit](../audits/audit-interaction.md) —
> [model audit](../audits/audit-model.md).

> [!WARNING] Design-time artifact
> This document is a **design-time reference** for the audit taxonomy used by
> the vitruv audit prompts. It is not the runtime artifact; it specifies the
> methodology behind those prompts.

---

## Problem Statement

A single audit prompt, run repeatedly against the same codebase, converges on
a stable class of findings and fails to detect defects outside that class. The
failure is not a deficiency of the prompt's rigor — it is a structural
consequence of the fact that different classes of architectural defect require
different epistemic operations, different evidence ontologies, and different
methodological entry points.

The original component-oriented audit was a **structural falsification tool**.
It examines components, boundaries, types, and layers. It finds violations:
code that is present and defective. It systematically fails to detect three
other defect classes:

1. **Interaction defects** — coordination failures between well-designed
   components that manifest not at any single code location but in the gap
   between components.
2. **Model defects** — conceptual mismatches between the problem domain and the
   code's abstractions, where the code is internally consistent but models the
   wrong thing.
3. **Evolution defects** — latent fragility that is invisible under the current
   feature set but manifests as cascade failures under specific change
   scenarios.

These defect classes are not subcategories of structural defects. They are
orthogonal failure modes that require distinct audit methodologies.

---

## Theoretical Foundation

### Why three audits are irreducible

The three audit types correspond to three distinct epistemic operations, each
with its own unit of evidence:

| Audit | Question | Unit of evidence | Failure mode |
| --- | --- | --- | --- |
| Component | Is each part well-built? | A *location* in the code | Implementation defect |
| Interaction | Do parts work together correctly? | A *relationship* between two locations | Integration defect |
| Model | Are these the right parts? | A *mapping* between domain concept and code construct | Conceptual defect |

**Irreducibility argument.** A system of individually correct components can
have incorrect interactions (well-typed functions composed in the wrong order).
A system with correct interactions can model the wrong thing (a correct program
that solves the wrong problem). Therefore:

- Component correctness does not entail interaction correctness.
- Interaction correctness does not entail model correctness.
- Each audit type detects defects that are invisible to the other two.

The three types also have fundamentally different **evidence ontologies**:

- **Component audit**: evidence is a point — a specific code location exhibiting
  a defect. A single file path plus line range is sufficient to anchor a finding.
- **Interaction audit**: evidence is an edge — a pair of code locations and the
  protocol (or absence thereof) between them. A finding must cite both sides of
  an interaction and the coordination mechanism that is missing, implicit, or
  incorrect.
- **Model audit**: evidence is a mapping — a correspondence (or failed
  correspondence) between a domain concept and a code construct. A finding must
  cite both the domain concept (derived independently of the code) and the code
  construct (or its absence).

An audit prompt whose evidence standard demands "exact code location" will
produce component findings exclusively, because interaction and model findings
do not live at single locations. This is the structural reason why the former
single structural audit, despite its rigor, converged on local defects.

### Relationship to alternative taxonomies

**Local vs. global scope.** The binary split (component-level vs. system-level)
correctly identifies the scale gap but conflates interaction defects with model
defects. "Global" is not a single concern — how components interact (an
engineering question about the code) and whether the model is right for the
problem (a conceptual question about the domain) are distinct concerns that
require different methodologies. The former can be answered by reading the code
more carefully; the latter cannot be answered by reading the code at all.

**Structural / creational / behavioral (GoF).** This taxonomy classifies
solutions (design patterns), not defects (what the audit detects). An audit
organized by pattern type asks "are the right patterns used?" — which is
prescriptive and biases toward specific implementation idioms. None of the three
GoF categories covers domain model adequacy: a domain model that is the wrong
model for the problem does not violate any structural, creational, or behavioral
pattern.

**The principled organizing axis is the epistemic operation**, not the subject
matter or the solution space. All three audits examine the same codebase. What
differs is the kind of question asked, the kind of evidence required, and the
kind of reasoning applied.

---

## Audit Type 1 — Component Audit

### Purpose

Evaluate the structural quality of individual components: modules, classes,
functions, types, and the boundaries between them. The component audit asks:
**is each part well-built?**

### Posture

Adversarial. The architecture is presumed defective until the code disproves
it. Every negative judgment must be anchored in a concrete code location and an
explicit architectural principle.

### Methodology

The component audit operates in two passes:

**Top-down pass.** Examine system architecture, subsystem boundaries, dependency
graph shape, layering, public API shape, extension seams, configuration flow,
ownership of state and side effects, orchestration centers, lifecycle
boundaries.

**Bottom-up pass.** Examine module responsibilities, class cohesion, function
granularity, repeated imperative patterns, hidden dependency assumptions,
control-flow encoding of variation, contract ambiguity, invalid state exposure,
boundary violations between policy, mechanism, orchestration, interface
adaptation, persistence, and domain logic.

### Dimension model

The component audit evaluates against the nine dimensions defined in the
[design principles](../standards/design-principles.md):
redundancy, separation of concerns, modularity, flexibility, configurability,
extensibility, predictability, robustness, ease of use.

Each finding is assigned exactly one primary dimension and up to two secondary
dimensions.

### Evidence standard

Every finding must contain:

1. **Exact location**: file path and line range.
2. **Observed code pattern**: what is concretely wrong.
3. **Violated principle**: which architectural rule is broken.
4. **Root cause**: the structural deficiency generating the symptom.
5. **Blast radius**: which other modules or layers are affected.
6. **Future break scenario**: a plausible change request that would expose the
   defect.
7. **Remediation**: a named structural mechanism, not a vague directive.

### Scope and limits

The component audit is effective at detecting:

- wrong types, wrong layers, wrong boundaries
- redundancy at all granularities
- missing contracts and broken encapsulation
- fragile extension points and hardcoded policy
- type erasure and contract ambiguity

The component audit is blind to:

- coordination failures between well-structured components
- domain concepts that should exist but have no code counterpart
- emergent behavior arising from the composition of correct parts
- latent cascade failures under specific evolution scenarios

### Relationship to existing prompts

The current [component audit](../audits/audit-component.md) is the direct
descendant of the former architecture audit. Its methodology, dimension model,
evidence standard, and finding format are appropriate for this audit type.

---

## Audit Type 2 — Interaction Audit

### Purpose

Evaluate the correctness and adequacy of coordination between components. The
interaction audit asks: **do parts work together correctly?**

Where the component audit examines nodes in isolation, the interaction audit
examines edges — the protocols, data flows, shared computations, and sequencing
assumptions that govern how components interact at runtime.

### Posture

Adversarial, but directed at boundaries rather than components. The default
assumption is that every interaction between components relies on implicit
assumptions that are not structurally enforced. The audit seeks to make these
assumptions explicit and determine whether each one is managed, unmanaged, or
incorrectly managed.

### Methodology

The interaction audit operates in three passes:

**Pass 1 — Boundary enumeration.** Identify every interaction boundary in the
system. A boundary exists wherever:

- one component calls, imports, or depends on another
- one component produces data that another consumes
- two components operate on the same input or produce outputs that are
  aggregated
- two components must execute in a specific order
- two components share a concern (same configuration, same resource, same
  concept) without an explicit coordination mechanism

For each boundary, record:

- the two components involved
- the data that crosses the boundary and its form
- the direction of the dependency
- whether the interaction is explicit (protocol, interface, contract) or
  implicit (convention, assumption, coincidence)

**Pass 2 — Protocol analysis.** For each boundary, determine whether the
interaction protocol is adequate. Examine:

- **Result sharing**: when multiple consumers derive the same intermediate result
  from the same input, is the computation performed once and shared, or
  duplicated independently? The cost is not merely performance — independent
  derivation creates divergence risk if one consumer's derivation logic changes
  without the other's.
- **Scope coordination**: when multiple components operate on overlapping input
  domains (e.g., multiple rules scanning for the same patterns), is the
  partitioning of scope explicit, or do components define their own scope
  independently with no coordination mechanism? Independent scope definition
  produces overlap when scopes grow and gaps when scopes shrink.
- **Sequencing assumptions**: when components must execute in a specific order,
  is the ordering structurally enforced (pipeline stages, dependency injection,
  explicit orchestration), or implicitly assumed (documentation, convention,
  registration order)?
- **Consistency maintenance**: when the same fact is represented in multiple
  components (e.g., a default value in a schema and a fallback in a consumer),
  is there a single source of truth with derived consumers, or are multiple
  independent representations maintained manually?
- **Conflict management**: when components produce outputs that may conflict
  (e.g., overlapping text edits, contradictory diagnostics), is conflict
  detected pre-hoc (at production time) or post-hoc (after aggregation)?
  Post-hoc detection is structurally weaker: it can reject conflicts but cannot
  prevent them or compose compatible outputs.
- **Failure propagation**: when one component fails, how does the failure
  propagate to its consumers? Is the failure boundary explicit (result types,
  error channels), or does the failure manifest as incorrect data at a
  downstream component with no traceable cause?

**Pass 3 — Interaction pattern assessment.** Examine the system's interaction
patterns as a whole. Determine:

- whether the dominant interaction pattern (e.g., independent parallel
  evaluation, sequential pipeline, event-driven coordination) is appropriate
  for the problem's structure
- whether the interaction patterns scale: if the number of interacting
  components doubles, does the unmanaged interaction surface grow linearly or
  quadratically?
- whether the system has a coordination center (mediator, orchestrator,
  registry) where it needs one, or whether coordination is distributed with no
  explicit protocol

### Evidence standard

Every finding must contain:

1. **Boundary identification**: the two components involved, cited by file path
   and the specific interface (function, protocol, data type) at the boundary.
2. **Interaction description**: what data flows across the boundary, in what
   form, and with what assumptions.
3. **Protocol assessment**: the coordination mechanism that exists (or is
   absent).
4. **Violated interaction principle**: which of the six protocol dimensions
   (result sharing, scope coordination, sequencing, consistency, conflict
   management, failure propagation) is deficient.
5. **Consequence**: the concrete operational failure that results from the gap —
   not a hypothetical degradation but a specific scenario (e.g., "rules D302
   and D303 independently compute the same set difference; if the parameter
   extraction logic is updated in one but not the other, the two rules will
   produce inconsistent diagnostics for the same target").
6. **Remediation**: a named coordination mechanism — shared computation cache,
   explicit scope partition, mediator, result-sharing protocol, consistency
   constraint, pre-hoc conflict resolution — not a vague directive to
   "coordinate better."

### Dimension model

The interaction audit evaluates against six dimensions:

1. **Result sharing** — Are shared computations performed once or duplicated?
2. **Scope coordination** — Are overlapping concerns partitioned explicitly?
3. **Sequencing** — Are ordering dependencies structurally enforced?
4. **Consistency** — Is each fact represented once with derived consumers?
5. **Conflict management** — Are conflicts prevented, detected, or unmanaged?
6. **Failure propagation** — Are failure boundaries explicit and traceable?

Each finding is assigned exactly one primary dimension and up to two secondary
dimensions.

### Severity model

The severity model mirrors the component audit's four levels (critical, high,
medium, low) but the criteria are interaction-specific:

- **Critical**: an unmanaged interaction that produces incorrect results under
  normal operation (not merely under edge cases or evolution).
- **High**: an interaction gap that produces redundant computation, inconsistent
  outputs, or undetected conflicts under conditions that are already present in
  the codebase.
- **Medium**: an interaction gap that will produce failures when the number of
  interacting components grows or when a specific component is modified.
- **Low**: an implicit assumption that is currently correct but is not
  structurally enforced and will break under a plausible change.

### Scope and limits

The interaction audit is effective at detecting:

- duplicated cross-boundary computation
- overlapping scopes without coordination
- implicit sequencing dependencies
- inconsistent representations of shared facts
- post-hoc conflict detection where pre-hoc prevention is possible
- silent failure propagation

The interaction audit is blind to:

- whether the components themselves are well-designed (component audit)
- whether the interaction patterns, even when correct, are the right patterns
  for the problem (model audit)
- whether the domain model captures the right concepts (model audit)

---

## Audit Type 3 — Model Audit

### Purpose

Evaluate whether the code's abstractions correctly represent the problem domain.
The model audit asks: **are these the right parts?**

Where the component audit examines whether parts are well-built and the
interaction audit examines whether parts work together, the model audit examines
whether the parts correspond to the right concepts — whether the domain model
captures the structure of the problem or imposes a structure that the problem
does not have.

### Posture

The model audit is the only audit type that must begin **outside the code**. Its
adversarial stance is directed at the mapping between the problem domain and the
implementation, not at the implementation's internal quality.

The default assumption is that the code's abstractions are arbitrary choices that
may or may not correspond to the problem's structure. The audit seeks to
determine whether each abstraction has a domain justification and whether each
domain concept has a code counterpart.

### Methodology

The model audit operates in three phases. The ordering is strict: the auditor
must complete each phase before proceeding to the next.

**Phase 1 — Domain model derivation (code-independent).** Before reading any
source code, the auditor must derive the domain model from the problem statement
alone. This phase requires:

1. **Problem statement**: a concise description of what the system does, from
   the README, design document, or user documentation. If no such document
   exists, the auditor must construct one from the project's stated purpose.
2. **Concept enumeration**: list the core concepts in the problem domain. For
   each concept, determine:
   - its essential attributes
   - its relationships to other concepts
   - whether it is a thing (entity), a relationship, a process, a constraint,
     or a classification
3. **Relationship enumeration**: list the relationships between domain concepts.
   For each relationship, determine:
   - whether it is structural (A contains B), behavioral (A triggers B),
     derivational (A is computed from B and C), or classificatory (A is a kind
     of B)
   - whether it is one-to-one, one-to-many, or many-to-many
   - whether it is always present or conditional

The output of Phase 1 is a **domain concept map**: a structured enumeration of
concepts and relationships derived solely from the problem domain, with no
reference to the implementation.

> [!WARNING] Critical methodological constraint
> The domain concept map must be derived before reading the source code. Reading
> the code first contaminates the domain model with implementation choices: the
> auditor will unconsciously treat the code's abstractions as domain concepts,
> making it impossible to detect cases where the code models the wrong thing.
> This contamination is the primary reason that repeated structural audits
> never surface model defects — the auditor enters the code, adopts its
> vocabulary, and evaluates the code on its own terms.

**Phase 2 — Code model extraction.** Read the source code and extract the
implementation's implicit domain model:

1. **Abstraction enumeration**: list every type, class, module, protocol, and
   named data structure that represents a domain concept. For each:
   - identify the domain concept it claims to represent
   - identify its attributes and relationships
2. **Relationship enumeration**: list every relationship between code
   abstractions — containment, delegation, inheritance, protocol conformance,
   data flow, call dependency.
3. **Derived computation inventory**: identify every computation that derives
   a domain relationship at runtime rather than representing it as a first-class
   object. For each:
   - identify what domain relationship is being computed
   - identify where the computation occurs (which module, which function)
   - identify whether the same computation is performed in multiple locations

**Phase 3 — Mapping and gap analysis.** Align the domain concept map (Phase 1)
with the code model (Phase 2). For each entry in either map:

- **Concept with code counterpart**: the domain concept has a corresponding type
  or module in the code. Evaluate whether the code counterpart captures the
  concept's essential attributes and relationships or only a subset.
- **Concept without code counterpart** (domain gap): the domain concept exists
  in the problem but has no explicit representation in the code. Determine
  whether the concept is:
  - **Derived ad-hoc**: computed by one or more functions at runtime but not
    represented as a named type. This is a model defect if multiple consumers
    need the same derivation.
  - **Implicit**: assumed by the code but never computed or represented. This is
    a model defect if the implicit assumption is load-bearing (i.e., incorrect
    assumptions would produce incorrect results).
  - **Out of scope**: genuinely outside the system's responsibility. This is not
    a defect.
- **Code construct without domain counterpart** (phantom abstraction): the code
  contains a type, module, or named abstraction that does not correspond to any
  concept in the domain. Determine whether the construct is:
  - **Infrastructure**: a technical necessity (e.g., a configuration loader, a
    serializer) with no domain meaning. This is not a defect.
  - **Accidental complexity**: an abstraction introduced for implementation
    convenience that models nothing in the domain and complicates the code. This
    is a model defect.
- **Misaligned mapping**: a code construct that claims to represent a domain
  concept but captures the wrong attributes, the wrong granularity, or the wrong
  relationships. This is a model defect.

### Evidence standard

Every finding must contain:

1. **Domain concept**: the concept from the domain concept map, with its
   essential attributes and relationships as derived in Phase 1.
2. **Code construct** (or its absence): the type, module, or computation in the
   code that corresponds to the domain concept, cited by file path. If no
   construct exists, the finding must cite the locations where the concept is
   derived ad-hoc or implicitly assumed.
3. **Mapping assessment**: which of the four mapping categories (adequate,
   domain gap, phantom abstraction, misalignment) applies.
4. **Architectural cost**: the concrete consequence of the mapping defect —
   redundant computation, inability to support a use case, conceptual confusion,
   forced ad-hoc derivation.
5. **Remediation**: a named domain-modeling mechanism — introduce a domain
   object, introduce a relationship type, split a conflated concept, remove a
   phantom abstraction, realign an existing type's attributes. The remediation
   must be justified in terms of the domain, not in terms of code quality.

### Dimension model

The model audit evaluates against four dimensions:

1. **Concept coverage** — Does every load-bearing domain concept have an
   explicit code counterpart?
2. **Relationship coverage** — Does every load-bearing domain relationship have
   an explicit representation, or is it derived ad-hoc by consumers?
3. **Abstraction fidelity** — Do code constructs that claim to represent domain
   concepts capture the right attributes and relationships?
4. **Abstraction economy** — Does the code contain phantom abstractions that
   model nothing in the domain?

Each finding is assigned exactly one primary dimension and up to one secondary
dimension.

### Severity model

- **Critical**: a domain concept that is load-bearing (multiple components
  depend on it) and has no code counterpart, forcing every consumer to derive it
  independently. The derivations are not guaranteed to be consistent.
- **High**: a domain relationship that is derived ad-hoc in multiple locations,
  creating redundancy that is invisible to the component audit (because each
  derivation is internally correct).
- **Medium**: a misaligned mapping where the code construct captures a subset of
  a domain concept's attributes, limiting the system's ability to support use
  cases that require the full concept.
- **Low**: a phantom abstraction that increases cognitive load without modeling
  anything in the domain, or a domain concept that is out of scope but whose
  absence creates user-facing friction.

### Scope and limits

The model audit is effective at detecting:

- missing domain abstractions
- ad-hoc derivation of relationships that should be first-class
- phantom abstractions that model nothing
- misaligned mappings between concepts and code
- inability to support use cases that require domain concepts the code doesn't
  represent

The model audit is blind to:

- whether individual components are well-designed (component audit)
- whether components interact correctly (interaction audit)
- implementation-level defects that do not affect the domain model

The model audit requires domain expertise. An auditor who does not understand
the problem space cannot perform this audit — the domain concept map will be
either trivial (enumerating only what the code already represents) or incorrect
(projecting concepts from a different domain).

---

## Execution Protocol

### Ordering

The three audits should be executed in order:

1. **Component audit** first. Resolve local structural defects before examining
   interactions, because structural defects introduce noise into the interaction
   analysis (e.g., a misplaced package creates spurious cross-layer dependencies
   that obscure the real interaction patterns).
2. **Interaction audit** second. Resolve coordination gaps before examining the
   domain model, because interaction defects can be symptoms of model defects
   (e.g., redundant cross-referencing across rules may be a symptom of a missing
   domain object). The interaction audit surfaces these symptoms; the model audit
   determines their root cause.
3. **Model audit** third. With structural and interaction defects resolved, the
   model audit operates on a clean substrate and can focus exclusively on the
   mapping between the problem domain and the code's abstractions.

### Finding budget

Each audit type has an independent finding budget of at most **10 findings**.
Prefer fewer findings of greater depth. Do not create findings merely to
populate dimensions.

### Cross-audit references

Findings from a later audit may reference findings from an earlier audit to
establish a symptom-root-cause chain. For example:

- An interaction finding (redundant computation across rules) may be referenced
  by a model finding (missing domain object that would eliminate the redundancy)
  to show that the interaction defect is a symptom of a model defect.
- A component finding (stringly-typed field) may be referenced by an interaction
  finding (fragile protocol between producer and consumer) to show that the type
  defect creates an interaction gap.

Cross-audit references must be explicit: cite the earlier finding by its title
and audit type.

### Independence of findings

A defect must not be reported in multiple audits. If a defect is visible from
multiple audit perspectives, it belongs in the audit whose evidence type most
naturally captures it:

- A defect visible at a single code location → component audit.
- A defect visible as a relationship between two locations → interaction audit.
- A defect visible as a mismatch between a domain concept and the code → model
  audit.

If the assignment is ambiguous, prefer the audit type whose remediation is more
fundamental. A missing domain object that causes both a model defect and an
interaction defect (redundant derivation) belongs in the model audit, because
introducing the domain object resolves both defects simultaneously.

---

## Output Format

Each audit type uses the same top-level report structure:

### 1. Verdict

Classify the codebase on the audit's specific axis:

- **Component audit**: structurally sound / serviceable but fragile /
  significantly flawed / fundamentally unsound.
- **Interaction audit**: well-coordinated / partially coordinated /
  under-coordinated / uncoordinated.
- **Model audit**: well-modeled / partially modeled / under-modeled /
  mismodeled.

State the main evidence for the classification in 3 to 6 sentences.

### 2. Executive findings

Tabular summary of the most consequential findings, with severity, primary
dimension, and structural impact.

### 3. Detailed findings

Findings ordered by severity, then by structural leverage, using the evidence
standard and finding template specific to each audit type.
