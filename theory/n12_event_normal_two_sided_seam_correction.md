# N12 event-normal two-sided seam correction

Status: `ONE_SIDED_W_ONLY_INITIALIZATION_SUPERSEDED_TWO_SIDED_AE2_SEAM_RESPONSE_OPEN`.

The event-normal Riccati equation remains an exact transfer identity on each
regular arm,

`D_s M=L_spatial(Y(s))-zI-M^2`,

with linearized geometry equation

`D_s(delta M)=delta L-M delta M-delta M M`.

The physical AE2 event, however, is an internal two-sided transmission seam,
not a one-sided terminal Robin wall.  Eliminating the child arm gives

`S_AE2(z)=M_event(z)+U_R^dagger M_child(z) U_R+W_phys`,

so the effective load seen by the event arm is

`B_event(z)=U_R^dagger M_child(z) U_R+W_phys`.

Consequently the physical event-arm Riccati transfer may be initialized only
after `B_event(z)` is known.  The earlier statement `M(0,z)=W_phys` omitted
the opposite-arm Calderon response and is superseded.  For AE2 fermions the
local surface block is exactly `W_phys=0`, but this makes the effective load
`U_R^dagger M_child U_R`; it does not make the child response zero.

The geometry force also requires the complete derivative

`D B_event=(D U_R^dagger) M_child U_R`
`+U_R^dagger (D M_child) U_R`
`+U_R^dagger M_child (D U_R)+D W_phys`.

The nonfermionic lower-bound theorem is unchanged: positivity of the child
map and retained Wentzell block closes the zero-threshold sign without their
full values.  That order argument does not provide the spectral family and
geometry jets needed by the heat-minus-zeta force.

Finite-encapsulation ontology removes infinite nonencapsulating histories
from the particle observable domain, but it does not remove the AE2 internal
event-to-child glue.  Formation ends at the event and child decay/evolution
begins immediately; both regular traces remain in the action domain.

The exact missing theorem is therefore the child-arm Calderon map and its
geometry/reset-lift jets on the realized finite event-child history, or an
equivalent joint two-sided finite-history operator solve.  No arbitrary
cutoff, Robin datum, contour, selector, phase, scale, or new gate is allowed.

`FULL_BHSM_COMPLETE=false`.
