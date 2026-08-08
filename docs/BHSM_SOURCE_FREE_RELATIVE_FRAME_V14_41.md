# BHSM v14.41 — Source-Free Relative-Frame and Vacuum-Polarization Gate

## Primary verdict

`BHSM_SOURCE_FREE_CLASSICAL_COMPACT_CAP_ADM_ACTION_HAS_ONLY_KILLING_COEXACT_SHIFT_ZERO_MODES_AND_CANNOT_SPONTANEOUSLY_SELECT_THE_L2_L3_RELATIVE_FRAME_BACKGROUND`

## Secondary verdict

`A_COLLECTIVE_FERMION_VACUUM_DETERMINANT_CAN_REOPEN_THE_GATE_ONLY_IF_ITS_RENORMALIZED_COEXACT_STRESS_POLARIZATION_DRIVES_A_PHYSICAL_L2_OR_L3_EIGENVALUE_THROUGH_ZERO`

## 1. Question

v14.40 showed that the presently constructed classical sources do not supply a universal connected `L=2` and `L=3` Spin(4) shift:

- static eta has zero momentum;
- the rigid FR eta rotor is `L=1` only;
- static Wilson insertions have no universal coexact momentum;
- diagonal family occupations have `r=0` only;
- off-diagonal family coherence would be circular if inserted before the action selects it.

The remaining classical possibility was a family-independent nonaxisymmetric **vacuum relative frame** selected by the source-free compact-cap action itself. This report evaluates that possibility exactly.

## 2. Stationary ADM shift functional

Use the stationary ADM decomposition

\[
ds^2=-N^2dt^2+h_{ij}(dx^i+\beta^i dt)(dx^j+\beta^jdt).
\]

For a time-independent spatial metric,

\[
K_{ij}
=-\frac1{2N}
(D_i\beta_j+D_j\beta_i).
\]

On the coexact sector,

\[
D_i\beta^i=0,
\qquad K=0.
\]

The Einstein kinetic block therefore gives

\[
\boxed{
Q[\beta]
=
\frac{\kappa_G}{8}
\int d\mu_h\,N^{-1}
|\mathcal L_\beta h|^2
\ge0.
}
\]

Define the Killing operator

\[
D_K\beta=\mathcal L_\beta h.
\]

The source-free stationary equation is

\[
\boxed{
D_K^*\big(N^{-1}D_K\beta\big)=0.
}
\]

Multiplying by `beta` and using the self-adjoint cap/seam boundary conditions gives

\[
\int d\mu_h\,N^{-1}|D_K\beta|^2=0.
\]

Hence

\[
\boxed{\mathcal L_\beta h=0.}
\]

Every source-free stationary coexact solution is a Killing field compatible with the boundary data. With a nonrotating cap boundary and the common global-rotation quotient, the physical solution is

\[
\boxed{\beta_{\rm rel}=0.}
\]

This is stronger than a numerical positive-Hessian observation. At fixed stationary `h` and `N`, the shift enters through `K_ij`, which is linear in `beta`; the functional is **exactly quadratic**. There is no hidden quartic term that can create a finite-amplitude pitchfork once the non-Killing quadratic spectrum is positive.

## 3. Round compact-cap spectrum

On a round `S^3(R)`, the Hodge-Laplacian eigenvalue on a coexact one-form of level `L=1,2,...` is

\[
\lambda_L^{H}=\frac{(L+1)^2}{R^2}.
\]

Since

\[
\operatorname{Ric}=\frac2{R^2}h,
\]

the shift operator is

\[
\mathcal O_{\rm shift}
=D_K^*D_K
=\Delta_H-2\operatorname{Ric},
\]

and therefore

\[
\boxed{
\lambda_L^{\rm shift}
=
\frac{(L+1)^2-4}{R^2}
=
\frac{(L-1)(L+3)}{R^2}.
}
\]

The relevant values are

\[
\lambda_1^{\rm shift}=0,
\qquad
\lambda_2^{\rm shift}=\frac5{R^2},
\qquad
\lambda_3^{\rm shift}=\frac{12}{R^2}.
\]

`L=1` is the six-dimensional Killing algebra of `S^3`. The two flavor-generating channels are strictly positive:

| Channel | Shift eigenvalue | Classical status |
|---:|---:|---|
| `L=1` | `0` | Killing/global rotation |
| `L=2` | `5/R^2` | strictly positive, off |
| `L=3` | `12/R^2` | strictly positive, off |

The physical cap radius and normalization remain open; their absence does not affect the signs or the no-go.

## 4. Two-cap relative frame

The core and boundary caps contribute a sum of weighted Killing-operator squares. Without a source or rotating boundary datum,

\[
Q_{\rm total}
=Q_{\rm core}[\beta_c]+Q_{\rm wall}[\beta_w]\ge0.
\]

The homogeneous matcher can identify their boundary data but cannot create a negative mode. Each source-free solution is Killing. After quotienting the common global rotation, the relative non-Killing field vanishes.

Thus the classical action does not select the v12.1 `L=2\oplus L=3` differential frame.

## 5. Collective-fermion vacuum determinant

A quantum effective action could alter the quadratic operator:

\[
\Gamma_{\rm eff}[\beta]
=
S_{\rm ADM}[\beta]
-\log\det D_{\rm collective}[\beta]
+\Gamma_{\rm counterterms}.
\]

In the coexact harmonic basis,

\[
\Gamma_{\rm eff}^{(2)}
=
\frac12
\sum_{Lr\epsilon}
\left[
 c_G\lambda_L^{\rm shift}
 +\Pi_{Lr}^{\epsilon,\rm ren}
\right]
|\beta_{Lr}^{\epsilon}|^2.
\]

A bifurcation requires

\[
\boxed{
\min\operatorname{spec}
\left(c_G\mathcal O_{\rm shift}+\Pi_{\rm ren}\right)=0.
}
\]

On the round cap, the normalized thresholds are

\[
\Pi_2^{\rm ren}=-\frac{5c_G}{R^2},
\qquad
\Pi_3^{\rm ren}=-\frac{12c_G}{R^2}.
\]

This is an exact future calculation, not a claim that the polarization has either sign.

BHSM still lacks the objects needed to evaluate it:

1. the normalized Path-B/FR one-knot Hilbert bundle;
2. the collective Weyl/Dirac principal symbol;
3. the compact-cap self-adjoint boundary and seam domain;
4. the matched relative tetrad and spin connection;
5. the vacuum and zero-mode quotient;
6. a diffeomorphism-preserving regulator;
7. the renormalized gravitational counterterm prescription;
8. sector-resolved up/down embeddings and stress-current matrix elements;
9. two independently oriented CP-capable channels.

The live family current remains `I3`. A family-factorized collective operator produces a family-central polarization. A CKM-capable determinant must first receive action-derived inequivalent up/down embeddings; otherwise a vacuum instability would break spatial symmetry without deriving flavor mixing.

## 6. Hindsight 20/20

### Validated

- The stationary source-free coexact ADM functional is a nonnegative weighted Killing-operator square.
- Its kernel consists only of Killing fields compatible with the cap/seam domain.
- The round-cap `L=2` and `L=3` eigenvalues are `5/R^2` and `12/R^2`.
- At fixed stationary geometry, shift dependence is exactly quadratic.
- A collective-fermion determinant has a precise zero-crossing test once its operator and renormalization are owned.

### Invalidated

- A source-free classical `L=2` or `L=3` pitchfork.
- Hidden nonlinear Einstein self-coupling of the stationary shift as an unrecorded negative potential.
- Treating an absolute ADM shift as a physical flavor frame before relative matching and the gauge quotient.

### Reclassified

- The universal relative-frame route is now a **quantum or explicitly sourced** problem, not a classical source-free branch of the current action.
- The collective-fermion determinant is the shortest surviving universal mechanism, but it is not numerically evaluable yet.

### Open

- Collective Dirac action and normalized knot Hilbert bundle.
- Compact self-adjoint cap/seam domain.
- Renormalized coexact stress polarization in `L=2` and `L=3`.
- Matched relative tetrad/spin connection.
- Action-derived up/down response matrices, CKM and CP.

## Exact next object

`ACTION_NORMALIZED_COLLECTIVE_DIRAC_OPERATOR_ON_THE_PATH_B_FR_KNOT_HILBERT_BUNDLE_WITH_COMPACT_CAP_SELF_ADJOINT_DOMAIN_RENORMALIZED_COEXACT_STRESS_POLARIZATION_PI_L_FOR_L2_L3_AND_MATCHED_RELATIVE_TETRAD`

BHSM remains incomplete. Frozen predictions are unchanged. No physical CKM, CP phase, mass, scale, or quantum polarization is emitted.
