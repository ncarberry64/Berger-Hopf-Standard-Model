# Gate-7 recentered-cone boundary-cluster spectrum

The retained stop history, its fine signed Green correction, and the nonlinear
causal-radius halo are covered on the union refinement of two existing meshes:
the 64-way Hermite stop mesh and the fine correction mesh.  On each union cell
the base cubic plus the piecewise-linear correction is exactly cubic.

If `P` is its three-coordinate action projection and `rho` is the global
nonlinear action radius, then

`sqrt(2) [P, rho I_98]`

contains the product of the corrected path ellipsoid and the nonlinear ball.
The established correlated boundary-cluster Kato proof is evaluated on this
101-dimensional projection.  Retained exact action Hessians fix the centers;
batched automatic differentiation of the same action formula accelerates only
the center `D3` directions; and retained MixedBound `D4` is the outward
authority.

Internal hard-branch 26/27 proximity remains inside the invariant positive
cluster 25--27 and is never used as a selected-line denominator.
