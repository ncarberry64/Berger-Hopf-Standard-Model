# BHSM v6.30.1 fixed-action off-shell radial-family audit

Primary result:
`BHSM_FIXED_ACTION_OFFSHELL_RADIAL_FAMILY_BLOCKED_BY_UNDERIVED_FIXED_H_MATCHER_DIRICHLET_RANGE_OPERATOR`.

All action controls are held fixed, including
\(d\mu/dq=0\). The coordinate manifold is the same
\([0,1]_t\times M_4\) for every \(q\), B1 remains at \(t=1\), and the
reduced density is defined per one fixed regulator functional
\(\operatorname{Vol}_{\rm reg}(M_4,h)\). The M4 metric is independent, with
an optional curvature probe \(R_4=R_c+r\) satisfying \(dr/dq=0\).

The audit reaches a new domain obstruction before a valid second-order range
solve.

## Matcher ensembles

Before eliminating the matcher multiplier, the boundary variations have the
schematic form

\[
\Pi_{\rm bulk}+\Lambda=0,\qquad
-\Lambda+2C_\partial G^{(4)}-T_{B1}=0,\qquad
h-\iota^*\gamma=0.
\]

Combining all three equations imposes the independent M4 metric equation and
produces the tensor junction. This is the on-shell-\(h\) ensemble used by the
v6.28 matcher-eliminated operator. Its metric boundary condition is

\[
P_\psi(1)+12C_\partial\lambda\psi(1)=0.
\]

An off-shell effective action \(\Gamma[h,q]\) instead holds \(h_{\mu\nu}\)
fixed and does not impose \(\delta_h\Gamma=0\). The matcher then supplies
Dirichlet induced-metric data,

\[
\psi(1)=0,
\]

while \(\Lambda_{\mu\nu}\) is retained as the boundary response. The Robin
and Dirichlet domains are not equal. The inherited metric modulus has
\(\psi_z(1)=1\): it obeys the zero-derivative Robin junction equation but is
excluded by fixed-\(h\) Dirichlet data.

Consequently the v6.28 projected inverse cannot be reused for the requested
off-shell family. Doing so would impose the M4 equation before extracting
\(F(q)\) and \(V_J(q)\), contrary to the construction.

## Order reached

The fixed-action coordinates are \(q\), the independent curvature probe
\(r\), and the one-sided sheet label \(\tau\). On the fixed-\(h\) domain the
intended kernel is the normalized scalar Jacobi mode \(u_1\), with higher
responses orthogonal to it.

The first-order scalar equation

\[
L_0u_1=0,\qquad
\int_0^1N_0a_0^4u_1^2dt=1
\]

is retained. The Puiseux \(a_1,N_1\) profiles are not imported because they
belong to the neighboring-action, curvature-varying curve.

No \(\Phi_2\) is emitted. Before solving

\[
QL_0Q\,\Phi_2=S_2,
\]

the frozen action must be re-varied with the multiplier uneliminated to
derive:

- the fixed-\(h\) Dirichlet radial operator;
- its adjoint domain and Green current;
- its kernel and closed range;
- complement invertibility;
- the nonlinear B1/matcher source through the required order.

These objects are not the v6.28 Robin objects with a renamed endpoint.

## Potential and continuation

The inherited exact coefficients remain

\[
F_0=\frac{\pi}{2},\qquad
F_{1,\tau}=\tau\frac{\chi_1(\pi-4)}4,
\]

and v6.30 still gives

\[
V_E'(0)=V_E''(0)=0.
\]

\(F_2,V_2\), the first nonzero self-interaction, and the canonical
self-coupling are unresolved because \(\Phi_2\) is unavailable on the
required domain. Missing coefficients are not set to zero.

The unique local-stability verdict is
`BHSM_FOLD_LOCAL_STABILITY_BLOCKED_BY_UNDERIVED_FIXED_H_MATCHER_DIRICHLET_RANGE_OPERATOR`.
The unique scale verdict is
`BHSM_SCALE_BRIDGE_PHASE_NOT_PERMITTED_BEFORE_FIXED_H_MATCHER_DIRICHLET_RANGE_CLOSURE`.

This is a class-C missing derivation within the frozen action, not a
contradiction or fatal inconsistency. The next exact target is the
uneliminated-matcher fixed-\(h\) operator/domain theorem.

No measured input, empirical inverse coefficient, fitted parameter,
q-dependent control, q-dependent regulator, local \(X_{\rm FRW}\) field,
new action, primitive, scale, vacuum subtraction, physical mass, global
stability, frozen change, or official prediction-logic change is introduced.
