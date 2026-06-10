# Unreleased / Development: v2.15 Projector Graph-Domain Stability

Branch: `bhsm-v2.15-projector-graph-domain-stability`

The v2.15 branch closes `PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP` for the formal
sector-labeled complement projector.  It proves the graph-domain inclusion
`P_perp D(A0+V) subset D(A0+V)` inside the current complete BHSM operator
package by combining the complete-operator/action-uniqueness results, the
relative-bound package with `a < 1`, and v2.14 projector commutator control.

Final result:

- projector graph-domain stability: `PROJECTOR_GRAPH_DOMAIN_STABILITY_CLOSED`
- graph-domain theorem status: `PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN`
- interacting domain: `D(A0+V)=D(A0)`
- complete-operator identification: `COMPLETE_OPERATOR_IDENTIFICATION_PROVEN`
- projector commutator control: `PROJECTOR_COMMUTATOR_CONTROL_PROVEN`
- full H_T theorem: not proven
- next blocker: `HT_LOWER_BOUND_TRANSFER_GAP`
- recommended next branch: `bhsm-v2.16-ht-lower-bound-transfer`
- final paper allowed: `False`

Frozen predictions, canonical constants, frozen modes, tolerances, outputs, and
virtual dressing are unchanged.

# Unreleased / Development: v2.14 Projector Commutator Control

Branch: `bhsm-v2.14-projector-commutator-control`

The v2.14 branch closes `PROJECTOR_COMMUTATOR_CONTROL_GAP` for the formal
sector-labeled complement projector and the complete BHSM operator package.
The formal kernel remains `(0,18,36)` with one protected lepton, up, and down
state; the old coordinate-first kernel `(0,1,2)` is not used.

Final result:

- projector commutator control: `PROJECTOR_COMMUTATOR_CONTROL_CLOSED`
- commutator theorem status: `PROJECTOR_COMMUTATOR_CONTROL_PROVEN`
- total relative commutator bound: `a_C = 0.015621013485509948`, `b_C = 0.0`
- complete-operator identification: `COMPLETE_OPERATOR_IDENTIFICATION_PROVEN`
- action uniqueness: `COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED`
- full H_T theorem: not proven
- next blocker: `PROJECTOR_GRAPH_DOMAIN_STABILITY_GAP`
- recommended next branch: `bhsm-v2.15-projector-graph-domain-stability`
- final paper allowed: `False`

No empirical masses, CKM values, PMNS values, residual data, or prediction fits
are used in the commutator-control proof. Frozen predictions, canonical
constants, frozen modes, tolerances, outputs, and virtual dressing are
unchanged.

# Unreleased / Development: v2.13 Complete Operator Action Uniqueness

Branch: `bhsm-v2.13-complete-operator-action-uniqueness`

The v2.13 branch closes `COMPLETE_OPERATOR_ACTION_UNIQUENESS_GAP` under
the explicit BHSM action/axiom package. The complete operator package is
uniquely forced up to zero, represented, screened/lifted,
positive-semidefinite/relatively-bounded-safe, or axiom-forbidden terms.

Final result:

- complete-operator action uniqueness: `COMPLETE_OPERATOR_ACTION_UNIQUENESS_CLOSED`
- operator axiom uniqueness: `COMPLETE_OPERATOR_ACTION_UNIQUENESS_PROVEN`
- complete-operator identification: `COMPLETE_OPERATOR_IDENTIFICATION_PROVEN`
- full H_T theorem: not proven
- next blocker: `PROJECTOR_COMMUTATOR_CONTROL_GAP`
- recommended next branch: `bhsm-v2.14-projector-commutator-control`
- final paper allowed: `False`

No empirical masses, CKM values, PMNS values, residual data, or prediction fits
are used to select the operator. Frozen predictions, canonical constants,
frozen modes, tolerances, outputs, and virtual dressing are unchanged.

# Unreleased / Development: v2.12 Bundle Curvature Formula Closure

Branch: `bhsm-v2.12-bundle-curvature-formula-closure`

The v2.12 branch closes the downstream
`BUNDLE_CURVATURE_FORMULA_CONDITIONAL_GAP` by applying the v2.11
`BUNDLE_CONNECTION_SEPARATION_WITH_TOPOGRAPHIC_REPRESENTATION` axiom to the
remaining mixed Hopf/base/boundary/coframe curvature channel.

Final result:

- bundle curvature formula decision: `BUNDLE_CURVATURE_FORMULA_CLOSED`
- term-map status: `BUNDLE_CURVATURE_TERM_MAP_CLOSED`
- `R_bundle` classification: `REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR`
- independent `R_bundle` contribution: none
- lower-bound contribution added by the remainder: `0.0`
- complete-operator status: `COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL_STRONG`
- next blocker: `COMPLETE_OPERATOR_ACTION_UNIQUENESS_GAP`
- final paper allowed: `False`

This closure does not prove the full H_T theorem or the full BHSM theorem
package. It only closes the bundle-curvature formula gap under the
topographic-representation rule. Frozen predictions, canonical constants,
frozen modes, tolerances, outputs, and virtual dressing are unchanged.

# Unreleased / Development: v2.11 Mixed Connection Coefficient Rule

Branch: `bhsm-v2.11-mixed-connection-coefficient-rule`

The v2.11 branch formalizes
`BUNDLE_CONNECTION_SEPARATION_WITH_TOPOGRAPHIC_REPRESENTATION`: local Standard
Model bundle dynamics remain locally unchanged, and mixed
Hopf/base/boundary/coframe effects are represented through existing
boundary/profile/topographic/screening/lift sectors rather than a new free
bundle-curvature coefficient.

Final result:

- mixed coefficient rule decision: `MIXED_COEFFICIENT_RULE_CLOSED`
- mixed coefficient rule status: `MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR`
- mixed connection classification: `MIXED_CONNECTION_REPRESENTED_BY_TOPOGRAPHIC_SECTOR`
- independent free mixed coefficient: forbidden
- `R_bundle` contribution from the mixed coefficient rule: none
- downstream blocker: `BUNDLE_CURVATURE_FORMULA_CONDITIONAL_GAP`
- final paper allowed: `False`

No coefficient is chosen by tuning or residual improvement. Frozen predictions,
canonical constants, frozen modes, tolerances, outputs, and virtual dressing are
unchanged.

# Unreleased / Development: v2.10 Mixed Connection Coefficients

Branch: `bhsm-v2.10-mixed-connection-coefficients`

The v2.10 branch identifies the mixed Hopf/base/boundary/coframe connection
coefficient slots that feed the open Lichnerowicz bundle-curvature remainder.
It audits the resulting mixed curvature, Clifford contraction, and relative
bound requirements.

Final result:

- mixed connection decision: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- mixed connection classification: `MIXED_CONNECTION_OPEN`
- coefficient status: `MIXED_COEFFICIENT_OPEN`
- curvature status: `MIXED_CURVATURE_OPEN`
- Clifford status: `CLIFFORD_CONTRACTION_OPEN`
- exact missing rule: `MIXED_HOPF_BASE_BOUNDARY_COFRAME_COEFFICIENT_RULE`
- exact remaining gap: `MIXED_CONNECTION_COEFFICIENT_RULE_GAP`
- recommended next branch: `bhsm-v2.11-mixed-connection-coefficient-rule`
- final paper allowed: `False`

No coefficient is chosen by tuning or residual improvement. Frozen predictions,
canonical constants, frozen modes, tolerances, outputs, and virtual dressing are
unchanged.

# Unreleased / Development: v2.9 Complete Bundle Connection Curvature

Branch: `bhsm-v2.9-complete-bundle-connection-curvature`

The v2.9 branch inventories the complete BHSM bundle connection, maps each
curvature contribution to the existing operator package or to `R_bundle`, and
audits the Lichnerowicz curvature action.

Final result:

- connection-curvature decision: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- connection status: `COMPLETE_BUNDLE_CONNECTION_OPEN`
- curvature formula status: `CURVATURE_FORMULA_OPEN`
- `R_bundle` classification: `REMAINDER_OPEN`
- exact missing component: `mixed_hopf_base_boundary_coframe_connection`
- exact remaining gap: `MIXED_HOPF_BASE_BOUNDARY_COFRAME_CONNECTION_GAP`
- recommended next branch: `bhsm-v2.10-mixed-connection-coefficients`
- final paper allowed: `False`

Every listed connection component and curvature contribution is classified, but
the mixed Hopf/base/boundary/coframe connection coefficients and Clifford
curvature contraction are still missing. Frozen predictions, canonical
constants, frozen modes, tolerances, outputs, and virtual dressing are
unchanged.

# Unreleased / Development: v2.8 Curvature Remainder Formula and Bound

Branch: `bhsm-v2.8-curvature-remainder-formula-bound`

The v2.8 branch formalizes the Lichnerowicz-type expression for the remaining
bundle-curvature term and audits its basis, sector, formal-kernel, complement,
relative-bound, and lower-bound-transfer implications.

Final result:

- formula/bound decision: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- formula status: `REMAINDER_FORMULA_OPEN`
- basis-action status: `REMAINDER_BASIS_ACTION_OPEN`
- kernel/complement status: `REMAINDER_KERNEL_COMPLEMENT_OPEN`
- final classification: `REMAINDER_OPEN`
- exact remaining gap: `COMPLETE_BHSM_BUNDLE_CONNECTION_CURVATURE_FORMULA_GAP`
- recommended next branch: `bhsm-v2.9-complete-bundle-connection-curvature`
- final paper allowed: `False`

The Lichnerowicz identity is now explicit, but the complete BHSM bundle
connection curvature formula is still missing. No zero, represented, PSD,
screened/lifted, or relative-bound-safe classification is adopted without that
formula/action proof. Frozen predictions, canonical constants, frozen modes,
tolerances, outputs, and virtual dressing are unchanged.

# Unreleased / Development: v2.7 Bundle Curvature Remainder

Branch: `bhsm-v2.7-bundle-curvature-remainder`

The v2.7 branch audits the single missing Lichnerowicz/bundle-curvature
remainder that blocked v2.6 complete-operator identification. It inventories
the geometric origin, bundle-connection sources, possible dispositions, and
lower-bound requirements for `lichnerowicz_bundle_curvature_remainder`.

Final result:

- curvature decision: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- remainder classification: `REMAINDER_OPEN`
- blocking term: `lichnerowicz_bundle_curvature_remainder`
- exact remaining gap: `BUNDLE_CURVATURE_REMAINDER_FORMULA_AND_BOUND_GAP`
- recommended next branch: `bhsm-v2.8-curvature-remainder-formula-bound`
- final paper allowed: `False`

The audit does not claim zero, representation by `A0+V`, PSD/profile control,
screening/lifting, or relative-bound safety without the missing formula/action
proof. Frozen predictions, canonical constants, frozen modes, tolerances,
outputs, and virtual dressing are unchanged.

# Unreleased / Development: v2.6 Complete Operator Identification

Branch: `bhsm-v2.6-complete-operator-identification`

The v2.6 branch audits the complete Berger-Hopf twisted Dirac/bundle operator
identification needed before downstream `H_T` theorem closure can honestly
advance. The audit inventories the operator terms, derives the currently
represented `A0+V` decomposition, checks for hidden missing terms, and makes a
strict theorem decision.

Final result:

- operator-identification status: `COMPLETE_OPERATOR_IDENTIFICATION_BLOCKED_BY_MISSING_TERM`
- v2.6 decision: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- single missing term: `lichnerowicz_bundle_curvature_remainder`
- target theorem gap: `BUNDLE_CONNECTION_CURVATURE_CLOSURE_GAP`
- recommended next branch: `bhsm-v2.7-bundle-curvature-remainder`
- final paper allowed: `False`

No theorem is marked proven from conditional assumptions. Frozen predictions,
canonical constants, frozen modes, tolerances, outputs, and virtual dressing are
unchanged.

# Unreleased / Development: v2.2 Formal Complement Stability

Branch: `bhsm-v2.2-formal-complement-stability`

The v2.2 focused branch closes the formal projector algebra and finite-projector convergence bridge for the corrected sector-labeled kernel. The lower bound now applies to `H_perp` conditionally under projector/domain scaffold assumptions.

Status remains conservative:

- formal kernel projector: `FORMAL_KERNEL_PROJECTOR_PROVEN`
- formal complement projector: `FORMAL_COMPLEMENT_PROJECTOR_PROVEN`
- domain stability: `PROJECTOR_DOMAIN_STABILITY_CONDITIONAL`
- finite-projector convergence: `FINITE_PROJECTOR_CONVERGENCE_PROVEN`
- complement lower-bound bridge: `COMPLEMENT_LOWER_BOUND_CONDITIONAL`
- H_T dependency: `HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR`

This branch does not change frozen BHSM predictions, constants, tolerances, mode ledgers, or virtual dressing. It does not prove the full H_T theorem; topological index and mirror exclusion remain open.

# Unreleased / Development: v2.3 Index and Mirror Exclusion

Branch: `bhsm-v2.3-index-mirror-exclusion`

The v2.3 focused branch sharpens the corrected formal-kernel topological-index
and mirror-exclusion scaffold. The sector count is verified as one protected
formal state in each charged sector, the visible scaffold index remains 3, and
the generated opposite-chirality mirror candidates are excluded by the internal
chiral projector channel at scaffold level.

Status remains conservative:

- topological index operator: `INDEX_THEOREM_CONDITIONAL`
- twisted Dirac index closure: `INDEX_THEOREM_CONDITIONAL`
- sector count: `SECTOR_COUNT_PROVEN`
- chiral projector closure: `CHIRAL_PROJECTOR_CLOSURE_CONDITIONAL`
- Higgs-selected U1 mirror channel: `HIGGS_U1_MIRROR_CHANNEL_CONDITIONAL`
- v1.2 boundary mirror channel: `BOUNDARY_MIRROR_CHANNEL_CONDITIONAL`
- full mirror exclusion: `MIRROR_EXCLUSION_CONDITIONAL`
- H_T dependency: `HT_THEOREM_CONDITIONAL_ON_DOMAIN_STABILITY`

This branch does not change frozen BHSM predictions, constants, tolerances, mode
ledgers, virtual dressing, or v1.2 action-origin outputs. It does not prove the
full H_T theorem; complete-operator topological index proof, standalone
complete-operator mirror exclusion, and perturbation/projector domain-stability
upgrades remain open.

# Unreleased / Development: v2.4 Complete-Operator Domain Stability

Branch: `bhsm-v2.4-complete-operator-domain-stability`

The v2.4 focused branch audits whether the v2.1/v2.2 perturbation,
projector, commutator, and lower-bound scaffolds are sufficient to advance the
complete-operator domain-stability blocker. The bridge is strengthened to a
termwise, dependency-clean conditional result, but it is not marked proven.

Status remains conservative:

- complete-operator identification: `COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL`
- perturbation domain stability: `PERTURBATION_DOMAIN_STABILITY_CONDITIONAL`
- projector graph-domain stability: `PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL`
- projector commutator control: `PROJECTOR_COMMUTATORS_CONDITIONAL`
- lower-bound transfer: `HT_LOWER_BOUND_TRANSFER_CONDITIONAL`
- H_T dependency: `HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG`

This branch does not change frozen BHSM predictions, constants, tolerances, mode
ledgers, virtual dressing, scalar/QCD outputs, or v2.3 index/mirror reports. It
does not prove the full H_T theorem; complete-operator identification,
commutator/domain stability, and final index/mirror upgrades remain open.

# Unreleased / Development: v2.5 Full H_T Theorem Closure Attempt

Branch: `bhsm-v2.5-full-ht-theorem-closure`

The v2.5 branch attempts full H_T theorem closure rather than stopping at a
generic scaffold status. The attempt checks complete-operator identification,
projector-perturbation commutators, projector graph-domain stability,
lower-bound transfer, topological index, and mirror exclusion.

Final result:

- full H_T result: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- full BHSM theorem result: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- single named gap: `COMPLETE_OPERATOR_IDENTIFICATION_THEOREM_GAP`
- recommended next branch: `bhsm-v2.6-complete-operator-identification`

No theorem is marked proven from conditional assumptions. Frozen predictions,
canonical constants, frozen modes, tolerances, outputs, and virtual dressing are
unchanged. Final paper remains blocked.

# Unreleased / Development: v2.1 Perturbation Domain and Infinite-Bound Proof

Branch: `bhsm-v2.1-perturbation-domain-bound-proof`

The v2.1 focused branch strengthens the v2.0 Kato-Rellich perturbation bridge.
It adds executable reports for the common domain, termwise perturbation
symmetry, infinite-basis sector-coupling bounds, Hopf/boundary/chirality
bounds, lift/projector domain behavior, and a consolidated perturbation closure
decision.

Status remains conservative:

- common domain: `COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL`
- perturbation symmetry: `PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL`
- sector coupling: `SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL`
- relative-bound closure: `RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS`
- Kato-Rellich closure: `KATO_RELLICH_CLOSURE_CONDITIONAL`
- lower-bound status: `LOWER_BOUND_BLOCKED_BY_COMPLEMENT`
- H_T dependency: `HT_THEOREM_CONDITIONAL_ON_COMPLEMENT`

This branch does not change frozen BHSM predictions, canonical constants,
tolerances, the mode ledger, or the virtual dressing rule. It does not prove the
full H_T theorem; formal complement stability and complete-operator
identification remain open.

# BHSM v1.1 Preprint Package Release Notes

Branch: `bhsm-v1.1-paper`

## Unreleased / Development: v1.2 Action-Origin Development

Branch: `bhsm-v1.2-action-origin`

The v1.2 development branch packages the action-origin audit for the
charged-sector boundary operators. The charged-sector operators are derived
from an explicit symbolic sector boundary functional, and that functional is
reduced from a symbolic parent internal-action scaffold. Minimality and
tested-variant uniqueness audits find the scaffold
`UNIQUE_UNDER_BHSM_AXIOMS`.

This is a development addendum only. It does not alter `BHSM_BARE_V1`,
`BHSM_DRESSED_V1_CANDIDATE`, canonical constants, frozen predictions,
tolerances, or v1.1 public release outputs. It does not claim global uniqueness
of the complete Berger-Hopf internal action.

## Unreleased / Development: v1.3 H_T Spectrum

Branch: `bhsm-v1.3-ht-spectrum`

The v1.3 development branch is opened to attack the full twisted Dirac /
`H_T` spectrum gap. Current finite-basis Level 2, spectral lower-bound, and
basis-convergence scaffolds are preserved. The near-term target is an analytic
or semi-analytic lower-bound program for:

```text
H_T|_{H_perp} >= (4 pi^2 v)^2
```

This planning branch does not retune predictions and does not claim completion
of the `H_T` theorem.

v1.3F adds a state ontology and particle/mode classification ledger. It
clarifies that internal Berger-Hopf modes, virtual excitations, and
virtual-environment dressing contributions are not automatically new
observable particles. Any extra observable light state remains forbidden
unless experimentally identified or lifted/screened by the `H_T` and
scalar-sector mechanisms.

v1.3G adds a zero-mode/index and complement-projector scaffold for
`H = ker(D_twist) direct_sum H_perp` with target `dim ker(D_twist)=3`. The
finite Level 2 projector identities pass, but the full topological index
calculation and mirror-mode exclusion remain open.

v1.3H audits the diagonal complement lower bound and generated mirror-mode
candidates. The finite diagonal complement lower bound clears the required
Dirac threshold, but all three opposite-chirality mirror candidates remain
`OPEN_MIRROR_RISK`.

v1.3I audits those mirror candidates through chiral, Higgs-`U(1)`, and
boundary-functional channels. The weak chiral projector excludes all three
generated mirror candidates at the scaffold-channel level; theorem completion
remains false because the topological index and infinite-basis complement
bound remain open.

v1.3J audits the alignment between the formal protected zero-mode labels and
the finite Level 2 coordinate-protected block. The result is partial alignment:
the lepton label aligns, while the up/down labels remain
`OPEN_ALIGNMENT_GAP`.

v1.3K builds the formal sector-labeled protected projector directly from
coordinates `(0,18,36)` and recomputes the gap. The current Level 2 scaffold is
classified `FORMAL_KERNEL_NOT_PROTECTED`; the old coordinate-first gap does not
survive the formal-projector audit.

v1.3L-O correct and package the formal-kernel `H_T` scaffold. The corrected
reference is `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`, with coordinate-free
`K_formal = span{|ell,0,0,q=0,chi=-1>, |u,0,0,q=0,chi=-1>, |d,0,0,q=0,chi=-1>}`
and finite `k_max=4` realization `(0,18,36)`. Coordinate-first conclusions
depending on `(0,1,2)` are superseded. The full `H_T` theorem remains open.

## Unreleased / Development: BHSM Completion Campaign

Branch: `bhsm-completion-campaign`

The completion campaign packages v1.3 formal-kernel `H_T` results, adds
scheme-aware QCD/RG comparison scaffolds, strengthens scalar/topographic
decoupling scaffolds, and builds a unified dependency/theorem ledger. It does
not retune predictions and does not claim completed first-principles proof
unless every theorem dependency is explicitly closed.

Gate 2 adds the v1.4 QCD/RG matching scaffold. It records
`MIXED_DEFAULT`, `COMMON_SCALE_APPROX`, `THRESHOLD_AWARE_APPROX`, and
`PRECISION_QCD_PLACEHOLDER` reference sets, recomputes quark-ratio comparison
tables including dressed `c/t`, and keeps precision QCD as an explicit future
placeholder. Frozen BHSM ratios are compared but not changed.

Gate 3 adds the v1.5 scalar/topographic decoupling scaffold. The current
action-level scaffold distinguishes the SM Higgs projection from heavy,
screened, virtual, and forbidden scalar/topographic modes. It reports exactly
one light Higgs projection and zero current `OPEN_SCALAR_RISK` rows. Filtered
and screened topographic modes remain conditional scaffolds, not full
action-level scalar decoupling proof.

Gate 4 adds the v2.0 dependency graph and theorem ledger. The graph separates
frozen predictions, boundary-functional derivations, parent-action reductions,
basis realizations, semi-analytic scaffolds, finite-basis scaffolds, adoption
candidates, open items, and forbidden states. It reports no hidden circularity
or dependency on empirical residual machinery.

## Unreleased / Development: Final Closure Campaign

Branch: `bhsm-final-closure-campaign`

The final closure campaign attempts to close the remaining BHSM theorem nodes
after the v1.6 scalar/topographic screening scaffold. It runs five gates:

- Gate 1: full `H_T` theorem closure attempt;
- Gate 2: virtual dressing closure attempt;
- Gate 3: precision QCD/RG closure attempt;
- Gate 4: unified action dependency closure;
- Gate 5: final theorem ledger and open obligations.

Final status: `BHSM_STRONG_SCAFFOLD`.

Correct claim: BHSM is a strong no-retuning geometric Standard Model
reinterpretation framework with frozen predictions and multiple theorem
scaffolds, but not a fully closed first-principles theorem package.

The campaign does not change frozen predictions, canonical constants, mode
ledgers, tolerance bands, or release tags. It does not claim completion of the
full twisted Dirac / `H_T` theorem, scalar/topographic action proof, virtual
dressing theorem, precision QCD matching, or unified action closure.

## Unreleased / Development: Full Theorem Completion Attempt

Branch: `bhsm-full-theorem-completion`

This branch starts from `bhsm-final-closure-campaign` at commit
`069f1aa2a869bf810d29d2450ba62686513d8153` and attempts to determine whether
the BHSM theorem package can honestly be upgraded before a final paper. It
adds explicit completion-decision reports for:

- full operator domain and self-adjointness;
- infinite-basis/formal-kernel `H_T` theorem dependencies;
- topological index and mirror exclusion;
- scalar/topographic full-action proof;
- virtual dressing derivation status;
- unified action theorem package status.

Current decision: `BHSM_THEOREM_CANDIDATE_WITH_OPEN_ASSUMPTIONS`.

Final paper/Zenodo release is not allowed from this branch unless the status
is upgraded to `FULL_BHSM_THEOREM_PACKAGE_COMPLETE` by implemented,
dependency-clean proofs. Frozen BHSM predictions and prior scaffold outputs
remain unchanged.

## Unreleased / Development: v1.7 Operator-Domain and Index Chain

Branch: `bhsm-v1.7-operator-domain-index`

The v1.7 focused branch attacks the upstream chain feeding the full `H_T`
theorem:

```text
D(D_FK) -> self-adjointness -> dim ker D_twist = 3 -> mirror exclusion -> H_T complement theorem
```

It adds a Kato-Rellich/relative-bound audit for Hopf, boundary, chirality,
sector-coupling, heat-lift, PSD-profile, and complement-projector terms. The
current relative-a estimates are below one, including sector coupling
`a_K = 0.015621013485509948`, but the result remains
`RELATIVE_BOUND_CONDITIONAL` because infinite-basis compatibility and complete
domain preservation are not proven.

Current v1.7 status:

- full operator domain: `SELF_ADJOINT_DOMAIN_OPEN`;
- relative-bound audit: `RELATIVE_BOUND_CONDITIONAL`;
- topological index: `INDEX_THEOREM_OPEN`;
- mirror exclusion: `MIRROR_EXCLUSION_OPEN`;
- `H_T` dependency: `HT_THEOREM_BLOCKED_BY_DOMAIN`.

The corrected sector-labeled formal kernel is preserved and the old
coordinate-first kernel `(0,1,2)` remains rejected. Frozen BHSM predictions and
prior scaffold outputs remain unchanged. Final paper/Zenodo release remains
blocked.

## Unreleased / Development: v1.8 Infinite-Basis Domain Proof

Branch: `bhsm-v1.8-infinite-basis-domain-proof`

The v1.8 focused branch attacks the infinite-basis operator-domain and
relative-bound blocker identified in v1.7. It defines the infinite
sector-labeled Hilbert basis, finite-mode core, graph norm, diagonal reference
operator, formal kernel, formal complement, and complement projector.

Current v1.8 status:

- infinite-basis domain: `INFINITE_DOMAIN_CONDITIONAL`;
- uniform relative-bound theorem attempt: `UNIFORM_RELATIVE_BOUND_CONDITIONAL`;
- self-adjointness closure: `SELF_ADJOINT_DOMAIN_CONDITIONAL`;
- formal complement stability: `FORMAL_COMPLEMENT_CONDITIONAL`;
- H_T bridge: `HT_THEOREM_CANDIDATE_STRENGTHENED`.

The aggregate relative-a estimate remains favorable:

```text
total a <= 0.015621013485509948 < 1
```

This strengthens the H_T theorem candidate but does not prove the full theorem.
Full closure still requires the complete infinite-basis relative-bound proof,
self-adjoint domain proof, formal-complement stability proof, topological
index theorem, and mirror exclusion theorem. Frozen outputs remain unchanged
and final paper/Zenodo release remains blocked.

## Unreleased / Development: v1.9 Diagonal-Core Self-Adjointness

Branch: `bhsm-v1.9-diagonal-core-self-adjointness`

The v1.9 focused branch closes the diagonal reference-operator foundation for
the Kato-Rellich route. It proves essential self-adjointness for the abstract
real diagonal multiplication operator `A0 = D_diag^2` on the finite-mode core
`C_fin` in the sector-labeled `l2` basis.

Current v1.9 status:

- finite core: `FINITE_CORE_DENSE`;
- diagonal reference operator: `DIAGONAL_REFERENCE_OPERATOR_PROVEN`;
- essential self-adjointness: `DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN`;
- graph-norm domain: `GRAPH_NORM_DOMAIN_PROVEN`;
- Kato-Rellich preconditions: `KATO_RELLICH_PRECONDITIONS_CONDITIONAL`;
- H_T dependency: `HT_THEOREM_REFERENCE_OPERATOR_CLOSED`.

This closes the reference-operator foundation only. Perturbation symmetry,
perturbation domain inclusion, complete infinite-basis relative bounds,
formal-complement stability, topological index, and mirror exclusion remain
open. Frozen outputs remain unchanged and final paper/Zenodo release remains
blocked.

## Unreleased / Development: v2.0 Kato-Rellich Perturbation Closure

Branch: `bhsm-v2.0-kato-rellich-perturbation-closure`

The v2.0 focused branch attacks the perturbation side of the Kato-Rellich
route relative to the proven diagonal reference operator `A0 = D_diag^2`.

Current v2.0 status:

- perturbation symmetry: `PERTURBATION_SYMMETRY_CONDITIONAL`;
- perturbation domain inclusion: `PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL`;
- relative-bound closure: `RELATIVE_BOUND_CONDITIONAL`;
- Kato-Rellich closure: `KATO_RELLICH_CLOSURE_CONDITIONAL`;
- lower-bound preservation: `LOWER_BOUND_CONDITIONAL`;
- H_T dependency: `HT_THEOREM_BLOCKED_BY_PERTURBATION`.

The relative-bound estimate remains favorable:

```text
a <= 0.015621013485509948 < 1
```

but complete infinite-basis perturbation bounds and D(A0)-level domain
inclusion are not fully proven. Frozen outputs remain unchanged and final
paper/Zenodo release remains blocked.

## Unreleased / Development: v1.4 Precision QCD/RG Matching

Branch: `bhsm-v1.4-precision-qcd-rg`

The v1.4 focused branch upgrades the quark-mass comparison architecture with
precision-oriented metadata, threshold-aware running scaffolds, uncertainty
propagation scaffolds, and placeholder shells for future PDG-style and
precision-QCD reference inputs. It does not change frozen BHSM predictions,
does not tune `a`, `S`, modes, tolerances, or `Z_virt`, and does not claim
precision quark matching is solved.

## Unreleased / Development: v1.5 Scalar/Topographic Action-Decoupling

Branch: `bhsm-v1.5-scalar-action-proof`

The v1.5 focused branch extends scalar/topographic decoupling toward an
action-level scaffold. It separates:

- `HIGGS_PROJECTED_LIGHT_MODE`;
- `HOPF_GAP_LIFTED`;
- `HT_COMPLEMENT_LIFTED`;
- `DERIVATIVE_SCREENED`;
- `CURVATURE_SCREENED`;
- `VIRTUAL_ONLY`;
- `FORBIDDEN_UNSCREENED_LIGHT_SCALAR`;
- `OPEN_SCALAR_RISK`.

The scaffold uses the corrected `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`
dependency for H_T-linked scalar complement lifting and keeps the forbidden
unscreened light scalar channel as an explicit falsifier. It does not change
frozen BHSM predictions and does not claim full scalar decoupling from the
complete action.

## Unreleased / Development: v1.6 Scalar/Topographic Screening Proof

Branch: `bhsm-v1.6-scalar-screening-proof`

The v1.6 focused branch extends the v1.5 scalar action scaffold with
derivative-screening, curvature-screening, matter-coupling, and fifth-force
exclusion scaffolds. It audits every v1.5 scalar/topographic channel and
reports zero current `OPEN_SCALAR_RISK` rows.

This branch constrains derivative couplings of the form
`L_int ~ (1/M_*) partial_mu phi J^mu_topo` and curvature/topographic couplings
of the form `L_int ~ phi R_topo` as sufficient screening conditions. It keeps
direct unscreened light scalar coupling as an explicit falsifier.

It does not change frozen BHSM predictions and does not claim a full
scalar-screening theorem from the complete action.

Frozen baseline:

- Tag: `bhsm-v1.0-freeze`
- Commit: `03039feb14fb4c988edce8453f6ee5b234797eb2`
- Model branches:
  - `BHSM_BARE_V1`
  - `BHSM_DRESSED_V1_CANDIDATE`

## Included

- BHSM v1.0 frozen executable model framework.
- BHSM v1.1 technical note in Markdown, LaTeX, and PDF form.
- No-retuning prediction and falsification ledgers.
- Bare canonical branch and dressed-candidate branch.
- Manuscript appendices for constants, mode ledger, frozen outputs,
  falsification criteria, `H_T`/scalar scaffold status, and reproducibility.
- Release checklist, citation metadata, and all-rights-reserved license notice.

## Bare and Dressed Candidate Branches

`BHSM_BARE_V1` is the frozen alpha-anchored Berger-Hopf overlap model.

`BHSM_DRESSED_V1_CANDIDATE` applies `Z_virt^{u,2}=1/2` only to the middle
up-sector ratio `c/t`. It leaves `u/t`, CKM `sin_theta_13`, down-sector ratios,
lepton ratios, gauge outputs, Higgs/electroweak outputs, `H_T`, and scalar
outputs unchanged.

The dressed branch remains a candidate, not final canonical adoption.

## No-Retuning Rule

The v1.0 freeze is invalidated if `a`, `S`, the supplied mode ledger,
tolerance bands, or `Z_virt` are changed based on residuals.

## Current Limitations

- Full analytic twisted Dirac / `H_T` spectrum remains open.
- `H_T` no-extra-light-state theorem remains proxy/scaffold audited.
- Scalar/topographic decoupling remains scaffold audited, not fully proven from
  the action.
- Boundary operators `Omega_f` remain action-linked, not fully action-derived.
- Precision QCD/RG matching remains open.
- Dressed branch remains a candidate branch.

## Reproducibility

Run:

```powershell
python -m pytest -q
```

The v1.1 paper branch test status at release preparation is `281 passed`.
