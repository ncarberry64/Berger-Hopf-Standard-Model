# N12 compact-history endpoint-role provenance

Status: `BIRTH_SOURCE_REFERENCE_AND_TERMINAL_AE2_LOAD_DISTINGUISHED`.

The compact history has ordered traces `(birth,new_event)`, but these traces
have different roles in the retained zero-source functional.

At birth, the trace is the external BRST-quotiented source variable.  The
restriction

`Gamma0_birth U=0`

is the retained Dirichlet reference used to define the source generating
functional at zero source.  It is not a new physical endpoint condition.  A
nonzero birth trace defines the Poisson extension and Weyl kernel, and the
physical birth graph is reimposed exactly once in the joint source response.
No earlier-event exterior response is needed to define this reference.

At the terminal new event, by contrast, the compact bulk field remains
subject to the action-owned maximal endpoint class.  For the certified
`E1 -> C2` reset this is the AE2 two-sided transmission graph.  Eliminating
the child arm gives

`B_terminal=U_R^dagger M_C2 U_R+W_phys`.

Thus the physical Dirichlet-reference operator for the compact history is
closed at birth by the zero-source restriction and at the terminal event by
the AE2 load.  Its determinant/heat force still requires the value and
geometry jets of `M_C2`, as proved by the gluing-force identity.  The missing
data are not an additional birth load and not a choice between Dirichlet,
Neumann, Robin, periodic, or reflected physical endpoints.

This distinction preserves the exact chain

`BHSM action -> compact operator -> terminal AE2 reduction -> zero-source force`.

`FULL_BHSM_COMPLETE=false`.
