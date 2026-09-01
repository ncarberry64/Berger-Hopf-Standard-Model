# N12 finite-endpoint force-sign shortcut no-go

Status: `FINITE_ENDPOINT_OPERATOR_STRUCTURE_ALONE_DOES_NOT_FIX_REPLACEMENT_FORCE_SIGN`.

The finite-encapsulation theorem and finite-endpoint compact-resolvent theorem
make the Gate-7 heat-minus-zeta force finite on each realized operator.  They
do not determine its sign.  This distinction is now certified using the
retained round spatial spectra, multiplicities, and supertrace signs on the
finite Dirichlet/Friedrichs reference interval.

For proper duration `T`, radius `R`, and

`nu_k^2=(pi k/T)^2`, `k>=1`,

the common-log-radius heat force is

`F_heat=sum_(C,l,k) -s_C d_C(l) a_C(l,R)
 exp[-(nu_k^2+a_C)]/(nu_k^2+a_C)`.

Here the resulting force signs are negative for the transverse gauge and
complex HS sectors and positive for the rank-16 three-family Weyl sector.
The replacement force is

`F_rep=F_heat-(59/30)T/R`.

At the same `T=3`, direct interval-tail certification gives

- `R=0.5`: `F_rep < -11.81601698628272294466`;
- `R=2`: `F_rep > 10.65355774189893328001`.

The angular and temporal omissions are bounded by separable Gaussian sums and
a decreasing-ratio tail, without cancellation.  The absolute error bounds
are respectively below `1.02e-123` and `2.61e-120`.

This is a theorem about the insufficiency of operator structure.  The two
constant-round reference operators are not asserted to be retained N12
Euler--Dirac histories, and their numbers are not physical N12 force values.
They prove only that compact resolvent, positivity, the retained sector
ledger, and the Friedrichs reference class cannot supply a universal sign
shortcut.  The actual action-owned coefficient path and endpoint/seam graph,
or the equivalent parametric Weyl--Calderón oracle and its physical geometry
jet, remain necessary before the projected force and coupled same-action
saddle can be certified.

No reset selector, endpoint parameter, physical scale, new action term, new
gate, or frozen-prediction change is introduced.
