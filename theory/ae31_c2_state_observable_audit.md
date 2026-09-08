# AE3.1 state nonuniqueness and observable independence

## Result

The absence of a unique state does not imply that every observable is
undetermined. The retained state-nonuniqueness theorem leaves the causal
operator and local singularity class unchanged. A quantity that is proved
constant across its admissible states can also be reported without choosing
one of them. Such independence must be established for the quantity itself.

This audit supplies an exact affine-response test on a complex extension of
the retained four-mode covariance family. It exhibits a sensitivity missed
by real-angle variations, and counterexamples to two invalid shortcuts:
zero first variation does not imply finite invariance, and the finite affine
test cannot be applied to a nonlinear functional's frozen gradient.

No physical lepton self-energy or pole functional is supplied. The result
does not establish state independence of the lepton dressing invariant, nor
independence on the full infinite-dimensional Hadamard class. It implements
one necessary family of checks for a future action-derived response.

## The same admissible states with a complex phase

Use the hypotheses of the retained
[fixed-history theorem](ae31_c2_fixed_history_state_nonuniqueness.md): smooth
orthonormal positive-subspace modes `e1,e2` of opposite charge in one family,
and their CAR conjugates `f1=Gamma e1`, `f2=Gamma e2`. On their four-dimensional
span, `P0=diag(1,1,0,0)`. Let

```text
u1 = cos(theta) e1 + exp(i phi) sin(theta) f2,
u2 = cos(theta) e2 - exp(i phi) sin(theta) f1,
P(theta,phi) = |u1><u1| + |u2><u2|.
```

The two vectors are orthonormal. Their span is orthogonal to its
antiunitary `Gamma` image, so

```text
P^dagger=P,   P^2=P,   0<=P<=I,   P+Gamma P Gamma=I.
```

In these coordinates `Gamma` means complex conjugation followed by exchange
of the upper/lower two components. The charge grading is
`diag(1,-1,-1,1)`; `P` commutes with it because each rotated vector has one
charge. The family sector is unchanged. Extending by `P0` on the orthogonal
complement changes the covariance by a finite-rank operator with smooth
range, preserving the Hadamard singularity class after the same causal
evolution. This is the same finite-rank mechanism used by the retained theorem.
The phase is a variation parameter, not a newly selected physical coupling.

At `phi=0`, this recovers the existing real-angle witness. That witness was
already sufficient to prove nonuniqueness; the new phase does not invalidate
the old theorem. It matters when testing independence of an observable.

The general existence theory is established curved-spacetime mathematics;
see Gérard and Stoskopf,
[Hadamard states for quantized Dirac fields on Lorentzian manifolds of bounded geometry](https://arxiv.org/abs/2108.11630).
That work constructs state classes; it is not an independent validation of
BHSM or a prescription for its missing physical state.

## Exact affine response and range

For a Hermitian four-mode matrix `B`, suppose the tested functional really is
affine, `F(C)=constant+Tr(B C)`. In one-based matrix indices define

```text
a = B33+B44-B11-B22,
b = B14-B23.
```

Direct multiplication gives

```text
F(P(theta,phi))-F(P0)
    = a sin(theta)^2 + sin(2 theta) Re[exp(i phi) b].
```

This difference vanishes for all angles and phases if and only if
`a=0` and the complex number `b=0`. Necessity follows by evaluating
`theta=pi/2`, then `theta=pi/4` with phases zero and `pi/2`; sufficiency
follows from the formula. The exact range over this family is

```text
[(a-sqrt(a^2+4|b|^2))/2, (a+sqrt(a^2+4|b|^2))/2].
```

It is the eigenvalue interval of the two-by-two Hermitian matrix
`[[0,b],[conj(b),a]]`, evaluated on normalized complex vectors
`(cos(theta), exp(i phi)sin(theta))`. Every endpoint is attained. This
algebraic formula is not a numerical outward certificate when `B` itself
is only a floating-point approximation.

Controls make the scope concrete:

| Algebraic response | a | b | Difference range | Consequence |
|---|---:|---:|---|---|
| `B=I` | 0 | 0 | `[0,0]` | Rank is unchanged despite distinct states |
| `B=Q_charge` | 0 | 0 | `[0,0]` | Charge trace is unchanged |
| `B=P0` | -2 | 0 | `[-2,0]` | Reference occupation changes |
| `B14=i`, `B41=-i`, all other entries zero | 0 | i | `[-1,1]` | Every real-angle test misses this imaginary response |

These are algebraic controls, not BHSM self-energies, measured observables,
or selected physical response matrices. An action-owned physical operator
must satisfy its additional symmetry, domain, and renormalization conditions.
Under a reset or basis change, both `B` and `C` must be conjugated by the
same unitary; cyclicity of the trace then preserves the response.

## Nonlinear and local-variation limits

At the reference state,

```text
d/dtheta F(P(theta,phi))|theta=0 = 2 Re[exp(i phi) b].
```

Its vanishing tests only `b=0`. For example, `B=P0` has zero first variation
and nevertheless changes at second order. A local tangent test is not a
finite-orbit independence theorem.

Nor can the affine finite-change formula be applied to a nonlinear
functional by freezing its derivative. For `F(C)=Tr(C^2)`, every pure
rank-two covariance has `F=2`. Its gradient at `P0` is `2P0`; treating that
gradient as a global affine response would incorrectly predict variation.
The functional's higher derivatives cancel that spurious change.

For a differentiable physical functional `R[C]`, testing its derivative on
all admissible tangents is a necessary local check. Vanishing along every
path throughout a connected admissible component establishes constancy on
that component; values on disconnected components require separate checks.
A single four-mode test at one state does not supply either result.

## Application gate for the charged-lepton invariant

### Causal response is not a quantum-state selector

The [AE4 future-child domain](ae4_future_collapse_relative_boundary_domain.md)
selects a retarded response. It must not be interpreted as automatically
selecting a Feynman covariance. For a fixed quadratic CAR field, with unitary
Cauchy evolution `U_t` and a reference covariance `C`, the two unordered
two-point matrices have the forms

```text
W_plus(t,s)  = U_t C U_s^dagger,
W_minus(t,s) = U_t (I-C) U_s^dagger.
```

Their sum, the anticommutator kernel, is `U_t U_s^dagger`. Consequently
`G_R=-i theta(t-s) U_t U_s^dagger` is independent of `C`. The time-ordered
function instead satisfies

```text
G_F(t,s) = -i U_t [C-theta(s-t)I] U_s^dagger,
delta G_F = -i U_t delta C U_s^dagger.
```

Thus identical free retarded dynamics can coexist with distinct time-ordered
states. This identity also gives a concrete state-independent object; lack
of a unique covariance is not a blanket obstruction to all operator results.
The report verifies it on a four-mode quadratic control whose dimensionless
energies are explicitly not BHSM masses. The argument does not assert
state independence of an interacting, dressed, or composite retarded kernel.
AE4's actual coupled child response still has to be evaluated on its own
declared action and domain.

### Required physical mass response

Conditional on positive differentiable physical mass readouts `M_f[C]`, the
already derived pole combination has first variation

```text
delta R = delta M_e/M_e - 9 delta M_mu/M_mu + 8 delta M_tau/M_tau.
```

If those variations admit a Hermitian covariance-response representation,
their weighted sum determines the response matrix to test on each admissible
finite-rank direction. This is conditional: the physical mass readouts and
their response kernels are not yet evaluated in BHSM, and no reference mass
or required dressing number is used to invent them.

There are therefore two distinct ways to remove state ambiguity for a
particular target: derive the physical state prescription, or prove the
target is independent of all remaining allowed state data. A controlled
state-uniform interval could also support an interval prediction if all
other physical dependencies and error bounds are closed. The present
algebraic control ranges are not such physical intervals.

The existing local tree relation survives as its conditional action/mode
identity. The new check does not promote it to globally dressed poles, repair
the photon obstruction, or replace the missing finite two-point calculation.
It also does not remove state selection from the requirements for a claimed
unique state-dependent Feynman function.

## Reproduction and status

The test suite proves the four-mode identities symbolically for arbitrary
real angles and general Hermitian `B`, checks extrema against an independent
eigenproblem, and verifies the nonlinear counterexamples. Numerical sampled
residuals are diagnostics rather than proofs. The retained report is written
twice and compared byte for byte; the test uses temporary outputs.

```sh
python scripts/materialize_ae31_c2_state_observable_audit.py
python -m pytest -q tests/test_ae31_c2_state_observable_audit.py
```

Artifact: `artifacts/action_extension/BHSM_AE31_C2_STATE_OBSERVABLE_AUDIT.json`.
`FULL_BHSM_COMPLETE = FALSE`. No additional state assumption is adopted.
