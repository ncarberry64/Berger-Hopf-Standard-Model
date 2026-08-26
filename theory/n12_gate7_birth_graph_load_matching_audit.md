# Gate-7 action-owned birth-graph load matching audit

Status: `AE2_BIRTH_GRAPH_TYPE_CLOSED_EVENT_SIDE_LOAD_AND_JET_OPEN`.

The physical birth of `C1` at `E0` is an internal AE2 seam.  It is not a
homogeneous Dirichlet wall and it is not created by the external source.  The
relevant diagram is

`pre-E0 --M_E0--> E0 --(U_R0,W_E0)--> C1 --M_form--> E1`.

AE2 fixes the trace and conormal transmission law.  With

`u_C1=U_R0 u_E0`

and all quantities expressed in the `C1` birth frame, elimination of the
event arm gives the action-owned birth load

`B_birth=U_R0 (M_E0+W_E0) U_R0^dagger`.

The compact formation Calderón matrix then obeys

`(M00+B_birth)X_birth=M01`,

`M_f^phys=M11-M10 X_birth`.

The covariant first jet of the load is

`D B_birth=(D U_R0)(M_E0+W_E0)U_R0^dagger`

`+U_R0(D M_E0+D W_E0)U_R0^dagger`

`+U_R0(M_E0+W_E0)(D U_R0)^dagger`.

In a reset-compatible covariant frame the explicit `D U_R0` terms are
absorbed into the covariant derivative, but the value and jet of `M_E0`
remain required.  `J_ext=0` removes only the external linear term on the
common birth trace and does not remove any term in this load.

The repository matching is sharp.  The AE2 lift `U_R0`, the transmission
type, the fermion result `W_E0=0`, and the retained gauge contact formula are
valid existing objects.  The zero-background Calderón closure applies only
at zero trace, and the local threshold transport is not the nonzero
event-side response.  No current artifact realizes the action-dependent
nonzero `M_E0(z;xi)` family and first quotient jet on the certified local
history family.  Therefore neither `B_birth` nor `M_f^phys` is yet a
numerically realized physical input.

The equivalent route is to keep the E0 event arm and the C1 birth trace in the
complete joint operator.  This avoids forming `B_birth`, but it does not
remove the need to realize that arm's action coefficients and first jet.

No second external source, seam force, selector, phase, action term, scale,
endpoint, recurrence, gate, or chord is introduced.  Gate 7 remains open and
`FULL_BHSM_COMPLETE=false`.
