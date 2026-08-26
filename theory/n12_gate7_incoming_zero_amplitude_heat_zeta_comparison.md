# Gate-7 incoming zero-amplitude heat--zeta comparison

Status: `FINITE_CORE_ZERO_AMPLITUDE_HEAT_COEFFICIENT_STRICTLY_DOMINATED_BY_ZETA`.

At zero incoming duration, the one-seam finite-core pencil reduces to the C2
descriptor with a Dirichlet birth trace.  Add one linear incoming element of
proper length `h`.  If `b_K` and `b_M` are the stiffness and mass couplings
from the C2 birth node to its first interior node, Schur elimination of the
new seam node gives, at generalized spectral value `rho`,

`D_h A_eff(rho)|_(h=0)=-b(rho)b(rho)^dagger`,

`b(rho)=b_K-rho*b_M`.

This is the exact regular-compliance derivative of the finite-core pencil.
No inverse of the child kinetic, mass, or Euler--Dirac block is formed.

For a mass-normalized child eigenvector, the generalized eigenvalue derivative
therefore obeys

`|D_h rho| <= 2*m0^(-1)*(||b_K||^2+rho^2||b_M||^2)`,

where `m0` is the Gershgorin lower bound of the positive linear-element child
mass matrix.  The retained heat multiplier gives

`|D_h Gamma_heat| <= sum exp(-rho)/rho`
`*m0^(-1)*(||b_K||^2+rho^2||b_M||^2)`.

The first child element supplies explicit bounds for `b_K` and `b_M`.  Their
angular loss is covered by `(1+mu)^4`.  Splitting one half of the heat
exponential absorbs the remaining `rho` factor, and the already-certified
temporal gap plus the Gaussian angular sum gives the stored logarithmic upper
bound for the complete absolute graded coefficient.

Since `D_lambda h/lambda=1/(-Delta)`, this bounds

`limsup_(lambda->0+) |D_lambda Gamma_heat|/lambda`.

The bound is strictly below the certified positive lower coefficient of
`-D_lambda Gamma_form^zeta/lambda`.  Hence the finite-core joint replacement
amplitude covector is strictly positive on some punctured action-owned
neighborhood of zero amplitude.  No radius for that neighborhood is claimed:
a finite-amplitude compliance remainder bound is still required to cover the
entire stored amplitude box.  This is not a componentwise KKT equation; it is
one evaluation direction of the complete closed-system functional.  It does
not close the maximal C2 tail or Gate 7.

No source, selector, fitted cutoff, endpoint, recurrence condition, scale,
gate, or chord is introduced.
