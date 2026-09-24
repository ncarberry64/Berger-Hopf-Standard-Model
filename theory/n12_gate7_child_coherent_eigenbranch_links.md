# Gate-7 child-coherence contribution: certified moving eigenbranch links

Status: `CERTIFIED_LOCAL_CONNECTED_EIGENBRANCH_EVALUATION_COVER_GATE7_OPEN`.

This separate line starts at authoritative source checkpoint
`24b1e0ea73331103f75ee84d0f440d1c464802aa` and uses the
[child-closure keystone](bhsm_child_closure_cross_scale_candidate.md) only where
there is an explicit operator correspondence. No proposed QCD, electroweak or
many-body physics enters the Gate-7 action.

## Result and exact scope

Two new action-derived links are certified, independently recomputed with
byte-identical output, and attached to existing frozen endpoint and actual-HS
midpoint eigenbranch domains:

| New center-line link | Image/radius upper | Contraction upper | Eigenvalue separation lower |
|---|---:|---:|---:|
| Endpoint 13 to actual-midpoint-13 domain center | 0.15269232454098894 | 0.08756832641277208 | 8.116990278265437e-9 |
| Actual-midpoint-13 domain center to endpoint 14 | 0.14780435367882075 | 0.08731900169779964 | 8.117304450070345e-9 |

The exact rational values, not this rounded table, are authoritative in
[the certificate](../artifacts/flagship_integration/gate7_shared_eigenbranch_links_20260923/certificate.json).
[The independent repeat](../artifacts/flagship_integration/gate7_shared_eigenbranch_links_20260923/independent_repeat.json)
is byte-identical, with
[a reproduction receipt](../artifacts/flagship_integration/gate7_shared_eigenbranch_links_20260923/reproduction.json).

The new connected set is the union of the two original endpoint affine domains,
the complete original coupled actual-HS midpoint outer domain, and the two
center-line links. The existing midpoint certificate is bound directly to
its independently reproduced HS image-domain file. It is not an invented
independent midpoint. All original physical radii match the current ledger.

On that union, the oriented normalized index-24 eigenbranch is linked through
overlapping certified witnesses. This is a **connected evaluation cover for
interval 13**, not a certificate for every continuous dense-output history
curve or its surrounding tube. No 370-interval cover is claimed. In particular,
the earlier eight-endpoint-only coverage audit remains true for the old union;
this result adds two links and reuses a midpoint domain outside that audit's
endpoint-only inventory.

Gate 7 remains OPEN. `kappa_L=None`, `kappa_T=None`, and
`FULL_BHSM_COMPLETE=False`. No physical remainder debit, interval-14 booking,
frozen point proof, full-history certificate, prediction or criterion changes.

## Why the keystone helps mathematically

Closure of an identity sector does not require a fixed state representative.
The corresponding numerical distinction here is between retaining the selected
eigenline and retaining one fixed eigenpair witness box. The frozen endpoint-13
and endpoint-14 eigenpair boxes are disjoint: coordinate 22 has positive gap
approximately `2.943482609009098e-4`. Thus the unchanged endpoint-13 witness
cannot enclose the whole link merely by a sharper estimate.

The construction transports the eigenpair predictor and the preconditioner
together. Their common interpolation parameter is retained before taking
support. This is the explicit reuse of coherence: one correlated operator
graph, rather than independently bounded drift terms. It supplies no new
physical child constraint or additional Gate-7 contraction assumption.

Direct connecting third-action bounds are also implemented in
[the shared connecting kernel](../src/bhsm/interface/shared_connecting_hessian.py).
The exploratory full-star and translated-tube bounds did not close their
sufficient tests; they are not promoted certificates and do not prove physical
instability. The successful result uses the actual midpoint's existing
eigenbranch as an intermediate anchor, then proves the new center-line links.
No new endpoint or midpoint eigenpair solve is performed.

## Frozen imports and moving objects

The direct imports from the existing evidence store are the reproduced records,
receipts and data in:

```text
.affine_eigenpair_pilot_work/endpoint_013/
.coupled_midpoint_eigenpair_pilot_work/interval_013/
.affine_eigenpair_pilot_work/endpoint_014/
.coupled_hs_midpoint_domain_work/interval_013/
```

Their raw SHA-256 bindings are recorded. Each eigenbranch already certifies the
oriented index-24 pair on its complete domain. Their center states and eigenpair
predictors are exact saved numbers. The stored center defect is `D_i=I-R_i J_i`;
recovering `J_i=R_i^(-1)(I-D_i)` with Arb interval matrix inversion recovers an
enclosure, not a newly evaluated physical Hessian.

For either new link let `x(s)=x0+s*(x1-x0)`, `0<=s<=1`, and put

```text
yhat(s) = (phat(s),lambdahat(s)) = (1-s)y0+s y1,
R(s) = (1-s)R0+s R1,
Jbar(s) = (1-s)J0+s J1.
```

`phat` is not assumed normalized. Normalization remains the last equation of
the exact bordered system

```text
F(x,p,lambda) = ((H_red(x)-lambda I)p, (p.p-1)/2).
```

This retained border uses top-right `-p` and bottom-left `p^T`. Its sign
convention is the existing `uniform_eigenpair_proposal._bordered` convention.

## Exact cancellation and the new action operator

Joint interpolation gives

```text
I-R(s)Jbar(s)
  = (1-s)D0+s D1+s(1-s)(R1-R0)(J1-J0).
```

For the two links the resulting surrogate defect bounds are approximately
`0.0029264740491552568` and `0.0027665330011284782`. These alone do not bound
the physical action Jacobian. Its missing block is the interpolation error

```text
E_H(s) = H_red(x(s)) - ((1-s)H_red(x0)+s H_red(x1)).
```

The Peano-kernel interpolation bound has mass `s(1-s)/2 <= 1/8`. Write
`dx=x1-x0`, `W=diag(w)`, and let the output dual vector range over a Euclidean
unit ball. For fixed output `s`, the complete scalar contraction is

```text
D4 S(x0+t*dx)[ pad(R(s)^T W^-1 dual), pad(eta), dx, dx ],
0<=s,t<=1.
```

Only the first 61 columns of the bordered preconditioner enter the padded
action leg; its final output row is included. Two choices of `eta` give all
the needed curvature blocks: the entire box `|eta_i|<=w_i`, and the moving
predictor `phat(s)`. The dual ball contains every weighted coordinate output,
so the scalar support bounds the weighted infinity norm of the entire output.
The action evaluation retains the signed preconditioner contraction, shared
`s`, global inertia reciprocal and boundary term. Independent `t` spans the
whole new segment; old endpoint derivatives are not extrapolated.

The new physical Jacobian interpolation-error bounds are approximately
`0.0010299159716363226` and `0.0009323291418785745`. Adding the respective
surrogate defects gives `0.003956390020791579` and `0.003698862143007053` before
the nonlinear eigenpair-witness correction. Both action domains have certified
positive inertia. First-order Taylor models retain their full outward tails;
no approximation tail is differentiated or treated as zero.

## Residual, witness and Banach proof

Let `dp=p1-p0`, `dlambda=lambda1-lambda0` and `dH=H1-H0`. The residual for the
linearly interpolated Hessian and eigenpair is exactly

```text
r_top(s) = (1-s)r0+s r1 - s(1-s)(dH-dlambda I)dp,
r_norm(s) = (1-s)n0+s n1 - s(1-s)(dp.dp)/2.
```

The implementation combines these signed functions with the same `R(s)` before
support. The action curvature contributes `R(s)(E_H(s)phat(s),0)`, bounded by
the second new D4 contraction. Thus neither normalization curvature nor the
moving-eigenpair residual is omitted.

Choose base weights as the componentwise maximum of the two frozen witness
radii. A deterministic finite search over `gamma=2^k`, `0<=k<=30`, selects an
eigenpair witness radius `gamma*w`. Both successful links select `gamma=16384`.
This enlarges only a proof witness in `(p,lambda)`; every physical state-domain
radius is unchanged. If the resulting inequalities fail, no certificate is
issued as successful. The search does not fit an observable.

With `Y` the residual bound in base weights, `q_base` the sum of surrogate and
physical interpolation defects, and `q_nl` the inherited quadratic eigenpair
variation bound per unit witness scale, the complete tests are

```text
q = q_base + gamma*q_nl < 1,
Y/gamma + q < 1.
```

The nonlinear term includes both variable-lambda/vector cross terms and the
normalization row, using a uniform entrywise bound on `R(s)`. The resulting
self-map and contraction inequalities hold uniformly on the complete link
parameter interval and eigenpair witness. They prove a unique normalized
eigenpair within each witness for every link point.

At both endpoints the new witness contains the entire corresponding frozen
eigenpair box. Therefore the root is the inherited oriented branch there.
Uniform invertibility and continuity prevent an eigenvalue collision along
the link; the inherited index 24 persists. This proves branch agreement on
the overlaps with the original endpoint/midpoint domains, not a fresh physical
selector or a new constraint on those domains.

At a normalized root the bordered Jacobian is sign-equivalent to the symmetric
border with eigenvalues `+1`, `-1` and the other eigenvalue differences. From
the weighted defect bound,

```text
||J^-1||_2 <= ||w||_2 * sup_s ||W^-1 R(s)||_infinity / (1-q).
```

Its reciprocal yields the positive gap lower bounds in the table. Scaling
all witness weights by `gamma` cancels in this inverse-norm conversion.

## Separate implementation and validation

The proof runs in
[the link producer](../scripts/certify_n12_gate7_shared_eigenbranch_links.py),
with the algebra in
[the shared transport kernel](../src/bhsm/interface/shared_eigenpair_transport.py).
[The packager](../scripts/package_n12_gate7_shared_eigenbranch_links.py) checks
byte identity, direct input hashes, exact rational inequalities and the unchanged
current physical radii; it does no numerical action work.

The first and independent repeat each evaluate the four new fourth-action
contractions from scratch. The package itself is materialized twice with
identical bytes. Frozen producers are never invoked. Focused tests exercise
the interpolation identities, shared preconditioner cancellation, Peano factor,
normalization cross term, full weighted input/output domains, exact acceptance
inequalities and rejection of false global promotion. Tests read the certificate
without regenerating tracked reports.

To reproduce only this new proof when an independent run is actually required:

```powershell
python scripts/certify_n12_gate7_shared_eigenbranch_links.py --evidence-root ../BHSM-ae32-crossing-correction --out tmp/new_links_first.json
python scripts/certify_n12_gate7_shared_eigenbranch_links.py --evidence-root ../BHSM-ae32-crossing-correction --out tmp/new_links_repeat.json
python scripts/package_n12_gate7_shared_eigenbranch_links.py --first tmp/new_links_first.json --repeat tmp/new_links_repeat.json --out tmp/new_links_package
python -m pytest -q tests/test_shared_connecting_hessian.py tests/test_shared_eigenpair_transport.py tests/test_shared_eigenbranch_link_certificate.py
```

The existing successful outputs must not be rerun just for confidence.

Validation at the checkpoint: 19 focused tests pass; exact first/repeat and
twice-materialized package bytes agree; status, forbidden-claim,
frozen-prediction-integrity and retained precision checks pass. The full
public-readiness audit on the authoritative checkout still reports a repository
hygiene failure while its other checks pass. This local research checkpoint
does not claim a clean public physical release or change artifact-retention
policy.

## Remaining Gate-7 work

This is a demonstrated local route for connecting already owned child/eigenline
data. It does not certify the remaining 369 intervals, a minimal anchor set,
or a continuous dense-output tube. Further links require their own actual
domain and operator evidence; none is authorized automatically by this result.

For physical remainder assembly, the original-domain mixed eigenline and
response operators, normalization, true HS first/second incidence, booked
quadratic subtraction and signed causal transport still have to be attached
over all required evaluations. This proof provides a branch/inverse connection
ingredient; it is not a complete rate Hessian and cannot be multiplied by the
history influence weights or charged to either kappa budget.

The useful next integration is to consume this reproduced local link receipt
as a separate cover ingredient, assess where existing midpoint certificates
can be reused, and distinguish evaluation-domain coverage from any additional
continuous-history-domain obligation. The authoritative Gate-7 numerical
criteria and global UNKNOWN verdicts remain unchanged.

A read-only inventory finds independently reproduced coupled midpoint
eigenbranch records for intervals 13 through 18. Only interval 13's direct
inputs were hash-verified and used in this proof. The remaining records are
candidates for a later bounded import and link calculation, not newly certified
coverage here and not authorization for a broad endpoint campaign.
