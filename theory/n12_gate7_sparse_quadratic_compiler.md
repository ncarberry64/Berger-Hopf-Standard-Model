# Interval-13 sparse quadratic numerical compiler

This work consumes the immutable `cef38b6b` shared-expression archive. It
does not regenerate an action block, endpoint, midpoint, cell, exact DAG,
or frozen remainder. `Gate7_closed = False`; no physical budget is debited.
The frozen affine diagnostics remain authoritative historical diagnostics:
`kappa_L <= 2.98824e10`, `kappa_T <= 5.77960e12`. They do not establish
physical failure.

## Representation and physical domain

The numerical representation is `P + e`, where

`P = c + sum_i a_i theta_i + sum_{i<=j} q_ij theta_i theta_j`, `|e| <= r`.

The archive's 450 ordered physical symbols and twelve product-ball groups
are retained unchanged: theta, u, and v each contain two endpoint blocks,
with one longitudinal interval and one 74-dimensional transverse Euclidean
ball per endpoint. A canonical pair of integer positions in that frozen
parameter order identifies a monomial everywhere. Off-diagonal polynomial
coefficients occur once; the corresponding symmetric matrix entry is q/2.
Coefficient balls are outward bounds, not new independent physical symbols.

Quadratics are stored as a disk-backed linear circuit of sparse outer-product
atoms. Equal circuit identifiers are combined before expanding monomials.
Only requested outputs are expanded. A read-only JSON-line/offset index
binds to the SHA256 of the frozen compressed midpoint graph, which already
contains the endpoint graphs. No scientific expression is reconstructed.
The active frontier is reference-counted; a disk cache supports larger
selected sets. Its Arb restoration is checked bit-for-bit so eviction
cannot change the result. A failed exact restoration raises an error.

## Outward arithmetic

Write `L=sum a_i theta_i`, `Q=sum q_ij theta_i theta_j`. Multiplication retains
`c_A c_B`, `c_A L_B+c_B L_A`, and `c_A Q_B+c_B Q_A+L_A L_B`. The discarded
polynomial terms are bounded by

`||L_A|| ||Q_B|| + ||L_B|| ||Q_A|| + ||Q_A|| ||Q_B||`.

Error propagation adds

`(||c_A||+||L_A||+||Q_A||) r_B
 + (||c_B||+||L_B||+||Q_B||) r_A + r_A r_B`.

For a scalar unary function, retain `f(c) + f'(c)(L+Q) + f''(c)L^2/2`.
With `w=||L||+||Q||+r` and a third-derivative bound M3 on the entire segment
from c to the physical family, an outward tail is

`|f'(c)|r + |f''(c)|[2||L||(||Q||+r)+(||Q||+r)^2]/2 + M3 w^3/6`.

Positive inverse and square-root lower bounds come from the same frozen
family, as in the original graph. No separate quotient-rule normalization
is introduced. Frozen certified value constraints may recenter an enclosure
and bound its error by the smaller of the translated tail and the certified
radius plus the retained polynomial support. They do not delete Q.

Intermediate Q bounds use triangle bounds on factored forms, while final
support uses the combined signed monomials. This can overestimate cubic
and higher tails and is explicitly a compiler relaxation. Scalar tail
labels are additive diagnostic enclosures; they are not physical sources
of instability. In particular the unary Taylor tail can include nonlinear
propagation of an inherited error, not solely true polynomial degree >= 3.

## Group support

One-dimensional diagonal quadratic-plus-linear blocks use endpoints and
any stationary point in [-1,1], with interval coefficient uncertainty added
outward. Symmetric Euclidean blocks use the intersection of a sparse
Gershgorin spectral enclosure and a Frobenius enclosure. Rectangular
cross-block forms use the smaller of Frobenius and
`sqrt(matrix_one_norm * matrix_infinity_norm)` operator bounds. Actual box
groups use their box norms. Euclidean directions are not replaced by
coordinate boxes. Block signs and cancellations survive coefficient fusion;
summing independent block ranges remains an explicit relaxation.

For the complete multi-affine longitudinal block, the final screen instead
enumerates the vertices of the six scalar interval variables. This is at
most 64 evaluations and preserves signs across distinct LL entries. Cases
with scalar squares retain the one-dimensional stationary-point enclosure.
The final rectangular matrix norm uses maxima of outward row/column
endpoints; ambiguous comparisons of overlapping balls are not used.

Output expansion has two implementations. The scalar implementation
accumulates canonical monomials directly. The block implementation streams
the same outer-product atoms into occupied physical group pairs, each at
most 74 by 74, then canonicalizes the symmetric entries. Exact synthetic
polynomials agree coefficient-by-coefficient. On uncertain coefficients,
both paths round outward; their accumulation orders need not give identical
coefficient radii. The forward scalar-tail ledger is independently compared.

## Scientific composition

The full frozen second incidence is `DF_m M_uv`, with
`M_uv = h(f_0,uv - f_1,uv)/8`, including all 99 components and the stored
physical weights. It must retain the same endpoint mixed-rate roots; it
cannot be introduced as a fresh scalar error. The exact output composition
is `(hP/6+h^2 P DF_m/12)H_0 + 2hP H_m/3
    +(hP/6-h^2 P DF_m/12)H_1`.

The common-border recurrence remains the expression authority:
`nu_uv=(Q_uv/2-nu_u nu_v)/nu` and
`rate_uv=(N_uv-nu_uv rate-nu_u rate_v-nu_v rate_u)/nu`.
The first-derivative products are quadratic atoms of the same symbols.

Frozen LL booking contributes
`Q_ab rL^2 (uLa vLb + vLa uLb)`; frozen LT booking contributes
`2 Q_ab,j rL rT (uLa vTb,j + vLa uTb,j)`.
Booking is projected into the identical output space, subtracted by
canonical monomial key, and only then supported. An assignment in raw J
units cannot be subtracted directly from Newton-output booking units.

## Prototype decision

First compile the dominant descriptor J assignments 13, 3, and 8, retaining
their exact frozen ancestors. Assignments 3 and 8 alias the same node.
Report the frozen sum of affine tails, combined quadratic support,
monomial/block counts, coefficient norms, scalar residual, and the precise
scope of any booking comparison. Extend to all selected incidence and
normalization outputs only with an explicit numerical decision recorded.
Do not turn a failed enclosure into a decay/instability claim or increase
polynomial order before locating the remaining representation loss.

The selected-source booking screen uses the frozen longitudinal axis at
causal destination 370 and the frozen center causal maps. It includes the
three dominant J assignments, all 99 second-incidence components, the common
normalization recurrence, and the full LL/LT subtraction in that same output
space. It is not the complete interval remainder. The causal map-error
correction and omitted source terms remain outside that prototype, so its
normalized support must not be relabelled `kappa_L_interval13`.

## Measured dominant descriptor screen

The three raw midpoint J assignments have frozen affine scalar-tail sum
`OLD = 10.01247127802717`. The combined degree-two model has outward support
`NEW <= 5.004286125` (rounded outward), a reduction of approximately
`2.00077913781`. It retains 22500 canonical mixed u/v monomials: four scalar
LL coefficients, eight LT/TL blocks of 74 coefficients, and four transverse
74-by-74 blocks. The canonical coefficient l2 norm is at most
`0.001535994565`; the equivalent symmetric-matrix Frobenius norm is at most
`0.001086112173` (both rounded outward).

The residual scalar tail is at most `4.998578356`. Its q-based implicit
correction component is approximately `4.998486141013162`, or 99.9981552%
of that tail. The remaining labelled components are approximately
`9.16173117e-5` from higher-order/error propagation and `5.97348165e-7`
from certified-value recentering. Setting the retained polynomial support
to zero while keeping these scalar enclosures would improve OLD by only
about 2.003064 times. This is a limit of this representation, not a lower
bound on the physical action or the physical remainder.

The retained polynomial support is at most `0.005707769073`. Almost all of
it is coefficient uncertainty: the polynomial formed from coefficient
midpoints alone has support about `1.20e-15`. That midpoint-only number is
not a bound for the physical parameter family.

The first missing representation object is the shared mixed bordered
resolvent correction jet, for the eigenline and response with their common
border and row coupling:

`delta_z_uv = ((I-E_border(theta))^(-1)-I) R_border rhs_uv(theta,u,v)`,
`E_border(theta) = I-R_border B_border(theta)`.

It must preserve signed u/v coefficients and shared correction identity
across rows and assignments. The frozen correction leaves instead retain
only `w_i*q/(1-q)*norm_w(R rhs)`, with no directional polynomial. Increasing
the compiler's polynomial order cannot recover information absent from
those leaves. This screen therefore does not justify extending to all
interval-13 roots or recomputing kappas. The classification remains
`CASE_1 = NUMERICAL_COMPILER_CORRELATION_LOSS`.

Two independent descriptor forward compilations produced byte-identical
numerical checkpoints (SHA256
`7af007a4ba82c3d79a006969e90a69a3c918625add2ac6456fe6f4d700c56cfb`).
All arithmetic uses 512-bit Arb and outward support. These are new numerical
compilations of frozen graphs; no frozen scientific producer was rerun.

## Reproduction and retained authority

At the user's requested Git stopping point, the selected forward compilation
is complete: 405 targets and 3607128 frozen ancestors. Signed target support,
LL/LT cancellation and the projected source ledger are **not yet measured**.
The worker was stopped only after its completed checkpoint and committed
SQLite coefficient store were saved. No numerical forward replay is needed
to resume on this machine. See `docs/GATE7_QUADRATIC_RESUME_20260924.md`.

The compact checkpoint evidence package is
`artifacts/flagship_integration/gate7_quadratic_models_20260924/`.
`descriptor_supported.json.gz` retains individual and combined quadratics,
their support and exact rational tails. `descriptor_metrics.json` retains
the restored combined support and coefficient norms. The selected forward
checkpoint is compressed alongside its scalar-tail ledger; `checkpoint.json`
records completed and pending work explicitly. The manifest binds every
retained payload and a source capsule. Temporary SQLite circuits are compiler
caches, not newly generated scientific DAGs.

The numerical workflow, with distinct output directories, is:

1. `index_n12_gate7_frozen_quadratic_graph.py --graph <frozen-middle-graph>
   --out <index>` reads and SHA256-verifies the frozen archive.
2. `prototype_n12_gate7_sparse_quadratic.py --index <index> --work <work>
   --out <report> --scope descriptor` compiles the three J assignments.
   Repeat in a separate directory to compare forward checkpoints exactly.
3. The same command with `--scope targets` compiles only the 405 named
   targets and their ancestors. It checkpoints before output support.
4. `support_n12_gate7_quadratic_checkpoint.py --checkpoint <checkpoint>
   --out <descriptor-report>` supports a completed numerical checkpoint.
   `reuse_n12_gate7_descriptor_support.py` can reuse that support in the
   selected-target pass only after verifying every reachable numerical
   coefficient and shared-node alias under an ID bijection. This check is
   numerical cache identity, not physical branch-identity recertification.
5. `screen_n12_gate7_quadratic_targets.py --compiled <targets-report>
   --evidence-root <frozen-evidence> --out <screen>` performs the selected
   signed composition and booking using frozen operands.
6. `freeze_n12_gate7_quadratic_prototype.py` binds both descriptor checkpoints,
   the selected-target checkpoint, supported models and screen. It
   materializes the evidence twice and requires byte-identical output.

The original long-running workers were checkpointed before their expensive
output-support phase. A guarded, owned-worker transition changed only the
final support implementation to batched physical-block arithmetic; the
forward arithmetic was unchanged. The retained source capsule includes that
recovery utility. New runs checkpoint automatically and do not need it.
