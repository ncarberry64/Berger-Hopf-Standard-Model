# BHSM v14.30 full Hopf-preimage effective-action proof audit

## Common domain and measure

Define

\[
\widetilde C_\eta=\pi_{85}^{-1}(C_5)\subset M_8,
\quad
\widetilde\Sigma=\pi_{85}^{-1}(M_4),
\quad
\Pi=r_{54}\circ\pi_{85}:\widetilde C_\eta\to M_4.
\]

Their dimensions are eight and seven. The physical bundle pulls back to
\(\Pi^*P_{\rm color}\), and
\(\Pi^*P_{\rm color}\times_{SU(3)}G_2/SU(3)\) is a valid associated bundle.
The pulled physical connection is globally covariant on that bundle and is not
the Berry connection.

On the v7.1 bundle-like round branch,

\[
d\mu_8=d\mu_F\cos^3\rho\,ds\,d\mu_4,
\qquad
\int_Fd\mu_F=16\pi^2a_F^3.
\]

Connection cross terms cancel from the determinant in an adapted coframe but
remain in horizontal covariant derivatives. This is an exact conditional
measure theorem, not a product-space claim.

## Algebraic branching and bundle-provenance obstruction

The retained eta fiber is the unit sphere in an eight-real-dimensional
triality-spinor bundle, hence \(S^7\), with seven tangent fluctuations. The
v14.29 candidate field has fiber \(G_2/SU(3)=S^6\), with six tangent
fluctuations. The v6.2 architecture already proves the relevant algebraic
branching:

\[
\mathbf7_{\mathbb R}=\mathbf1_{\mathbb R}\oplus\mathbf3\oplus\bar{\mathbf3},
\qquad
\mathbf8=\mathbf1\oplus\mathbf1\oplus\mathbf3\oplus\bar{\mathbf3}.
\]

The obstruction is therefore not the absence of an \(SU(3)\) representation.
The retained action does not identify the singlet with an eliminable wall
mode, select the branching as the physical color reduction globally, or
identify its transition cocycle with the independent physical color bundle.
The required local maps must obey

\[
\Phi_jh^{\eta}_{ij}=g^{\rm color}_{ij}\Phi_i.
\]

No such \(\Phi\) occurs in the action. Moreover the existing projector
rank-three bundle has \(c_2=0\), so it cannot be isomorphic to every retained
physical color sector. Pulling both bundles to the full preimage does not create
the missing morphism.

Consequently \(D^{\Pi^*A}\eta_8\) is not defined for the retained eta field.
Writing it would add the very cross-stratum representation being tested.

## Parent Hessian

At a covariantly constant, topologically trivial background with
\(X_0=0\) and \(\Lambda_{\eta,0}=0\), the Euclidean tangent Hessian is

\[
H_\eta=w\kappa_1P_T
(-\Delta_{\rm horizontal}-\Delta_{\rm normal}-\Delta_{\rm fiber})P_T
\]

on seven tangent modes. The \(X^4\) term begins at eighth fluctuation order.
For a nonconstant degree-one background,

\[
\delta^2F=F'(X_0)\delta^2X+\frac32X_0^2(\delta X)^2,
\]

so the \(p=8\) term changes the principal/background tensor. That background
has not been solved on \(\widetilde C_\eta\); v13.1 is a different flat
\(\mathbb R^7\) reduction. No self-adjoint full-cap domain is selected.

## Effective action result

The quadratic scalar DtN and Schur theorems are exact and expose the correct
variational correction. They cannot be promoted to

\[
S_{\rm eff}=\operatorname{Crit}_{\gamma\eta=\varphi}S_{\eta,8}^A
\]

because \(S_{\eta,8}^A\) itself is undefined under the retained bundle
ontology, and the degree-one critical point/domain are absent. The nonlinear
canonical momentum and physical color current therefore cannot be derived.

## Ledger

- Full-preimage diagram: `VALIDATED`.
- Pullback color bundle and connection: `VALIDATED` as independent geometry.
- Physical connection acting on retained eta: `INVALIDATED` under current
  action data.
- Peter--Weyl scalar multiplets: `VALIDATED`.
- Triality-spinor eta spectrum: `OPEN`.
- Round-branch measure: `VALIDATED_CONDITIONALLY`.
- Constant trivial-background Hessian: `VALIDATED_CONDITIONALLY`.
- Degree-one parent Hessian: `OPEN`.
- Quadratic proxy DtN/Schur complement: `VALIDATED_CONDITIONALLY`.
- Nonlinear physical effective action: `OPEN`.

## Full-recall correction

The v6.2 triality branching, v8 Hopf tower, v12 conditional rotation/holonomy
responses, v13--v14 eta-knot polarization, v14.19 zero-mode localization, and
v14.22 two-sided chiral architecture jointly lay out nearly the whole route.
They do not supply the one commuting bundle square or the full-preimage
stationary background. See
`docs/BHSM_FULL_RECALL_PATH_COMPOSITION_AUDIT_v14_30.md`.

The first missing object is

```text
ACTION_OWNED_TRIALITY_THREE_ANTITHREE_TO_PHYSICAL_COLOR_BUNDLE_IDENTIFICATION_WITH_DEGREE_ONE_FULL_HOPF_PREIMAGE_STATIONARY_BACKGROUND_AND_SELF_ADJOINT_CAP_DOMAIN
```
