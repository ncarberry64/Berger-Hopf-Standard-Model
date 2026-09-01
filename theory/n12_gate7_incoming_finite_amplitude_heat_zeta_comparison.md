# Gate-7 incoming finite-amplitude heat--zeta comparison

Status: `FINITE_CORE_CERTIFIED_AMPLITUDE_BOX_HEAT_STRICTLY_DOMINATED_BY_ZETA`.

Fix the certified fixed-terminal incoming family.  The child coefficients,
the event state, and the retained contact are fixed; only the single incoming
formation element varies.  With its external birth value set to zero, the
joint pencil differs from the birth-retained child pencil only in the seam
diagonal.  For a mass-normalized generalized eigenpair `(rho,u)`, the seam
row is

`D(h,rho) u_0 + b(rho) u_1=0`,

where `b(rho)=b_K-rho*b_M`.  Positivity of the scalar element and completion
of the square in either product-Dirac chirality give

`K_00(h)>=1/(4h)`.

Writing `q(h)=M_00^child+h/3`, every mode satisfying

`rho<=R(h)=1/(8 h q(h))`

therefore obeys the regular-compliance trace estimate

`|u_0|<=8h |b(rho)|/sqrt(m_0)`.

This is the finite-amplitude counterpart of the zero-length rank-one Schur
derivative.  It cancels the apparent `h^(-2)` coefficient derivative before
the heat cotangent is contracted.  The retained full-domain Poincare bound
and the scalar/product-Dirac spatial bounds imply `p<=c_p rho`, uniformly in
the angular label.  Hence the low-mode heat coefficient is at most the
already-certified zero-amplitude positive majorant multiplied by the explicit
finite factor stored in the theorem artifact.

For `rho>R(h)`, no compliance division is used.  The global mass Gershgorin
bound controls the seam coordinate directly, while

`exp(-rho)<=exp(-R(h)/2) exp(-g_mu/2)`.

The second factor is summed with the retained half-heat angular Gaussian.
The first dominates every remaining Laurent power uniformly on
`0<h<=h_max`; its worst endpoint is `h=h_max`.  Thus the high-mode part has a
separate explicit logarithmic bound and no hidden positive lower cutoff in
amplitude.

The sum of the low- and high-mode bounds remains strictly below the certified
replacement-zeta coefficient throughout
`0<lambda<=lambda_*`.  Therefore the complete finite-core closed-system
replacement covector in this fixed-terminal amplitude direction is strictly
positive on the entire certified amplitude box.  This is one joint
heat-minus-zeta contraction, not a componentwise KKT equation.  It does not
control the maximal C2 tail, and therefore does not yet exclude or certify the
full projected KKT root.

No source, selector, fitted cutoff, endpoint, recurrence condition, scale,
gate, or chord is introduced.
