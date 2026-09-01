# Gate-7 retained correction-direction bordered-response first jets

The action-owned 62-dimensional selected-complement system is

`K x = rhs`.

Along the normalized signed Green correction, its exact center derivative is

`K x' = rhs' - K' x`.

All terms are assembled from the retained 96-point action gradient, Hessian,
complex-step directional third-action matrix, and branchwise selected-line
first jet.  The bordered systems are solved directly; no explicit inverse and
no kinetic, Dirac, or history inverse is formed.

The resulting normalized graph-field derivative is checked by replaying the
differentiated bordered and normalization identities on the selected
quarter-step center.  The former half-step graph-Jacobian profile is not used
as a cross-center validator.  This closes the center response first jet only.
The second bordered derivative and the outward `D4`--`D5` remainder remain
necessary for the interval causal vector radius.

Because the retained border is strongly conditioned, its solve check is the
normalized backward error
`||Kx-rhs||/(||K|| ||x||+||rhs||)`; the absolute residual and condition number
are also retained in every seam row.
