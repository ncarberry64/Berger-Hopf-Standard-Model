# Release-candidate scientific review

Reviewed 2026-10-21 by the internal science agent. This is an adversarial internal computational review, not independent external peer review. The review covers the admission theorem, its implementation, the projection and estimator identities, the BHSM boundary interpretation, and an independent analytic point-lens benchmark. It does not certify astrophysical source identification, horizon matching, observational acquisition, or general interval coverage.

## Outcome and actual corrections

The stated uniform theorem and the scoped projection/estimator identities survive reconstruction. No missing factor in the five-mode normalization, Hessian coefficient, conormal energy, or Brown--York inverse was found. Two genuine admission defects were corrected in `product/bhtracker/physics_admission.py`:

1. A supplied null, nonnumeric, nonfinite or nonpositive intrinsic evolution timescale could silently become the absent-timescale, fixed-state assumption. The selected supplied value is now required to be positive and finite. An explicit parameter value overrides the analysis configuration; an absent value still means a prescribed fixed state. Invalid optional R1 input does not reject an otherwise valid ordinary-lens model.
2. The speed certificate was the spherical-background bound even for a nonzero deformation. The code now uses the conservative state-inclusive bound derived below for motion and intrinsic evolution, preserving the background value as a separate output. A regression selects speeds between the two thresholds and verifies rejection of the deformed model. The zero-state spherical result and the optical optimizer are unchanged.

The owned manuscript sections now state the three-mode restriction, the sufficient-only nature of the cap, the shear normalization, the first-order scopes, the correct extrinsic-curvature terminology, and the limitation of local Gaussian error pushforwards. These edits change neither the lens equations nor the ordinary fitted estimates.

## Uniform theorem reconstructed

Write the dimensionless scalar perturbation as

\[
\delta\widehat\pi=N f_2(x)n^TQn,
\quad N=\sqrt{15/(8\pi)},\quad Q\in\mathrm{STF}(3),
\quad \mathcal A=\|Q\|_F=\|a_5\|_2,\quad f_2(x_0)=1.
\]

This follows directly from the isotropic fourth moment of the unit sphere: \(\int(n^TQn)^2d\Omega=8\pi\|Q\|_F^2/15\). Thus the theorem covers all five orthonormal real modes. The public product accepts plus/cross/axial coordinates and fixes the two odd coordinates to zero. Their omission is a model restriction, not an inference that they vanish.

On the positive-charge, isolated decaying branch, assume \(C,D_t,\widehat\lambda>0\), \(P_0=x_0|p_0|>0\), and \(k=K_\Omega/K_r\in[1/4,1]\). The radial equation implies

\[
r^2f_2''+2krf_2'-6kf_2=0,
\qquad \dot y=(1-2k)y+6k-y^2,\quad y=d\log f_2/d\log r.
\]

At \(y=-3,-1\), the outward vector field is respectively \(12(k-1)\le0\) and \(8k-2\ge0\). The interval is invariant when integrating inward from the decaying far branch \(y=-3+9(r_V/r)^3/8+O((r_V/r)^6)\). Hence \(-3\le y\le-1\). The maximum principle gives \(f_2>0\) and \(f_2\le f_1=|p|/|p_0|\): the translation solution has \(L_2f_1=-4K_\Omega f_1/r^2<0\), with the same normalized inner and vanishing outer data.

At the north pole, the Cartesian Hessian map on the orthogonal \(m=2,1,0\) STF subspaces has singular coefficients

\[
2,\quad 2|y-1|,\quad {2\over\sqrt3}\sqrt{1+2k^2}(3-y).
\]

Each is at most 12. An additional independent symbolic Cartesian differentiation in this review produced the exact Gram matrix

\[
\operatorname{diag}\left(4,4,4(y-1)^2,4(y-1)^2,
{4\over3}(1+2k^2)(3-y)^2\right).
\]

This calculation differentiated a second-order Taylor representation of the radial field in Cartesian coordinates before evaluating on the axis; it did not reuse the implemented singular-value formula. With \(B=12N\), use \(\|H_0\|_F\ge\sqrt2|p|/x\), \(K_\Omega\ge2|p|/(\widehat\lambda x)\), and \(\|(\operatorname{tr}H)I-H\|_{op}\le\sqrt2\|H\|_F\). These yield the manuscript's uniform relative Hessian and spatial principal bounds.

For \(d_*=D_t/C>0\) and \(s=K_r/C\ge1\), the time ratio is

\[
{K_t\over |p|/(\widehat\lambda x)}
=6-{6\over s}+{8d_*\over s-1}.
\]

Its infimum is 6 if \(d_*\ge3/4\), otherwise \(R_t=6t(2-t)\), \(t=\sqrt{4d_*/3}\). Combining \(|\operatorname{tr}H|\le\sqrt3\|H\|_F\) gives

\[
e_H={B\mathcal A\over\sqrt2P_0},\quad
e_s={2\sqrt2B\mathcal A\over P_0},\quad
e_t={4\sqrt3B\mathcal A\over R_tP_0}.
\]

The implemented cap is exactly

\[
\mathcal A_{max}=P_0\min\left\{
{\eta_{max}\over6},{\sqrt2\epsilon_H\over B},
{\epsilon_Z\over2\sqrt2B},{\epsilon_ZR_t\over4\sqrt3B}\right\},
\quad 0<\epsilon_Z<1.
\]

It is a sufficient guarantee within the retained exterior, not a necessary physical limit. The new test doubles the default eta-limited cap: admission fails while both sufficient principal-positivity checks remain true. A failed principal certificate also does not compute an actual negative eigenvalue. The exact quadratic scalar residual obeys \(|\mathcal R_2|\le4\|\delta H\|_F^2/\widehat\lambda\); this is not a solution-error estimate without an inverse-operator estimate.

The exact linear conormal map is \(q=\Lambda_2a\), \(\Lambda_2=-x_0^2K_rf_{2,x}(x_0)>0\), with \(E_2/(M_{Pl}^2L_0)=\Lambda_2\|a\|^2/2\). Consequently \(\|q\|\le\Lambda_2\mathcal A_{max}\). Public conormal input is converted before the optical solve, and an inconsistent simultaneously supplied Dirichlet state is rejected. These are specified worldtube data, not a horizon-selected scalar charge.

At zero flux, \(p_0=0\) does not forbid a nonzero scalar boundary state. The separate branch has \(f_2=(x_0/x)^3\), \(K_r=K_\Omega=C\), \(K_t=D_t\), \(\Lambda_2=3Cx_0\), and the positive absolute cap

\[
\mathcal A\le\epsilon_Z\widehat\lambda x_0^2
\min\{C/(4\sqrt2B),D_t/(4\sqrt3B)\}.
\]

Relative eta is correctly unavailable on that branch.

## Enforced domain and corrected speed certificate

The provider requires positive mass, worldtube radius, Hubble scale, and retained coefficients, nonnegative flux, and a redshift within its pinned background range. Admission requires actual post-fit rays outside the actual worldtube, weak metric bounds, selected conditional flux provenance, small spatial/background-gradient controls, slow background drift, and observer-frame motion/timescale checks. Galactic zero/zero redshifts are accepted when the three supplied distances are positive. Regular-body proxy provenance requires unit flux; arbitrary nonnegative flux needs explicit conditional provenance. `horizon_matched_r1` remains false.

The background characteristic speed obeys

\[
c_{bg}^2=\inf_{s\ge1}{\min(4s^2,s^2+3)\over3(s-1)^2+4d_*s}.
\]

For a perturbed state, \(Z\succeq(1-e_s)Z_0\) and \(K_t\le(1+e_t)K_{t0}\), so a valid retained certificate is

\[
c_{min}=c_{bg}\sqrt{(1-e_s)/(1+e_t)}\quad(e_s<1).
\]

The corrected helper uses this quantity. If the sufficient spatial bound reaches one, zero in this certificate means no positive guarantee, not an actual zero sound speed. The background certificate remains available separately. The enforced advection ratio is \(v_\perp/(cc_{min})\), with \(v_\perp=|\mu_{obs}|D_l(1+z_l)\); intrinsic evolution uses \(L(1+z_l)/(cc_{min}\tau_{obs})\). Fixed state is an explicit assumption when no timescale is supplied. These are conservative approximation budgets for the frozen retained equations, not a proof of the full time-dependent coupled system or UV completion.

## Projection and estimator scopes

For a frozen radial exterior on a full symmetric straight line of sight, the xz/yz modes are odd and vanish exactly. The screened radial equation gives \((K_rr^{-4}Y')'=6K_r'r^{-5}Y<0\), \(Y=r^3f\). Decay at infinity implies \(Y'>0\), so the transverse integral is positive and the axial integral is positive by the stated integration by parts. Hence the screened map into projected functions has rank three; the harmonic \(f=C_o/r^3\) limit has zero axial integral and rank two. Finite endpoints, nonconstant weights, time evolution, fitted source freedoms and optical data rank are separate questions. In particular this function-space rank is not a claim of three identifiable measured state coordinates.

For the point-lens reference, \(s=\sqrt{u^2+4}\), \(h=us/2+2\operatorname{asinh}(u/2)\). At fixed source, a constant radial spin-two perturbation has zero first-order primary-pair delay, while \(\delta\ln R=-4q(s/u)\cos2\varphi\). Its apparent-mass first-variation response equals that of a unit \(r^2\cos2\varphi\): \(\mathcal K=s^3/(uh)\). Therefore \((r^2-1)\cos2\varphi\) is a first-order null of that scalar statistic for all nonsingular \(u>0\). The product shear potential has a factor one half, so a unit \(r^2\cos2\varphi\) means \(\gamma_+=2\), not one.

These statements do not imply equality of finite lens models or of all image observables. At generic angle the gradient difference of that null is \(2s\cos2\varphi\,e\), so one free source shift cannot preserve both fixed images. At \(\cos2\varphi=0\), one freely positioned source does admit a joint first-order null. Forward flux variations must include the displaced background Hessian; fixed-image formulas have different hypotheses. The matched finite profile can lift the leading delay null. The radial potential filter also does not exclude extended ordinary matter or unrestricted source/environment transformations.

## Boundary interpretation and analytic benchmark

On a static spherical Schwarzschild slice, the enclosing sphere has principal extrinsic curvatures \(\sqrt f/r\), versus \(1/r\) in the flat reference. Its intrinsic Gaussian curvature is \(1/r^2\) in both cases at fixed areal radius. Thus the correct object is the **principal extrinsic-curvature deficit of the enclosing sphere**,

\[
\delta k=(1-\sqrt f)/r,
\quad E_{BY}=c^4r(1-\sqrt f)/G,
\quad M=E_{BY}/c^2-GE_{BY}^2/(2c^6r),
\quad f=1-2GM/(c^2r)>0.
\]

The code rationalizes the difference as \((2GM/(c^2r))/(1+\sqrt f)\), avoiding weak-field cancellation. The fixed-radius first-order pushforwards \(\sigma_{E/c^2}=\sigma_M/\sqrt f\) and \(\sigma_{\delta k}=G\sigma_M/(c^2r^2\sqrt f)\) are correct. They are not finite Gaussian intervals across \(f=0\), nor full environmental boundary energies. The R1 mass is an action source/metric parameter with a scalar optical contribution; the Schwarzschild dictionary is correctly refused for R1. Neither representation adds a second potential, and a fitted mass does not determine a Hopf state or horizon.

The independent physical-unit point-lens test uses nominal solar GM, exact c and parsec units independently of the package lens helpers. It checks images, flux and delay against \(\theta_E^2=4GM D_{ls}/(c^2D_lD_s)\), \(\Delta t=4GM(1+z_l)h/c^3\), and \(\ln R=4\operatorname{asinh}(u/2)\). It passed. This checks arithmetic and units, not the accuracy of an astrophysical forecast.

## Executed evidence and primary references

Focused command from `product/`:

```text
python -m pytest tests/test_physics_admission.py tests/test_bhsm_interpretation.py tests/test_inference_contract.py::test_independent_point_lens_physical_units -q
32 passed in 7.27s
```

The two new near-threshold cases exercise motion and intrinsic evolution independently. The earlier 30-test run passed before the speed correction. The five-mode Cartesian Gram calculation above was separately executed and passed. Existing scientific scripts were replayed with their receipt/CSV writes intercepted in memory, preserving historical artifacts: projection identifiability PASS; perturbed mass estimator PASS (maximum Cartesian/scalar difference 3.9968e-15); point-lens invariant PASS (maximum mass-ratio error 2.8866e-15, stationary residual 7.4476e-16, convergence-control error 6.6613e-16). These are internal arithmetic checks; small residuals are not physical precision claims.

Primary-source checks performed during this review:

- [Brown and York, Phys. Rev. D 47, 1407 (1993)](https://arxiv.org/abs/gr-qc/9209012): action-derived boundary energy uses the mean curvature of the embedded enclosing surface and has the ADM limit. Bibliographic metadata and abstract were checked; the exact spherical expression and inverse above were independently derived here, not claimed as a fetched full-text quotation.
- [Muñoz et al., Phys. Rev. Lett. 117, 091301 (2016), equations 1--3](https://arxiv.org/html/1605.00008v2): direct full-text check of the Einstein radius, point-mass delay and flux ratio. The HTML carries a regenerated display date; version metadata and journal citation identify the 2016 paper.
- [Turyshev and Toth, Phys. Rev. D 105, 024022 (2022)](https://arxiv.org/abs/2107.13126): the abstract and metadata confirm the static harmonic STF projection's two transverse parameters. This supports the harmonic control, not a published proof of the screened rank-three result, which is derived above.

## Release scope and provenance

No remaining blocking algebraic defect was located in these reviewed claims after the fixes. The reviewed contribution is a BHSM-interpreted ordinary exterior reconstruction plus an explicitly conditional R1 response, with exact information losses and sufficient retained-model admission. It is not unique microscopic identification, a black-hole horizon solution, an empirical deformation detection, a UV stability theorem, or observational interval calibration. The 64-draw synthetic experiment is reviewed separately by the statistics lane. Main introduction/conclusion and workflow wording suggestions were sent to the root agent for integration; those files were not edited in this lane.

Review snapshot HEAD: `f737d30e7bd162e97ffaa38c621396d3dfa995d1`; the owned fixes below were present as working-tree changes. SHA-256 values bind the reviewed source, not an unbuilt wheel or a later PDF:

| Source | SHA-256 |
|---|---|
| `product/bhtracker/physics_admission.py` | `eb89ef40f95128078df390ce813c312ad302b1494424d57faea3191cafa58e60` |
| `product/tests/test_physics_admission.py` | `293bc4c49a816e1af64dc07ca8fd85a947fe63eefcf9157b5558214699d4e31f` |
| `product/bhtracker/interpretation.py` | `8b898d80d7cdb3f9c3d1a2bd929372b92c2e575827025013c0c5dff232c859c5` |
| `product/tests/test_bhsm_interpretation.py` | `60912091ddcb69167cbade03b76caa91ecfc934a8ef4391dd135b23060319851` |
| `product/tests/test_inference_contract.py` | `82fb1914151351df49abdbbe73aaee2e126f76ff4fed2875bedb72a4b5a7e4d4` |
| `manuscript/admission_bound.tex` | `e40fa679a31d74f631e98d5e851abddae911648d4fa10c340d5c3eb06a1683c8` |
| `manuscript/projection_theorem.tex` | `16d5148a7ac76f95296313a9f08f765d7076f71154fba26cc2ac669e61c5dbc7` |
| `manuscript/bhsm_interpretation.tex` | `6dc57ff854d8570279b9791b6d7d92b4fd138c9845f9734f3cea9b30fbe64423` |
