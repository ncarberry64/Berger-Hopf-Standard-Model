# N=12 DOP853 Bernstein action cells

Status: `EXACT_ADAPTIVE_DOP853_BOUNDARY_CLUSTER_SPECTRUM_CERTIFIED`.

The selected Gate-7 proof center is the stored seventh-order DOP853 dense
polynomial, not the older 47-seam cubic-Hermite interpolant.  The defect and
the exact rational descriptor first-hit already use that dense polynomial.
All interval geometry must therefore use the same object.

On each dense interval, convert the alternating SciPy DOP853 representation
exactly as a polynomial and then to its eight Bernstein control vectors
`B_0,...,B_7`.  After de Casteljau restriction to a proof subcell, put

`m=(1/8) sum_i B_i`,  `P=[B_0-m,...,B_7-m]`.

Every curve point is `B theta`, where the Bernstein weights obey
`theta_i>=0` and `sum_i theta_i=1`.  Hence

`B theta=m+P theta`,  `||theta||_2<=||theta||_1=1`.

The retained action-ball majorant can therefore consume `P` directly as an
eight-column action ellipsoid.  This is an enclosing proof coordinate; it
introduces no new trajectory, action term, selector, or physical scale.

A whole `0.25` action-length dense interval does not close the critical Kato
bootstrap.  The complete four-cell replay retains branch 24 and positive
selected-line boundary margins on all `370 x 4 = 1480` cells.  Its minimum
margin is `1.5132308723717805e-7`.  However, 242 cells in intervals 68 through
128 miss the separately retained quarter-gap bootstrap for the positive
cluster, so that coarse replay is a localization theorem rather than the
final spectrum certificate.

Replace exactly those 242 cells by their two de Casteljau children.  All 484
eighth-cells close the unchanged quarter-gap bootstrap.  Together with the
1,238 accepted quarter-cells they form an exact rational partition of every
stored dense interval: 1,722 cells total, with no gap, overlap, or sixteenth-
cell escalation.  The certified minimum selected-line boundary margin on
this adaptive cover is `1.6382875139534257e-7`; all cells retain branch 24 and
all eight degree-seven Bernstein controls.

This removes the former DOP853-to-cubic-Hermite transfer obligation for the
selected-line spectrum.  The denominator-resolved Kato graph calculation has
also now consumed the same 1,722 cells in the same order.  Every graph
Neumann bound closes; the maximum selected-projector motion is
`0.26738491116648233`.  The exact bordered identity

`sigma(K_border)={1,1,|lambda_j-lambda_24|:j!=24}`

then certifies the instantaneous bordered hard inverse on every cell without
forming the kinetic, Dirac, or history inverse.  The minimum hard gap is
`1.6382875139534257e-7`, and the largest charted bordered inverse bound is
`8842347.821182095`.

This does not by itself prove shadowing: the action-owned bordered response,
correlated `Y,Z1,Z2`, and domain-margin transfer must still be evaluated on
this identical adaptive dense-polynomial cover.
