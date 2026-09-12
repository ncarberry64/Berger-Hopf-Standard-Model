# Paired affine endpoint eigenpair certificate

Endpoint 13 now has an independently reproduced normalized action-eigenpair
enclosure throughout its frozen affine trial tube. The selected eigenvalue
retains zero-based index 24 by the connected-domain continuation argument in
`theory/n12_gate7_affine_eigenpair_contraction.md`. The point witness is contained
in the common eigenpair box, the global action inertia has a positive lower
bound throughout the segment hull, and orientation against the original stored
reference remains positive.

The physical radii are unchanged:

- Longitudinal: `4325777291715173/4722366482869645213696`.
- Transverse: `4683284956119277/2417851639229258349412352`.

The first eigenpair proposal failed, with weighted contraction upper bound
4.585820465055534 and image-radius ratio upper bound 5.085820465055534.
Only auxiliary eigenpair coordinates 46, 47 and 48 were enlarged using the
computed image bounds. Recomputing the complete action variation on that new
proposal gave contraction upper bound **0.6011408130859549** and image-radius
ratio upper bound **0.8633540252440827**. All 62 strict inequalities passed.
Both failed and successful trials remain in the artifact.

The improvement comes from completing signed preconditioned third-action
contractions along the original affine input directions before taking absolute
values. The physical domain, action, branch, normalization and measured-data
policy were not changed. The result does not certify the larger unstructured
coordinate-box family of Hessian matrices.

Two separate producer invocations recomputed the point witness, residual and
both variation trials from the action without loading earlier diagnostic
numerical arrays. The resulting record and data were byte identical.

Runtime evidence, relative to the scientific execution checkout:
`artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_013/`.

| File | SHA256 |
| --- | --- |
| `record.json` | `27C72C0087695DB31CAB932DA66FBCADBAAFB295F70794F96CE8347520DCF65D` |
| `eigenpair.npz` | `18F0B06F5102F48886BB496358FF579A3D03208066FB30BDEC564AF0DFAE8700` |
| `reproduction.json` | `7764345055206D470E8702ABB36C1A74A772484C908D6DE821E3FB18F1F211D5` |

Producer: `scripts/certify_n12_gate7_affine_eigenpair_pilot.py --endpoint 13`,
followed by a separate invocation adding `--recompute`. Source and normalized
input bindings are checked before and after evaluation. Seventeen focused tests
cover the new inequalities, failure retention and repeat discipline together
with the preceding affine-Hessian implementation; synthetic fixtures are not
physical evidence.

This closes one selected endpoint's uniform action-mode inclusion. The bordered
physical response, normalized field, actual HS midpoint neighborhoods, uniform
derivatives and remainder, full-history coverage, and physical quotient remain
separate requirements. `Gate7_closed` and `FULL_BHSM_COMPLETE` remain false.
