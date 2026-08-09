# BHSM v14.38 — Lambda85–eta Mixed-Hessian and Zero-Crossing Audit

## Primary verdict

`BHSM_V11_3_HOMOGENEOUS_LAMBDA85_ATTACHMENT_HAS_ZERO_MIXED_HESSIAN_WITH_ALL_NONTRIVIAL_HOPF_FLAVOR_CHANNELS_AND_CANNOT_TRIGGER_THE_V14_35_BIFURCATION`

## Secondary verdict

`THE_CANONICAL_C3_PROJECTION_OF_THE_SELECTED_ATTACHMENT_BRANCH_IS_FAMILY_DIAGONAL_AND_THE_SPIN4_ALTERNATIVE_REMAINS_UNATTACHED_TO_THE_ACTION`

## 1. Exact action scope

The v11.3 reciprocal compatibility term is

\[
S_{\rm attach}
=
\int_{M_5}d\mu_5\,
\left\langle
\Lambda_{85},
\upsilon^{-1/2}I_W-\upsilon^{1/2}I_C
\right\rangle,
\]

with

\[
I_C=Q_H(G_8),\qquad I_W=g_5.
\]

The action contains no direct eta field. Its available common-domain spectral reduction uses the three homogeneous collective coordinates

\[
(q_C,q_D,q_W)
\]

with constraint

\[
-q_C+q_D+q_W=0.
\]

Because the action is linear in \(\Lambda_{85}\),

\[
\frac{\delta^2S_{\rm attach}}{\delta\Lambda_{85}^2}=0.
\]

Thus \(\Lambda_{85}\) is a constraint multiplier, not a propagating attachment field. The unreduced quadratic operator has KKT saddle form

\[
\mathcal K=
\begin{pmatrix}
H_{\rm metric}&C^*\\
C&0
\end{pmatrix}.
\]

A physical spectrum exists only after restricting the metric/incidence fluctuations to \(\ker C\) and removing the multiplier.

The physical tangent Gram and Hessian are

\[
G_\parallel=
\begin{pmatrix}
1&1/2\\
1/2&17/4
\end{pmatrix},
\]

\[
H_\parallel(h_C)=
\begin{pmatrix}
h_C+3/4&h_C+7/8\\
h_C+7/8&h_C+7/4
\end{pmatrix}.
\]

For the stored degree-one representative,

\[
h_C=0.181391690148362,
\qquad
\mu_-=0.1633821478999081549.
\]

Both tangent branches are positive.

## 2. Exact harmonic selection rule

The available attachment coordinates transform in the trivial spatial/Hopf character:

\[
(\ell,p)_{\rm attach}=(0,0).
\]

The flavor texture channels are

\[
(2,2),\ (4,4),\ (6,6),\ (8,8),\ (10,8).
\]

Orthogonality on the compact angular/fiber orbit gives

\[
\boxed{
\langle A_{(0,0)},\eta_{(\ell,p)}\rangle=0
\quad\text{for}\quad(\ell,p)\ne(0,0).
}
\]

Consequently, on the current action-owned reduction,

\[
\boxed{
B_{\eta A}^{(\ell,p)}=0
}
\]

for every requested flavor channel.

This result has two independent origins:

1. the reciprocal attachment term has no direct eta dependence;
2. the only retained attachment modes are homogeneous singlets, while the flavor seeds are nontrivial harmonics.

A uniform metric/attachment variation may mix with the eta breathing sector, but not with these nontrivial flavor sectors.

## 3. Zero-crossing test

The exact bifurcation criterion is

\[
\sigma_{\max}
\left(
H_\eta^{-1/2}B_{\eta A}H_A^{-1/2}
\right)=1.
\]

For the current reduction,

\[
B_{\eta A}=0,
\]

therefore

\[
\boxed{\sigma_{\max}=0<1.}
\]

The bifurcation remains off.

Using the v14.37 reference-box eta curvatures and the lower attachment root, a hypothetical matched attachment mode would require the following mixed magnitudes:

| Channel | Reference eta curvature | Critical mixed magnitude |
|---|---:|---:|
| \((2,2)\) | 0.002202487352 | 0.018969636641 |
| \((4,4)\) | 0.003947861025 | 0.025397047346 |
| \((6,6)\) | 0.006125229600 | 0.031634682999 |
| \((8,8)\) | 0.008721313939 | 0.037747940392 |
| \((10,8)\) | 0.011726978214 | 0.043771896109 |

These are diagnostic reference-normalization thresholds, not physical compact-cap values.

## 4. Canonical C3 projection

The selected lower attachment carrier can be projected onto the exact C3 commutant:

\[
H_{\rm fam}^{(-)}
=
\frac13\sum_{n=0}^2C^nR_-C^{-n}
=
\sum_{k=0}^2\ell_kP_k.
\]

Because

\[
[H_{\rm fam}^{(-)},C]=0,
\]

it is diagonal in the exact family projector basis. Therefore

\[
\boxed{
P_rH_{\rm fam}^{(-)}P_s=0\quad(r\ne s).
}
\]

The canonical projection produces positive family stiffnesses, but it does not derive the historical nearest-neighbor chain coefficients

\[
\beta_f,\qquad\kappa_f.
\]

The reciprocal phase twist also retains the previously identified twofold degeneracy.

## 5. Why the unreduced Lambda85 route remains open

The full local Lambda85 tensor functional is not proved to contain only homogeneous modes. A nonhomogeneous route remains logically possible, but it currently lacks:

- a constraint-reduced kinetic or elliptic operator for nonhomogeneous metric/incidence modes;
- elimination of the algebraic Lambda85 multiplier on each harmonic block;
- a self-adjoint cap domain;
- a matched \((\ell,p)\) spectral decomposition;
- an explicit pullback of the Path B eta stress into \(Q_H(G_8)\) or \(g_5\);
- a normalized mixed second variation.

It would be incorrect to infer a nonzero mixed block from the homogeneous KKT matrix.

## 6. Spin(4) route

The v12.1 Spin(4) construction identifies representation channels capable of connecting the frozen family slots. It still lacks the matched parent-metric-to-tetrad/spin-connection pullback and action-normalized reduced matrix elements. Thus its mixed Hessian is not zero by theorem; it is not yet defined by the action.

## Hindsight 20/20

### Validated

- The v11.3 homogeneous KKT attachment branch is positive.
- All requested flavor channels are orthogonal to the homogeneous attachment character.
- The normalized mixed singular value is exactly zero on the available reduction.
- The canonical C3 projection is family diagonal.

### Invalidated

- Using the existing homogeneous Lambda85 KKT branch as the source of the v14.35 nonaxisymmetric bifurcation.
- Treating the coordinate-basis circulant entries as action-derived mixing among the exact C3 family projectors.
- Promoting the v12.1 Spin(4) representation witness to an action-owned mixed block.

### Open

- Nonhomogeneous Lambda85 tensor modes with a matched \((\ell,p)\) operator.
- Path B eta-stress pullback across the stratified metric incidences.
- Compact self-adjoint cap domain.
- Spin(4) tetrad and spin-connection pullback.
- A nonzero normalized singular value and nonlinear flavor branch.

## Exact next object

`ACTION_OWNED_NONHOMOGENEOUS_LAMBDA85_OR_SPIN4_ATTACHMENT_MODE_WITH_THE_SAME_ELL_P_CHARACTERS_AS_THE_ETA_FLAVOR_TEXTURE_AND_A_NONZERO_MIXED_HESSIAN_ON_A_COMPACT_SELF_ADJOINT_FULL_PREIMAGE_CAP`
