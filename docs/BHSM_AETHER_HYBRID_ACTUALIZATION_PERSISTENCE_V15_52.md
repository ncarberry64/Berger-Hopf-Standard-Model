# BHSM v15.52 — hybrid actualization persistence

The eta Legendre surface is an event surface, not a regular Hamiltonian chart:

\[
 \Sigma_L=\{\min_\chi(1+X_\eta^3)=0\}.
\]

At this event BHSM transports only

\[
 \mathcal I_*=(\deg\eta,\epsilon_c,(-1)^{FR},
 \text{endpoint order},\text{incidence},\text{boundary identities}),
\]

while metric, velocity, curvature, local energy density, and canonical metric
momentum are not transported as primitives. The post-event constrained
reconstruction is therefore a map

\[
 \mathcal R:\mathcal I_*\longmapsto z_*.
\]

On the eta-gauge finite chart, the coefficient-locked constraint projection
and transported negative-child orientation select one (z_*). Let
\(\Phi_t\) be the attached Euler--Dirac flow and (T_*) its next Legendre
event time. The hybrid return map is

\[
 \boxed{\mathcal P=\mathcal R\circ\mathcal E\circ\Phi_{T_*}},
 \qquad \mathcal P(z_*)=z_*.
\]

This is event-relative periodicity. It does not require the erased metric to
return smoothly before the event.

On a connected event component with fixed discrete tuple \(\mathcal I_*\),
the reconstruction output is independent of the erased continuous incoming
data. Hence

\[
 D\mathcal R=0,
 \qquad
 D\mathcal P
 =D\mathcal R\,D\mathcal E\,D\Phi_{T_*}=0.
\]

After the five reduced constraints and the flow direction are removed, the
physical Poincare tangent has dimension 12 in the present chart. All twelve
continuous hybrid Floquet multipliers are zero. The odd FR ground ray is
carried by its discrete parity and returns projectively to itself, with
projective multiplier one.

Thus the reconstructed child is asymptotically stable as a finite-chart
hybrid event cycle. The remaining theorem is to promote the single-valued
reconstruction and zero reset derivative to the full function space and then
include the massive interacting Standard Model operator in the event cycle.
