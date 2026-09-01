# Gate-7 two-seam closed-operator assembly

Status: `TWO_SEAM_CLOSED_OPERATOR_TOPOLOGY_AND_SCHUR_EQUIVALENCE_DERIVED`.

The closed Gate-7 history has two internal seams:

`pre-E0 -- E0/C1 -- compact C1 formation -- E1/C2 -- C2 exterior`.

Let the free compact formation Calderón matrix in its `(C1 birth,E1 event)`
frames be

`M_form=[[M00,M01],[M10,M11]]`.

Let `U0` map the E0 event trace to the C1 birth trace, let `U1` map the E1
event trace to the C2 birth trace, and define the two event-frame loads

`L0=M_E0+W0`,

`L1=U1^dagger M_C2 U1+W1`.

After eliminating only the three Dirichlet interiors, but retaining both
physical seam traces, the exact two-seam block is

`S_01=[[L0+U0^dagger M00 U0, U0^dagger M01],`

`      [M10 U0,                 M11+L1        ]]`.

The external datum couples linearly only to the E0 trace.  Setting `J_ext=0`
removes that linear term; it does not delete the first row and column of
`S_01`.

Because `U0` is unitary, define

`B_birth=U0 L0 U0^dagger`,

`H_birth=M00+B_birth`.

Bordered elimination of the E0 seam gives

`H_birth X_birth=M01`,

`S_E1=M11-M10 X_birth+L1=M_f^phys+L1`.

Consequently

`det(S_01)=det(L0+U0^dagger M00 U0)*det(S_E1)`.

Together with the Dirichlet-interior determinants, this is exactly the
determinant of the unreduced closed operator.  It is an evaluation identity,
not permission to count the direct and Schur forms separately.  The graded
heat-minus-zeta functional and its Fréchet derivative belong to the complete
operator; a resolvent/relative-determinant implementation must reproduce that
single functional.

Every first jet is fixed by the product rule.  In particular,

`D A0=D L0+(D U0^dagger)M00 U0+U0^dagger(D M00)U0+U0^dagger M00(D U0)`,

`D C01=(D U0^dagger)M01+U0^dagger(D M01)`,

and `D(M11+L1)` contains the corresponding `M_C2`, `U1`, and `W1` terms.
One reverse cotangent through this two-seam block therefore reaches the E0
event arm, compact formation arm, E1 reset, and C2 arm exactly once.

The operator topology, frame transports, determinant identity, and derivative
route are closed.  The numerical family is not: `M_E0` and its first jet are
missing, and the existing C2 family remains finite-core with maximal tail
open.  No source, seam force, selector, action term, scale, endpoint,
recurrence, gate, or chord is introduced.  Gate 7 remains open and
`FULL_BHSM_COMPLETE=false`.
