# Physics admission for the Blackhole Tracker product

Implemented repository-root file: `product/bhtracker/physics_admission.py`. Its public entry point is
`assess_physics(config, parameters, impact_pc=None)`. It depends only on NumPy,
the standard library, and the packaged `.theory.radial_response` provider.
The optional envelope family is a conditional worldtube exterior. The baseline
mass/center/motion model does not require an envelope amplitude or a selected
black-hole scalar charge. No present calculation identifies a worldtube with
a horizon.

## Computable source pairing

The retained cubic R1 action, homogeneous replay, and exact radial solution
are derived in `manuscript/exterior_derivation.tex`. Use the orthonormal real
quadrupoles and write

\[
 \delta\widehat\pi=f_2(x)\sum_A a_A Y_A,
 \quad \int Y_A Y_Bd\Omega=\delta_{AB},\quad f_2(x_0)=1,
 \quad A_2=\|a\|_2 .
\]

The same local action gives the positive exterior Dirichlet-to-Neumann map

\[
 q_A=\Lambda_2 a_A,\qquad
 \Lambda_2=-x_0^2K_r(x_0)f'_2(x_0)>0,\qquad
 {E_2\over M_{\rm Pl}^2L_0}={1\over2}\Lambda_2\|a\|_2^2.
\]

Thus a **specified conormal source** determines its boundary amplitude exactly:
\(a_A=q_A/\Lambda_2\). In physical scalar units the integrated harmonic
conormal is \(Q_A=M_{\rm Pl}L_0q_A\). Equivalently an external boundary work
term \(-M_{\rm Pl}^2L_0q\cdot a\) in the static energy yields this stationary
condition. This is source pairing for a declared boundary source; it supplies
no model of a black-hole interior. The code accepts either `boundary_amplitudes`
or `conormal_coefficients`, checks agreement if both are supplied, and returns
both. The ordinary mass and ordinary metric multipoles remain independent.

The three product coordinates are plus, cross, axial. The two odd projected
quadrupoles xz and yz are fixed zero as part of this template family; they are
not inferred to vanish from projected data. The bounds below hold for the
full five-dimensional quadrupole as well.

## A uniform exterior bound, with proof

Let \(S=C\sqrt{1+(r_V/r)^3}\), \(k=K_\Omega/K_r\), and
\(y=d\log f_2/d\log r\). The exact exterior has
\(1/4\le k\le1\), and the radial equation is

\[
 r^2 f_2''+2kr f_2'-6kf_2=0,
 \qquad \dot y=(1-2k)y+6k-y^2.
\]

The positive decaying solution obeys \(-3\le y\le-1\). One way to prove this
is to integrate the Riccati equation inward from its isolated far-field
condition \(y\to-3\): at the two barriers its outward vector field is
\(\dot y|_{-3}=12(k-1)\le0\) and
\(\dot y|_{-1}=8k-2\ge0\), so the interval is invariant under inward
integration. Positivity and uniqueness also follow from the elliptic radial
Dirichlet problem or the positive hypergeometric integral.

Furthermore, \(f_2\le f_1=|p(x)|/|p(x_0)|\). Both functions equal one at
the inner boundary and decay at infinity. With
\(L_l f=(r^2K_rf')'/r^2-l(l+1)K_\Omega f/r^2\),
\(L_2f_1=-4K_\Omega f_1/r^2<0\). The maximum principle applied to
\(f_2-f_1\) establishes the comparison. In particular \(f_2\le1\).

Represent a normalized quadrupole by a trace-free symmetric matrix \(A_{ij}\):
\(\delta\widehat\pi=N_{\rm STF}f_2 n^iA_{ij}n^j\),
\(N_{\rm STF}=\sqrt{15/(8\pi)}\), \(\|A\|_F=A_2\).
At a direction chosen as the z axis, the Hessian map splits into the
orthogonal m=0,1,2 matrix subspaces. Its singular coefficients after removing
\(N_{\rm STF}f_2/x^2\) are

\[
 2,\quad 2|y-1|,\quad
 {2\over\sqrt3}\sqrt{1+2k^2}\,(3-y).
\]

Each is at most 12. Therefore, at **every** exterior radius and orientation,

\[
 \|\delta\Pi\|_F\le B A_2 {f_2\over x^2},\qquad
 B=12\sqrt{15/(8\pi)}=9.27058084855655.
\]

Since \(\|\Pi_0\|_F\ge\sqrt2|p|/x\) and
\(\delta Z=-4[(\operatorname{tr}\delta\Pi)I-\delta\Pi]/\widehat\lambda\),
the comparison bound gives

\[
 {\|\delta\Pi\|_F\over\|\Pi_0\|_F}
 \le {B A_2\over\sqrt2 x_0|p_0|},\qquad
 {\|\delta Z\|_{op}\over K_\Omega}
 \le {2\sqrt2 B A_2\over x_0|p_0|}.
\]

Here \(\| (\operatorname{tr}H)I-H\|_{op}\le\sqrt2\|H\|_F\), and
\(K_\Omega\ge2|p|/(\widehat\lambda x)\). For the time coefficient,
\(|\delta K_t|\le4\sqrt3\|\delta\Pi\|_F/\widehat\lambda\). Write
\(d_*=D/C>0\), \(s=S/C\ge1\); then

\[
 {K_t\over |p|/(\widehat\lambda x)}
 =6-{6\over s}+{8d_*\over s-1}\ge R_t,
\quad
 R_t=\begin{cases}6,&d_*\ge3/4,\\
 6t(2-t),\quad t=\sqrt{4d_*/3},&0<d_*<3/4.
 \end{cases}
\]

Consequently
\(|\delta K_t|/K_t\le4\sqrt3 B A_2/(R_tx_0|p_0|)\).
Bounds below one preserve both retained leading principal signs. The product
uses a stricter declared principal-fraction budget, default 0.01, and a
default state budget \(\eta=6A_2/(x_0|p_0|)\le10^{-3}\). It also exposes the
separate relative-Hessian budget, default 0.01. These numerical budgets are
user-selected approximation controls, not physical constants or a new
measurement of a source amplitude.

The exact quadratic scalar remainder satisfies

\[
 |\mathcal R_2|={2\over\widehat\lambda}
 |(\operatorname{tr}\delta\Pi)^2-\delta\Pi:\delta\Pi|
 \le {4\over\widehat\lambda}\|\delta\Pi\|_F^2.
\]

The helper returns the consequent bound
\(|\mathcal R_2|/(K_\Omega\|\delta\Pi\|_F)\le2BA_2/(x_0|p_0|)\).
This normalized residual is not a global solution-error estimate: a small
residual alone does not bound the inverse boundary-value operator.

### Zero monopole flux

At zero supplied flux, \(p_0=0\), \(K_r=K_\Omega=C\), \(K_t=D\), and
\(f_2=(x_0/x)^3\). A relative background Hessian or eta is undefined.
The code returns `None` for those quantities and uses the nonzero absolute
amplitude limits

\[
 A_2\le\min\left\{
 {\epsilon_Z\widehat\lambda Cx_0^2\over4\sqrt2 B},
 {\epsilon_Z\widehat\lambda Dx_0^2\over4\sqrt3 B}\right\}.
\]

Here \(\epsilon_Z\) is the declared principal-fraction budget. Thus zero
monopole does **not** silently require zero boundary quadrupole. The same
conormal map remains positive and finite, \(\Lambda_2=3Cx_0\).

## Domain and time checks

The product enforces positive physical inputs and, once fitted impact radii
are supplied, \(b\ge r_0\). It bounds the worldtube potential using

\[
 |\Phi(r_0)|\le(1+\epsilon_\infty){m\over r_0}
 +{|\widehat\beta|A_2\over2}\sqrt{5/(4\pi)}.
\]

The second term follows from the normalized STF eigenvalue bound and
\(f_2\le1\). The gradient map has largest coefficient
\(\sqrt6N_{\rm STF}f_2/x\), by the same m=0,1,2 decomposition. Hence the
total spatial/time-background-gradient ratio is uniformly bounded by
\([(|p_0|+\sqrt6N_{\rm STF}A_2/x_0)/|\widehat v|]^2\). The helper tests this
against a declared default 0.01 budget and also reports
\(p_0^2/\widehat v^2\) separately. The provider solves only the leading
weak-metric frozen-background equations.

Observer proper motion is converted by
\(v_\perp/c=|\mu_{obs}|D_l(1+z_l)/c\), with mas converted to radians and
years to local physical units. The factor \(1+z_l\) is required. The
retained characteristic-speed lower bound is computed from

\[
 c_r^2={4s^2\over3(s-1)^2+4d_*s},\qquad
 c_\Omega^2={s^2+3\over3(s-1)^2+4d_*s}.
\]

The radial infimum is \(\min(1/d_*,4/3)\). The angular infimum is 1/3 for
\(d_*\le3/2\); otherwise evaluate the function at
\(s_*=(6+\sqrt{36+3(4d_*-6)^2})/(4d_*-6)\), including endpoints.
The product checks the advective ratio \(v_\perp/c_{min}\) against a declared
default 0.01 budget. A supplied intrinsic observer timescale is similarly
checked after division by \(1+z_l\). If it is absent the state is explicitly
assumed fixed in the moving worldtube; no ringdown or relaxation time is
invented. A frozen-background drift estimate over
\(L=\max(r_0,r_V,b_{max})\) is
\(\max(|\widehat H|,2|\widehat d/\widehat v|)L/L_0\).

These are local controls. Full line-of-sight projection still uses the
declared decaying isolated extension. A small local bound does not certify
cosmological matching, full covariant hyperbolicity, radiation corrections,
or an observational error budget. The provider's finite matching tail bounds
can be applied after selecting a matching radius; they control the omitted
tail alone.

## Default replay and independent numerical checks

At \(M=10^9M_\odot,z_l=0.3,H_0=67.4\), \(r_0=10\) pc, flux ratio one:

| Quantity | Value |
|---|---:|
| C, D, beta_hat | 4.238858559433703, 4.396221028708140, 0.11306384489513412 |
| L0, rV | 4.447959317507418e9 pc, 45680.311759140604 pc |
| p0, x0 abs(p0) | -3.6778186794260046e-4, 8.268552873111729e-13 |
| Lambda2 | 0.0029422644948379566 |
| A2 at eta=1e-3 | 1.3780921455186215e-16 |
| Default sufficient conormal-norm cap | 4.054711590374503e-19 |
| Uniform relative Hessian bound | 0.0010925484305920792 |
| Uniform spatial principal fraction | 0.004370193722368317 |
| Uniform time principal fraction | 0.0017841241161527714 |
| Uniform nonlinear residual / principal scale | 0.0030901936161855167 |
| Worldtube potential bound | 4.792631704311209e-6 |
| p0 squared / v squared | 2.3926924210441333e-6 |
| Background drift over rV | 2.1464862400921376e-5 |
| Absolute zero-flux A2 cap, default principal budget | 3.459635478247056e-21 |

Independent tests executed with Python 3.14, NumPy and SciPy:

* 372 Cartesian finite-difference Hessians of the actual hypergeometric
  field, using 31 radii from 1.002 r0 to 100 rV, random directions and random
  unit trace-free symmetric states, seed 1974. Step h=2e-4 r. The largest
  numerical/uniform-bound ratios were 0.311506 (relative Hessian), 0.291740
  (spatial principal), and 0.157867 (time principal). These checks use field
  values in Cartesian differences rather than the singular-coefficient
  expression used for the proof.
  The corresponding gradient bound had maximum numerical/uniform ratio
  0.534395. A further 501-radius radial check obtained max(f2/f1)=1 and
  logarithmic slopes within [-3,-1] to 2e-12 tolerance.
* The analytic time and sound-speed minima were checked over 401 D/C values
  from 1e-4 to 1e4 and 4001 s values from 1+1e-9 to 1+1e10. The smallest
  actual/lower-bound ratios were 1.00000000000114 and 1.00000000000306.
* API checks passed for the capitalized public distance keys D_l_pc,
  D_s_pc, D_ls_pc; admitted default state; rejection of b<r0; pending-domain
  state without impacts; Dirichlet/conormal agreement; baseline eligibility
  without flux provenance; and a nonzero zero-flux boundary state below its
  absolute cap. All returned records serialized with `allow_nan=False`.
  A lens outside the packaged R1 redshift range also preserved independent
  baseline eligibility. Baseline proper motion uses its own declared
  quasistatic speed budget and does not depend on R1 sound speeds.

These sampled checks corroborate the derivation; the analytic inequalities,
not numerical sampling, establish the uniform bounds. The helper also
returns a 129-radius sampled maximum per unit boundary state, explicitly
marked as not a certificate.

Replay from the repository root:

```text
python product/tests/test_physics_admission.py --receipt papers/bhsm_blackhole_tracker_20261021/review/product_physics_admission_check.json
python -m pytest product/tests/test_physics_admission.py -q
```

The persisted `product_physics_admission_check.json` records the coefficients,
unit conventions, complete API case list, independent inequality values,
Python/library versions, and SHA256 of the helper, test and packaged provider.

Product-contract follow-up: both redshifts may equal zero when all three
positive distances are supplied, for either the baseline or conditional R1
family. The helper imports the packaged IAU nominal solar GM conversion, so
its weak-field boundary uses the same mass length as the forward provider.
Additional replay cases admit a Galactic 10-solar-mass state outside its
worldtube, reject missing local distances, reject excessive post-fit speed
for both families, and reject an excessive boundary deformation even when
the impact radii are outside the worldtube. The numerical receipt has been
regenerated against that packaged provider.

## What the later black-hole papers establish, and what can now be done

Babichev et al. study shift-symmetric Horndeski models on a cosmological
background. Horizon regularity and branch matching select scalar charges
through current reality and double-root conditions, rather than the
regular-origin material-source rule. Their action and branch assumptions
therefore matter to importing a charge relation. See
[Babichev et al., Phys. Rev. D 112, 024043 (2025)](https://arxiv.org/html/2504.07882v2).

Smulders and Noller construct cubic-Galileon solutions with cosmological
hair and explain why a nonzero radial scalar current requires a
quasistationary treatment of the coupled metric. Their conservation law is
time dependent; replacing only the scalar flux equation does not solve the
remaining Einstein equations. Their action has no R1 linear scalar
potential. See
[Smulders and Noller, Phys. Rev. D 114, 044072 (2026)](https://arxiv.org/html/2603.22398v3).

R1 has a rolling background and a linear potential, with
\(\dot J+3HJ=\mu^3\). The full current is not the source-free conserved
current assumed in those shift-symmetric horizon calculations. The QS
exterior flux is conserved only after the local approximations and
background subtraction. Consequently neither paper supplies the missing
R1 horizon charge or quadrupole amplitude by parameter substitution.

A further R1 horizon-matching calculation requires **no new bulk theory**:
the action and its complete field equations already specify it. The minimal
additional calculation is a coupled, horizon-penetrating spherical evolution
or boundary-value problem, for example
\(ds^2=-e^{2\delta(v,r)}F(v,r)dv^2+2e^{\delta(v,r)}dvdr+r^2d\Omega^2\)
and \(T(v,r)\). It must impose future-horizon regularity, the recovered rolling
FLRW data at an outer matching surface, specified mass/initial data, and the
full Einstein constraints. Its output is the time-dependent scalar flux and
the match to the weak exterior; reality and principal-cone checks must be
performed on that output. A nonspherical source amplitude additionally
requires the coupled l=2 perturbation problem with specified horizon/outer
or source data. There is no uniqueness or stationary-hair theorem here that
turns the current boundary coefficient into an intrinsic black-hole state.

The implementable advance now is narrower and constructive: fixed conormal
data map exactly to admissible amplitude intervals, with uniform retained
principal/Hessian bounds and explicit motion/domain checks. Product labels
must retain `regular_body_proxy`, `supplied_conditional_flux`, or
`supplied_worldtube_flux`; an unselected or alleged horizon-derived flux is
not automatically admitted as a physical R1 compact-source solution. The
baseline tracking product remains usable independently.
