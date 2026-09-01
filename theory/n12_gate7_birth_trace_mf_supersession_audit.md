# Gate-7 birth-trace and incoming-response supersession audit

Status: `ZERO_SOURCE_DIRICHLET_MF_IDENTIFICATION_SUPERSEDED_BIRTH_GRAPH_REDUCTION_OPEN`.

The compact formation history has the free two-boundary Calderón response

`[n_0,n_1]^T=[[M00,M01],[M10,M11]] [u_0,u_1]^T`,

with endpoint order `(birth,new_event)`.  The owner-authorized Gate-7 source
ontology distinguishes the external linear datum `J_ext` from the birth
trace `u_0`.  Therefore `J_ext=0` cannot be implemented by `u_0=0`.

Write the retained self-adjoint birth graph, in the outward-conormal
convention of the compact operator, as

`n_0+B_birth u_0=J_ext`.

Here `B_birth` denotes only action-owned internal birth/reset/contact
response already present in the complete closed operator.  It is not an
additional source or seam force.  At zero external source, stationarity gives

`(M00+B_birth) X_birth=M01`,

`u_0=-X_birth u_1`,

and hence the physical incoming response at the new event is

`M_f^phys=M11-M10 X_birth`.

This is an inverse-free bordered solve.  Its first geometry jet is obtained
from

`H_birth X_birth,h=M01,h-H_birth,h X_birth`,

where `H_birth=M00+B_birth`, followed by

`D_h M_f^phys=M11,h-M10,h X_birth-M10 X_birth,h`.

The old equality `M_f=M11` is the restriction `u_0=0`.  It is a legitimate
Dirichlet reference block for constructing Poisson/Weyl data, but it is not
the physical zero-source reduction.  A positive definite two-by-two witness
already separates them: for `M=[[3,1],[1,4]]`, `B_birth=2`, `J_ext=0`, and
`u_1=1`, stationarity gives `u_0=-1/5` and `M_f^phys=19/5`, whereas the
Dirichlet block is `M11=4`.

The retained compact transfer, its coefficient path, its two-boundary jets,
and the negative-axis form bounds remain valid.  What is superseded is their
interpretation as a physical incoming `M_f` after setting the birth trace to
zero.  To finish the incoming slot one must either:

- instantiate `B_birth` and its action jet from the retained birth/reset
  graph and apply the bordered reduction above; or
- retain the birth trace explicitly in the complete joint operator and
  differentiate that unreduced operator once.

If the retained action proves that the initial birth endpoint is freely
varied with no internal quadratic birth term, then `B_birth=0` is the natural
graph and the same formula applies.  That specialization must be proved from
the action; it cannot be inferred from `J_ext=0`.

No forward-history existence, reset/recurrence semantics, selector, source,
scale, action term, endpoint, gate, or chord is introduced.  Gate 7 remains
open and `FULL_BHSM_COMPLETE=false`.
