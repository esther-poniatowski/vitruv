# Interaction Principles

Architectural rules governing the coordination between components. Authoritative
source for interaction standards enforced by the
[interaction audit prompt](../audits/audit-interaction.md).

Where the [design principles](design-principles.md) govern the quality of
individual components, these principles govern the quality of the protocols
between them.

---

## 1. Result Sharing

When multiple consumers derive the same intermediate result from the same input,
the computation must be performed once and shared, not duplicated independently.

### 1.1 Shared Computation Rule

If two or more components perform the same transformation on the same data —
even through different code paths — the transformation must be factored into a
shared computation whose result is consumed by both.

### 1.2 Cost of Independent Derivation

Independent derivation is not merely a performance concern. It creates
**divergence risk**: if one consumer's derivation logic is updated without
updating the other's, the two consumers silently produce inconsistent results
from the same input. The inconsistency is invisible to any audit that examines
each consumer in isolation.

### 1.3 Acceptable Independence

Independent computation is acceptable when:

- the computations are genuinely different (different inputs, different
  transformations, or different output granularity)
- sharing would require coupling components that are otherwise independent
  across a layer boundary
- the computation is trivially cheap and the sharing mechanism would introduce
  complexity disproportionate to the savings

### 1.4 Violation Indicators

- two modules that import the same helper and call it independently on the same
  data at the same pipeline stage
- two evaluators that both extract the same subset from a shared input before
  performing their distinct logic
- a helper module that exists solely because multiple consumers need the same
  derivation — the helper eliminates code duplication but not computation
  duplication

---

## 2. Scope Coordination

When multiple components operate on overlapping input domains, the partitioning
of scope must be explicit and coordinated, not independently defined.

### 2.1 Explicit Scope Rule

Every component that selects a subset of inputs to operate on must declare its
scope. When two components' scopes overlap, the overlap must be explicitly
acknowledged and managed — either by making the scopes disjoint or by
introducing a deduplication mechanism for their outputs.

### 2.2 Independent Scope Definition

Components that independently define their own scope without a coordination
mechanism produce:

- **overlap** when scopes grow (two components detect the same defect and
  produce duplicate outputs)
- **gaps** when scopes shrink (a defect falls between two components because
  each assumes the other covers it)

### 2.3 Coordination Mechanisms

Valid scope coordination mechanisms:

- disjoint scope declaration (component A covers set X; component B covers
  set Y; X and Y are disjoint by construction)
- hierarchical scope (component A covers the broad set; component B covers a
  specific subset with a more precise response; the broader component explicitly
  excludes the subset)
- output deduplication (components may overlap in scope, but a downstream
  aggregator deduplicates their outputs by a well-defined key)

### 2.4 Violation Indicators

- two components whose input filters overlap without an explicit coordination
  mechanism
- a downstream aggregator that receives duplicate outputs and either passes
  them through (user-visible duplication) or silently deduplicates without a
  declared policy
- a component whose scope is defined as a hardcoded set that was constructed
  independently of the other components' scope definitions

---

## 3. Sequencing

When components must execute in a specific order, the ordering must be
structurally enforced, not implicitly assumed.

### 3.1 Structural Enforcement Rule

Every ordering dependency between components must be expressed through a
structural mechanism: pipeline stages, dependency injection, explicit
orchestration, or type-level constraints (a component's input type is another
component's output type).

### 3.2 Implicit Sequencing

Implicit ordering — where correctness depends on components being invoked in a
particular order but nothing in the code enforces that order — is a latent
defect. It manifests when:

- a component is added to a registration list and its position affects the
  result
- a refactoring reorders independently registered components
- a parallel execution mode is introduced that violates the assumed serial order

### 3.3 Acceptable Implicit Ordering

Implicit ordering is acceptable when:

- the components are genuinely order-independent (commutative)
- the ordering is enforced by a pipeline architecture that is documented and
  structural (not merely conventional)

### 3.4 Violation Indicators

- a flat list of registered components whose evaluation order affects the
  result
- a pipeline stage that silently assumes a previous stage has run
- components that produce correct results only when invoked in a specific
  sequence, without the sequence being declared or enforced

---

## 4. Consistency

When the same fact is represented in multiple locations, there must be a single
source of truth with derived consumers.

### 4.1 Single Source of Truth Rule

Every fact (a default value, a classification, a scope definition, a format
string) must have exactly one authoritative declaration. All other locations
that need the fact must derive it from the source, not redeclare it
independently.

### 4.2 Cost of Multiple Declarations

Independent declarations of the same fact create a maintenance coupling that is
invisible to dependency analysis. The two declarations are not linked by any
import, protocol, or type — they are linked only by the developer's knowledge
that they must be kept in sync. This is the most fragile form of coupling.

### 4.3 Acceptable Redundancy

Redundant declarations are acceptable when:

- the redundancy is enforced by a validation mechanism that fails if the
  declarations diverge
- the declarations are in different deployment contexts where the source is
  not accessible (e.g., a client and a server that share a constant)

### 4.4 Violation Indicators

- a default value declared in a schema definition and re-declared as a fallback
  in a consumer
- a classification (e.g., a set of valid values) defined in one module and
  independently hardcoded in another
- a format string or pattern declared in both a producer and a consumer

---

## 5. Conflict Management

When components produce outputs that may conflict, conflicts must be prevented
or detected at the earliest possible point.

### 5.1 Pre-Hoc Prevention Rule

Where possible, prevent conflicts by construction: ensure that components cannot
produce conflicting outputs through scope partitioning, type constraints, or
composition rules.

### 5.2 Detection Hierarchy

When prevention is not possible, conflicts must be detected at the earliest
point:

1. **Production-time detection** (strongest): the producing component detects
   the conflict before emitting the output. Requires the producer to have
   visibility into what other producers have already emitted.
2. **Aggregation-time detection** (adequate): the downstream aggregator detects
   the conflict when combining outputs. Requires a well-defined conflict
   detection criterion and a resolution policy.
3. **Consumption-time detection** (weakest): the consumer discovers the conflict
   when it attempts to use inconsistent data. This is a defect, not a detection
   mechanism.
4. **No detection** (failure): conflicts pass through silently.

### 5.3 Resolution Policies

When conflicts are detected, the resolution policy must be explicit:

- reject the later / lower-priority output
- merge compatible outputs and reject incompatible ones
- escalate the conflict to the user or an orchestrator
- never silently discard or silently merge without a declared policy

### 5.4 Violation Indicators

- components that produce overlapping outputs with no conflict detection at
  any level
- a post-hoc conflict detector that rejects conflicts but cannot compose
  compatible outputs
- a consumer that receives potentially conflicting inputs and proceeds with
  the first one without checking for alternatives

---

## 6. Failure Propagation

When a component fails, the failure must propagate through explicit channels
with traceable cause information.

### 6.1 Explicit Failure Boundary Rule

Every interaction boundary must declare how failures propagate across it: result
types, error channels, fallback values, or operational issue records.

### 6.2 Silent Failure Propagation

A failure that manifests as incorrect data at a downstream component — rather
than as an explicit error signal — is a boundary defect. The downstream
component cannot distinguish a legitimate result from a failure artifact.

### 6.3 Failure Containment

Failures must be contained at the narrowest possible scope:

- a failure in one evaluation must not prevent other independent evaluations
  from completing
- a failure must be recorded with sufficient context for a human to diagnose
  it without re-running the pipeline
- a failure must not be silently swallowed, even when the system can continue
  without the failed component's output

### 6.4 Violation Indicators

- a try/except block that catches a broad exception and substitutes a default
  value without recording the failure
- a component that receives `None` from an upstream component and cannot
  distinguish "no result" from "failed to compute"
- an operational issue that is logged to stderr but not included in the
  structured output
