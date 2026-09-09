# Physical Hessian evaluation at interval-valued HS points

Status: arithmetic implementation for the retained action graph. No new
physical Hessian campaign or neighborhood theorem is certified here.

The independently reproduced direct HS value campaign represents the actual
weighted midpoint with Arb balls. Unweighting this point also requires Arb
arithmetic. The older batched Hessian graph was used at stored binary64
points: its configuration vector explicitly converted state entries to
float, and its axis/direction inputs did likewise. The older factored
integrand also converted the selected state to float before caching local
geometry. Reusing those paths at the direct physical midpoint would erase
the incoming uncertainty. This does not invalidate their original stored-
point evidence, but prevents treating it as direct-midpoint evidence.

## Separate graph

`certify_n12_gate7_ball_physical_hessian_graph.py` retains the complete
batched physical mixed-derivative formulas and changes exactly three input
conversions: the axis, the transverse columns, and the configuration state.
Each conversion preserves an Arb ball or lifts an integer/binary64 value
exactly. Wider floating operands require an explicit exact conversion.
All quadrature constants, weights, solves, contractions, normalization and
descriptor formulas remain unchanged. The parent function's source hash is
guarded at import, and an AST comparison checks the entire function against
the parent with only those three substitutions allowed.

`use_ball_factored_integrand` retains the existing symbolic factorization,
binary64 constants and contraction ordering. It caches the full interval
state. Cache identity compares the represented midpoint and radius of every
entry: equality of uncertain real values is not an appropriate cache-key
test. State or precision changes are rejected, and the original integrand
is restored on every exit. An AST comparison limits this adapter's changes
to state preservation and represented-ball equality.

The original action jet constructor, prescribed-action contractions and
boundary expressions already accept Arb state entries. Their sources are
unchanged. Bulk matrix transfers can still be used because they preserve
every Arb entry, including radii.

`VerifiedHessianBase` constructs the original action jets and independently
checks the normalized index-24 eigenpair once per process and physical point.
Its context temporarily reuses those exact objects across row evaluations,
rejecting changes to represented state balls, Hessian identity, reference or
precision. It restores both parent functions on failure or normal exit.
The future producer remains responsible for source fingerprints, value
consistency, complete row coverage and independent point recomputation.

## Validation and use

Tests enclose point corners with the factored interval geometry and its
fifth-order local jets. A separate two-state quadratic-action fixture reduces
the complete normalized rate to

    f(p,q,s) = (s*q, p, 0) / sqrt(s*s*q*q + p*p).

Symbolic differentiation supplies an independent Hessian. The ball graph's
output encloses these derivatives at corners of the state and descriptor
box, including an uncertain input axis and a descriptor direction. This
tests the derivative algebra and operand handling; the fixture is not BHSM
physical data.

A direct physical row producer must still bind the complete paired physical
value inputs, construct the original action jets at that interval state,
independently certify the normalized eigenpair, positive reference overlap
and selected index 24, and export finite outward rows with independent
reproduction. Cached base jets/eigenpairs must compare represented interval
states, not `np.array_equal` on uncertain values. All 99 input directions
must be represented before a point is called complete. Existing Hessian
caches remain in their original workspaces and are not silently adopted.

Even a complete direct point Hessian is not a bound over the full proof
neighborhood. Physical quotient identification, branch continuation and
remaining operator/observable dependencies remain open. The running direct
DF and global-linear pipelines use their unchanged bound source files.
