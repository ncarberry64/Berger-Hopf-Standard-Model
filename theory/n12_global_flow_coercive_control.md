# Coercive-control audit for the continuum child flow

The retained autonomous action supplies a local canonical Hamiltonian, but
global flow control requires more than conservation: the conserved quantity
must bound the strong \(S_2\) norm on the physical constraint and gauge
quotient.

Before constraint reduction, the retained ADM metric-velocity block contains

\[
 Q(\dot c,\dot h,\dot u)
 =-12\dot c\dot h-30\dot h^2+6\dot u^2,
\]

with eigenvalues of both signs. More sharply,

\[
 z_k=k(-5/2,1,0),\qquad Q(z_k)=0,
 \qquad \|z_k\|\longrightarrow\infty .
\]

Thus a fixed value of the unreduced autonomous kinetic Hamiltonian cannot
control even the finite metric-velocity norm, let alone the continuum strong
norm. This exact null-cone countersequence does not prove that the physical
constraint-reduced energy is indefinite. It proves that imposing the actual
Hamiltonian/momentum constraints and gauge quotient is indispensable; a
fixed-volume diagnostic cannot be substituted for that reduction.

No existing repository theorem supplies a positive/coercive Hamiltonian on
the complete continuum child constraint manifold. The local Legendre energy
is not the complete boundary-improved \(Q_\xi\), and the matched-parent charge
is unavailable. Therefore neither may be used as the missing a priori bound
or interpreted as mass.

The constraint-reduced identity has now been derived.  The unchanged
constraint map is

\[
C_N=(\partial_mL_N,E_N),\qquad E_N=\partial_vL_N\cdot v-L_N,
\]

so (E_N\) is identically zero on the complete-child constraint set.  Its
intrinsic first and second variations on that set vanish, and the gauge
quotient cannot turn the zero function into a coercive norm.  The earlier
possibility that this local Legendre energy might control the strong
topology is therefore invalidated, not merely left open.  The full proof is
recorded in `theory/n12_constraint_reduced_energy_identity.md`.

The next action-owned lemma is to derive the complete child-only
boundary-improved Hamiltonian variation from the retained action and test
its gauge-reduced strong-(S_2) control.  This is not the unavailable matched
parent subtraction and may not be called mass.  If it is also unavailable or
noncoercive, global continuation must instead come from a direct analytic
continuation/physical-domain-exit estimate for the existing flow.
