# BHSM v6.22.0 M4 X-metric tangent and fold-Schur audit

Primary tangent verdict:

`BHSM_M4_X_METRIC_TANGENT_BLOCKED_BY_X_TO_R4_NORMALIZATION_CONFLICT`.

Schur verdict:

`BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_X_TO_R4_NORMALIZATION_CONFLICT`.

Kinetic verdict:

`BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_X_TO_R4_NORMALIZATION_CONFLICT`.

This is the earliest-stop result of the v6.22 critical-path sprint. It does
not introduce a metric family, choose a Green prescription, manufacture a
pseudoinverse, or assign a value to the missing gravitational Schur term.

## 1. Frozen action and inherited results

The audit preserves the normalized representative

```text
q5 = kappa_1 = Z5 = 1,
C_partial/kappa_1 = 1/2,
X_c = 2,
N_0 = pi/4,
a_0(t) = sqrt(2) sin(pi t/4).
```

The action remains the two reflected P1 caps, their capwise GHY
completions, one common intrinsic B1 action, the exact metric matcher, and
the bulk scalar action. No action or boundary primitive is added.

The v6.18 threading response is unchanged:

```text
Pi_perp S_Sigma
  = -tau (pi chi_1/16) Pi_perp q,
C_Sigma = 0.
```

The dynamic threading domain remains nonempty, its unresolved trace count is
zero, and no explicit energy threshold is required.

The v6.20 radial measure and principal lapse--Weyl block remain

```text
dmu_rad = pi sin^4(pi t/4) dt,

L_Apsi^crit
  = (6 kappa_1/a_0^2) [[0,1],[1,2]].
```

Nothing in this sprint reinterprets the saddle determinant as a ghost.

## 2. Exact repository definition of X

The relevant symbol is the M4 curvature parameter `X`; unrelated embedding
maps also named `X` and ordinary coordinates `x` are excluded.

The earliest Lorentzian M4 definition is

```text
X = H^2 + a^-2,
A = N^-1 dot(H) + H^2,
R4 = 6(A+X).
```

Sources:

- `src/bhsm/interface/intrinsic_m4_junction_background.py:264`;
- `src/bhsm/interface/m5_m4_boundary_reduction.py:90-96`;
- `docs/bhsm_parent_m5_to_m4_boundary_reduction_v6_1_1.md:74-89`.

The scalar-wall action then declares

```text
signature = (-,+,+,+,+),
Ric_mu_nu(h) = 3 X h_mu_nu.
```

Source:
`src/bhsm/interface/scalar_wall_junction_audit.py:268-275`.

Therefore the maximally symmetric M4 factor in that frozen action obeys

```text
R4 = 12 X.
```

`X` is not stored as an independent local scalar field `X(x)`. It is solved
with the homogeneous cap geometry and becomes the Puiseux branch coordinate

```text
X = 2 + tau chi_1 r + O(r^2).
```

Promoting `r` to a slow field `q(x)` does not by itself supply a local
metric solution `hbar[X(x)]`.

## 3. Branch inventory at X=2

The repository stores two distinct exact critical M4 branches.

### Maximally symmetric de Sitter-4 branch

For the retained nonstatic junction branch,

```text
A = X,
Ric(h) = 3 X h,
R4 = 12 X,
dR4/dX = 12.
```

A homogeneous representative is

```text
ds4^2
  = -du^2
    + X^-1 cosh^2(sqrt(X)(u-u0)) dOmega3^2.
```

This is the branch used in the scalar-wall reduced action and in the
analytic maximally symmetric M4 volume regulator
`Vol4(X)=Vol4(1)X^-2`.

### Critical static R x S3 branch

At the critical coefficient the separate exact branch has

```text
H = A = 0,
a = X^-1/2,
R4 = 6 X,
dR4/dX = 6.
```

A homogeneous representative is

```text
ds4^2 = -du^2 + X^-1 dOmega3^2.
```

The intrinsic-junction doctrine explicitly states that this branch and the
critical de Sitter bounce are distinct even though both have `X=2q5`.

Thus `X` is an FRW invariant, a homogeneous family parameter, and an on-shell
branch coordinate. It is not universally equal to `R4`, `R4/6`, or `R4/12`.

## 4. Which branch enters v6.20

The v6.20 action density inherits the maximally symmetric Einstein M4
convention and the analytic maximally symmetric volume regulator. This
selects the de Sitter-type action density rather than the separate static
critical branch.

It does not, however, store:

- a coordinate-level covariant family `hbar_mu_nu[X]`;
- the regulated M4 manifold;
- its temporal or spatial boundary;
- an M4 tensor domain;
- boundary-preserving diffeomorphisms;
- an adjoint domain.

Consequently the repository contains an ordinary homogeneous ansatz
derivative in principle, but no local field-valued right inverse and no
declared combination of the two.

## 5. Scalar-curvature variation convention

Use a covariant metric variation

```text
k_mu_nu = delta h_mu_nu,
delta h^mu_nu = -k^mu_nu.
```

The connection variation is

```text
delta Gamma^rho_mu_nu
  = 1/2 h^rho_lambda
    (nabla_mu k^lambda_nu
     +nabla_nu k^lambda_mu
     -nabla^lambda k_mu_nu).
```

Contracting the Ricci variation and including the inverse-metric variation
gives

```text
DR_h[k]
  = nabla_mu nabla_nu k^mu_nu
    - Box tr_h(k)
    - Ric_mu_nu k^mu_nu.
```

This agrees with the repository curvature convention
`R4=6(A+X)` and Lorentzian signature `(-,+,+,+)`.

## 6. Independent checks of DR_h

### Conformal check

For

```text
k_mu_nu = 2 phi h_mu_nu
```

in four dimensions,

```text
div div k = 2 Box phi,
Box tr(k) = 8 Box phi,
Ric:k = 2 R4 phi,
```

so

```text
DR_h[2 phi h] = -6 Box phi - 2 R4 phi.
```

The same result follows by differentiating the exact conformal law

```text
R[e^(2 epsilon phi)h]
  = e^(-2 epsilon phi)
    [R[h]-6 epsilon Box phi+O(epsilon^2)].
```

### Pure-diffeomorphism check

Naturality gives

```text
DR_h[L_xi h] = L_xi R4.
```

It vanishes on either constant-`R4` background for an admissible
boundary-preserving diffeomorphism. This identifies the expected gauge
image but does not define the admissible boundary gauge group.

### Homogeneous-family check

Direct differentiation gives

```text
dR4/dX = 12  (maximally symmetric branch),
dR4/dX = 6   (critical static branch).
```

Neither equals the coefficient stored by the v6.20 target.

## 7. Earliest exact conflict

The frozen scalar-wall action requires

```text
Ric_mu_nu(h)=3X h_mu_nu
  => delta R4 = 12 delta X
```

along its maximally symmetric homogeneous family.

The v6.20 missing-object ledger instead requires

```text
delta R4[T_X] = delta X = tau chi_1 q.
```

Sources:

- action convention:
  `src/bhsm/interface/scalar_wall_junction_audit.py:270`;
- v6.20 target:
  `src/bhsm/interface/critical_lapse_weyl_hessian.py:269-271`.

The residual coefficient is `12-1=11`. It is not removable by a
diffeomorphism or a gauge convention because scalar curvature is a scalar
and the background value is constant.

The separate static branch reinforces the need for an explicit declaration:
there the coefficient would be `6`, not `12` or `1`.

This is the first exact inconsistency, before any inverse or boundary-value
problem:

`BHSM_M4_X_METRIC_TANGENT_BLOCKED_BY_X_TO_R4_NORMALIZATION_CONFLICT`.

## 8. Gauge quotient and kernel firewall

A York/Hodge decomposition on the actual regulated M4 background would be
required:

```text
k = k_TT + L_xi h + k_scalar-longitudinal + k_trace.
```

The scalar-curvature equation cannot determine this decomposition alone. On
the Einstein de Sitter branch, every transverse-traceless tensor obeys

```text
DR_h[k_TT] = 0.
```

The action source and matcher have not been projected onto that kernel, so
the repository has not proved that the TT component is unsourced. Nor has it
specified boundary-preserving vector, conformal-Killing, Killing,
homogeneous, or regulator zero modes.

Therefore no kernel dimension, adjoint-kernel dimension, source projector,
or quotient Green operator is reported.

## 9. Formal adjoint and open domain

Before boundary terms, the formal scalar-to-tensor adjoint is

```text
DR_h^*[f]_mu_nu
  = nabla_mu nabla_nu f
    - h_mu_nu Box f
    - f Ric_mu_nu.
```

The associated boundary current is

```text
n_mu [
  f nabla_nu k^mu_nu
  - f nabla^mu tr(k)
  - (nabla_nu f) k^mu_nu
  + (nabla^mu f) tr(k)
].
```

The analytic M4 volume regulator does not declare a boundary on which this
flux can be evaluated. Hence the actual domain, adjoint domain, Green flux,
and Fredholm compatibility remain undefined.

No retarded, advanced, Euclidean, Dirichlet, Neumann, Robin, or
pseudoinverse prescription is adopted.

## 10. Action insertion stop

Because the tangent normalization fails its homogeneous check, the sprint
does not insert an invented tensor into P1, GHY, B1, or the matcher.

The historical capwise GHY cancellation is preserved. The following new
objects remain undefined:

- tangent contributions to P1 and intrinsic B1 `R4`;
- matcher pullback;
- complete `J_A`, `J_psi`, and `J_E`;
- independent scalar B1 and matcher conditions;
- endpoint and junction conditions;
- complete operator and adjoint domain;
- source orthogonality and compatibility.

This yields

`BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_X_TO_R4_NORMALIZATION_CONFLICT`.

## 11. Frame and double-counting firewall

The inherited Einstein-frame term remains

```text
K_Weyl = 3 chi_1^2(4-pi)^2/(16 pi).
```

Without a normalized local `X`-metric tangent, the sprint cannot determine
whether the response is an independent tensor, an affine shift of the Weyl
variable, a constraint solution, or a background-family derivative. An
explicit quadratic change of variables is therefore unavailable.

No `X` response is added to `K_Weyl`, and no no-double-counting theorem is
claimed.

## 12. Schur and kinetic verdict

The inherited known terms are

```text
K_scalar = 2 integral a0^2 u1^2 d rho >= 2 > 0,
K_Weyl   = 3 chi_1^2(4-pi)^2/(16 pi).
```

But

```text
K_grav,constraint^J = undefined,
k_q^E               = undefined.
```

No numerical solve is launched. Consequently there is no numerical
uncertainty, sign, sheet dependence, or total scalar-sign dependence to
report.

The exact kinetic verdict is

`BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_X_TO_R4_NORMALIZATION_CONFLICT`.

No physical mass, tachyon, nonlinear-stability, global-sheet,
white-hole-dynamics, production, or cosmological claim follows.

## 13. Integrity and next construction target

No measured value, fit, chat-only candidate, new action, primitive, scale,
threshold, tension, or boundary parameter entered.

The exact next construction target is:

1. declare whether the local response variable is `X`, `R4`, or `R4/12`;
2. make the v6.20 tangent normalization agree with
   `Ric(h)=3Xh`;
3. store the covariant maximally symmetric family `hbar[X]` and its regulated
   M4 domain;
4. only then perform the York quotient, TT-source audit, adjoint-domain
   analysis, and action insertion.

Until those repository-level declarations exist, the complete mixed source,
Schur complement, and fold kinetic sign remain active construction targets.
