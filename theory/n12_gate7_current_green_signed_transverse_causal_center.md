# Current-Green signed transverse causal center

The component-box screen took absolute values of the 99 output rows before
the Hermite--Simpson test frame, midpoint incidence, reduced inverse, and
causal Green products.  It therefore discarded precisely the correlations
needed by the frozen proof norm.  The recovered signed center tensors permit
the correct order of operations.

For interval `i`, let `B_i` and `B_{i+1}` be the recovered endpoint
transverse Hessians, already pulled back to the endpoint coordinate blocks.
The midpoint input map must be the full Hermite--Simpson first variation
used by the certified mixed operator.  A transverse endpoint variation can
have both longitudinal and frame-normal components at the midpoint.
Writing `A_i=-R_i^{-1}E_{i+1}^T` for the unchanged reduced solve and test
frame, the signed local pure-transverse tensor is assembled as

\[
 \begin{split}
 S_i={}&\left({h_i\over6}A_i+{h_i^2\over12}A_iDF_{i+1/2}\right)B_i\\
 &+{2h_i\over3}A_i\,D^2F_{i+1/2}[M_i,M_i]
 +\left({h_i\over6}A_i-{h_i^2\over12}A_iDF_{i+1/2}\right)B_{i+1}.
 \end{split}
\]

The signs in the `DF` terms are the exact second variation of the midpoint
incidence `h_i(B_i-B_{i+1})/8`.  Each Hessian is pulled back to the same pair
of endpoint transverse-coordinate blocks before addition.

Only after this signed assembly is `S_i` separated into its left-left,
combined left-right, and right-right input blocks.  For each block `T`, the
output covariance `C=T T^T` is retained.  A causal product `P` then has the
exact center Frobenius identity

\[
 \|PT\|_{\rm F}^2=\operatorname{tr}(PCP^T).
\]

Projection on the current Green axis and its orthogonal complement is also
performed on `PCP^T`, so no output component box is introduced.  The
right-right contribution from interval `i-1` and left-left contribution from
interval `i` act on the same global diagonal input block.  They are causally
transported and added with their signed cross covariance before a norm is
taken.  Only distinct global diagonal and nearest-neighbor input monomials are
joined by the triangle inequality required by the existing block-sup proof
domain.

## Complete midpoint pullback

Let `E` be the unchanged midpoint trial frame, including its descriptor
scale, `e` its unit current-Green coordinate axis, and `V` the **stored**
73-column transverse basis of the recovered tensor.  The endpoint pair map
is

\[
 M=[M_L\ M_R],\qquad
 M_L=\tfrac12E_iP_i+\tfrac{h_i}{8}DF_iE_iP_i,\qquad
 M_R=\tfrac12E_{i+1}P_{i+1}-\tfrac{h_i}{8}DF_{i+1}E_{i+1}P_{i+1}.
\]

The fixed reset contributes zero at the left endpoint of interval zero.
Retain both parts of the least-squares decomposition

\[
 K=E^+M,\quad N=M-EK,\quad \ell=e^TK,\quad T=V^TK.
\]

With `H=D²F` at the midpoint, the complete tangent contribution has four
signed terms:

\[
 H[EK,EK]
 =H[EVT,EVT]
 +H[Ee,EVT]\otimes\ell
 +\ell\otimes H[EVT,Ee]
 +H[Ee,Ee]\,\ell\otimes\ell.
\]

The recovered `quadratic_tensor` determines the first term.  Endpoint
transversality does not remove the other three.  Applying only `V.T @ K`
to the recovered tensor omits them, even at the exact frozen center.
Their signs can reinforce or cancel the retained term; the incomplete
signed norm is neither an upper nor a lower bound for the complete norm.

The full ambient pullback additionally requires

\[
 H[M,M]=H[EK,EK]+H[EK,N]+H[N,EK]+H[N,N].
\]

The size of `N` alone does not bound these Hessian contributions.  The
composition now stops if a normal direction has no attached signed Hessian
correction.  This includes arbitrarily small nonzero normal residuals;
roundoff also needs an explicit enclosure before it can be discarded.
Existing recovery tensors and their kernel are unchanged.

## What the existing scalar and mixed data mean

The correlated scalar array stores `H[g,g]`, where `g` is the actual central
Hermite--Simpson midpoint direction.  The mixed midpoint shard stores
`H[g,W]`, where `W=M_L+M_R` uses the same 74 source coordinates on both
endpoints.  It does not store `H[Ee,EV]` in the recovered 73-column basis.

Only if the source directions have no unresolved normal component and
`g=s E e`, the conversion is

\[
 C=H[Ee,Ee]=H[g,g]/s^2,\qquad
 H[Ee,EV]\,(V^TE^+W)=H[g,W]/s-C\,(e^TE^+W).
\]

The last equation must determine all 73 transverse columns and reproduce
the retained mixed data.  The code checks rank, source scale, source axis,
and coordinate consistency; it never equates the 74 source columns with
the 73 recovered basis columns.  Scalar and mixed data hashes, common
geometry provenance, and local mixed-shard fingerprints are checked before
reuse.  Their ball radii are not relabelled as a complete outward enclosure
for this binary64 algebra.

With the presently unfilled normal attachment, a run reports
`SIGNED_TRANSVERSE_CAUSAL_CENTER_CHAIN_RULE_INCOMPLETE`, emits no
coefficient or two-radius screen, and sets center-operator authority and
`validation_passed` false.  It may still identify recovered center tensors
as recovered.  A missing campaign file also blocks execution; no array is
fabricated to fill it.

Only after these center dependencies are complete is a two-radius center
screen meaningful.  A positive complete center screen is a prerequisite for
the unchanged outward remainder calculation; it does not itself close
Gate 7.  Neither an incomplete screen nor its repair is a root-nonexistence,
physical-instability, or completed-BHSM result.  No fitted coefficient,
changed norm, or retuned background is introduced.

The focused regression includes an independent symbolic Hessian of a
nonlinear Hermite--Simpson polynomial with endpoint-transverse inputs that
acquire a midpoint axis component.  It also covers signed and reordered
source coordinates, nonunit scalar-direction scale, both tangent-normal
legs, a pure normal Hessian invisible to the tangent restriction, deficient
mixed rank, and fail-closed result claims.

## Supplemental recovery without repeating the transverse campaign

The conservative next calculation adds the missing ambient blocks at the
370 midpoints while retaining all recovered endpoint and midpoint tensors.
Let `U=EV` be the actual 99-by-73 ambient direction matrix used by a stored
midpoint tensor `Q_UU`.  Complete it to an invertible ambient basis
`S=[U C]`, where `C` has 26 columns, and solve

\[
 M=UA+CD.
\]

For each output component, its full midpoint Hessian pullback is

\[
 H[M,M]=A^TQ_{UU}A+A^TQ_{UC}D
       +D^TQ_{UC}^TA+D^TQ_{CC}D.
\]

Only `Q_UC=H[U,C]` and `Q_CC=H[C,C]` require new contractions.  These
blocks include the missing axis and normal effects.  They contain
`73*26 + 26*27/2 = 2249` distinct directional pairs per midpoint, compared
with `73*74/2 = 2701` pairs in the retained symmetric transverse block.
These are algebraic contraction counts, **not CPU estimates**.

The existing `_mixed_axis_map` in
`certify_n12_gate7_current_green_mixed_transverse_all_endpoints.py` accepts
an arbitrary ambient left direction and an arbitrary-width matrix of
right directions.  A direct supplemental evaluator can use 26 calls with
left direction `C[:,j]` and right directions `[U,C[:,j:]]`.  The existing
ball-preserving mixed kernel supports enclosing direction inputs.  For a
binary64 center evaluator, the signed action tensor API also permits a
rectangular left/right broadcast with shared first-order intermediates.
Neither route changes the action or requires recomputing `Q_UU`.  Implement
the supplemental evaluator separately: preserve the original source
kernels and recovery fingerprints so existing shards remain reusable.

The full basis and solve need an exact rank/nonsingularity certificate or
an outward verification.  A rounded least-squares residual followed by an
SVD tolerance does not justify dropping directions.  Preserve or enclose
the residual of `S*[A;D]=M`, including direction reconstruction roundoff;
a smaller complement is permissible only with a proved spanning relation.
The actual stored tensor directions, their ordering, and descriptor scale
must be bound to this calculation, rather than inferred from a newly
computed transverse basis.

Required retained inputs are the signed tensor and stored basis; midpoint
state and descriptor from the replay; state weights and branch reference
from the endpoint candidate; midpoint frame geometry from the Jacobians;
and the endpoint first-variation data and fixed HS steps defining `M`.
Keep their hashes and the supplemental basis, solve, and block provenance.
The existing recovery shards do not retain the action jets, eigenline
variations, or bordered-response first variations.  Compute these once per
supplemental midpoint and cache them across its cross-block evaluations.
Existing scalar and mixed contractions can validate the new blocks only
after reconstructing their actual directions, scales, and ball inputs.

The separate midpoint first-derivative contribution `DF[M_TT]`, where
`M_TT` is the second HS incidence, remains required; use the retained
ambient midpoint `DF` attachment.  Add it and the endpoint Hessian terms
with their signs before the frozen test/inverse maps and norms.  This
prescription is not an executed recovery or a certificate.  A completed
binary64 recovery supplies center-screen data only.  Outward authority
still requires enclosures for tensor arithmetic, the full-basis solve and
its residual, and the unchanged neighborhood remainder.
