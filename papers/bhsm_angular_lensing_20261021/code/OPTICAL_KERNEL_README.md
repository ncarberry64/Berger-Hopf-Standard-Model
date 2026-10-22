# Executed six-state angular optical kernel

`angular_optical_response.py` computes the first-order tracefree cosmological
Jacobi maps for the full scalar n=2 harmonic family on the frozen closed R1
background. The executable result is `artifacts/temporal/angular_response.json`.
This is a conditional response to specified normalized initial coefficients;
it does not select a physical state or an observed amplitude.

## Reproduction

From the new paper's root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/angular_optical_response.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/audit_nodal_angular_geodesic.py
```

Python 3.12, NumPy 2.3.5 and SciPy 1.17.0 were used for this execution. The
algorithms use ordinary NumPy/SciPy APIs; no telescope data are read.

## Source and state

The vendor directory contains exact Git blobs from
`ncarberry64/Manuscript-Generation@06cf7c1b85d6605bfee0cc0d07fb2af86a66cae9`.
`vendor_original/SOURCE_MANIFEST.json` records Git identities, SHA-256 hashes,
byte lengths and immutable source URLs. Only the background fields of the
original prediction manifest are consumed. Its historical calibration and
forecast entries are not inputs to this calculation.

The physical anchor at z=2.1 is

`(zeta, Pi2_reference, delta_m_ADM, delta_r_ADM, v_m_ADM, v_r_ADM)`.

The provider reconstructs the full canonical six-state initial data from the
current action rows; it does not identify the reference momentum Pi2 with the
full canonical momentum p_zeta. Each normalized harmonic has these six
coordinates. A general n=2 initial state therefore is not universally a
two-parameter family.

The scalar metric convention is

`ds^2 = a^2[-(1+2 Phi)deta^2 + (1-2 Psi)gamma_ij dx^i dx^j]`,

with Weyl combination `Phi+Psi`. The seven row outputs from `provider.rows(N)`
are `(Phi,Psi,pi,delta_m,v_m,delta_r,v_r)` and act on the six physical anchor
coordinates. Lengths use c/H0; the state and harmonic normalizations use the
same H0=1 convention as the action provider.

## Normalized angular family

The real STF4 matrices A have `Tr(A_i A_j)=delta_ij`. With unit embedding
coordinates X on S3 and radius R=K^(-1/2), the normalized harmonics are

`Q_A = N X^T A X`, `N=sqrt(6/(pi^2 R^3))`.

The order is one angular monopole, three dipoles, then five quadrupoles. This
is a decomposition within the same n=2 eigenspace; no higher n modes are added.
For STF3 C with `Tr(C^2)=1`,

`Q_C=N sin^2(sqrt(K)chi) n^T C n`,

and a radial orthonormal screen E has

`H_C=2 E^T C E+(n^T C n)I`.

The tracefree spatial Hessian is exactly `N K H_C`; radial dependence cancels.
The monopole and dipole sectors have zero tracefree screen Hessian. These are
first-order smooth-background selection rules, not a zero-shear assertion
about a complete galaxy lens.

## Applied kernel

For observer-centered background radial coordinate chi, an interval a to b has

`d_ab=S_K(chi_b-chi_a)/(1+z_b)`

and six-vector

`g_ab = (N K/S_K(b-a)) integral_a^b S_K(b-chi) S_K(chi-a) [phi(chi)+psi(chi)] dchi`.

The physical tracefree map is `D_ab^TF=-d_ab (g_ab dot q) H_C`. There is no
additional factor of a_a. Measured-redshift endpoint motion and local clock or
aberration corrections multiply the background identity at this order and
do not change this tracefree formula. They are required in a generic full
distance perturbation; this module does not claim that the Weyl term alone
supplies the generic trace or delay.

The nodal profile `C=diag(1,-1,0)/sqrt2`, central direction z, has Q and its
gradient zero along the central ray. Its independent original angular
geodesic audit is supplied separately. The full image/time-delay calculation
must state its paraxial encounter and fixed-source assumptions separately.

## Executed numerical checks

Four lens/source pairs were calculated: (0.3,1.0), (0.3,0.6), (0.5,1.5),
(0.8,2.0). All remain inside the z=2.1 action anchor domain.

- Physical anchor reconstruction: maximum absolute defect 2.22e-16.
- Original action constraint residual, scaled by max(1, canonical state norm):
  maximum 1.46e-11 over 37 sampled epochs and all six columns.
- Green-function quadrature versus an independent forced Jacobi ODE:
  maximum absolute g difference 1.45e-14 over all twelve segments.
- 801 to 1601 temporal samples plus tighter propagator integration:
  maximum absolute g difference 1.47e-13.
- Angular shear design on 31 fixed generic directions: rank five; monopole
  and dipole outputs vanish to 2.22e-16.
- Original angular Euler momentum integration for the nodal metric:
  complex-step derivatives agree to 2.08e-15; weak real central differences
  at half step agree to 5.70e-13 for all six columns and three segments.
- The constant-Weyl curved-space Green integral is independently checked
  against `[S_K(L)-L cos(sqrt(K)L)]/(2K)`.

These quantify implementation accuracy for the stated equations. They do not
establish microscopic BHSM normalization, observational validation, a global
stability theorem, or a unique physical state.

## Illustrative seed qualification

For the coefficient vector q=(0,0,0.001,0,0,0), exact angular maxima sampled
at 2001 radial points give maximum 2|Phi| of 3.26782e-6 through z=1 and
2.03826e-5 through z=2. The corresponding maximum first-order matter speeds
are 4.88720e-6 and 1.71552e-5 in units of c. These are sampled radial maxima,
not certified continuum bounds. The number 0.001 is a normalized harmonic
coefficient, not a spatially uniform 0.1% density perturbation.
