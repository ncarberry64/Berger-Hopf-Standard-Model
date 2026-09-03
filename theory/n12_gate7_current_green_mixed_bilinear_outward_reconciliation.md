# Current Green mixed-map outward reconciliation

For every twice Fréchet-differentiable retained rate map, the Hessian is a
symmetric bilinear form and therefore obeys

`D2F[u,v] = (D2F[u+v,u+v] - D2F[u-v,u-v]) / 4`.

The direct and polarized implementations traverse the same current-C2 action
but round and dependency-track their intermediate eigenline, bordered
response, normalized field, and scalar readout differently.  Their small
center discrepancy is therefore carried explicitly instead of discarded or
renormalized.  One directed common hull contains both graphs for all 74
columns at each of the four independently certified seed nodes.  A fresh
512-bit polarized evaluation additionally tests the leading right-singular
direction at the all-endpoint reconnaissance owner.

Containment alone is not accepted as evidence of equivalence because a hull
can contain inconsistent evaluations merely by becoming wide.  Promotion
also requires every one of the 296 seed-column centers and the fresh owner
direction center to agree below `1e-8` absolute and `1e-9` after unit-floor
scaling.  A larger discrepancy fails the unit instead of being absorbed into
the common hull.

The completed reconciliation has maximum seed-center difference
`6.256328788367682e-12` absolute and `2.1949664308351657e-12` after unit-floor
scaling.  The maximum seed common-hull radius is `3.129940751023242e-12`.
The all-endpoint survey selects node 9; its fresh 512-bit leading-direction
polarization agrees with the direct evaluation to
`1.8332002582610585e-12` absolute and `8.000920959132899e-14` scaled, with
common-hull radius at most `9.379164112033326e-13`.

This unit neither fits the discrepancy nor assumes that nonoverlapping narrow
exports overlap.  It combines the exact mathematical identity with a common
outward numerical graph, reuses all 370 direct endpoint maps, and introduces
no empirical value, physical scale, center, or trajectory.  It establishes
endpoint mixed-map representation authority only.  Correlated midpoint
transport, causal preconditioning, the full transverse operator majorant, and
the two-radius theorem remain open.

The next transport is fixed by the already-used Hermite--Simpson chain rule,
not by a new interpolation choice.  Write `c_i` for the correlated central
ambient direction, `T_i` for the ambient transverse coordinate map,
`f_i^c = DF_i c_i`, `F_i^T = DF_i T_i`, and
`B_i = D2F_i[c_i,T_i]`.  On an interval of length `h`, the two midpoint first
directions and their mixed second incidence are

```text
c_m = (c_L+c_R)/2 + h(f_L^c-f_R^c)/8,
T_m = (T_L+T_R)/2 + h(F_L^T-F_R^T)/8,
W_m = h(B_L-B_R)/8.
```

Therefore the correlation-preserving local mixed residual operator is

```text
B_m^tot = D2F_m[c_m,T_m] + DF_m W_m,
L_i^mix = -h(B_L + 4 B_m^tot + B_R)/6.
```

The reset-side values on interval zero are fixed to zero, as in the certified
central-scalar construction.  Projecting `L_i^mix` through the same frozen
test/trial frames and Newton blocks then gives the causal operator recurrence

```text
C_0 = 0,
C_(i+1) = -R_i^-1 [E_(i+1)^T L_i^mix
                    + E_(i+1)^T A_i E_i C_i].
```

Here `A_i` and `R_i` are the already-certified left and reduced-right Newton
blocks.  This formula identifies the only additional endpoint data needed:
the transverse first variations `DF_i T_i`.  It does not authorize replacing
them with norms, transporting the old 48-seam maps, or discarding the changing
Green projector.
