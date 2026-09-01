# Gate-7 closed-system zero-external-source ontology

Status: `OWNER_SOURCE_ONTOLOGY_RECONCILED_WITH_JOINT_AE2_OPERATOR`.

This statement is owner-authorized physical ontology, not a theorem derived
from the retained action.  It fixes the meaning of "zero source" at Gate 7.
Only the independent external birth/Cauchy linear datum `J_ext` is set to
zero.  The formation response `M_f`, outgoing child response `M_C`, reset
transport `U_R`, retained seam/contact block `W_phys`, and the gauge,
transverse, scalar, topographic, Hubbard--Stratonovich, and ghost contact
vertices are internal action-owned blocks.  None is an independent external
source and none may be set to zero by the zero-source instruction.

In the quadratic generating functional the external datum appears only as a
linear coupling,

`S_J[U]=(1/2)<U,P_joint U>-Re<J_ext,Gamma_birth U>`.

Setting `J_ext=0` removes that linear term.  It does not impose
`Gamma_birth U=0`, delete the birth trace degree of freedom, or replace the
retained self-adjoint birth graph by a homogeneous Dirichlet condition.  The
zero-source partition function still contains the determinant and response of
the complete joint operator.

In one compatible event frame, write the joint quadratic pencil as

`P_joint=[[A,C,0],[C^dagger,H+G+W_phys,E^dagger],[0,E,F]]`,

with `U_R` used to transport the child trace and conormal data into that frame.
Here `A` is the complete formation off-event block, including the dynamical
birth trace and its retained self-adjoint birth graph.  It is not obtained by
setting that trace to zero.  In the free two-boundary Calderón representation,

`A -> M00+B_birth`, `C -> M01`, `C^dagger -> M10`, `H -> M11`,

where the birth stationarity law is

`n_birth+B_birth u_birth=J_ext`.

Inverse-free elimination of the two complete off-seam blocks gives

`M_f=H-C^dagger A^(-1)C`,

`M_C=G-E^dagger F^(-1)E`,

`S_AE2=M_f+U_R^dagger M_C U_R+W_phys`.

At `J_ext=0`, the equivalent compact-history formula is

`(M00+B_birth)X_birth=M01`,

`M_f=M11-M10 X_birth`.

Thus the Dirichlet-reference identity `M_f=M11` is not the physical
zero-source reduction.  The retained birth graph and its action jet must be
instantiated, or the birth trace must be kept in the unreduced joint operator.

These formulas are assembly identities.  The physical functional is first
formed from the complete positive self-adjoint `P_joint`, with the retained
BRST grading and no-double-counting heat-minus-zeta accounting.  A Schur or
relative-determinant representation may be used to evaluate that same
functional, but it may not add a second seam force or repeat a block already
present in `P_joint`.

For an admissible geometry/reset parameter `xi`, the physical Gate-7 covector
is therefore

`q_rep(xi)=D_xi Gamma_closed[P_joint(xi)]` evaluated at `J_ext=0`.

The derivative acts on every internal block through its action-owned first
jet.  Only after the joint graded functional has been differentiated is the
external source set to zero.  On a regular reset stratum `C(xi)=0`, the force
root is the intrinsic quotient condition

`[q_rep]=0 on ker(D C)/span(g_tau)`,

equivalently the bordered KKT equation

`q_rep+D C^dagger delta_lambda=0`.

This reconciliation removes an ambiguity in older phrases such as "nonzero
source incidence": those incidence matrices are internal operator-variation
vertices.  They are not external Cauchy data.  It also removes any route that
sets `M_C`, `M_f`, `W_phys`, or a retained contact response to zero before the
joint functional is assembled.

The remaining numerical owner is now more sharply typed: instantiate the
retained birth graph (or keep its trace unreduced), assemble the complete
joint graded heat-minus-zeta coefficient cotangent, reverse it
once through the joint seam and both histories, take the projected Cauchy
limit (or an actual finite event/canonical stop), and solve the same-action KKT
root.  The 1,222-segment child prefix is valid input to this reverse assembly,
not a physical endpoint or a complete closed-system force.

No external source, seam force, selector, endpoint, recurrence, scale, fit,
action term, time direction, gate, or chord is introduced.  Gate 7 remains
open, Gate 8 remains locked, chord 3 remains unauthorized, and
`FULL_BHSM_COMPLETE=false`.
