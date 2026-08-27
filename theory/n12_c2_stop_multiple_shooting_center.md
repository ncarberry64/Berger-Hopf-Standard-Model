# N=12 C2 finite stop multiple-shooting center

Status: `FINITE_47_SEAM_HERMITE_STOP_CENTER_ASSEMBLED; INTERVAL SHADOWING OPEN`.

The global denominator-free reconnaissance and the refined transverse stop
are now one finite mesh with 48 nodes and 47 seams over action length
`0<=a<=92.3033209053828`.  The first 46 seams have length two and the final
stop seam has length `0.30332090538280454`.

Write the graph-preserving augmented field in action coordinates as

`U(Y,s)=(G_theta/||G_theta||, Delta/||G_theta||)`.

Its state component has unit action norm.  It uses only the retained selected
line and hard-complement bordered response; neither `Delta` nor the full
Euler--Dirac matrix is inverted.  On each seam, let `P_j` be the cubic Hermite
curve determined by the two stored nodes and their exact `U` rates.  The exact
center residual is

`R_j(a)=P_j'(a)-U(P_j(a))`.

For an exact correction `e`, the standard variation-of-constants identity is

`e(a)=Phi_j(a,a_j)e(a_j)-integral Phi_j(a,t)
 [R_j(t)+N_j(e(t))] dt`,

where `Phi_j` is the variational propagator of the same retained field and
`N_j` is the quadratic Taylor remainder.  This is the general ODE/Green
identity already specialized successfully in the first-chord certificate;
it adds no foreign physical dynamics.  Joining the seams gives a block lower
bidiagonal multiple-shooting derivative.  Forward substitution or its
bordered adjoint is the Green operator, so no dense full-history inverse is
required.  The terminal scalar row is `s=0`, with nonzero time derivative
`D s[U]=Delta/||G_theta||`.

Exact retained-field evaluations at all 48 nodes and 47 Hermite midpoints
give the following center profile:

- maximum midpoint state-rate defect in action norm:
  `1.2884161962408744e-5`, on seam 0;
- maximum after the first four seams: `3.8189193984057584e-7`;
- integrated midpoint-defect proxy: `4.692906258217994e-5`;
- the first four seams carry `0.7497030153591059` of that proxy;
- maximum midpoint descriptor-rate defect: `1.3017536154116308e-13`, also
  on seam 0;
- maximum adjacent tangent turn: `0.008585365855750721` radians;
- total adjacent tangent turn: `0.09115311568352155` radians.

Thus the path is a slowly rotating correlated center, not an axis-aligned
98-dimensional box.  The proof mesh should refine the first four seams and
retain a moving tangent/complement frame; uniform subdivision and an ambient
hull would spend the certificate on already small later defects.

All node and midpoint samples retain selected branch 24.  The minimum sampled
selected-line gap is `1.7341678902683903e-7`, minimum lapse is
`0.7003486460991334`, minimum radius is `0.9949167164637879`, and minimum
cancelled-field action norm is `0.00023257472984556459`.

These are center values, not interval bounds.  The exact remaining proof is
to enclose the between-node Green/Hermite remainder and conjugated transverse
propagator on this correlated mesh, with strict earlier-domain boundary
exclusion, then apply scalar interval Newton to the transverse terminal row.
The existing first-chord 64-subspan certificate supplies the algebraic proof
pattern; its constants may not be copied without reevaluation on this path.

No reset member is promoted to a selector, and no recurrence, chord, action
term, endpoint, scale, or physical time direction is added.
