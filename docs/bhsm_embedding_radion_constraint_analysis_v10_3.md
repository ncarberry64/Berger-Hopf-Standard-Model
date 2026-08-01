# BHSM v10.3 Embedding and Radion Constraint Analysis

## Embedding candidate

For an embedding `X`,

\[
h_{\mu\nu}=G_{AB}(X)e^A_\mu e^B_\nu,
\qquad e^A_\mu=\partial_\mu X^A.
\]

Tangential variations are M4 reparametrizations. A formal normal variation of
an induced intrinsic action gives

\[
\mathcal E_I=T_{(4)}^{\mu\nu}K^I_{\mu\nu}
+\text{bulk and matcher reactions}.
\]

The current action does not vary `X`, so it supplies no conjugate momentum,
embedding constraint algebra, or shape equation. Intrinsic M4 matter
distinguishes a localized stratum but does not automatically select whether
that stratum is direct codimension four, a lifted codimension-one seam, or a
smooth parent defect.

The v6.27 theorem remains authoritative: for the M5 scalar-wall fold problem,
the complete momentum constraint fixes the endpoint response and the normal
support residual vanishes through `O(D^2 q)`. A new B1 embedding is not needed
for that problem. This special theorem is not promoted to an all-sector
nonlinear M4-to-M8 embedding theorem.

Verdict:
`BHSM_SEAM_EMBEDDING_NOT_IN_CURRENT_CONFIGURATION_SPACE_AND_CODIMENSION_CHOICE_NOT_UNIQUE`.

## Radion candidate

For a base dimension `d` and fiber dimension `n`, the Einstein-frame
breathing coefficient is

\[
C_\beta=\frac{n(n+d-2)}{d-2}.
\]

At `d=5,n=3`, `C_beta=6`; the canonical field is
`phi_beta=sqrt(6 kappa5) beta`. The internal-curvature exponent is `-4`.
Thus the local Hopf breathing field is not pure gauge within the invariant
bundle-metric sector and has healthy kinetic sign for positive Einstein
coefficient.

The complete source

\[
J_\beta(x)=-\frac{\delta S_{\rm total}}{\delta\beta(x)}
\]

is nevertheless unavailable. M8 fields contribute through their vertical
metric and fiber-volume dependence, but independently owned intrinsic M4
matter has no completed pullback; the v7.3 mixed matter/radion blocks vanish.

Verdict:
`BHSM_LOCALIZED_HOPF_RADION_IS_AN_EXISTING_METRIC_DEGREE_BUT_NOT_A_COMPLETE_STRATIFIED_ACTION_VARIABLE`.

## Coupled invariant

Under a radial diffeomorphism,

\[
\delta\beta\mapsto\delta\beta-\beta_0'\xi,
\qquad
\psi\mapsto\psi+\xi,
\]

so `q_env=delta beta+beta_0' psi` is invariant. On the present homogeneous
background `beta_0'=0`, and `psi` is absent; the combination reduces to the
radion perturbation and does not join the inequivalent embedding domains.

The earlier fold `q` is a different normalized scalar-wall Jacobi amplitude.
Its conditional kinetic norm is positive, but it is not renamed as depth.
