# Daughter collar: actual nodal pullback and inherited-prefix coverage

Continue PR #465 from `bddd4e68ebc6b84efab29c051c5df4c53ba727c6`,
branch `codex/muon-parent-maxwell-density-review`. Scientific reference:
`524ed90689bd5923c249bba2e699abf627e703cd`.

The new result is an evaluated transverse, volume and spin pullback on the
continued saved collar, followed by a consumed inherited-prefix coverage
enclosure. **It is not an evaluated full wall overlap or native anomaly.**
This particular Gaussian patch reaches the inherited E1 reset before reaching
the saved source support. That is a coverage result for this realization,
not an absence theorem for every compatible representation or physical model.

The adopted daughter eta identification stays resolved:

\[
 f_{\eta,c}=\rho(X)/2,\qquad m_{\eta,c}=-\rho_s\cot(\rho/2)/2.
\]

All prior four checks/seven identities, source-H repair, contact, pairings,
common-A actions, angular outputs and conditional local results are preserved.
No earlier production calculation, covariance witness, normalization audit,
symbolic replay or full test suite is run. No incoming static profile is reused.

## Actual inputs and continuation

The original `daughter_collar_profile.npz` is read, not reintegrated. Its 33
phase samples on `s=0..0.001` are given an explicit cubic Hermite representation.
Only their previously absent transverse variation, spin line integral and
unnormalized normal integral are integrated. The newly solved phase begins
at the saved endpoint. The geometric metric is unchanged:

\[
 g_2=\nu^2d\tau^2-C^2(d\rho+\zeta d\tau)^2.
\]

`SavedNodalMetric.jet` differentiates the actual products of the supplied
bilinear nu/C/shift, including their mixed derivatives. It does not make g
bilinear or replace a metric time derivative with H. The original wall base
time `0.00009585390525338264` is a coordinate point, not a state/endpoint choice.
The differentiation coordinate remains b, with `beta=T_b b` and
`A_Q=sqrt(2)beta`; Q and the original radial hat stay unchanged. No vertex 2/3
factor or source-dependent spin/pairing derivative is assigned zero.

For phase z=(X,n), transverse V=(xi,eta), the implemented equations are

\[
 X_s=n,\quad n_s=-\Gamma(n,n),\quad
 \xi_s=\eta,\quad
 \eta_s=-\partial\Gamma[\xi](n,n)-2\Gamma(n,\eta).
\]

At a transverse cell face h(X)=0, X and n are continuous. The fixed-s
variation has the essential saltation

\[
 \xi_+=\xi_-,\qquad
 \eta_+=\eta_--[\Gamma](n,n)\frac{dh(\xi_-)}{dh(n)}.
\]

Grazing/corner/turning cases stop explicitly instead of being regularized or
reset into another coordinate chart. The executed curve crosses temporal
cells 23 through 0, with the radial cell fixed at63. No physical output is
extrapolated outside the cache. A fixed-cell polynomial is used for internal
Runge-Kutta stages terminating at each event, not as exterior physical data.

The actual pulled-back volume uses, per boundary proper time and the saved
normalized S3 Haar convention,

\[
 \Delta_X=\tau_y\rho_s-\tau_s\rho_y,\quad
 J_c=\frac{\nu C r^3|\Delta_X|}{\sqrt{h_{wall,yy}}r_{wall}^3}.
\]

The wall Haar volume factor `2*pi^2` cancels between numerator and denominator
here. It remains in the existing M4/T pairings exactly once; no family count
or wall-density multiplier is added to this J.

## Evaluated geometric and spin actions

At the artificial cut the computed normal data are

| Quantity | Value in the declared nodal reconstruction |
|---|---:|
| normal s |0.0064899805503247044|
| tau |0|
| rho |1.564030196575592|
| tau_s |−0.029571640719287792|
| rho_s |−1.0437589497587703|
| J_c |1.0015886348802674|
| minimum abs(Delta_X) |1.0419477793105136|
| unnormalized I_partial |0.003234015478131905|

The covered rho region is `[1.564030196575592,pi/2]`. The saved source
support is `[0.5890486225480862,0.9817477042468103]`, from the actual saved
Gauss cells. The radial gap is about0.58228249, not an interpolation residual.
Observed normal, orthogonality and transverse metric identity residuals are
respectively at most `7.42e-14`, `6.54e-12`, and `7.44e-14`. These observations
do not certify ODE solution error or chart rank of an unknown continuum metric.

Cartan's same-frame normal spin connection is evaluated as

\[
 \omega_{01}=\left[\nu_\rho/C+\zeta b_0\right]d\tau+b_0d\rho,
 \qquad b_0=(C_\tau-\zeta C_\rho-C\zeta_\rho)/\nu.
\]

The saved signature is +----, with `parent_gamma[4]=i*gamma5`. The actual
4x4 boost is `U=exp[-(integral omega01) gamma0 gamma4/2]`, tensored with the
unchanged SM16/family factors. The adopted common-A connection is angular
in this section and has zero contraction along a fixed-angle normal; its
angular/source outputs are retained, not projected away. No new carrier
connection or curvature fit is introduced.

`U^dagger gamma0 U=gamma0` is checked on the actual arrays. This boost is
not Euclidean unitary. It mixes the fixed four-dimensional chiral frame,
so both projectors are transported as `U P_L/R U^-1`; a claim that it
commutes with fixed gamma5 would be incorrect. Both oriented normal signs
and both chiral sectors remain available. Full source, pairing and domain
variations of that transport remain unevaluated, rather than declared zero.

## Consumed inherited prefix

The chosen 1222-segment chain is followed, excluding alternative historical
covers and overlapping superseded launch segments. Its already supplied
proper-duration intervals sum outward to

\[
 T_{prefix}\in[1.082320108470697\,10^{-27},
                    1.4944995686293672\,10^{-27}].
\]

Thus the E1 reset is at `tau=-T_prefix` in the tail clock; tau=0 is never
declared the physical past endpoint. `prefix_coefficients` materializes the
actual cached centers and retained recenter sides (1238 rows) with
`boundary_log_radius -> current_parent_fields`. Their endpoint C/r fields
match the tail exactly, and lapse/shift differences are at most2.67e-15.
The same b-source T_b coefficients are continued on those rows. Original
source support/Q/lifts are not replaced by new profiles. The 34 newly
consumed prefix files match the current primary workspace; its newer dirty
work and running calculations are untouched.

A Hamiltonian first-exit enclosure consumes those coefficients without
inventing a resolved time profile from interval midpoints. Along a spacelike
geodesic, with its retained norm `g(n,n)=-kappa`,

\[
 p_\rho=-C^2(n^\rho+\zeta n^\tau),\quad
 (p_\rho)_s=\tfrac12\partial_\rho g_{ab}n^an^b,
 \quad n^\tau=-\sqrt{p_\rho^2/C^2-\kappa}/\nu,
 \quad n^\rho=-p_\rho/C^2-\zeta n^\tau.
\]

Temporal derivatives need not be bounded in this covector equation.
Arb evaluates a bootstrap strip around the cut, using the complete prefix
coefficient hull and geometric radial slopes. The computational widths
`1e-12` for rho/p_rho are enclosure widths, not physical parameters. The
first-exit bounds close strictly within them and exclude a normal-time turn:

\[
 \Delta s<5.054\,10^{-26},\quad |\Delta\rho|<5.275\,10^{-26},
 \quad |\Delta p_\rho|<4.296\,10^{-27}.
\]

These are certified for the stated binary64 **nodal coefficient hull**, at
the supplied cut phase. They are not a new interval certification of the
continuum history/geometry or the binary64 tail ODE. Constant-momentum
normal/Spin rapidity centers are also saved with their phase enclosure;
rapidity uses `asinh(nu*n_tau/sqrt(kappa))`. Prefix transverse J is not
promoted from those centers. No heat/resolvent complement claim follows.

The numerical daughter normal therefore reaches the inherited E1 boundary
near rho1.56403 within this representation, still far outside support. A
patch ending there is not continued through another branch without the
owned matching. A different compatible representation has not been ruled
out, and reset crossing is not asserted to be its uniquely required route.

## Overlap scope and one next action

The compact-source factor is identically zero on the covered patch and
enclosed prefix, because their rho range is disjoint from the saved support.
This is only an **unnormalized partial source integral**. It does not set
`T_required`, `B54,F`, any propagated resolvent trace or N_out to zero.

One inherited normalization remains:

\[
 I(y)=\int_{\text{owned normal domain}}\sin^2(\rho(X)/2)ds,
 \quad u_c=J_c^{-1/2}\sin(\rho(X)/2)/\sqrt{I(y)}.
\]

The new I_partial and the bounded prefix addition do not supply its full
domain/remainder. No segment or patch is independently normalized. Neither
the full overlap `T=<W_eta e,p>_5` nor `M4 B=T` is evaluated, so no interface
matrix is fed to a purported complete exterior K/M or stationary conormal.

**The next explicit map is the inverse/patched collar action at the saved
source points:** find admissible `(s_j,y_j)` with
`X(s_j,y_j)=(tau_cut=0,rho_j)` for the actual Gauss points, or the sufficient
same-domain half-density/Spin action in a justified compatible representation.
Its consumer is the already saved n1/n3 T integrands. A new disjoint curve
does not evaluate it. A patch transition must transport the same source and
geometric pairing; normalization remains global. If the owned route crosses
E1, the existing AE2 spinor trace must hold with its typed wall-input map:
`Gamma0_child W_child T_R=U_R Gamma0_event W_event`. Together with
`W^dagger M5 W=M4`, these are necessary compatibility conditions, not a
producer or unique interior extension. No new boundary datum is selected.
This is an uncomputed source-restricted geometry/interface action, not an
unselected eta profile or a proof of physical non-identifiability.

## Reproducibility and uncertainties

The one new tail solve took about1.80s. Prefix coefficients/enclosure took
about1.01s. Only that inexpensive prefix action was reevaluated (~0.88s)
after two concrete corrections: directed Arb-to-JSON bounds and the retained
norm factor in rapidity. The tail curve was not rerun. Earlier receipts are
preserved in Downloads. The new four targeted tests pass, covering actual
transverse geometry, actual Dirac transport, consumed prefix/support scope,
and an independent Hamiltonian covector identity. No old scientific checks
are counted as new operator evaluations.

The reused Hermite segment's maximum sampled geodesic defect is6.14e-5;
its stability/absolute error bound is not established. Solver tolerances,
observed residuals, spectral complement, continuum/history reconstruction,
normalization remainder and source/pairing/domain derivative errors remain
separate. H_f and its inherited interval stay unchanged, and are not
identified with the different affine-logR slope. The nodal prefix certificate
does not bound any of these omitted errors.

All six native contribution-ledger entries and physical a_mu/g_mu remain
unevaluated. Native physical transfer directions: zero. Frozen local results
are copied with their original calibration-only convention; they are not
refit, refined or added again. No experimental anomaly is used or compared.

Replay (fresh output):
`python scripts/replay_muon_collar_source_coverage.py --output <fresh-directory>`.
The optional `--resume-collar <run_1>` consumes saved new collar actions and
reruns only the prefix action. Input hashes, exact execution revision,
relevant source diff, actual action arrays, orientations, chronology and
error scope are in `artifacts/muon_collar_source_coverage_20261003`.
