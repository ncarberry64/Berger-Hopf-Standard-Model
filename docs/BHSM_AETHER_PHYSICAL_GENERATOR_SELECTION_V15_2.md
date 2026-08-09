# BHSM v15.2 physical Aether-generator selection

Primary verdict:

`BHSM_V15_2_PHYSICAL_EQUIVALENCE_IDENTIFIES_STRUCTURE_PRESERVING_UNITARY_INTERTWINERS_AS_BASIS_GAUGE_AND_PRECLOCK_POSITIVE_GENERATOR_SCALING_AS_PROCESS_REPARAMETERIZATION_WHILE_UNIFORM_CENTRAL_SHIFTS_REMAIN_ONLY_CONDITIONALLY_PROJECTIVE_BECAUSE_THE_EVENT_INTERFERENCE_FUNCTOR_IS_NOT_ACTION_OWNED;_THE_REGULAR_ACTION_SUPPLIES_REGULAR_STRATUM_INCIDENCE_AND_THEOREM_CLASS_CALDERON_WENTZELL_DATA_BUT_NO_PREGEOMETRIC_CORE_HILBERT_MODULE_CORE_OPERATOR_ATTACHMENT_QUADRATIC_FORM_OR_STABLE_REFERENCE_CYCLE_SO_NO_PARENT_VARIATION_SCHUR_FESHBACH_COMMUTANT_COMPOSITION_OR_MINIMALITY_ARGUMENT_SELECTS_THE_PHYSICAL_GENERATOR_CLOCK_OR_HAMILTONIAN`

The result is `OUTCOME_F_UPSTREAM_OWNERSHIP_OBSTRUCTION`.

The current BHSM action does not uniquely select a physical Aether generator
or clock. More strongly, the physical selection problem cannot yet be posed
on an action-owned core representation: the retained action has no
pregeometric core Hilbert correspondence, trace pairing, core operator, or
core-boundary quadratic form. This is a precise no-go, not a choice of another
admissible generator.

## 1. Physical generator equivalence

The complete mathematical datum to be compared is not a matrix alone. It is
the structured tuple

\[
(\mathcal H_A,\pi_A,\mathcal D_{\rm rel},K_A,
\{Q_i\},P_G,\Theta_A,C_{\rm clk}).
\]

Here `pi_A` represents the invariant algebra, `D_rel` is the relative domain,
`P_G` is regular reconstruction, `Theta_A` is the boundary response, and
`C_clk` is any action-selected reference cycle.

Two tuples are unitarily equivalent only if one unitary intertwines every
owned structure:

\[
K_A'=UK_AU^*,\qquad Q_i'=UQ_iU^*,\qquad
P_G'=UP_GU^*,
\]

and carries the relative domain, matching observables, boundary form, and
clock structure to their primed counterparts. Such a transformation is a
basis change, not new physics. Intertwining `K_A` alone is insufficient.

The true target is therefore

\[
\mathcal K_{\rm physical}=\mathcal K_{\rm admissible}/\sim,
\]

but the equivalence relation contains one presently conditional component:
central shifts.

## 2. Central-shift gate

For a uniform central shift,

\[
K_A' = K_A+cI,
\]

the event kernel becomes

\[
U_A'(E)=e^{-ic\chi(E)}U_A(E).
\]

At one fixed process depth, normalized transition probabilities are
unchanged. A block-relative shift between geometric and core sectors is not a
central shift and can change relative phases directly.

The uniform character is not automatically gauge in the full event system.
Two histories with the same endpoints and different additive depths acquire a
relative phase unless one of the following is proved:

1. only projective rays are physical for every event amplitude;
2. the cocycle `chi` is an object coboundary, so the character is removable by
   endpoint phases; or
3. the action-derived interference law makes the character unobservable.

None is presently action-owned. Thus

`CENTRAL_SHIFT = CONDITIONAL_PROJECTIVE_EQUIVALENCE_NOT_UNCONDITIONAL_PHYSICAL_GAUGE`.

## 3. Pre-clock scaling and the corrected v15.1 witness

Before a stable clock is selected,

\[
K_A\mapsto aK_A,\qquad
\chi\mapsto\frac{\chi}{a},\qquad a>0,
\]

leaves the kernel exactly unchanged:

\[
e^{-i(\chi/a)(aK_A)}=e^{-i\chi K_A}.
\]

Therefore positive scaling is a process reparameterization on the pre-clock
branch. This reclassifies the v15.1 pair

\[
\operatorname{diag}(0,1),\qquad\operatorname{diag}(0,2):
\]

it proves literal non-unitary equivalence, but not physical pre-clock
inequivalence.

The corrected clock-covariant relation retains the depth of the selected
cycle explicitly:

\[
\boxed{
H_{\rm eff}
=\hbar\frac{\Delta\chi_{\rm clk}}{\tau_{\rm clk}}K_A.
}
\]

Under

\[
K_A'=aK_A,
\qquad
\Delta\chi_{\rm clk}'=\frac{\Delta\chi_{\rm clk}}a,
\]

the joint Hamiltonian is invariant. The v15.1 formula
`H_eff=(hbar/tau_clk)K_A` is the unit-cycle convention
`Delta chi_clk=1`, valid only after cycle selection.

## 4. Corrected constructive nonuniqueness witness

On one fixed three-sector theorem representation, take

\[
Q=\operatorname{diag}(-1,0,1),
\]

and the two fixed generators

\[
K_A^{(1)}=\operatorname{diag}(0,1,2),
\qquad
K_A^{(2)}=\operatorname{diag}(0,1,3).
\]

Both are self-adjoint, commute with the same invariant, preserve norm, obey
the event composition and identity laws, and use the same exact self-adjoint
Wentzell theorem domain. No real tuning parameter is used.

Their ordered gap ratios are respectively

\[
\frac{2-1}{1-0}=1,
\qquad
\frac{3-1}{1-0}=2.
\]

No positive affine spectral map

\[
\operatorname{spec}K_A^{(2)}
=a\operatorname{spec}K_A^{(1)}+c
\]

exists. Hence the pair remains inequivalent after unitary, central-shift, and
positive-scaling quotients.

This proves that the theorem-class admissibility axioms do not select one
class. It is not promoted to two physical Aether laws because the shared
three-sector representation itself is not action-derived.

## 5. Invariant commutant

For the simple three-sector invariant above,

\[
\dim_{\mathbb C}\operatorname{Comm}(Q)=3.
\]

The Hermitian commutant therefore has real dimension three. Positive scaling
removes one dimension. If a central-shift quotient is later justified, it
removes one more, leaving a one-dimensional continuous shape quotient. Without
that projective theorem, two continuous dimensions remain.

The actual complete Aether invariant representation is itself not derived, so
these are exact retained-representation results rather than a claimed
cardinality for Nature. Symmetry compatibility does not select dynamics.

## 6. Parent action and core Hilbert module

The v14.64 geometric direct sum is

\[
\mathcal H_8\oplus\mathcal H_{5,+}\oplus
\mathcal H_{5,-}\oplus\mathcal H_4.
\]

It uses owned geometric measures on reconstructible strata. It does not
contain `C_A`. In v15.0, the core was deliberately defined without spacetime
coordinates, conventional time, metric, measure, energy, or preferred-frame
data. The abstract event word supplies no Hilbert inner product.

Consequently the archive does not derive:

- `H_C` as a Hilbert space or module;
- a representation of the invariant algebra on `H_C`;
- a core trace pairing or grading;
- a core operator `D_C`;
- a core-boundary trace map;
- the physical relative operator domain.

Choosing `C^n` for convenience would add exactly the primitive structure the
sprint forbids. No such choice is adopted.

## 7. Does the action select the boundary condition?

If an owned boundary quadratic term existed,

\[
\mathcal Q_{\partial}[\Psi]
=\frac12\langle\Gamma_0\Psi,
\Theta_A\Gamma_0\Psi\rangle,
\]

its variation could produce

\[
\Gamma_1\Psi+\Theta_A\Gamma_0\Psi=0.
\]

The retained archive instead supplies:

- v14.65: a scalar self-adjoint boundary theorem class;
- v14.66: operator-valued Calderon/Wentzell admissibility;
- v14.67: a whitened attachment response on an author-selected finite-radius
  regular branch;
- v14.68: a canonical rank-two incidence lift inside the regular
  M8/M5/M4 envelopment.

These regular results do not define a core Calderon projector or core DtN map.
There is no retained `G_A`--`C_A` boundary action whose variation fixes
`Theta_A`. Therefore boundary theory classifies allowed domains; the current
action does not select the physical one.

## 8. Schur/Feshbach route

For a supplied block operator,

\[
\mathscr D_A=
\begin{pmatrix}
D_G&B\\
B^*&D_C
\end{pmatrix},
\]

the formal reduction is

\[
K_{\rm eff}(z)=D_G-B(D_C-z)^{-1}B^*.
\]

Using an ordinary energy `z` before clock reconstruction would be circular.
At `z=0`, an invertible self-adjoint `D_C` gives the exact Hermitian Schur
operator

\[
K_{\rm eff}(0)=D_G-BD_C^{-1}B^*.
\]

This avoids the energy circularity but not the ownership obstruction:
`D_C`, `B`, their domain, and their pairing are absent. Existing KKT/Schur
theorems show what follows after these blocks are supplied; they do not
manufacture the blocks.

## 9. Composition, functoriality, and minimality

Every self-adjoint commutant generator produces

\[
U(\chi_2)U(\chi_1)=U(\chi_1+\chi_2).
\]

Thus one-parameter composition does not select `K_A`. The fuller event
category does not yet help because its core morphisms, local gluing maps, and
action amplitudes are abstract. Moreover the additive cocycle permits the
unresolved one-dimensional characters appearing in the central-shift gate.

Lowest matrix size, smallest norm, lowest differential order, minimal block
count, or minimal spectral complexity are not derived BHSM axioms. The zero
generator minimizes several such criteria but gives only identity transport.
Likewise v14.64 proves the heat semigroup is canonical after an operator is
known; it does not prove that a heat trace is the microscopic action.

## 10. Stable clock audit

No retained recurrence is a physical Aether reference clock:

- the v14.74 Goldstone rotor is conditional on uncomputed action coefficients,
  has gapless symmetric modes, and belongs to reconstructed geometry;
- the FR rotor has conditional inertia and embedding and does not select a
  recurring core event;
- relative-periodic and monodromy witnesses are synthetic or remain absent on
  physical branches;
- no stable action-owned core orbit, holonomy cycle, or recurrence is present.

Therefore neither `tau_clk`, `Delta chi_clk`, nor their physical pair with
`K_A` is selected. The joint `H_eff` is not unique.

## 11. T1--T13 result

| Gate | Result |
|---|---|
| T1 physical equivalence | structurally defined |
| T2 central shift | conditional projective equivalence |
| T3 relational scaling | pre-clock reparameterization |
| T4 core Hilbert module | not action-owned |
| T5 boundary block | admissible class only; not selected |
| T6 parent quadratic form | absent for the core correspondence |
| T7 Schur/Feshbach | exact conditionally; physical blocks absent |
| T8 invariant commutant | nontrivial; no unique generator |
| T9 event composition | no additional uniqueness |
| T10 stable clock | not derived |
| T11 joint generator/clock | not unique |
| T12 regular recovery | exact v15.1 identity limit retained |
| T13 physical uniqueness | unresolved because upstream ownership is absent |

The theorem-class admissible quotient is continuously infinite in the
representative three-sector case. The cardinality of the physical quotient is
`UNDEFINED_NOT_ZERO`, because the action-owned core representation required to
define that set does not exist.

## 12. Exact regular BHSM recovery

No regular action term is changed. At identity/core decoupling,

\[
U_A(0)=I,
\qquad
\Gamma_{\rm total}[\Phi,E_{\rm id}]
=\Gamma_{\rm BHSM}[\Phi].
\]

The v15.1 exact symbolic metric--eta variation residuals remain

\[
(0,0,0).
\]

M8/M5/M4 structure, support/Haar geometry, regular self-adjoint domains,
historical no-go results, frozen predictions, and official prediction logic
are unchanged.

## Hindsight 20/20

### Validated

- Structure-preserving unitary intertwiners are basis gauge.
- Positive generator scaling is pre-clock process reparameterization.
- The scale-covariant observable is
  `H_eff=hbar*(Delta_chi_clk/tau_clk)*K_A`.
- A fixed three-sector witness survives unitary, shift, and scale quotients.
- The retained action lacks the core module and boundary quadratic form needed
  to define physical selection.
- Exact regular BHSM recovery remains intact.

### Invalidated

- The v15.1 two-level pair proves physical pre-clock inequivalence.
- Self-adjointness selects the physical boundary condition.
- Invariant conservation selects unique dynamics.
- Unitary composition selects unique dynamics.
- Minimal matrix complexity is a physical selection theorem.
- Arbitrary clock normalization is a derived scale.

### Reclassified

- Literal `K_A` uniqueness becomes physical equivalence-class uniqueness.
- Generator selection becomes joint generator/cycle selection.
- Central shifts become a projectivization/interference gate.
- Admissible boundary triples become an action-selected physical boundary
  block problem.

### Open

Exactly one next irreducible object:

`MICROSCOPIC_ACTION_DERIVATION_OF_THE_PREGEOMETRIC_CORE_BOUNDARY_HILBERT_CORRESPONDENCE_QUADRATIC_FORM_WITH_TRACE_PAIRING_CORE_OPERATOR_ATTACHMENT_COUPLING_AND_STABLE_REFERENCE_CYCLE_WHOSE_VARIATION_JOINTLY_SELECTS_THETA_A_K_A_AND_H_EFF`

## Completion boundary

```text
K_A_LITERAL_UNIQUE = FALSE
K_A_PHYSICAL_CLASS_UNIQUE = FALSE
PHYSICAL_K_A_QUOTIENT_ACTION_DEFINED = FALSE
CORE_HILBERT_MODULE_ACTION_DERIVED = FALSE
PHYSICAL_WENTZELL_CALDERON_BLOCK_ACTION_DERIVED = FALSE
STABLE_REFERENCE_CLOCK_ACTION_DERIVED = FALSE
H_EFF_UNIQUELY_DETERMINED = FALSE
OUTCOME = OUTCOME_F_UPSTREAM_OWNERSHIP_OBSTRUCTION
FULL_BHSM_COMPLETE = FALSE
MARK_III = NOT_REACHED
USB_SYNCHRONIZATION_ELIGIBLE = FALSE
```

No continuous parameter, primitive core field, preferred frame, empirical
input, frozen-prediction change, official-prediction change, or USB operation
enters v15.2.
