# BHSM v15.28: eta-induced material skin and enclosure instability

## Inverse variational completion

The normalized eta trace is

\[
\sigma_*(r)=C_\eta(r)-\frac12,
\qquad
\sigma_*'(r)=w_\eta(r)>0.
\]

Instead of treating \(dC_\eta\) as a connection, v15.28 asks which local
material potential makes this profile a stationary spherical enclosure for
the canonical scalar energy

\[
E_\sigma=\Omega_6 Z_\sigma\int_0^\infty r^6
\left[\frac12(\partial_r\sigma)^2+U_\eta(\sigma)\right]dr.
\]

The Euler equation fixes

\[
U_\eta'(\sigma_*(r))
=w_\eta'(r)+\frac6r w_\eta(r).
\]

Because \(w_\eta>0\) on the open wall interval, \(r\) is a function of
sigma.  Thus \(U_\eta'\), and then \(U_\eta\), are unique on
\((-1/2,1/2)\) up to one additive constant.  Exterior parent-relative
subtraction fixes that constant by \(U_\eta(+1/2)=0\).  No polynomial fit,
measured input, or new continuous coefficient is used.  This is classified as
`BHSM_ACTION_COMPLETION`, not as a term already present in the retained
bosonic action.

## Numerical retained-profile result

At \(\kappa_1=1\), the solved \(p=2+p=8\) eta profile gives approximately

- 10--90% material width: 1.3617;
- median enclosure radius: 1.1679;
- interior-to-parent pressure jump per \(Z_\sigma\): 3.2533;
- surface-of-tension radius: 1.3510;
- surface tension per \(Z_\sigma\): 0.7325;
- orientation force \(U_\eta'(0)\): 3.4280;
- unstable scaling growth rate: 1.2459.

Lengths scale with \(\ell_\eta=\kappa_1^{-1/6}\), the potential and pressure
with \(\ell_\eta^{-2}\), and the growth rate with \(\ell_\eta^{-1}\).

The actual curved radial potential is asymmetric.  Therefore exact sigma zero
is no longer a solution after the event selects an oriented material domain.
The conjugate eta orientation has

\[
U_-(\sigma)=U_+(-\sigma),
\qquad
U_-'(0)=-U_+'(0).
\]

The physical symmetry is the diagonal orientation--sigma reversal, not an
independent sigma reflection on a fixed oriented branch.

## Enclosure instability

Write the radial energy as \(E=\Omega_6Z_\sigma(K+P)\).  Under
\(\sigma(r)\mapsto\sigma(r/L)\),

\[
E(L)=\Omega_6Z_\sigma(KL^5+PL^7).
\]

The solved profile satisfies the Derrick identity

\[
5K+7P=0,
\]

while

\[
E''(1)=\Omega_6Z_\sigma(20K+42P)
=-10\Omega_6Z_\sigma K<0.
\]

Thus the material enclosure is a critical solution with a genuine physical
negative scaling direction.  This is the requested enclosure instability,
not a coordinate shift or gauge mode.

For a constant-area analytic collar, the inverse construction reduces to

\[
U_\eta=\frac12\left(\frac12-2\sigma^2\right)^2
=\frac18-\sigma^2+2\sigma^4,
\]

so the historical quartic is recovered exactly as the flat analytic limit,
not imposed on the curved retained profile.

## Claim boundary

The construction is evaluated on the fixed retained eta and round radial
background.  It does not yet include sigma stress in the Einstein and eta
equations, solve the constraints, or continue the negative mode into a
nonlinear expanding/de-enveloping trajectory.  Those coupled equations are
the immediate continuation target; no Hopf child or full-BHSM completion is
claimed here.
