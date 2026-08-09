# BHSM v15.0 Aether pregeometric parent calculus

Primary verdict:

`AETHER_PARENT_STRATIFICATION_IS_MATHEMATICALLY_COMPATIBLE_WITH_CURRENT_BHSM_BUT_FINITE_CORE_TRANSITION_REQUIRES_AN_ACTION_OWNED_PREGEOMETRIC_CORRESPONDENCE_LAW`

This is Outcome B. The package constructs a conservative typed extension and
several exact conditional theorems. It does not derive a physical Aether
transition, prove that spacetime is emergent in nature, or complete BHSM.

`BHSM_AETHER_NOT_LUMINIFEROUS_ETHER = TRUE`.

## 1. Haar barrier theorem

The v11.0 support axioms remain unchanged:

\[
q_D(\upsilon)=-\lambda_D\log\upsilon,
\qquad
ds_D^2=\lambda_D^2\frac{d\upsilon^2}{\upsilon^2},
\qquad 0<\upsilon\leq1.
\]

Hence

\[
d(\upsilon_1,\upsilon_2)
=\lambda_D\left|\log\frac{\upsilon_1}{\upsilon_2}\right|,
\qquad
d(1,\upsilon)\longrightarrow\infty
\quad(\upsilon\to0^+).
\]

This line is isometric to the half-line in `q_D`; `upsilon=0` is not a finite
point of its metric completion. For every smooth change of regular coordinate,
the line element is pulled back and curve length is invariant. For example,
the bounded plotting coordinate

\[
z=\frac{q_D}{\lambda_D+q_D}\in[0,1)
\]

puts the ideal endpoint at `z=1`, but

\[
q_D=\lambda_D\frac{z}{1-z}
\]

still diverges. Coordinate compactification is not a dynamical solution.

There is also a finite-action obstruction. If a regular path has finite
exterior parameter interval `Delta` and finite squared-speed integral `K`,
Cauchy--Schwarz gives

\[
L\leq\sqrt{\Delta K}<\infty.
\]

It cannot reach an infinite-distance endpoint. Therefore Option A cannot
represent a finite-duration, finite-regular-action encapsulation event.

## 2. Core nonidentification and conservative extension

The admissible candidate extension is

\[
\mathfrak S=\mathfrak G_A\sqcup\mathfrak C_A,
\qquad
\mathfrak C_A\ne\{\upsilon=0\}.
\]

`upsilon` exists only on the reconstructible regular stratum
`G_A`. The core schema has no spacetime coordinates, conventional time,
duration, metric size, conventional energy, energy density, velocity, or
preferred-frame variable. This is a conservative mathematical extension:
restriction to `G_A` returns the existing theory exactly.

The extension alone does not supply an adjacency between `G_A` and `C_A`.
That adjacency and its transition weight/action are new missing upstream
structure. No new M8/M5/M4 field or continuous coefficient is adopted.

## 3. Reconstruction and emergent distance

The executable reconstruction predicate requires, on the proposed branch:

1. a self-adjoint operator/domain;
2. bounded commutators on a dense coordinate algebra;
3. full-rank geometric principal symbol;
4. the appropriate BHSM spectral dimension;
5. compatible relative/boundary domains;
6. a valid continuum correspondence realization; and
7. recovery of the regular support formula.

Only when all conditions hold is the state classified
`RECONSTRUCTIBLE_BHSM_GEOMETRY`. Otherwise it is
`NONRECONSTRUCTIBLE_AETHER_STATE`.

This is a sharp conditional predicate, not a derivation of the missing global
operator. In particular, the v14.64 result remains binding: a finite diamond
incidence matrix is not the continuum operator because bulk-to-boundary trace
is unbounded on plain `L2`. The edge-restricted calibration

\[
d_{ij}=|D_{ij}|^{-1}
\]

is reused, but no global continuum Connes metric is claimed. Distance on
`C_A` is undefined. Infinite regular Haar depth and absence of a core metric
are mathematically distinct statements.

The proposed identification of singularity with reconstruction failure remains
a hypothesis, not a theorem.

## 4. Relational order, clocks, and energy

A minimum algebraic process depth can be a dimensionless cocycle

\[
\chi(\gamma_2\circ\gamma_1)=\chi(\gamma_2)+\chi(\gamma_1).
\]

It is not called time. If a stable recurring reference process exists, the
noncircular clock output is only the ratio

\[
\frac{t_{\rm eff}}{\tau_{\rm ref}}
=\frac{\chi(\gamma)}{\chi(\gamma_{\rm ref})}.
\]

The process category and cocycle are defined before the reference clock, so
the clock calibrates relational order rather than defining it. Absolute
seconds are not derived in this sprint.

Conditionally, if the process translations admit a strongly continuous
unitary representation

\[
U(\chi)=e^{-i\chi K},\qquad K\psi=\kappa\psi,
\]

then after a clock period is supplied, Stone-generator linearity yields

\[
E_{\rm eff}=\frac{\hbar}{\tau_{\rm clock}}\kappa.
\]

Thus conventional energy appears only after clock calibration on this branch.
The unitary representation and stable clock are conditional structures, not
results of the current BHSM action, and `tau_clock` is not adopted as a new
fundamental Aether parameter.

## 5. Encapsulation event correspondence

The package implements an abstract boundary-to-boundary span with incoming
and outgoing objects in `G_A`, an internal event word in `C_A`, an additive
process depth, and a parent invariant signature. Two events compose exactly
when the middle boundary and invariant signature agree. Composition
concatenates event words and adds process depth, so associativity and invariant
matching are executable.

Exterior clock readings may satisfy

\[
t_-<t_+<\infty
\]

without assigning an intrinsic clock continuation or duration to the core.
There is no contradiction: finite separation of reconstructed boundary
readings does not imply that the non-geometric intermediate object has a
Lorentzian history.

This event calculus is an algebraic consistency witness only. The existing
action does not select the event relation, its amplitude, its allowed invariant
signature, or its reconstruction projection. Brown--York energy, ADM
constraints, cap currents, and Noether charges remain conditional projections
after a physical boundary/domain and action-owned functor are provided.

## 6. High excitation versus reconstructibility

No monotonic theorem follows from current BHSM. The executable independence
witness holds reconstruction fixed while changing a dimensionless generator
excitation. Therefore

`HIGH_EXCITATION_IMPLIES_LOW_RECONSTRUCTIBILITY = NOT_DERIVED`.

The missing object is an action-owned coupling between the transition
generator and a reconstruction defect or operator-domain loss. It may not be
inserted because the desired physical interpretation is attractive.

## 7. Low-energy recovery and microscopic-action discipline

The conservative extension recovers on `G_A`, without retuning:

- M8/M5/M4 and Berger--Hopf stratification;
- the regular support variable and logarithmic Haar depth;
- v14.64 relative/boundary correspondence and trace obstruction;
- current cap/attachment domains;
- v14.91 Lorentzian controls;
- v14.93 radial no-bifurcation result;
- v14.94 absence of a controlled encapsulation event;
- all frozen predictions and existing no-go results.

The existing action, heat-trace branch, zeta branch, and abstract event-span
branch were audited separately. None derives the core transition. The heat
and zeta functionals remain candidate microscopic choices requiring an
operator, domain, trace/renormalization data, and pre-comparison selection.
No microscopic functional is adopted in v15.0.

## 8. Preferred-frame firewall

The typed construction contains no inertial-frame, rest-frame, medium
velocity, detector, background-spacetime propagation, or new gravity-mediator
variable. The reconstructed regular theory is unchanged, including its
Lorentz-covariant claim boundary. A preferred-frame Aether is invalidated.

## 9. T1--T12 gate status

| Gate | Status |
|---|---|
| T1 Haar barrier | proved |
| T2 core nonidentification | proved for finite-action finite events |
| T3 stratified extension | conservatively admissible; event law missing |
| T4 reconstruction | conditional operator/domain predicate |
| T5 distance | regular edge rule retained; core distance undefined |
| T6 clock | conditional relative clock ratio |
| T7 energy | conditional clocked Stone-generator map |
| T8 event | associative abstract span; not action-owned |
| T9 invariants | abstract matching closes; physical set open |
| T10 recovery | proved by restriction for the conservative extension |
| T11 excitation/reconstructibility | underdetermined; monotonicity not derived |
| T12 preferred frame | firewall passes by construction |

## Hindsight 20/20

### Validated

- The regular support endpoint is infinitely far away and cannot be made
  finite by a bounded chart.
- A separate non-geometric core stratum is mathematically compatible as a
  conservative extension.
- Relative process order can precede clock calibration.
- Conventional energy can be represented conditionally only after clock
  calibration.
- Invariant-matched abstract event spans compose associatively.
- Finite exterior clock separation is compatible with no intrinsic core time.

### Invalidated

- `Aether core = upsilon 0` as a finite-action accessible regular state.
- Coordinate compactification as finite physical distance.
- Conventional time or energy as primitive core data.
- The naive finite diamond as the continuum correspondence operator.
- High excitation alone as a theorem of reduced reconstructibility.
- Linear instability as completed encapsulation.
- Preferred-frame or material-medium Aether.

### Reclassified

- `upsilon` is a regular geometric-support coordinate, not a core coordinate.
- Core size is undefined, not zero or infinitely small.
- Singularity as reconstruction failure remains a hypothesis.
- Finite encapsulation may be represented by a boundary correspondence, but
  the present correspondence is only a candidate algebraic model.
- Energy is a clock-calibrated generator representation on the conditional
  unitary branch.

### Open

Exactly one next irreducible object:

`ACTION_OWNED_PREGEOMETRIC_CORE_EVENT_CORRESPONDENCE_WITH_SELF_ADJOINT_RELATIVE_BOUNDARY_DOMAIN_PARENT_INVARIANT_MATCHING_CLOCK_CALIBRATION_AND_EXACT_REGULAR_BHSM_RECOVERY`

## Completion boundary

```text
OUTCOME = OUTCOME_B
FULL_BHSM_COMPLETE = FALSE
MARK_III = NOT_REACHED
PHYSICAL_AETHER_TRANSITION_DERIVED = FALSE
FINITE_TIME_ENCAPSULATION_EVENT_DERIVED = FALSE
USB_SYNCHRONIZATION_ELIGIBLE = FALSE
```

Frozen predictions and official prediction logic are unchanged. No measured
particle, mixing, coupling, or cosmological target entered the construction.
No new continuous parameter or fundamental dynamical field was introduced.
USB/removable media was not touched.
