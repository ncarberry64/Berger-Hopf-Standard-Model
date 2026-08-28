# N=12 Gate-7 recentered-cone bordered internal response

Status: `RECENTERED_GATE7_CONE_ACTION_OWNED_BORDERED_RHS_RESPONSE_CERTIFIED`.

## Closed-system source ledger

Only the external Cauchy/birth source is set to zero.  The outgoing child,
incoming matter, reset/event transport, physical weight, gauge/transverse,
scalar/topographic/contact, and retained AE2 seam contributions are internal
parts of one action-owned Euler--Lagrange system.  They are assembled before
the bordered solve.  No additional seam force is inserted, no internal
response is separately zeroed, and no term already contained in the joint
operator is counted twice.

At a recentered cone state `z`, the retained reduced forcing is

`r(z)=W_red ([W_q grad_q S(z),0]-H_red,q(z)(W_q qdot))`.

This is the complete internal right-hand side consumed by the certificate.

## Inverse-free response enclosure

For the simple selected branch `24`, write `psi` and `lambda` for its
normalized eigenline and eigenvalue.  The bordered physical descriptor is

`K=[[H_red-lambda I,psi],[psi^T,0]]`.

The center equation `K x=[r,0]` is solved directly only as a backward-error
check.  The proof calculation uses the analytical selected-line spectral
solve: the 60 hard components are divided by their own signed spectral gaps,
while the selected component is carried by the border.  It never inverts the
ill-conditioned kinetic/Dirac block or a history operator.

The complete internal source is differentiated as an assembled object.  Its
first- and second-coefficient derivative majorants include the gradient,
mixed configuration/contact, and configuration-variation product rules.  A
cell's relative bordered perturbation is the sum of its signed `D3` block,
the correlated `D4` remainder, and the certified selected-line shift.  For
`eta<1`, the response enclosure is

`chart_factor (1-eta)^-1
 (||K_center^-1 r_center||+||K_center^-1(r-r_center)||)`.

## Certified cover

The 3,009 certified recentered-cone spectrum/projector/inverse parents are
each replaced by eight ordered response children.  Thus 24,072 cells cover
the same full 101-dimensional `sqrt(2)` product cone, including the complete
nonlinear halo on every child.  The eightfold subdivision is proof mesh
refinement only; it changes no action, source convention, event, selector,
physical scale, gate, or chord.

Every relative bordered perturbation is below one, every center solve has
residual below `1e-7`, and all complete response enclosures are finite.  The
global extrema are:

- maximum center internal-source norm: `1300.8934530013148`;
- maximum center bordered-response norm: `13529.816750282167`;
- maximum preconditioned internal-source variation: `148621.8449643774`;
- maximum relative bordered perturbation: `0.7035342221246246`;
- maximum bordered Neumann factor: `3.3730706028416124`;
- maximum complete bordered-response norm: `496147.8931521741`;
- maximum center bordered-solve residual: `2.1828771252109465e-10`.

The complete-response owner is seam `45`, parent `63`, child `7`, on the
action interval `[91.99609375,92.0]`.  Its full row is stored in
`BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RHS_RESPONSE.json` and verified by
the associated hash-provenance test.

## Claim boundary

This certifies a finite complete internal bordered response on the entire
recentered Gate-7 cone.  It does not yet certify the response first-variation
tube, causal interval-vector radius, or first-hit/domain transfer.  The exact
next dependency is the differentiated complete bordered identity

`D x=K^-1 (D r-(D K)x)`

on this identical cover.  Gate 7 remains active, frozen predictions remain
unchanged, and `FULL_BHSM_COMPLETE` remains false.
