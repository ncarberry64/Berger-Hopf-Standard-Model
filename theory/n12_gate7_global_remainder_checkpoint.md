# Current-radius global physical remainder criterion

This is a sufficient theorem and a deterministic missing-evidence checkpoint.
It is not a numerical enclosure of the missing global physical remainder.
Gate 7 and whole-system BHSM completion remain open.

Use the frozen history, its original two-radius domain, and one common vector
of history parameters. Let T be the same-action physical Newton map. Subtract
the exact functions whose bounds are already included in the current ledger,
including the interval-14 contribution exactly once. Let R denote the remaining
function. Its constant and linear parts must be accounted for in that ledger:
the identities R(0)=0 and DR(0)=0 are required proof obligations, not inferred
from a list of point certificates.

For h=D_r z, use the maximum of the longitudinal and transverse history norms,
so the original domain is ||z|| <= 1. Normalize output i by r_i and set
G_i(z)=R_i(D_r z)/r_i. Suppose the full original domain and its radial segments
are valid for the physical action, selected eigenbranch, implicit response,
normalization, actual Hermite--Simpson midpoint relation and output projection.
If a shared-parameter proof establishes

    sup_{||z|| <= 1} ||D^2 G_i(z)|| <= kappa_i,

in the bilinear operator norm, integration along the radial segment gives

    G_i(z) = integral_0^1 (1-t) D^2 G_i(t*z)[z,z] dt,
    DG_i(z)[v] = integral_0^1 D^2 G_i(t*z)[z,v] dt.

Consequently the physical value remainder is at most r_i*kappa_i/2 and
the normalized derivative row remainder is at most kappa_i. The norm is
taken after the shared physical action/solve/midpoint/output dependencies and
history transport are assembled. Separate interval maxima or point Hessians
are not interchangeable with this global supremum.

Writing b_i for the booked self-map upper bound and d_i for the booked
normalized derivative row upper bound, a sufficient condition is

    kappa_i < min(2*(r_i-b_i)/r_i, 1-d_i).

The current ledger gives strict target values (rounded downward for display):

| Output | Sufficient strict kappa target |
|---|---:|
| Longitudinal | 0.6542911248664067 |
| Transverse | 0.7452414479024602 |

The exact rational targets are in the global checkpoint. These are targets,
not established kappa values. They are not the historical local coefficient
cap 0.14566258071899124 and do not replace either physical radius.

The available 143 point-Hessian manifests, 27 midpoint pullbacks, one endpoint
pullback and eight endpoint eigenbranch records do not establish this uniform
operator bound over all 370 intervals. The point-Hessian reproduction at
endpoint 71 is already complete. Its isolated transported diagnostic is not
an input to this checkpoint and does not prove a physical failure.

Until the uniform certificate is supplied, all three complete physical LHS
bounds and margins remain unknown. The classification is
`INCOMPLETE_REMAINDER_INFORMATION`. Even a successful future self-map and
contraction result will not close the action-owned projected-root, operator,
physical-domain and other Gate-7 obligations automatically.
