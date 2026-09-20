# Complete local input/output vector bound

This package certifies all 74 physical inputs and all 74 projected output
rows of interval 13's right Hermite–Simpson block on the original domain.
It does not close Gate 7 or identify the full nonlinear 72D history family.

The Euclidean operator upper bound is `0.016032551992846547`.
The original fixed-axis two-radius weighted row bounds are
`0.0005576922403983423` and `0.5832743292213708`; both are strictly below one.
The smallest local weighted margin is at least `0.4167256707786291`.
The original radii are retained exactly in `record.json`.

`REPRODUCTION.json` binds two fresh complete transport evaluations, their
byte-identical constant archives and records, and independent norm replay.
All 61 velocity residual models in each family were reproduced numerically.
The 124 base equations and 125 contracted directional equations in each
family were reproduced with fresh residual arithmetic using immutable,
previously verified action-derivative caches. Those action derivatives were
not evaluated again. The two retained-axis majorants reproduced byte for
byte, including every finite outward error-box intersection.

The complete certified row bounds are the `support`, `linear`, `nonlinear`,
and `longitudinal_input_support` fields. The diagnostic field
`uncorrected_longitudinal_input_support` excludes the endpoint base-residual
tail and is not a certified total or an input to any reported inequality.

`LINEAGE.json` records every copied proof input's exact size, SHA-256, and
original campaign location. The retained original physical evidence root
is still required for full source verification. No raw historical evidence
or frozen prediction was replaced by this package.

From the repository root, set `$evidence` to the preserved
`BHSM-ae32-crossing-correction` checkout, `$capsule` to this directory, and
`$out` to a fresh output directory. Reproduce the transport with:

```powershell
python scripts/certify_n12_gate7_refined_directional_transport.py `
  --evidence-root $evidence `
  --midpoint "$capsule/midpoint/parent" `
  --endpoint "$capsule/endpoint/parent" `
  --midpoint-adjoint "$capsule/midpoint/anchor_adjoint.json" `
  --endpoint-adjoint "$capsule/endpoint/anchor_adjoint.json" `
  --midpoint-refined artifacts/gate7/GATE7_PROJECTED_VECTOR_CERTIFICATE_v2.json `
  --endpoint-refined artifacts/gate7/GATE7_ENDPOINT_VECTOR_CERTIFICATE_v1/record.json `
  --midpoint-corrected "$capsule/midpoint/velocity" `
  --endpoint-corrected "$capsule/endpoint/velocity" `
  --midpoint-base-residual "$capsule/midpoint/base_residual" `
  --endpoint-base-residual "$capsule/endpoint/base_residual" `
  --midpoint-error-refinement "$capsule/midpoint/error_refinement.json" `
  --endpoint-error-refinement "$capsule/endpoint/error_refinement.json" `
  --pullback-state-errors --out $out
python scripts/verify_n12_gate7_refined_transport.py --transport $out --out "$out/verification.json"
```

The mathematical identities and remainder rules are in
`theory/n12_gate7_full_input_shared_residual.md`.
