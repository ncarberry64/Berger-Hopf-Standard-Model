# Selected DOP853 nonlinear product-cone spectrum

The exact adaptive DOP853 spectrum already certifies the selected branch on
the retained degree-seven path carrier.  The current construction does not
replace or replay that carrier.  It attaches a candidate transverse action
ball whose radius is twice the exact signed center radius.

For one path cell, write its centered Bernstein enclosure as `P u`,
`||u||<=1`, and the nonlinear displacement as `H v`, `H=r I_98`,
`||v||<=1`.  The product is contained in the single retained-action proof
ellipsoid

`sqrt(2) [P,H] w`, `||w||<=1`.

At the cell midpoint, same-formula center `D3` is evaluated on the full halo
basis.  The retained-action `D4` majorant bounds its change on the complete
path-times-halo product.  Their sum is the incremental halo Hessian motion
`eta`.  Since the path gap is already certified, Weyl transfer gives the
product-cone gap `g_product >= g_path-2 eta`.  This preserves the cellwise
path correlation instead of collapsing the DOP853 cover to a global gap or
response maximum.

The radius is a proof candidate, not a fitted threshold and not yet an
interval history certificate.  It is promoted only if the downstream signed
common-frame radii inequalities `Y+Z1 r+Z2 r^2<r` and
`Z1+2 Z2 r<1` close.  Gate 7 remains active until that contraction and the
first-hit/domain-margin transfer are complete.
