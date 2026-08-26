# Gate-7 external birth-source role supersession

Status: `EXTERNAL_BIRTH_TRACE_DIRICHLET_REFERENCE_REAFFIRMED_E0_ARM_REMOVED`.

Norman's source ontology says that only the external Cauchy/birth source is
set to zero, while `M_f`, `M_C2`, `U_R`, `W_phys`, and all retained contacts
remain internal. The tracked endpoint-role theorem fixes the mathematical
type of that external source: it is the BRST-quotiented birth trace used as
Dirichlet generating data for the compact `C1` history.

Consequently the ordered operation is:

1. assemble the complete internal `E1/C2` seam operator using the nonzero
   internal response `M_f`;
2. apply the retained grading and heat-minus-zeta functional;
3. differentiate at fixed external birth trace;
4. set only that trace to zero.

At zero external source the formation interior is therefore the retained
Dirichlet reference at `E0`. In the free two-boundary Calderón matrix

`M_form=[[M00,M01],[M10,M11]]`,

the incoming terminal response is

`M_f=M11`.

This does not set `M_f` to zero. `M11` is a generally nonzero internal
Dirichlet-to-Neumann response. The physical seam remains

`S_AE2=M_f+U_R^dagger M_C2 U_R+W_phys`.

A nonzero birth source produces the usual affine Poisson/source-response
terms. Differentiating before setting the source to zero preserves the
closed-system determinant and every internal operator variation. It does not
turn the external trace into a dynamical integrated seam variable.

The recently introduced pre-E0 block `M_E0`, birth load `B_birth`, and
two-seam `E0/C1--E1/C2` physical topology arose from that category error.
Their general block-Schur algebra remains mathematically valid for a theory
with a dynamical first seam, but the current BHSM Gate-7 diagram does not
contain that seam. No pre-E0 parent response is required.

The current diagram is therefore

`external birth trace at E0 -> compact C1 response M_f -> E1/C2 seam -> M_C2`.

The live numerical owner returns to the complete graded `E1/C2` seam
cotangent and the maximal projected `C2` tail. No internal response is zeroed,
no source or seam force is added, and no recurrence or reflected parent
history is introduced.

Gate 7 remains open and `FULL_BHSM_COMPLETE=false`.
