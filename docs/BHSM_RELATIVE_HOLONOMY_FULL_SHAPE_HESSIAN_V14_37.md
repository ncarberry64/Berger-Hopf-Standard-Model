# BHSM v14.37 — Relative-Holonomy and Full-Shape Hessian Audit

## Primary verdict

`BHSM_V12_Z6_RELATIVE_HOLONOMY_IS_AN_ORIENTATION_CONSTRAINT_NOT_A_QUADRATIC_BIFURCATION_SOURCE_AND_THE_V13_1_DEGREE_ONE_FULL_SHAPE_SURROGATE_HAS_NO_NEGATIVE_MODE_IN_THE_TESTED_ELL_SECTORS`

## Secondary verdict

`A_JOINT_ETA_ATTACHMENT_BIFURCATION_REQUIRES_AN_ACTION_OWNED_MIXED_HESSIAN_BLOCK_WHOSE_NORMALIZED_SINGULAR_VALUE_REACHES_ONE`

## Exact next object

`ACTION_OWNED_LAMBDA85_OR_SPIN4_MIXED_SECOND_VARIATION_BETWEEN_FULL_PREIMAGE_ETA_SHAPE_MODES_AND_UP_DOWN_ATTACHMENT_MODES_WITH_HOPF_RESOLVED_ELL_P_CHANNELS_COMPACT_CAP_DOMAIN_AND_ZERO_CROSSING_TEST`

---

## 1. Question resolved

v14.36 proved that the isometry-generated phase Hessian of the foundational
Path B eta action is nonnegative. The next question was whether the recovered
v12 sector-relative `Z6` holonomy supplies the signed term needed to make a
flavor channel cross zero.

The answer is **no at quadratic order**.

The v12 holonomy can orient an already nonzero bridge and make the combined
up/down response CP odd. It does not generate the bridge amplitude, and it does
not supply a negative eta curvature around the zero-amplitude branch.

The audit also extends the v13.1 stability calculation beyond radial variations
to all three standard tangent sectors of the round `R7 -> S7` hedgehog:

1. scalar-polar modes;
2. coexact transverse-vector modes;
3. coupled scalar-polar and exact-vector modes.

No negative mode is found in the tested angular sectors.

---

## 2. Why the isolated v12 phases do not change the Hessian spectrum

For one tridiagonal family response, write

\[
H_f(\phi)=
\begin{pmatrix}
 d_{f0} & \beta_f e^{i\phi_{f,01}} & 0\\
 \beta_f e^{-i\phi_{f,01}} & d_{f1} &
 \kappa_f e^{i\phi_{f,12}}\\
 0 & \kappa_f e^{-i\phi_{f,12}} & d_{f2}
\end{pmatrix}.
\]

Define

\[
U_f=
\operatorname{diag}
\left(1,e^{i\phi_{f,01}},
 e^{i(\phi_{f,01}+\phi_{f,12})}\right).
\]

Then

\[
\boxed{H_f(\phi)=U_f^\dagger H_f(0)U_f.}
\]

Therefore the isolated eigenvalues are phase independent. The physical phase is
only the cross-sector loop

\[
\Phi_{ud}
=
(\phi_{d,01}+\phi_{d,12})
-(\phi_{u,01}+\phi_{u,12}).
\]

The recovered value `pi/3` can distinguish the relative orientation of the two
response bases, but it cannot make either isolated Hessian negative.

A flat holonomy gives the same conclusion. With twisted boundary condition

\[
\varphi(s+L)=e^{i\delta}\varphi(s),
\]

its covariant-Laplacian spectrum is

\[
\boxed{
\lambda_n=\left(\frac{2\pi n+\delta}{L}\right)^2\ge0.
}
\]

A flat phase twist shifts momenta but does not create a tachyonic quadratic
term.

---

## 3. `Z6` fixes orientation only after an amplitude exists

For a unit-charge complex order parameter

\[
z=\rho e^{i\Phi},
\]

the lowest local `Z6` anisotropy is

\[
V_6(z)=c(z^6+\bar z^6)
=2c\rho^6\cos(6\Phi).
\]

At the symmetric branch `rho=0`,

\[
\boxed{
\operatorname{Hess}_{z=0}V_6=0.
}
\]

Consequently the `Z6` term cannot turn on the order-parameter amplitude at a
quadratic bifurcation. It becomes relevant only after another action term has
created a nonzero bridge or deformation amplitude. It can then select among
six orientations, including a CP-conjugate pair.

This separates two physical jobs:

- **amplitude creation:** requires a signed mixed Hessian or another instability;
- **phase orientation:** may be supplied by the relative `Z6` holonomy.

---

## 4. Complete tangent Jacobi form on the v13.1 surrogate

For

\[
S_\eta=\int d\mu\,w F(X),
\qquad
F(X)=\frac{\kappa_1}{2}X+\frac18X^4,
\qquad
X=|d\eta|^2,
\]

the sphere-target second variation around a stationary map is

\[
\boxed{
Q[V]=\int d\mu\,w\left\{
2F'(X)\left(
|\nabla V|^2-
\langle R(V,d\eta_i)d\eta_i,V\rangle
\right)
+4F''(X)
\left(\sum_i\langle\nabla_iV,d\eta_i\rangle\right)^2
\right\}.
}
\]

The degree-one hedgehog is

\[
\eta=(\cos f,\sin f\,n),
\qquad n\in S^6.
\]

Use logarithmic radius `x=log r` and define

\[
Y=f_x^2+6\sin^2f,
\qquad
X=e^{-2x}Y,
\]

\[
A=e^{5x}(\kappa_1+X^3),
\qquad
D=6e^{-x}Y^2,
\qquad
M=e^{7x}(\kappa_1+X^3),
\]

\[
\Lambda_\ell=\ell(\ell+5).
\]

### 4.1 Scalar-polar sector

For

\[
V=u(x)Y_\ell e_f,
\]

the exact radial quadratic form is

\[
\boxed{
Q_P=\int dx\left\{
A\left[u_x^2+(\Lambda_\ell+6\cos2f)u^2\right]
+D\left[f_xu_x+6\sin f\cos f\,u\right]^2
\right\}.
}
\]

### 4.2 Coexact transverse-vector sector

For a divergence-free vector harmonic,

\[
\boxed{
Q_T=\int dx\,A\left[
v_x^2+
(\Lambda_\ell-6\sin^2f-f_x^2)v^2
\right].
}
\]

The `ell=1` coexact sector contains the target-space stabilizer rotation and
must converge toward a symmetry zero mode.

### 4.3 Coupled polar/exact-vector sector

For

\[
V=uY_\ell e_f+
 v\frac{\nabla Y_\ell}{\sqrt{\Lambda_\ell}},
\]

the coupled form is

\[
\begin{aligned}
Q_E=\int dx\{&
A[u_x^2+v_x^2
 +(\Lambda_\ell+6\cos2f)u^2\\
&+(\Lambda_\ell-4-6\sin^2f-f_x^2)v^2
 -4\cos f\sqrt{\Lambda_\ell}\,uv]\\
&+D[f_xu_x+6\sin f\cos f\,u
 -\sin f\sqrt{\Lambda_\ell}v]^2
\}.
\end{aligned}
\]

The generalized-eigenvalue norm is

\[
\|V\|^2=\int dx\,M(x)(u^2+v^2).
\]

---

## 5. Numerical finite-box spectrum

Reference interval:

\[
x\in[-7,5],
\]

with 240 finite-element nodes and Dirichlet endpoint conditions.

| `ell` | polar lowest | coexact lowest | polar/exact lowest |
|---:|---:|---:|---:|
| 2 | 0.003585838472 | 0.003020455154 | 0.002202487352 |
| 4 | 0.005480576013 | 0.004983674562 | 0.003947861025 |
| 6 | 0.007826900790 | 0.007372141502 | 0.006125229600 |
| 8 | 0.010601057484 | 0.010174315943 | 0.008721313939 |
| 10 | 0.013788389878 | 0.013380915966 | 0.011726978214 |

No negative finite-box mode is found in these sectors.

The `ell=1` coexact symmetry mode converges toward zero as the mesh is refined:

| nodes | lowest eigenvalue |
|---:|---:|
| 160 | 0.001341918494 |
| 240 | 0.000594247469 |
| 320 | 0.000333589456 |

This is an internal correctness check on the angular decomposition.

Expanding the noncompact radial box moves the lowest positive modes toward zero
from above. Thus the surrogate has a continuum threshold rather than a derived
positive physical mass gap.

---

## 6. The only surviving quadratic route

Let `H_eta` be the nonnegative eta-shape Hessian and `H_A` the attachment or
relative-rotation Hessian. A joint quadratic operator has the form

\[
\mathcal H=
\begin{pmatrix}
H_\eta & B\\
B^\dagger & H_A
\end{pmatrix}.
\]

For one eta and one attachment mode,

\[
\mathcal H_2=
\begin{pmatrix}
\lambda_\eta &-b e^{i\delta}\\
-b e^{-i\delta}&\lambda_A
\end{pmatrix}.
\]

Its eigenvalues are

\[
\lambda_\pm=
\frac{\lambda_\eta+\lambda_A}{2}
\pm
\sqrt{
\left(\frac{\lambda_\eta-\lambda_A}{2}\right)^2+|b|^2
}.
\]

The zero-crossing threshold is

\[
\boxed{|b|_{\rm crit}=\sqrt{\lambda_\eta\lambda_A}.}
\]

The relative phase `delta` does not change the threshold. It fixes the complex
orientation of the unstable eigenvector after the bridge magnitude reaches the
threshold.

In the multimode problem the exact criterion is

\[
\boxed{
\sigma_{\max}
\left(
H_\eta^{-1/2}BH_A^{-1/2}
\right)=1.
}
\]

Equivalently, integrating out the stable attachment block gives

\[
H_{\rm eff}
=
H_\eta-BH_A^{-1}B^\dagger.
\]

This is the precise calculation that can turn the bifurcation on.

---

## 7. Action-ownership boundary

The v12 work already identifies the correct possible sources of `B`:

- the projected second variation of the reciprocal `Lambda85` attachment;
- the matched Spin(4) core–boundary tetrad and relative spin connection;
- normalized common-domain family tangent embeddings.

But it does not calculate the mixed block. The historical `beta`, `kappa`, and
`pi/3` values remain mechanism diagnostics rather than coefficients of the
current Path B/full-preimage Hessian.

The next derivation must supply:

1. the compact full-preimage eta background and self-adjoint cap domain;
2. Hopf-resolved `(ell,p)` eta modes;
3. attachment/Spin(4) fluctuation modes on the same domain;
4. the mixed second variation `B` with its action measure;
5. the normalized singular-value crossing test;
6. only after a crossing, nonlinear branch continuation and `Z6` phase locking.

---

## 8. Hindsight 20/20 ledger

### Validated

- The v12 sector-relative phase is a genuine cross-sector invariant.
- It preserves each isolated response spectrum.
- A flat holonomy has a nonnegative twisted-Laplacian spectrum.
- The lowest local `Z6` anisotropy has zero Hessian at zero amplitude.
- The complete polar, coexact, and polar/exact Jacobi forms can be evaluated on
  the v13.1 surrogate.
- No negative mode appears in the tested `ell=2,4,6,8,10` sectors.
- A mixed Hessian block has an exact zero-crossing criterion.

### Invalidated

- Treating `delta_BH=pi/3` as an automatically negative quadratic potential.
- Treating a phase constraint as the source of a nonzero bridge amplitude.
- Claiming that the pure Path B eta action spontaneously selects the flavor
  branch.
- Promoting the finite-box surrogate values to physical mass gaps.

### Reclassified

- The `Z6` holonomy is a branch-orientation mechanism, not an amplitude-creation
  mechanism.
- v12.1 differential rotation and v12.2 reciprocal attachment are candidate
  providers of the **mixed Hessian block**, not replacements for the eta action.
- The v13.1 profile is a controlled flat-`R7` surrogate, not the compact physical
  full-preimage solution.

### Open

- Action-owned `Lambda85` or Spin(4) mixed second variation.
- Compact cap background and self-adjoint domain.
- Hopf-resolved `(ell,p)` full-shape spectrum.
- A certified zero crossing.
- Nonlinear bifurcating branch, phase locking, CKM and CP.
- Physical scale, masses, RG transport and full BHSM completion.

---

## 9. Completion status

- Path B phase Hessian: nonnegative.
- Full non-isometric v13.1 surrogate: no negative tested mode.
- v12 holonomy as direct quadratic source: failed.
- Mixed eta–attachment bifurcation: open and sharply defined.
- Physical CKM/CP outputs: withheld.
- Frozen predictions: unchanged.
- BHSM complete: no.
- USB: untouched.
