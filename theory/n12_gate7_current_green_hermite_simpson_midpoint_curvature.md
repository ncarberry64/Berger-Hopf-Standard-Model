# Current Green Hermite--Simpson midpoint curvature

For the correlated all-node unit-Green trial path, the Hermite--Simpson
midpoint is not assigned an independent fitted direction.  Its first and
second incidences follow from the collocation map:

```text
u_m = (u_0+u_1)/2 + h(DF_0 u_0-DF_1 u_1)/8,
w_m = h(D2F_0[u_0,u_0]-D2F_1[u_1,u_1])/8.
```

The complete midpoint second rate variation is therefore

```text
D2F_m[u_m,u_m] + DF_m w_m,
```

not merely the intrinsic directional Hessian.  The local collocation residual
second variation is assembled with the frozen step and signs,

```text
-h(F''_0 + 4 F''_m + F''_1)/6.
```

All retained-action differentiations use 384-bit Arb on the accepted center
and selected branch.  The induced midpoint direction and second incidence stay
finite on all 370 intervals, as does `DF_m w_m`.  The intrinsic midpoint
Hessian enclosure is finite through interval 354 but becomes indeterminate on
intervals 355--369 when the independently exported component balls of the
normalized endpoint axes are propagated through the increasingly stiff
collapse-side first variation.

This is a fail-closed coordinate-enclosure result.  It does not prove that the
correlated Green path, a physical solution, or the action is singular.  It
shows that independent componentwise intervalization discards too much of the
normalization/transport correlation to complete the midpoint Hessian.  The
next calculation must retain the Green normalization and endpoint-to-midpoint
transport as one correlated longitudinal scalar parameterization, beginning
at interval 355.  No frozen test-frame or causal-preconditioner promotion is
allowed before that finite enclosure is recovered.
