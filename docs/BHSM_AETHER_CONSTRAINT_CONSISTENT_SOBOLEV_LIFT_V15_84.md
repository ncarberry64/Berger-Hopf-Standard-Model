# BHSM constraint-consistent Sobolev lift v15.84

A higher-order Hessian is physically meaningful only at a state satisfying
the constraints of that higher-order space.  At radial order (N), v15.84
therefore solves

\[
 \frac{\partial L_N}{\partial n_k}=0,
 \qquad
 \frac{\partial L_N}{\partial b_j}=0,
 \qquad
 E_N=\dot q\cdot\frac{\partial L_N}{\partial\dot q}-L_N=0,
\]

for all (k=1,\ldots,N) and (j=0,\ldots,N-1).  The underdetermined physical
velocity is selected by minimizing its weighted distance to the embedded
preceding-order velocity.  This is the same constraint projection used by the
child construction, not a new coefficient or fitted mode.

Only after this projection is the exact Euler--Dirac Hessian inverted against
the fermion source covector.  The resulting sequence through (N=8) is the
first constraint-consistent radial Sobolev lift of the joint Schur response.
The remaining operations are continuation to higher order, a radial tail
bound, and reintegration of the backreacted event orbit.
