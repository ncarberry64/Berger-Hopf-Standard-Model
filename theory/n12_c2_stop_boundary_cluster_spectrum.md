# N=12 finite-stop boundary-cluster spectrum theorem

Status: `ALL_3008_STOP_PATH_BOUNDARY_CLUSTER_DENOMINATORS_CERTIFIED`.

## Why clusters are the retained object

The physical Gate-7 line is the action-selected reduced-Hessian line.  The
hard complement is not required to carry a globally ordered collection of
individual physical lines.  In particular, the close approach of ordered
hard branches 26 and 27 is internal to the hard complement and must not be
inserted into the selected-line denominator.  Kato's invariant-subspace
formulation therefore uses the three boundary groups

`I_-={23}`, `I_0={24}`, and `I_+={25,26,27}`.

Only the two gaps between `I_0` and its neighboring groups can destroy
simplicity of the selected line.  Treating `I_+` as one block is an
equivalence transformation of the retained Hessian; it adds no selector,
coupling, threshold, action term, or physical mode.

## Correlated Hermite action ball

On each of the 47 multiple-shooting seams, restrict the established cubic
Hermite/Bézier curve to each of its existing 64 subspans.  In action-weighted
coordinates, let `x0,x1` and `r0,r1` be its endpoint states and rates, and
write

`P=[(x1-x0)/2, h*r0-(x1-x0), (x1-x0)-h*r1]`.

The subspan is contained in the exact correlated three-coordinate ellipsoid
`x=x_mid+P*z`, `||z||_2<=1`.  This is the already-derived first-chord
Hermite representation.  It is essential: an independent coordinate box
for the same curve discards the cancellations and does not close.

## Denominator-resolved cluster estimate

Let `H0` be the exact reduced Hessian at the ellipsoid center, with ordered
eigenvalues `lambda_j` and orthonormal eigenvectors.  For a cluster `I`, set

`A_i=V_I^T D H0[P_i] V_I`,

`B_{J,i}=V_J^T D H0[P_i] V_I`.

For every complementary spectral group `J`, define

`d_JI=(1/2) min_{j in J,k in I}|lambda_j-lambda_k|`,

`E_JI=sum_i sum_{j in J,k in I}|(B_{J,i})_{jk}|^2/d_jk`,

where `d_jk=|lambda_j-lambda_k|/2`.  The retained mixed-action majorant gives
outward upper bounds `a_I` and `b_JI` for, respectively,

`D^4 S[V_I,V_I,P,P]` and `D^4 S[V_J,V_I,P,P]`.

The cluster slope and curvature bounds are

`L_I=(sum_i ||A_i||_op^2)^(1/2)`,

`K_I=a_I+2 sum_J (sqrt(E_JI)+b_JI/sqrt(d_JI))^2`,

and the spectral displacement is bounded by

`rho_I=L_I+K_I/2`.

This is the inverse-free Sylvester/Kato estimate: no kinetic/Dirac block is
inverted.  Complementary eigenvectors are used only as an orthogonal proof
basis for the reduced descriptor pencil.

The complementary spectrum is partitioned into proof-only distance bands:
starting at its smallest remaining distance from `I`, a band contains every
branch at distance at most four times that minimum.  The bands are disjoint
and exhaustive.  Splitting the orthogonal Sylvester sum this way is an exact
termwise refinement; the factor four changes proof efficiency only and is
not an action or observable parameter.  It prevents a large far-mode fourth
derivative from being divided by an unrelated nearest-mode denominator.

For each subspan the continuation bootstrap requires

`rho_I < gap_ext(I)/4`

for all three boundary groups, and the two physical boundary margins are

`lambda_24-lambda_23-rho_0-rho_- > 0`,

`lambda_25-lambda_24-rho_0-rho_+ > 0`.

These inequalities imply that branch 24 has one simple continuation on the
whole correlated subspan, while the internal ordering of branches 25--27 is
irrelevant.

## Certified finite-path result

The calculation consumes all `47*64=3008` subspans in order.  Every center
selects branch 24, every cluster satisfies the quarter-gap bootstrap, and
both boundary margins are positive on every correlated action ball.  The
global bounds are:

- minimum selected-line boundary gap:
  `1.7274638520643627e-7`;
- minimum negative/selected gap: `2.354938118100243e-6`;
- minimum selected/positive gap: `1.7274638520643627e-7`;
- maximum selected-line shift: `3.720698270373399e-12`;
- maximum negative-cluster shift: `4.199354764378623e-9`;
- maximum positive-cluster shift: `1.2763237419902918e-8`.

The minimum-margin owner is seam 45, subspan 63.  There the center external
gap is `1.7360349904235292e-7` and the certified remaining margin is
`1.7274638520643627e-7`.

## Claim boundary

This theorem certifies only the selected-line spectral denominator on the
finite Hermite reference path.  It does not yet certify the selected
projector derivative tube, the bordered hard response, the Green/Hermite
shadowing radius from the reference path to an exact retained flow, the
first scalar stop hit, or the earlier physical-domain margins.  Gate 7
therefore remains active, Gate 8 remains locked, and no frozen prediction is
changed.
