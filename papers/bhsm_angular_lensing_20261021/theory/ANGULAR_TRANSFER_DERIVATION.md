# Angular selection and shared-state time-delay response on closed spatial sections

## Status and scope

This is a new analytic derivation for the separate BHSM angular-lensing paper. It uses the retained six-state R1 metric response as a declared effective realization of the BHSM program. It does not identify a microscopic BHSM preparation, select a preferred cosmological axis, infer a physical amplitude, or establish observational validation.

The calculation is first order in a smooth scalar metric perturbation about closed FLRW. A local, weak, thin galaxy lens is treated with the standard distance-matrix encounter formalism, with infinitesimal bundles propagated about a common fiducial null ray. The finite matrix completions used to check derivatives are numerical controls; no second-order metric or global nonlinear BHSM solution is supplied.

The retained source is `Manuscript-Generation@06cf7c1b85d6605bfee0cc0d07fb2af86a66cae9`, especially `docs/STRONG_LENSING_TRANSPORT_20261020.md` and `code/action_native_matter_n2.py`. The new work uses the harmonic family and the relevant dynamical provider; no HE 0435 photometry, image pixels, PSFs, or fitted detector response enters these results.

## 1. The complete normalized n=2 scalar sector

Let the spatial metric and volume be

\[
\gamma=d\chi^2+S_K^2(\chi)d\Omega^2,\qquad
S_K(\chi)=R\sin(\chi/R),\qquad K=R^{-2}>0,
\]
\[
dV_\gamma=R^3\sin^2u\,du\,d\Omega,\qquad u=\chi/R.
\]

Embed the unit three-sphere in four Euclidean coordinates,

\[
X^0=\cos u,\qquad X^i=\sin u\,n^i,\qquad n^in_i=1.
\]

For a real symmetric tracefree four-by-four matrix A, define

\[
Q_A=\mathcal N X^I A_{IJ}X^J,
\qquad \mathcal N=\sqrt{\frac{6}{\pi^2R^3}}.
\tag{1}
\]

The polynomial is harmonic and homogeneous of degree two in the ambient Euclidean space. Restriction to the sphere therefore gives

\[
D^2Q_A=-8KQ_A.
\tag{2}
\]

The exact fourth moment of the uniform unit three-sphere is

\[
\left\langle X_I X_J X_K X_L\right\rangle
=\frac{\delta_{IJ}\delta_{KL}+\delta_{IK}\delta_{JL}
+\delta_{IL}\delta_{JK}}{24}.
\]

Since its dimensional volume is 2 pi squared R cubed,

\[
\int Q_AQ_B\,dV_\gamma=\operatorname{Tr}(AB).
\tag{3}
\]

Thus any Frobenius-orthonormal STF matrix basis produces nine globally normalized modes. The dimension is 4(4+1)/2 minus one, or nine.

Write the spatial three-by-three block as

\[
A_{ij}=C_{ij}-\frac{A_{00}}3\delta_{ij},\qquad
\operatorname{Tr}C=0.
\]

Then

\[
\frac{Q_A}{\mathcal N}
=A_{00}\left(\cos^2u-\frac13\sin^2u\right)
+2A_{0i}\sin u\cos u\,n^i
+\sin^2u\,n^iC_{ij}n^j.
\tag{4}
\]

This is the observer-centered angular decomposition into one monopole, three dipoles, and five quadrupoles: 1+3+5=9. The index n=2 labels the scalar harmonic on S3; the angular indices ell=0,1,2 label the observer's S2 sky and must not be confused with n.

One convenient orthonormal basis is

\[
Q_0=\frac{4\cos^2u-1}{\sqrt2\,\pi R^{3/2}},
\qquad
Q_{1i}=\frac{\sqrt3}{\pi R^{3/2}}\sin(2u)n_i,
\tag{5}
\]
\[
Q_{2A}=\mathcal N\sin^2u\,n^TC_A n,\qquad A=1,\ldots,5,
\tag{6}
\]

where Tr(C_A C_B)=delta_AB. A concrete choice for C_A is

- diag(1,-1,0)/sqrt(2);
- diag(1,1,-2)/sqrt(6);
- (e_x e_y^T+e_y e_x^T)/sqrt(2);
- (e_x e_z^T+e_z e_x^T)/sqrt(2);
- (e_y e_z^T+e_z e_y^T)/sqrt(2).

The former axial profile is Q_1z. The quadrupoles are other components of the same retained spatial eigenspace, not an independently invented higher harmonic.

## 2. The state dimension and the optical potential

For every normalized spatial harmonic alpha, the current coupled provider has six initial coordinates

\[
y_{j\alpha}=(\zeta,\Pi_2,\delta_m^{\rm ADM},\delta_r^{\rm ADM},
v_m^{\rm ADM},v_r^{\rm ADM})_{j\alpha}.
\tag{7}
\]

On the isotropic background, the same temporal transfer applies independently to each harmonic. Write

\[
\Phi(\eta,x)=\sum_{j=1}^{6}\sum_{\alpha=1}^{9}
\phi_j(\eta)y_{j\alpha}Q_\alpha(x),\qquad
\Psi(\eta,x)=\sum_{j,\alpha}\psi_j(\eta)y_{j\alpha}Q_\alpha(x).
\tag{8}
\]

Here the metric convention is

\[
ds^2=a^2(\eta)\{-(1+2\Phi)d\eta^2+(1-2\Psi)\gamma_{ij}dx^idx^j\}.
\tag{9}
\]

The scalar optical potential is Phi+Psi in this convention. Define w_j=phi_j+psi_j; equality of the two metric potentials is not imposed. The coordinates and transfer coefficients inherit their units from the canonically normalized provider. A dimensionful volume-normalized Q must not be combined with amplitudes silently treated as unitless.

The fully unrestricted retained initial state has 6 times 9, or 54, coefficients. A single shared spatial profile is a physical restriction on that state; it is not a consequence of the existence of six temporal equations.

## 3. Angular optical selection rule

Let E be a three-by-two orthonormal screen matrix with E^T E=I and E^T n=0. Along an unperturbed observer-centered radial ray, for a scalar f(chi)Y_ell,m(n),

\[
\left(D_{\hat A}D_{\hat B}[fY]\right)_{\rm TF}
=\frac{f}{S_K^2}
\left(\nabla_A\nabla_B Y-\frac12s_{AB}\Delta_\Omega Y\right).
\tag{10}
\]

The omitted radial connection term is (S'_K/S_K)f'Y times the screen identity, so it is pure trace. For ell=0 the angular derivative vanishes. For ell=1,

\[
\nabla_A\nabla_B Y_{1m}=-s_{AB}Y_{1m},\qquad
\Delta_\Omega Y_{1m}=-2Y_{1m},
\]

and the bracket vanishes identically. Therefore all four monopole/dipole spatial modes have zero first-order smooth-background optical shear along every observer-centered radial background ray. Rotating the existing dipole away from its axis does not activate first-order spin-two shear.

This is a statement about the smooth scalar perturbation. It is not a claim of zero galaxy-lens shear, zero convergence, zero redshift response, or zero time-delay response. Deflected paths, coupling to a strong lens beyond the adopted distance-matrix/tidal approximation, and higher-order smooth perturbations are distinct calculations.

For a quadrupole C, let

\[
h_C=n^TCn,\qquad
H_C(n)=2E^TCE+h_CI_2.
\tag{11}
\]

H_C is symmetric and tracefree. The angular Hessian of h_C is 2E^TCE-2h_C I, whose tracefree part is H_C. Since S_K squared equals R squared sin squared u,

\[
\boxed{(D_{\hat A}D_{\hat B}Q_C)_{\rm TF}
=\mathcal N K H_C(n).}
\tag{12}
\]

The radial factor cancels exactly. The first-order quadrupole tidal shape is fixed along a radial background ray; all radial and time dependence enters the six temporal metric responses.

## 4. Three physical Jacobi maps

Let chi_a<chi_b be background locations of observer, lens, or source, with endpoints defined by fixed measured redshifts. The background map from a physical angle at a to physical separation at b is

\[
d_{ab}=a_b S_K(\chi_b-\chi_a).
\tag{13}
\]

The physical Sachs initialization is D_ab(lambda_a)=0 and D'_ab(lambda_a)=omega_a I, using one observer-normalized affine parameter. At the FLRW background, dchi/dlambda=a^{-2} and omega_a=a_a^{-1}. Writing the physical separation as a times the conformal separation therefore gives a unit conformal derivative at chi_a. No extra a_a or redshift factor belongs in (13).

Linearizing the Sachs equation around the background, the tracefree conformal separation obeys

\[
(\partial_\chi^2+K)\delta\widetilde D_{ab}^{\rm TF}
=-S_K(\chi-\chi_a)
\left[D_\perp D_\perp(\Phi+\Psi)\right]_{\rm TF}.
\tag{14}
\]

The sign follows the convention D=d[(1-kappa)I-Gamma]: a positive Hessian of the optical potential reduces the separation in its positive-curvature direction. The Green function of partial_chi squared plus K is S_K(chi_b-chi). Equations (12)-(14) give

\[
\boxed{
\Gamma_{ab}(n)=\sum_{j=1}^{6}\sum_{A=1}^{5}
g_{ab,j}\,y_{jA}H_{C_A}(n),}
\tag{15}
\]
\[
\boxed{
g_{ab,j}=\frac{\mathcal NK}{S_K(\chi_b-\chi_a)}
\int_{\chi_a}^{\chi_b}
S_K(\chi_b-\chi)S_K(\chi-\chi_a)
w_j(\eta_o-\chi)\,d\chi.}
\tag{16}
\]

The dimensional physical tracefree map is delta D_ab^TF=-d_ab Gamma_ab. This applies independently to ol, os and ls; D_ls is not D_os minus D_ol.

### Endpoint and frame terms

At first order, moving measured-redshift endpoints changes the isotropic background map by a scalar times I. The variation of the moving vertex conditions is also isotropic. Multiplying an already first-order tracefree integral by a first-order endpoint or clock correction would be second order. The endpoint factors in the Green-function integrand vanish at the endpoints. Thus the tracefree response (15) is complete at the retained order even though the full trace requires the frequency, radial-event, local-scale and observer/source-frame terms.

Local boosts act conformally on infinitesimal celestial angles and introduce no physical first-order spin-two distortion of an initially circular bundle. Screen rotations are basis choices; the matrices must be compared after parallel transport in a common screen. No independent Doppler or aberration multiplier may be appended to (16).

## 5. Exact shared-state statements

### 5.1 Which modes shear can access

The linear smooth-shear operator annihilates all 6 times 4 monopole/dipole state coefficients. It can depend on at most 30 quadrupole coefficients before observational nuisance projection. At a fixed redshift pair the full-sky shear is a pure E-type ell=2 pattern with five coefficients. The number of inferable combinations can be smaller because of temporal-kernel rank, incomplete sky sampling, or lens/source nuisance freedoms.

For several vertex/redshift pairs r, the five angular coefficients obey

\[
S_{rA}=\sum_{j=1}^{6}G_{rj}y_{jA},\qquad G_{rj}=g_{r,j}.
\tag{17}
\]

Every independently established left-null vector l of G yields l^T S_{\cdot A}=0. Numerical conditioning and physical units must be treated before interpreting an approximate null vector. Merely counting six equations or many observations does not establish full rank or observable identifiability.

### 5.2 A single common quadrupole profile

If all six initial components share one fixed physical quadrupole C, y_jA=y_j c_A, then

\[
\Gamma_{ab}=(g_{ab}\cdot y)H_C.
\tag{18}
\]

For a common screen, every pair of segment shears is collinear in its two shear components:

\[
\gamma_{1,ab}\gamma_{2,cd}-\gamma_{2,ab}\gamma_{1,cd}=0.
\tag{19}
\]

This allows arbitrary six-component temporal preparation along the same profile. It does not require a historical two-state reduction. It is conditional on common spatial preparation; a generic six-by-five quadrupole state need not satisfy (19). A vanishing segment shear has no defined orientation, although the determinant identity still holds.

These are forward-map consistency relations, not automatic direct astronomical observables. The physical Jacobi maps must be constrained with an actual observation model, including galaxy and source freedoms. A complete common-state test acts on the observable response after that nuisance model is specified.

## 6. Fermat-matrix response and the full stationary-delay derivative

For the standard weak thin encounter, define

\[
\beta=D_{os}^{-1}X_s,\qquad
T=(1+z_l)D_{ol}^{T}D_{ls}^{-1}D_{os},
\]
\[
ct(\theta)=\frac12(\theta-\beta)^TT(\theta-\beta)
-(1+z_l)\widehat\psi(D_{ol}\theta)+f(\beta).
\tag{20}
\]

Let D_ab=d_ab(I+E_ab), with E_ab symmetric to the retained first order, and let T_0=(1+z_l)d_ol d_os/d_ls. Then

\[
\frac{\delta T}{T_0}=E_{ol}+E_{os}-E_{ls}.
\tag{21}
\]

In particular, the tracefree part is -(Gamma_ol+Gamma_os-Gamma_ls). This identity is standard distance-matrix optics; the BHSM-specific content is the state-derived response in (15)-(16).

At a stationary image theta_i, its image-position variation drops out of the first derivative of its arrival time. Hold fixed measured redshifts, the transverse physical source X_s, and the local physical galaxy potential. Let v_i=theta_i-beta. Since delta beta=-E_os beta,

\[
c\,\delta t_i
=\frac12v_i^T\delta T v_i-v_i^TT_0\delta\beta
-(1+z_l)\widehat\alpha(d_{ol}\theta_i)^T
\delta D_{ol}\theta_i+\delta f.
\tag{22}
\]

Using the background lens equation (1+z_l)d_ol alpha_hat=T_0 v_i,

\[
\boxed{\frac{c\,\delta t_i-\delta f}{T_0}
=\frac12v_i^T(E_{os}-E_{ol}-E_{ls})v_i
+v_i^T(E_{os}-E_{ol})\beta.}
\tag{23}
\]

Subtract the two expressions to obtain a relative delay. The common source term cancels. Equation (23) includes the changing source angle and physical impact in the local potential. Using only delta T would omit both effects and would generally give an incorrect timing prediction.

## 7. A nodal quadrupole with a complete first-order SIS timing prediction

Choose

\[
C_\star=\frac1{\sqrt2}\operatorname{diag}(1,-1,0),
\qquad n_\star=e_z,
\qquad E=(e_x,e_y).
\tag{24}
\]

Then along the fiducial ray Q=0 and its entire first spatial gradient vanishes, while

\[
H_{C_\star}=\sqrt2\operatorname{diag}(1,-1).
\tag{25}
\]

All temporal derivatives of the potential evaluated on that ray vanish as well. The transverse Hessian has zero trace. Therefore the central frequency, radial geodesic, moving measured-redshift events, matter-frame velocities, local screen-scale correction and first-order trace of the Jacobi response vanish for this preparation. The nonzero first-order response is tracefree. This removes the need to borrow uncomputed trace terms for this particular benchmark.

Let the local physical lens be an SIS, with hat psi(x)=b|x|, b>0. Set the source physical displacement X_s=s e with s>0, e=(cos varphi,sin varphi), and hold b,s fixed across preparations. On the background,

\[
\beta=\frac{s}{d_{os}},\qquad
\theta_E=\frac{b d_{ls}}{d_{os}},\qquad
\theta_\pm=(\beta\pm\theta_E)e,
\]
\[
\Delta t_0=t_- - t_+
=\frac{2T_0\theta_E\beta}{c}
=\frac{2(1+z_l)bs}{c}\frac{d_{ol}}{d_{os}}.
\tag{26}
\]

Assume 0<beta<theta_E and fixed noncritical image branches. Then v_+=theta_E e and v_-=-theta_E e. The quadratic term in (23) is the same for both images and cancels. Consequently

\[
\boxed{
\frac{\delta\Delta t}{\Delta t_0}
=e^T(E_{ol}-E_{os})e
=e^T(\Gamma_{os}-\Gamma_{ol})e.}
\tag{27}
\]

For the common C_star preparation,

\[
\boxed{
\frac{\delta\Delta t}{\Delta t_0}
=\sqrt2\,[(g_{os}-g_{ol})\cdot y]\cos(2\varphi).}
\tag{28}
\]

The lens-to-source shear cancels in this fixed-physical-source SIS delay response. This cancellation does not remove D_ls from the image locations or from more general lens profiles. It also does not apply unchanged to a comparison holding angular source position fixed.

Equation (28) is a complete first-order conditional prediction of the stated smooth quadrupole plus local SIS experiment. It predicts a sign reversal under a 90-degree source rotation and zero first-order delay change at 45 degrees to the quadrupole principal axes. It does not select y or predict an absolute observed amplitude. Terms quadratic in the smooth perturbation, galaxy evolution, finite lens thickness, and finite-field departures from the adopted paraxial encounter are outside this derivation.

## 8. Scientific interpretation and prior art

The angular derivative and distance-matrix methods are established optics. The new paper's contribution is the explicit normalized retained spatial family, its complete angular selection rule, its composition with the current six-state effective evolution, and the reproducible conditional timing relationship for a well-specified preparation. This is not a proof that these effects identify BHSM uniquely: lens ellipticity, source geometry, convergence/shear and other freedoms must be assessed in the actual observable model.

The shared-profile relation (19), linear response constraints (17), and nodal timing law (28) are different statements. They must not be collapsed into a universal low-rank covariance prediction. A stochastic covariance additionally requires a specified source law and spatial coherence. One local noise type can supply independent increments at several locations and is not one global random amplitude. The current calculation supplies deterministic response coefficients.

### Primary references

1. P. Fleury, J. Larena, J.-P. Uzan, "Gravitational lenses in arbitrary space-times," Classical and Quantum Gravity 38 (2021) 085002. https://arxiv.org/abs/2011.04440 ; https://doi.org/10.1088/1361-6382/abea2d . General distance-matrix lens equation, time-delay function and observer/lens clock normalization.
2. F. Bernardeau, C. Bonvin, F. Vernizzi, "Full-sky lensing shear at second order," Physical Review D 81 (2010) 083002. https://arxiv.org/abs/0911.2244 ; https://doi.org/10.1103/PhysRevD.81.083002 . Sachs and full-sky spin-two framework and the scope of higher-order corrections.
3. P. Schneider, "Generalized multi-plane gravitational lensing: time delays, recursive lens equation, and the mass-sheet transformation," Astronomy and Astrophysics 624 (2019) A54. https://arxiv.org/abs/1409.0015 ; https://doi.org/10.1051/0004-6361/201424881 . Distance-matrix/Fermat and degeneracy context.
4. Retained effective metric/state source: https://github.com/ncarberry64/Manuscript-Generation/blob/06cf7c1b85d6605bfee0cc0d07fb2af86a66cae9/docs/STRONG_LENSING_TRANSPORT_20261020.md . Six-state physical anchor, metric-sign convention, measured-redshift endpoint and frame prescription.
5. Retained full spatial/environmental family: https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/00614fa0d479a2de78460ca061cc5304cdb610cf/museum/public/research/r1-coupled-environment-section.tex . Nine spatial harmonics, environmental transfer, common-profile assumptions and microscopic-normalization limits.
