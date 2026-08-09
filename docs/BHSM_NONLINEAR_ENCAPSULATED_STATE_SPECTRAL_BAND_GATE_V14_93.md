# BHSM v14.93 nonlinear encapsulation and spectral-band gate

Primary verdict:

`BHSM_V14_93_THE_COMPLETE_COMPACT_VIRIAL_IDENTITY_DOES_NOT_FORBID_STATIC_LOCALIZATION_BUT_THE_EXACT_DEGREE_ONE_IDENTITY_SEED_IS_QUADRATICALLY_STABLE_IN_EVERY_NONCONFORMAL_EQUIVARIANT_RADIAL_MODE_AND_QUARTICALLY_STABLE_ALONG_ITS_UNIQUE_CONFORMAL_ZERO_DIRECTION_SO_NO_NEARBY_RADIAL_ENCAPSULATED_BRANCH_PROTECTED_INTERNAL_BAND_OR_SMOOTH_PROJECTOR_BIFURCATES_FROM_THE_SEED;_THE_FULL_NONHOMOGENEOUS_COUPLED_BOUNDARY_VALUE_PROBLEM_REMAINS_UNSOLVED`

## Action and charge ownership

No energy field is added. The state-bearing system is the constrained,
gauge-reduced Lorentzian M8 phase space

```text
[h,pi; chi,p_chi; sigma,p_sigma; eta,p_eta]constraints/diffeomorphisms.
```

The retained nonlinear blocks are P1 gravity, the constrained eta
`p2+p8` block, chi/sigma, and the existing cap/GHY/KKT architecture. The M4
gauge and Dirac variables remain intrinsic foundational data and are not used
as M8 localization fields. A complete DtN response is conditional on a
selected background and domain; it cannot be evaluated before the state is
found.

The exact global topological charge is `degree(eta)=1` in `pi7(S7)=Z`. It
prevents continuous decay to degree zero but does not itself prove spatial
localization on compact S7. Hamiltonian, momentum, target-isometry charge and
physical angular momentum retain their ordinary conditional roles. No wave
action or empirical stabilizing charge is introduced.

## Virial screen

For a flat seven-dimensional eta configuration with
`eta_lambda(x)=eta(lambda*x)`, the two derivative blocks scale as

```text
E2(lambda)=lambda^-5 E2,
E8(lambda)=lambda E8,
```

so an eta-only flat stationary point would obey `E8=5 E2`. This is not the
compact v14.91 radius variation. On the identity branch,

```text
E8/E2 = X^3/(4 kappa1) = 5/4.
```

The compact stationarity identity also varies the Einstein curvature,
cosmological volume, compact measure and any boundary, scalar and KKT blocks.
Those terms close on the v14.91 coefficient locus. Consequently a flat
Derrick argument does not forbid a static compact state, while the identity
seed is not a localized state.

## Minimal degree-one nonhomogeneous ansatz

On round S7 use

```text
eta(chi,n) = (cos f(chi), sin f(chi) n),  n in S6,
f(0)=0, f(pi)=pi,
X = [f'(chi)^2 + 6 sin(f)^2/sin(chi)^2]/a^2.
```

With the S6 volume suppressed, the retained eta energy is

```text
E[f] = integral_0^pi sin(chi)^6
       [kappa1 X/2 + X^4/8] dchi.
```

The identity seed is `f(chi)=chi`, `X^3=5 kappa1`, and `a^2=7/X`.

## Exact radial stability theorem

For `f=chi+epsilon y`, the second variation is

```text
delta2 E = (72 X^4/245) integral_0^pi sin(chi)^6
           [y'^2 + (6 cot(chi)^2-1)y^2] dchi.
```

The radial operator is

```text
Lrad = -d2/dchi2 - 6 cot(chi)d/dchi + 6 cot(chi)^2 - 1.
```

Writing `y=sin(chi)u` reduces it to the Gegenbauer operator. Its regular
Dirichlet eigenfunctions and eigenvalues are

```text
y_n = sin(chi) C_n^(4)(cos chi),
lambda_n = n(n+8),  n=0,1,... .
```

Thus every `n>=1` radial mode is strictly positive. The unique quadratic zero
mode is `y_0=sin(chi)`. It is tangent to the exact degree-one conformal family

```text
f_s(chi)=2 atan(exp(s) tan(chi/2)).
```

Reflection sends `s` to `-s`, so all odd derivatives vanish at the identity.
Direct expansion of the retained action gives

```text
E''(0)=0,
E'''(0)=0,
E''''(0)=27 pi X^4/128 > 0,

E(s)=E(0)+(9 pi X^4/1024)s^4+O(s^6).
```

The conformal zero direction is therefore quartically stable. No nearby
equivariant radial encapsulated branch bifurcates from the identity seed.
This is a local branch theorem, not a global no-go for general eta, metric,
Hopf-fiber, L2, chi or sigma dependence. A multi-guess `solve_bvp` scan found
no distinct radial branch, but that exploratory observation is not used as a
proof.

## Resonance and normal form

The exact round-S7 scalar frequency relation `omega_10=2 omega_4` remains.
The required sigma `10-4-4` cubic coefficient is exactly zero at `sigma=0`
by the retained Z2 symmetry. Frequency commensurability therefore does not
produce a three-wave interaction. The conformal radial normal form has no
quadratic or cubic term and a positive quartic term, so it supplies saturation
at the seed rather than a new phase-locked multimode state.

No surviving action-derived multimode tensor, amplitude equations,
phase-locked state or `ENERGY_GEOMETRY_INTERFERENCE_PATTERN` is derived.

## State and protected-band verdict

No nonlinear localized stationary or relative-periodic solution has yet been
derived. Consequently all of the following remain undefined rather than
zero:

- encapsulation localization diagnostic and Hamiltonian gap;
- physical reduced Hessian or monodromy about an encapsulated state;
- isolated spectral interval and gap;
- Riesz projector, rank, rank constancy and smoothness;
- real-to-complex promotion and `E_enc`;
- internal connection, holonomy and characteristic classes;
- L2 overlap.

Emergent-color and Dirac-emergence eligibility are false at this gate because
the prerequisite bundle does not exist.

The campaign's A--E list has no scientifically valid terminal choice at this
intermediate theorem. Outcomes A--C require a derived state, Outcome D
requires a global static no-go, and Outcome E requires a retained-action
no-go. None has been proved. Therefore:

```text
PATH_A_STATUS = OPEN_NO_A_TO_E_TERMINAL_VERDICT_SCIENTIFICALLY_JUSTIFIED
ENCAPSULATED_STATE_DERIVED = FALSE
PROTECTED_INTERNAL_SPECTRAL_BAND_DERIVED = FALSE
SMOOTH_INTERNAL_MODE_BUNDLE_DERIVED = FALSE

FULL_BHSM_COMPLETE = FALSE
MARK_III = NOT_REACHED
PHYSICAL_EXECUTION_BLOCKED = TRUE
USB_SYNCHRONIZATION_ELIGIBLE = FALSE
```

Path B is not activated because Outcome E is not proved.

## Hindsight 20/20

### Validated

- Compact full-action scaling does not kill a stationary degree-one state.
- Every nonconformal equivariant radial mode of the exact seed is positive.
- The unique conformal Hessian zero is lifted by a positive exact quartic.

### Invalidated

- The homogeneous identity seed as an encapsulated state.
- A nearby equivariant radial encapsulated branch from that seed.
- Frequency commensurability alone as phase locking.

### Reclassified

- The eta identity ratio is `5/4`; gravity and compact scale terms complete
  the full virial identity.
- The conformal Hessian zero is a quartically stable direction, not an
  instability.

### Open

Exactly one next irreducible object:

`ACTION_OWNED_NONHOMOGENEOUS_DEGREE_ONE_M8_EINSTEIN_ETA_CHI_SIGMA_COMMON_DOMAIN_BOUNDARY_VALUE_PROBLEM_WITH_LOCALIZATION_AND_CONSTRAINT_CONVERGENCE`

Frozen predictions and flavor/CKM provenance gates are unchanged. USB is
untouched.
