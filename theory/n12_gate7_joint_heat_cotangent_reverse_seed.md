# Gate-7 joint heat cotangent and reverse seed

Status: `COMPLETE_JOINT_REVERSE_SEED_DERIVED_NUMERICAL_REALIZATION_OPEN`.

The owner-authorized source ontology fixes `J_ext=0` only after the complete
internal AE2 operator has been assembled and differentiated.  For one graded
sector let

`P=[[A,C,0],[C^dagger,H+G+W,E^dagger],[0,E,F]] > 0`,

where the child trace block and coupling have already been transported by
`U_R` into the common seam frame.

At retained heat length `ell`, the exact first derivative of

`Gamma_heat(P)=-(1/2) Tr E1(ell^2 P)`

is

`D Gamma_heat[P_h]=Re Tr(Q_heat^dagger P_h)`,

`Q_heat=(1/2) exp(-ell^2 P) P^(-1)`.

After the retained signs and multiplicities are applied, the complete seed is

`Q_joint=(1/2) direct_sum_C s_C m_C exp(-ell^2 P_C) P_C^(-1)`.

This formula does not require an inverse of the Euler--Dirac or kinetic
descriptor block.  Equivalently,

`exp(-ell^2 P) P^(-1)=integral_(ell^2)^infinity exp(-sP) ds`,

so the seed may be evaluated by the retained heat semigroup or reconstructed
from a controlled resolvent/Weyl functional calculus.

Writing `Q` in the same formation/seam/child blocks, its direct reverse seeds
are

`q_A=Q_AA`, `q_C=2 Q_AS`, `q_H=q_G=q_W=Q_SS`,

`q_E=2 Q_FS`, `q_F=Q_FF`,

with real parts understood in the complex Hermitian case.  Equal seeds for
`H`, `G`, and `W` do not duplicate a force: they are the chain-rule inputs for
three distinct internal dependencies occupying the same assembled seam block.

There is an equivalent inverse-free seam route.  At every resolvent point,

`S=M_f+U_R^dagger M_C U_R+W_phys`.

If `Omega_S` is the seam cotangent produced by the exact functional-calculus
weight, reverse propagation gives

`q_Mf=Omega_S`, `q_MC=U_R Omega_S U_R^dagger`, `q_W=Omega_S`,

and

`D_U Gamma=Re Tr[Omega_S^dagger((D U_R)^dagger M_C U_R
                               +U_R^dagger M_C D U_R)]`.

In the retained compatible event-child connection, `nabla U_R=0`.  Thus the
covariant physical reverse sweep absorbs the displayed ordinary-frame terms
into `nabla M_C`; they are not an additional source or an independently
varied seam degree of freedom.

The Dirichlet formation and child bulk factors and the seam factor are each
included once.  One may use either the direct joint-block route or the
factorized resolvent route; summing both would double count the same closed
operator.

The direct retained zeta term supplies the separate action covector

`q_zeta=(59/30) D integral d_tau/R4`,

and the replacement covector is `q_rep=q_heat-q_zeta` at the retained
local-action root.  The common-scale moving-duration Ward identity continues
to cancel the zeta contribution exactly in that one physical direction.  It
does not delete the non-scale zeta covector.

For every certified finite core this theorem fixes the exact algebraic seed
and reverse order.  The unresolved numerical input is now only the complete
joint self-adjoint graded operator (or an equivalent sharp whole-axis joint
Weyl realization) and its action-owned coefficient jets.  Once supplied, the
same seed is reversed through both histories, projected to the physical
quotient, and tested for a Cauchy limit or evaluated at an actual finite
event/canonical stop.

No internal response is zeroed, no additional seam source is introduced, and
no term is counted twice.  The 1,222-segment child edge remains a finite proof
edge.  Gate 7 remains open, Gate 8 remains locked, chord 3 remains
unauthorized, and `FULL_BHSM_COMPLETE=false`.
