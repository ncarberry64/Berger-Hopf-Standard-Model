# BHSM v10.3 Common-Domain Stress Pullback

For intrinsic seam stress, the formal distributional lift is

\[
T_{\Sigma}^{AB}(x)=\int_{M_4}\frac{\sqrt{|h|}}{\sqrt{|G|}}
T_{(4)}^{\mu\nu}e^A_\mu e^B_\nu
\delta^{(8)}(x-X(y))\,d^4y.
\]

This lift is purely tangential:

\[
T_{\Sigma}^{AB}n_A^I n_B^J=0,
\qquad
T_{\Sigma}^{AB}n_A^I e_B^\mu=0.
\]

The normal force appears in its distributional divergence,

\[
\nabla_AT_\Sigma^{AB}=\delta_\Sigma
\left[(D_\mu T_{(4)}^{\mu\nu})e_\nu^B
-T_{(4)}^{\mu\nu}K^I_{\mu\nu}n_I^B\right].
\]

Intrinsic equations remove the tangential term. The normal term requires a
shape equation or an exactly balancing bulk/matcher reaction. Since the
current embedding is fixed, that equation is absent.

The delta-supported lift is meaningful linearly but nonlinear self-products
require additional control. A finite collar needs a profile/width; a smooth
domain wall needs an action-selected parent localization; and the normalized
cap/fiber pushforward retains distinct off-shell action owners. None is
silently selected.

The v7.1 KKT adjoints transport reactions between strata, but a compatibility
multiplier is not automatically a physical M8 stress tensor. The v6.27
normal-residual cancellation is retained for its special fold sector and
order, not promoted to complete nonlinear all-sector conservation.

Verdict:
`BHSM_STRATIFIED_ACTION_LACKS_A_CONSERVED_COMMON_DOMAIN_STRESS_TENSOR`.
