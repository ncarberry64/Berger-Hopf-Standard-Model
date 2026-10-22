# Independent internal review of the ordered state response

This is an AI-assisted internal check, not external peer review. Reviewed `code/rotation_response.py` and its inherited `angular_optical_response.py` read-only, and independently executed `review/independent_rotation_check.py`. The latter uses analytic synthetic tides; it does not validate the microscopic BHSM-to-R1 identification.

## Algebra and signs

With `Z=diag(1,-1)`, `X=[[0,1],[1,0]]`, `J=ZX`, one has `XZ=-J`, `[Z,X]=2J`. Declare

\[
D''+KD=-\epsilon T_1D-\epsilon^2T_2D+O(\epsilon^3),\quad
T_1=c[(w\cdot u)Z+(w\cdot v)X],\quad c=\sqrt2\mathcal N K,
\]

on a smooth isotropic closed-background segment `[a,b]`, with `D(a)=0`, `D'(a)=I`, and `S(x)=sin(sqrt(K)x)/sqrt(K)`. Expanding `D=S I+epsilon D1+epsilon^2 D2+...` gives

\[
G''+KG=cwS,\qquad D_1=-(G\cdot u)Z-(G\cdot v)X,
\]

\[
\operatorname{skew}D_2''+K\operatorname{skew}D_2
=c[(w\cdot u)(G\cdot v)-(w\cdot v)(G\cdot u)]J.
\]

Thus the implemented matrix equation `B''+KB=c(wG^T-Gw^T)` has the correct sign. With the code returning `B(b)/S(b-a)`, its dimensionless coefficient is

\[
\omega_2=u^TBv
=\frac{c^2}{S(b-a)}\int_a^b dt\int_a^t dr\,
S(b-t)S(t-r)S(r-a)
\{[w(t)\cdot u][w(r)\cdot v]-[w(t)\cdot v][w(r)\cdot u]\}.
\]

This is path ordering of two symmetric optical tides; it is not optical twist. `D'^T D-D^T D'=0` remains true, and `D'D^-1` is symmetric wherever D is invertible. Nonsymmetry of D itself is compatible with this identity.

Any symmetric `T2` contributes `-S T2` to D2, whose Green integral is symmetric. Therefore the leading antisymmetric coefficient requires only the first-order tide **on an isotropic smooth reference segment with D0=S I**. This is a useful robustness statement; it does not constitute a full second-order distance, magnification, shear or time-delay calculation. It does not apply directly to a reference bundle already containing an order-one anisotropic strong lens.

## Independent executed controls

For the synthetic analytic provider `c=1`, `w=(1,t,0,0,0,0)`, `K=0.3`, segment `[0,1]`, the response ODE returns `B01=-0.0028595982197431274`. Independently nested scalar quadrature returns `-0.002859598219743126`, difference `1.30e-18`. The matrix is antisymmetric to stored precision. The direct original matrix ODE gives amplitude-even coefficient errors `2.3843e-9`, `5.9608e-10`, `1.4902e-10` at amplitudes `.04,.02,.01`, consistent with quadratic convergence of the rescaled coefficient. A near-flat synthetic test matches the exact `-1/360` result within `2.65e-12`. This control deliberately holds c fixed by rescaling the test normalization and is **not** the physical K→0 limit of the normalized closed R1 harmonics. A finite rotating-tide run has nonzero Jacobi skew `-1.0875e-4` and zero stored Wronskian residual.

## State and physical-chain conditions

The recovered R1 effective system admits six independent normalized initial coordinates for every real n=2 harmonic. Assigning distinct u and v to the nodal plus/cross harmonics retains this admitted freedom. It adds no scalar degree of freedom or selected statistical state. Common spatial profile means `v=lambda u`, which forces every commutator and the bilinear to vanish. Independent states permit nonzero rotation but do not guarantee it: proportional Weyl histories, an optical null direction, symmetry or integrated cancellations can still annihilate `u^T Bv`.

The nodal fields have vanishing scalar value and first spatial gradient along their common central axis. Under the inherited first-order scalar metric/matter prescription, the background central ray and first-order redshift/endpoint shifts are therefore controlled more strongly than on a generic ray. That nodal statement should be proved using the actual chosen plus/cross STF matrices and stated boundary/velocity conditions. It must not be generalized to arbitrary n=2 rays. The second-order antisymmetric segment theorem above follows from symmetric tidal structure and the isotropic reference, not an assumption that all second-order metric perturbations vanish.

The microscopic record supplies action machinery and response contracts, but the evaluated common-domain BHSM-to-R1 metric normalization remains uncompleted in the recovered records. Thus the physical chain is: **supplied conditional R1 action and independently specified state coefficients → action-derived linear evolution/Weyl rows → exact nodal harmonic tidal projection → ordered Jacobi bilinear → conditional transfer/strong-lens map**. State coefficients and microscopic identification must remain explicit qualifications.

## Strong-lens and observable interpretation

The implemented fixed-source chart lens equation uses segment maps `M_ab=I-epsilon Gamma_ab` and `A=I-M_os^-1 M_ls L M_ol`, with symmetric local lens Hessian L. Its derivative

\[
\delta A=-(\Gamma_{os}-\Gamma_{ls})L+L\Gamma_{ol}
\]

has the correct algebra and can be antisymmetric already at first order through lens/environment coupling. This first-order chart antisymmetry is a different object from the smooth-segment `omega2`. Let `F=Gamma_ol+Gamma_os-Gamma_ls`; then

\[
\delta A-F(I-L)=\Gamma_{ol}L+L\Gamma_{ol}-F
\]

is symmetric. This validates the code's Fermat-weighted symmetry check and prevents confusing a nonsymmetric source-chart Jacobian with violation of a scalar Fermat potential.

Absolute image rotation is not a source-orientation independent astronomical measurement. The result requires declared observer/source screen conventions and a local lens/source model. Source-position transformations, source morphology/orientation, mass-sheet freedoms, distance conventions and line-of-sight freedom must remain in the interpretation. Multiple redshifts alone do not remove all these freedoms. Report the transfer bilinear and its null controls as the established object, and state which additional information would turn it into an inference.

## Novelty and scope verdict

The commutator mechanism, multi-plane rotation and nonsymmetric Jacobi maps are standard geometrical optics. The potential contribution is the reproducible six-coordinate R1 bilinear on a normalized closed n=2 sector, the precise common-profile null restriction, and its fixed-source lens/Fermat consistency. The microscopic BHSM derivation, a Berger-squashed spacetime/Hopf-fibre effect, a state amplitude, and an observational detection have not been established by these checks. Numerical singular values of B depend on the chosen state coordinate normalization; their magnitudes are not coordinate-free physical bounds. Independent direct ODE/quadrature agreement validates the declared transfer equations, not universal stability or the cosmological model.
