# First variation of the point-lens apparent-mass estimator

## Preparation, image labels and physical quantities held fixed

Use the reference point-mass Einstein angle theta_E and arrival-time scale

\[
\theta_E^2=\frac{4GM}{c^2}\frac{D_{ls}}{D_lD_s},\qquad
t_M=\frac{4GM}{c^3}(1+z_l).
\]

Hold the physical source, point mass M, distances, redshift, lens position and screen convention fixed while varying the additional local potential. This holds the dimensionless source y=beta/theta_E fixed. Let

\[
\tau_\epsilon(\mathbf x;\mathbf y)
=\tfrac12|\mathbf x-\mathbf y|^2-\ln|\mathbf x|
-\epsilon p(\mathbf x).
\]

The perturbing p is dimensionless in this lens potential convention; any physical worldtube/action amplitude must first be converted to this normalization. No horizon response, state amplitude or new coupling is selected by this derivation.

For u=|y|>0, continue the reference outer positive-parity minimum x_+ and inner negative-parity saddle x_- as epsilon varies. At epsilon=0 the plus image is brighter and earlier. Assume their Hessians remain nonsingular, their flux ordering does not reverse, and Delta tau=tau_-−tau_+ stays positive on the interval used. The ratio is R=|mu_+|/|mu_-|>1 and Delta t=t_M Delta tau. These are two **continued primary images**. Singular multipoles may create additional images near an excluded origin; this two-branch derivative neither proves their absence nor includes their flux in R.

## 1. Generic perturbation: image shifts must be included

At epsilon=0 define

\[
H_0(\mathbf x)=D^2\ln r
=\frac{I}{r^2}-\frac{2\mathbf x\mathbf x^T}{r^4},
\qquad A_i=I-H_0(\mathbf x_i).
\]

The stationary lens equation is

`x−y−grad ln r−epsilon grad p=0`.

Its derivative at a fixed physical source gives

\[
\boxed{\delta\mathbf x_i=A_i^{-1}\nabla p(\mathbf x_i).}
\]

Here and below delta is the coefficient of epsilon at zero. The **total** variation of the lens Jacobian, including displacement of the evaluation point, is

\[
\boxed{\delta A_i=-D^2p(\mathbf x_i)
-DH_0(\mathbf x_i)[\delta\mathbf x_i].}
\]

The needed third-derivative contraction is explicitly

\[
DH_0(\mathbf x)[\mathbf v]
=-\frac{2(\mathbf x\cdot\mathbf v)}{r^4}I
-\frac{2(\mathbf v\mathbf x^T+\mathbf x\mathbf v^T)}{r^4}
+\frac{8(\mathbf x\cdot\mathbf v)}{r^6}\mathbf x\mathbf x^T.
\]

For either signed magnification mu_i=1/det A_i, sign is locally constant away from a critical curve, so

\[
\boxed{\delta\ln|\mu_i|
=-\operatorname{tr}(A_i^{-1}\delta A_i).}
\]

Keeping only D²p while dropping the shift term is generally incorrect even at first order. It changes the compact-quadrupole response and can falsely turn an ordinary alignment/convergence effect into an apparent mass variation.

Fermat stationarity cancels the image-position variation in each first-order arrival time:

\[
\delta\tau_i=-p(\mathbf x_i),\qquad
\boxed{\delta\Delta\tau=p(\mathbf x_+)-p(\mathbf x_-).}
\]

There is no analogous cancellation in the magnification Hessian. Define

\[
\delta\ln R=\delta\ln|\mu_+|-\delta\ln|\mu_-|.
\]

For the reference point lens, set s=sqrt(u²+4) and

\[
h(u)=\tfrac12us+2\operatorname{asinh}(u/2),\qquad
\ln R_0=4\operatorname{asinh}(u/2).
\]

Since h'=s and (ln R_0)'=4/s, the point-lens estimator applied to the perturbed pair has first variation

\[
\boxed{\delta\ln M_{\rm app}
=\frac{p(\mathbf x_+)-p(\mathbf x_-)}{h(u)}
-\frac{u^2+4}{4h(u)}\,
\left[\delta\ln|\mu_+|-\delta\ln|\mu_-|\right].}
\]

This formula is exact at first order for any C³ perturbing potential near the two primary images. It uses the same fixed source and body throughout. A physical change of M or the redshift/distance time prefactor must be added separately rather than hidden in p. At fixed redshift a true infinitesimal point-mass rescaling is correctly represented by p=ln r and gives delta ln M_app=1 per unit fractional mass perturbation in these reference coordinates.

## 2. Radial quadrupole: an explicit one-dimensional response operator

Let

\[
p(r,\varphi)=q(r)\cos[2(\varphi-\varphi_q)],
\quad c_2=\cos[2(\varphi_s-\varphi_q)],
\quad s_2=\sin[2(\varphi_s-\varphi_q)].
\]

The two reference image angles differ by pi, so both have the same c2,s2. Their radii are

\[
r_+=\tfrac12(u+s),\qquad r_-=1/r_+.
\]

In a local radial/tangential orthonormal basis at an image, write

\[
a_r=1+r^{-2},\qquad a_t=1-r^{-2}.
\]

The displacement components are

\[
\delta x_r=\frac{q'c_2}{a_r},\qquad
\delta x_t=-\frac{2q s_2}{r a_t}.
\]

The perturbing Hessian in that basis is

\[
D^2p=\begin{pmatrix}
q''c_2&-2(q'/r-q/r^2)s_2\\
-2(q'/r-q/r^2)s_2&(q'/r-4q/r^2)c_2
\end{pmatrix}.
\]

For the trace entering the magnification variation, the tangential shift contributes off-diagonal terms only. The radial shift contributes `DH0_rr=2 delta x_r/r³` and `DH0_tt=−2 delta x_r/r³`. Consequently

\[
\boxed{\delta\ln|\mu_i|=c_2\mathcal F_q(r_i),}
\]

\[
\boxed{\mathcal F_q(r)=
\frac{q''}{a_r}
+\frac{q'/r-4q/r^2}{a_t}
+\frac{2q'}{r^3a_r}\left(\frac1{a_r}-\frac1{a_t}\right).}
\]

The last term is precisely the position-shift contribution. Thus the full first-order tracker response is

\[
\boxed{\delta\ln M_{\rm app}
=c_2\mathcal K_q(u),}
\]

\[
\boxed{\mathcal K_q(u)=
\frac{q(r_+)-q(r_-)}{h(u)}
-\frac{s^2}{4h(u)}
\left[\mathcal F_q(r_+)-\mathcal F_q(r_-)\right].}
\]

The operator is linear in q. Given an action-derived, normalized q(r) and its two derivatives on the actual image annuli, it produces a prediction without choosing an unrelated optical coefficient. At c2=0 this estimator has no first-order quadrupole response, although the images can have tangential shifts; a zero estimator response does not mean no lens perturbation.

## 3. Compact quadrupole and external shear: closed reference responses

For any power q=r^k,

\[
\mathcal F_{r^k}(r)=r^k\left[
\frac{k(k-1)}{r^2+1}+\frac{k-4}{r^2-1}
-\frac{4k}{(r^2+1)^2(r^2-1)}\right].
\]

In particular,

\[
\mathcal F_{r^2}=-\frac{4r^2(r^2+3)}{(r^2-1)(r^2+1)^2},\quad
\mathcal F_{r^{-2}}=-\frac{4(3r^2+1)}{r^2(r^2-1)(r^2+1)^2}.
\]

Define the positive alignment function

\[
K_*(u)=\frac{(u^2+4)^{3/2}}{u h(u)},\qquad u>0.
\]

Using r_-r_+=1 gives the exact identities

\[
\boxed{\mathcal K_{r^2}=K_*,\qquad
\mathcal K_{r^{-2}}=(u^2+1)K_*.}
\]

An ordinary compact projected quadrupole written `delta psi=B r^(-2) cos 2(phi−phi_B)` therefore contributes

`delta ln M_app=B (u²+1) K_*(u) cos 2(phi_s−phi_B)`.

An external shear in the convention `delta psi=(gamma/2) r² cos 2(phi−phi_gamma)` contributes

`delta ln M_app=(gamma/2) K_*(u) cos 2(phi_s−phi_gamma)`.

These fix sign and factor-of-two conventions. At a single alignment the amplitudes can absorb their different coefficients. Several sufficiently separated u values can distinguish these two fixed shapes in principle, but that is not a theorem against a general angular/radial nuisance family.

## 4. A nontrivial exact first-order null and inference design

Distinct radial potentials need not give distinct mass-estimator histories. A constant radial quadrupole q=1 has

\[
\mathcal F_1=-4/(r^2-1),\qquad
\mathcal K_1=K_*.
\]

It follows that

\[
\boxed{\mathcal K_{r^2-1}(u)=0\quad\text{for all }u>0.}
\]

The perturbation `(r²−1)cos 2phi` is therefore invisible to this scalar estimator at first order for every primary-image alignment. It is not a zero lens perturbation: its image shifts, delay and flux ratio generally change. The cancellation is only in this particular statistic. It is also only a first-order null; an explicit finite-perturbation check gives a nonzero quadratic departure. This is a local smooth-potential counterexample on the image annuli, not a claim that an arbitrary compact positive source generates this entire radial profile. Physical source and boundary admissibility require their own checks.

Accordingly an inference experiment must compare the **evaluated response functions**, not just the different symbols in their source potentials. For a prescribed trajectory with freely fitted ordinary quadrupole/shear orientation and amplitude, the natural first-order nuisance columns are

\[
K_*(u)\cos2\varphi_s,\quad K_*(u)\sin2\varphi_s,
\quad (u^2+1)K_*(u)\cos2\varphi_s,
\quad (u^2+1)K_*(u)\sin2\varphi_s.
\]

An action-derived candidate supplies its own K_q times the same angular basis if it is a scalar quadrupole. Only the component outside the justified nuisance column space is identifiable by M_app in that experiment. A narrow u range can make different columns nearly collinear, and a constant source angle constrains only one projected orientation combination. The design matrix, its normalization and its singular values must therefore be reported. Numerical rank alone does not demonstrate a physical prior or defeat an unrestricted line-of-sight potential.

The fuller delay, separate geometric fluxes and astrometric shifts can retain information discarded by M_app; they require a consistently declared data model. Choosing a nuisance family after seeing an apparent separation would overstate the result. No observational claim or selected black-hole surface amplitude follows from these formulas.

## 5. Independent checks and approximation domain

`check_perturbed_mass_estimator.py` contains exact symbolic checks, a Cartesian matrix calculation of the total Hessian variation, and an independent **on-axis polynomial branch test**. The polynomial test uses exact stationary equations for finite even radial powers and continues the two reference roots; it is not a competing general nonlinear lens solver. It compares central finite differences of image positions, signed magnifications and Fermat delays to the analytic first variation.

Structural controls include a constant potential, a uniform deflection, isotropic convergence and a point-mass rescaling. The first three must leave the estimator unchanged at first order; a unit fractional mass perturbation must give unity. Compact/external quadrupoles, a mixed polynomial profile and the nontrivial null above test the actual optical projection rather than simply echoing the formula.

The derivation assumes geometric optics, a point source, a stationary thin-lens potential for the relevant emission pair, weak-field image paths and noncritical continued primary branches. It does not describe photon rings, horizon evolution, total flux from newly created images, time-dependent source emission effects, extinction or unresolved independent microlensing. Those limitations belong to the declared observable and are not numerical uncertainty bars on an unknown action coupling. All checks here are internal AI-assisted verification.
