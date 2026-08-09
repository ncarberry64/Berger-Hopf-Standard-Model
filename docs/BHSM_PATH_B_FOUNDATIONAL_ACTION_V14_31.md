# BHSM v14.31 — Path B foundational physical action

## Verdict

`BHSM_V14_31_PATH_B_ADOPTS_THE_CANONICAL_G2_EXTENSION_OF_THE_PHYSICAL_COLOR_BUNDLE_AND_THE_COMPOSITE_ETA_SU3_SIGMA_ACTION_AS_FOUNDATIONAL_PHYSICAL_DATA_CLOSING_THE_COLOR_ETA_ACTION_OWNERSHIP_GATE_WITHOUT_ADDITIONAL_VECTOR_FIELDS`

This is an explicit foundational completion of the physical color–eta action. It is not presented as a derivation from the unclosed higher-dimensional `M8` reduction.

## Foundational bundle postulate

Fix the standard embedding `SU(3) -> G2`. For the retained physical color bundle,

\[
P_{\rm color}\to M_4,
\]

define

\[
Q_{G_2}=P_{\rm color}\times_{SU(3)}G_2.
\]

The physical selector is

\[
\eta\in\Gamma(Q_{G_2}/SU(3))
=\Gamma(P_{\rm color}\times_{SU(3)}S^6).
\]

The eta tangent `3/bar3` transition functions are therefore the transition functions of the retained physical color bundle by construction. General retained `c2(P_color)` sectors remain allowed.

## Composite connection and field ontology

Use

\[
\mathcal A[A,\eta]=\iota_*A+\theta[A,\eta],
\qquad
\theta=\Theta_\eta(D_A\eta).
\]

The independent configuration variables are `(A,eta)`. There is no independent `theta` variation. The quadratic field content consists of eight Yang–Mills vector directions and six eta tangent scalar directions. No six additional vector poles are introduced.

A fully independent `G2` connection would instead contain six extra colored vector directions. Pure `G2` Yang–Mills also fails to supply the quadratic eta `p=2` term: around the stabilizer vacuum, `theta=d phi+O(phi^2)` and `d theta=O(phi^2)`, so the curvature action has no leading `(d phi)^2` term. Path B therefore uses ordinary `SU(3)` Yang–Mills plus the eta sigma action, not full independent `G2` Yang–Mills.

## Authoritative physical action

\[
S_{\rm color-\eta}
=S_{\rm YM}[A]
-\int_{M_4}d\mu_h\,w(\sigma)
\left[\frac{\kappa_1}{2}X_\eta+\frac18X_\eta^4\right]
+S_{\rm constraint},
\]

where

\[
X_\eta=h^{\mu\nu}G_{IJ}(\eta)
D_\mu^A\eta^I D_\nu^A\eta^J.
\]

No new continuous coefficient is introduced.

The prior `M8` eta construction is reclassified as a candidate ultraviolet origin and future matching theorem. It is not simultaneously varied as a second physical copy of eta.

## Action-derived source

With

\[
\delta_A S=-\int d\mu_h\,J_a^\mu\delta A_\mu^a,
\]

the intrinsic real-coordinate current is

\[
J_a^\mu=w(\sigma)(\kappa_1+X_\eta^3)
K_{aI}(\eta)D^\mu\eta^I.
\]

The Yang–Mills equation is

\[
\frac1{g_3^2}(D_\nu F^{\nu\mu})_a
=J_{\eta,a}^\mu+J_{{\rm retained},a}^\mu.
\]

Gauge invariance gives

\[
(D_\mu J^\mu)_a-E_{\eta,I}K_a^I=0,
\]

and therefore covariant current conservation on the eta equation of motion.

The exact stabilizer selector and a featureless pure normal wall retain zero tangential color current. Generic eta tangent motion has a nonzero mixed eta–connection response.

## Gate changes

Passed by explicit model specification:

- one global physical color bundle and one `G2` extension;
- authoritative joint eta–color action;
- action-derived bosonic eta Gauss source;
- no independent coset-vector spectrum;
- classical Wilson-sourced non-Abelian BVP eligibility.

Reclassified:

- the `M8 -> eta_phys` derivation is an open ultraviolet provenance theorem, not a blocker on the physical action;
- v14.30 remains correct that the former parent action did not derive v14.29;
- BVP eligibility does not mean that the BVP, confinement, or a string tension has been solved.

Still open:

1. `GAUGE_FIXED_WILSON_SOURCED_ETA_SU3_NONABELIAN_STATIONARY_BVP_WITH_SELF_ADJOINT_DOMAIN_PARENT_RELATIVE_SUBTRACTION_NONRADIAL_HESSIAN_AND_RELATIVE_DETERMINANT`
2. FR collective-coordinate/Dirac matching and no-double-counting at the quantum level.
3. Wilson area law, worldsheet limit, and dynamical string breaking.
4. Common Yang–Mills normalization and physical scale.
5. Chiral completion, family response, masses, CKM, PMNS, and neutrino outputs.

BHSM is not yet physically complete. Frozen predictions remain unchanged and no physical output is emitted in v14.31.
