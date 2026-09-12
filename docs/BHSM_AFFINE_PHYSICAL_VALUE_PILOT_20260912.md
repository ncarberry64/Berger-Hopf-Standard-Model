# Paired physical value on the selected affine endpoint tube

Endpoint 13 now has a uniform enclosure of the implemented retained-action
physical field on its original affine trial tube. Two separate invocations
recomputed the point response, signed action derivatives, bordered response
enclosure and complete original field formula. Their record and numerical data
are byte identical. The physical field norm has lower bound
**0.0003492756222840398** (the artifact stores the sharper outward rational bound).

The source is the independently paired index-24 affine action-eigenpair
certificate documented in `BHSM_AFFINE_EIGENPAIR_PILOT_20260912.md`. With
K=J*diag(I,-1), the eigenpair Jacobian contraction also proves invertibility of
the actual coupled bordered-response family. No invertibility of a larger
independent-entry Hessian hull is assumed.

The initial direct residual enclosure failed to produce a finite normalized
field. Its maximum response radius was about 28.9 million, compared with a
maximum response-center magnitude of about 6,551.8. That failure remains in
`tmp/bhsm_affine_response_diagnostic_20260912/` in the execution checkout.

Keeping the signed affine directions inside the response-source derivatives
reduced the maximum response radius to about **0.07831**. The derivative includes
the state-dependent configuration term, both third-action terms, the fixed
center residual, and both eigenpair border terms. The largest component radius
of the resulting 99-component field enclosure is about **2.256e-5**. The new
uniform enclosure overlaps the independently verified point value.

No physical tube radius, action, branch rule, measured input policy or frozen
point producer was changed. The rate formula is the original bound source;
only its eigenpair and linear-solve enclosures are supplied by the coupled-domain
proof. The complete third-action descriptor terms and normalization are retained.

Runtime evidence, relative to the scientific execution checkout:
`artifacts/flagship_integration/.affine_physical_value_pilot_work/endpoint_013/`.

| File | SHA256 |
| --- | --- |
| `record.json` | `8C439B79AA4E10616973CD9D3CEE9129350EA3AACB77ABF894ED6E18845FA233` |
| `value.npz` | `545EF861432F339A4EE93ADE8F9FFE249A8546B6BC0389F8AE50A07834C22011` |
| `reproduction.json` | `F5D3AD1404E2491044B41D15301E567EB811E9D74B71F44CB6345E297C478A36` |

Reproduction commands: run
`scripts/certify_n12_gate7_affine_physical_value_pilot.py --endpoint 13`, then
run a separate invocation adding `--recompute`. The producer rejects unpaired
or changed eigenpair inputs, retains failed candidates, checks all sources
before and after evaluation, and requires a positive physical field norm.
Sixteen focused tests cover the response algebra, the actual configuration
derivative, both border terms, failure retention, repeat discipline and the
preceding eigenpair implementation. Synthetic tests are not physical evidence.

This is one endpoint's uniform value enclosure. Actual HS midpoint domains,
uniform field derivatives and remainder bounds, full-history coverage, and the
physical quotient remain open. It does not complete Gate7 or establish a
physical observable prediction. `FULL_BHSM_COMPLETE` remains false.
