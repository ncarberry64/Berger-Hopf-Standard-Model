# Gate-7 retained correction-direction eigenline first jets

At each of the 48 finite-history seams, the authoritative 96-point retained
action Hessian is evaluated at a complex step along the normalized signed
Green correction.  The imaginary part gives the complete directional
third-action matrix without finite subtraction.

The selected branch is then differentiated in its complete eigenbasis:

`lambda' = <psi,A' psi>`,

`psi' = sum_(k != selected) psi_k <psi_k,A' psi>/(lambda-lambda_k)`.

Every branch keeps its own signed denominator.  No smallest-gap replacement
and no full Euler--Dirac inverse is used.  The differentiated eigenpair and
normalization equations are replayed directly.

This is an authoritative retained-action center jet.  It does not yet bound
the eigenline jet on the full `3.6e-6` correction tube.  The existing
directional `D4`--`D5` majorants and adaptive spectral-response intervals
must be composed with this center before the causal vector radius is outward.
