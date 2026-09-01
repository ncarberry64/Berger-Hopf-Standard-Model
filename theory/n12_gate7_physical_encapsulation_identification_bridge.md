# N12 Gate-7 physical-encapsulation identification bridge

Status:
`BRIDGE_INTERFACE_SPECIFIED__PHYSICAL_IDENTIFICATION_OPEN_MISSING_ACTION_OWNED_DOMAIN_AND_FULL_FIELD_ATTACHMENT`.

This bridge implements the outcome of the Norman/BHSM school reconstruction.
It does not strengthen the branch-24 first-stop proof, change AE2, add an
enclosure term, choose a junction condition, or promote a particle.

## 1. Source and target

The certified source is the mathematical chain

```text
same-AE2 parent history
  -> canonical earliest branch-24 stop
  -> regular event-to-complete-child relation
  -> positive-duration retained child history.
```

The existing BHSM particle-state registry is also an upstream source, not a
new derivation target.  It includes frozen family/mode modules,
representations, sector and family projectors, current objects, topological
labels, and the forward-history particle class.  A BHSM family or mode state
may manifest as a Standard Model particle through the already-defined
manifestation/readout architecture.

The desired target is stronger only in the localization direction:

```text
action-identified physical local enclosure
  -> enclosure geometry and existing particle-state data inherited by the child
  -> existing Standard Model manifestation class.
```

The bridge is denoted schematically by

```text
I_phys : (P_BHSM, H_parent, E_stop, R_EC, S_AE2)
      -> (route, D_enc, Sigma_enc, C_child, M_SM(P_BHSM)).
```

Here `P_BHSM` is imported by provenance and `M_SM` is the existing
manifestation map.  This owner derives neither object.  The missing map is
the structure-preserving attachment through the current selected-stop and
event-child dynamics into the enclosure.

## 2. Three admissible enclosure routes

The physical identification must not assume that a canonical stop is the end
of spacetime.  The unchanged action must select one route, or derive an
equivalence class among them:

1. `LOCAL_SAME_SPACETIME_ENCLOSURE`: a localized region forms inside a
   continuing spacetime phase;
2. `CORE_BOUNDARY_OR_COLLAR_ENCLOSURE`: a genuine geometric boundary/collar
   carries the enclosure and matching data;
3. `SPACETIME_EDGE_TRANSITION`: the spacetime variables cease to be the
   operative environmental description.

The third is strictly stronger.  Current evidence proves none of the route
selectors and explicitly forbids
`CANONICAL_STOP_EVENT = SPACETIME_EDGE` without a theorem.

## 3. Enclosure carrier

Historical BHSM geometry already declares the candidate data.  A physical
carrier must place them on one action-owned domain.

Intrinsic data include

```text
(D_enc, h_enc, A_enc, L_enc, T_enc),
```

where `D_enc` is the local domain, `h_enc` its intrinsic metric, `A_enc` its
area/measure data, `L_enc` its relational or cross-distance data, and `T_enc`
its topology.

External data include

```text
(X, n, K, g_ambient, A_attach, Delta_rel),
```

with embedding, normal bundle, extrinsic curvature, ambient metric,
attachment morphism, and relational interval.  The dynamical carrier must
also include lapse/shift, canonical momenta, boundary traces, and the
full-field restriction.

The v11.2 identity

```text
delta h_enc_ab = i_X^*(delta g)_ab
               + 2 nabla_(a xi_b)
               + 2 K^I_ab xi_I
```

shows why a fixed intrinsic enclosure is not automatic.  The stored action
contains no constraint or stability term that enforces it.

## 4. Identification conjunction

Generic physical encapsulation requires all of `PEI_01` through `PEI_10`:

| ID | Obligation | Current status |
|---|---|---|
| `PEI_01` | same-action parent reaches canonical stop | closed |
| `PEI_02` | regular nonempty event-child relation | closed |
| `PEI_03` | action selects enclosure route | open |
| `PEI_04` | action-owned enclosure carrier/domain | open |
| `PEI_05` | induced geometry, lapse/shift, flux, trace, and junction matching on one domain | open |
| `PEI_06` | full-field restriction or invariant zero-field subdomain | open |
| `PEI_07` | complete parent/event/child Noether-Hamiltonian balance | open |
| `PEI_08` | nontrivial nonlinear localized completion | open |
| `PEI_09` | enclosure and full-field inheritance by child | open |
| `PEI_10` | positive-duration child, kept separate from stability | closed |

`PEI_11` additionally requires that the provenance-frozen BHSM family/mode,
representation, projector, current, and topological state be attached to the
parent and transported through the event-child enclosure map into its
existing Standard Model manifestation class.  It does **not** rederive the
particle spectrum, family count, representation ledger, projectors, or
currents.

This conjunction is intentionally stricter than `lambda_24=0` and weaker than
eternal stability.  It is the minimum bridge between those two errors.

### 4.1 Four-kernel reduction and retained subclosures

The eleven rows reduce to four unresolved kernels without deleting their
individual acceptance tests:

| Kernel | PEI coverage | Current result |
|---|---|---|
| A: localization carrier | `PEI_03`, `PEI_04`, much of `PEI_08` | no qualifying carrier in unchanged AE2 |
| B: physical interface variation | `PEI_05`--`PEI_07` | fermionic reset trace reusable; physical junction and full-field flux open |
| C: child inheritance | `PEI_09` | open |
| D: C2 family/mode instantiation | `PEI_11` | algebraic intertwiner reusable; actual C2 slot and enclosure inheritance open |

Thus `PEI_05a`, fermionic event-child reset trace matching, is available,
while `PEI_05b` geometric junction matching and `PEI_05c` dependency-closed
full-field flux matching remain open.  Likewise, the tensor-product identity

```text
[U_R tensor I_F, I_Spin tensor Pi_r,n] = 0
```

closes the algebraic `PEI_11a` intertwiner.  It does not instantiate the
family/mode slot on the actual C2 parent (`PEI_11b`) or prove that a physical
child enclosure inherits it (`PEI_11c`).

## 5. Current no-go operands

The missing rows are not placeholders invented in this sprint.  They are
preserved results already on disk:

- the collar formula has no action-selected embedding or physical thickness;
- exact metric matching is conditional on provisional Boundary Axiom B1;
- the current action selects no unique self-adjoint junction domain;
- the retained N12 adapter has no gauge/ghost, fermion, or scalar/HS slots;
- event and child energy rows close, but the complete paired
  parent/event/child Noether-Hamiltonian balance remains open;
- the stop theorem supplies a Hessian zero and singular normal form, not a
  local nonlinear enclosure construction;
- the C2 enclosure signature is invariant along the certified continuation,
  but its physical carrier and inheritance map are not derived.

These facts force the bridge to fail closed at the current evidence boundary.

### 5.1 Unchanged-AE2 carrier kill screen

A localization carrier must be an action-owned object of the type

```text
D_A : z -> (D_enc, Sigma_enc, X, n, K, ...)
```

or a covariant scalar realization

```text
Sigma_enc = {x : chi_A[Phi](x)=0},
d chi_A restricted to Sigma_enc != 0,
```

with enough regularity and action variation to determine its interface data.
The selected eigenvalue `lambda_24 : C -> R` has a different type: it detects
an event time in reduced state space.  Its zero cannot be relabelled as the
embedded spacetime surface `Sigma_enc`.

The executable audit tests six stored candidate classes: `lambda_24`, the AE2
reset locus, fixed `B1`/collar vocabulary, the unassigned support character,
the 98-variable retained oracle, and the spacetime-edge route.  None supplies
all of action ownership, local-domain selection, embedded-interface data,
regularity/domain control, and owned interface variation.  This is a bounded
no-carrier result for unchanged AE2, not a theorem against a future action
extension.

For `PEI_06`, transport is restricted to the action dependency closure

```text
Dep_A(B_i) = TC(
  fields defining B_i,
  fields required by M_SM(B_i),
  fields entering delta S on Sigma_enc
).
```

The enclosure must carry this closure; it need not carry every field
everywhere.

## 6. Frozen upstream particle assets

The bridge imports, with hashes and original claim boundaries:

- the v15.53 global `Spin x G_SM` bundle, representations, hypercharge, and
  event-gluing data;
- the v8.2 frozen three-slot family modules and sector/mode projectors;
- the historical harmonic/mode representation results at their stored claim
  strength;
- the family-count and raw/Yukawa-labelled mode ledgers;
- the parent-action charged-current object and variation provenance;
- the electromagnetic surviving generator;
- the topological configuration/spectrum and conditional Hopf phase closure;
- the corrected complete-forward-history particle class.

Their import policy is:

```text
reuse every valid result at its stored claim strength;
do not rederive, retune, reorder, or replace the particle/family/mode spectrum.
```

The missing transport must intertwine the imported sector and family
projectors, bundle representation, current incidence, and topological labels
with the child enclosure and the existing SM manifestation map.

## 7. Enclosure signature

Once derived, the child enclosure signature must contain

```text
Sigma_enc = (
  AE2 action/domain version,
  history component and orientation,
  intrinsic domain and topology,
  embedding/normal/K/collar data,
  reset-glued Spin x G_SM bundle and field traces,
  boundary-incidence and junction-domain class,
  selected-eigenline class,
  constraint and complete Noether level set,
  admissible child-domain component
).
```

It must not contain proof-box indices, mesh cutoffs, floating-point failures,
or the branch-24 value by itself.

## 8. Forbidden substitutions

The executable interface rejects:

```text
lambda_24 = 0  <=>  theta = 2*pi,
canonical stop <=> spacetime edge,
positive duration <=> stability.
```

It also records that a reset state is not automatically a new spacetime
domain and that a proof cutoff is not a physical boundary.

## 9. Closure and next object

The bridge may report `PHYSICAL_ENCAPSULATION_IDENTIFIED` only when every
required row is true on the same action and compatible domain.  A
particle-state enclosure/SM manifestation claim requires `PEI_11` as well,
with the upstream registry unchanged.

Even then, this bridge would not by itself close the existing Gate-7
force/KKT, saddle, pair-plus-contact Hessian, Ward/BRST trace, or physical
scalar-readout nodes.

The unchanged-AE2 audit has now exhausted the stored carrier candidates.  The
exact next dependency is therefore an owner-authorized action-version decision,
not another refinement of the first-stop theorem:

```text
OWNER_AUTHORIZED_ACTION_VERSION_DECISION_SELECTING_A_COVARIANT_LOCALIZATION_OR_DOMAIN_CARRIER;
THEN DERIVE ITS INTERFACE VARIATION,
DEPENDENCY-CLOSED FIELD TRANSPORT,
CHILD INHERITANCE,
AND C2 FAMILY/MODE INSTANTIATION.
```

No action term, coefficient, selector, or physical parameter is introduced by
this audit.  No first-stop refinement is part of that owner.

`FULL_BHSM_COMPLETE = FALSE`.
