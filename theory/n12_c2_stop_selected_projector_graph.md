# N=12 finite-stop selected-projector graph theorem

Status: `ALL_3008_STOP_PATH_SELECTED_PROJECTOR_GRAPHS_CERTIFIED`.

## Inputs and quotient

The complete boundary-cluster theorem supplies one simple branch-24 line on
each of the `47*64=3008` correlated Hermite action balls.  All calculations
remain on the intrinsic gauge/time quotient.  No Euler--Dirac kinetic block
or dense history operator is inverted.

Let `psi` be the center branch-24 unit vector, `V_J` an orthogonal hard
spectral band, and `P` the exact three-coordinate Hermite projection.  The
center numerator and retained action remainder are

`c_J=(sum_i ||V_J^T D H[P_i] psi||_2^2)^(1/2)`,

`r_J=sup |D4 S[V_J,psi,P,P]|`.

The latter is evaluated by the same outward retained-action majorant used by
the boundary-cluster certificate.

## Near and far denominator union

Let `g_*` be the certified two-sided selected-line boundary gap from the
cluster theorem.  Independently, let

`R_H=(sum_i ||D H[P_i]||_op^2)^(1/2)
     +(1/2) sup |D4 S[V_red,V_red,P,P]|`

be the ordered-Weyl Hessian displacement bound, and let `rho_24` be the
certified selected-line shift.  For a band whose minimum center distance is
`d_J`, both

`g_*` and `d_J-rho_24-R_H`

are valid lower bounds when positive.  The calculation therefore consumes

`gamma_J=max(g_*,d_J-rho_24-R_H)`.

This union keeps the cluster theorem at the genuinely near modes and uses
ordered Weyl only where the center distance is large.  It does not assume
that individual hard lines retain a physical identity through internal hard
crossings.

The coefficient graph bound is

`k_J=2(c_J+r_J)/gamma_J`,

`k=(sum_J k_J^2)^(1/2)`.

The factor two is the retained half-gap Neumann factor.  The complementary
spectrum is split into the same exhaustive factor-four distance bands as in
the cluster theorem.  This is a proof decomposition, not a fitted physical
threshold.

## Certified result

All 3008 cells select branch 24 and satisfy `k<1`.  The global results are:

- maximum selected graph/projector motion: `0.014138530083434563`;
- owner: seam 11, subspan 20;
- minimum consumed gap: `1.7274638520643627e-7`;
- maximum spectral distance bands on one cell: `15`;
- maximum ambient Hessian shift: `0.00427406712705646`.

At the owner, `R_H=0.004141415714128116`, while the near certified gap is
`2.2835343775581396e-7`.  Near bands consume that cluster gap; sufficiently
far bands consume their much larger ordered-Weyl lower bounds.  The resulting
graph radius is over 70 times below the Neumann threshold.

## Claim boundary

This closes the moving selected-projector graph on the finite reference-path
balls.  The denominator-resolved bordered hard response, Green/Hermite
shadowing radius, scalar first hit, and strict earlier domain-margin
exclusion remain open.  Gate 7 stays active, Gate 8 stays locked, chord 3 is
unauthorized, and frozen predictions are unchanged.
