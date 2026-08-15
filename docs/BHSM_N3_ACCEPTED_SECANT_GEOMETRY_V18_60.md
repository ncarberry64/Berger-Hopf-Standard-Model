# BHSM N=3 accepted secant geometry v18.60

Status: **VALIDATED measurement; no new constraint or manifold theorem.**

This diagnostic applies the existing validated v18.15 right-coordinate map in one fixed v18.33 tangent frame. For each consecutive accepted state it measures `s_k=P^{-1}(z_k-z_{k-1})`. The fixed frame makes inter-secant angles comparable and changes neither the physical state nor the exact 376-row residual.

| Accepted secant | Raw norm | Action-owned norm | scale+w+v squared fraction | u+eta-shift+lapse fraction |
|---|---:|---:|---:|---:|
| v18.33 -> v18.37 | 9.76566e-2 | 1.20422e-3 | 0.989948 | 1.05390e-5 |
| v18.37 -> v18.41 | 4.48850e-2 | 5.81736e-4 | 0.987233 | 1.01757e-5 |
| v18.41 -> v18.47 | 4.55263e-3 | 1.77980e-4 | 0.991002 | 6.74308e-7 |
| v18.47 -> v18.54 | 1.39826e-2 | 2.46668e-4 | 0.981967 | 6.26777e-6 |
| v18.54 -> v18.58 | 2.44390e-2 | 3.83685e-4 | 0.979724 | 7.28178e-6 |

The complete artifact reports all nine requested blocks separately: scale, u, w, v, eta-sensitive shift, lapse, period, explicit event multiplier, and remaining retained blocks.

Consecutive action-owned turning angles are `10.0629`, `66.0695`, `99.4945`, and `8.55769` degrees. The accepted continuation therefore does not remain collinear.

## Measurement answers

1. **VALIDATED_CURVED_NOT_COLLINEAR:** accepted physical secants have finite, materially nonzero turning angles. The strongest supported wording is: “The accepted continuation exhibits a measured curved secant geometry in action-owned coordinates.”
2. **VALIDATED:** finite accepted displacement is primarily carried by scale/w/v geometry; its mean action-owned squared fraction is `0.985975`.
3. **RECLASSIFIED:** lapse and eta-sensitive shift are important to the earlier local plateau-loss measurement, but u+eta-shift+lapse carry only `6.98773e-6` mean squared fraction of these finite accepted secants.
4. **INVALIDATED:** two available rejected directions are not systematically more u/eta-shift/lapse-compressed than accepted directions from the same sources. One comparison is lower and one higher.
5. **INSUFFICIENT_RESOLUTION_FOR_CAUSAL_COUPLING:** scale/w/v co-participation and secant rotation are measurable, but five finite secants cannot establish a causal coupling or manifold theorem.

The informal wave-trough picture is at most an analogy for this finite turning record. No continuation restriction is derived from it.

Machine-readable source: `artifacts/BHSM_aether_n3_accepted_secant_geometry_v18_60.json`.
