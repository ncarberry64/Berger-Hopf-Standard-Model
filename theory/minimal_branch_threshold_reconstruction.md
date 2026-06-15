# Minimal Branch-Threshold Reconstruction

Status: `MINIMAL_BRANCH_THRESHOLD_RECONSTRUCTION_COMPLETE`

This candidate-only audit tests whether simple universal branch-threshold laws can approximate the read-only existing BHSM bare mass pattern. It introduces no official mass formula.

## Best Diagnostic Law

Law: `D_log_threshold_plus_type`
RMS log error to existing bare: `0.510697459271581`
Max abs log error: `1.0380747597108453`
Ordering pass: `True`
Middle-vs-light separation pass: `True`
Parameter count: `4` of sample count `6`
Overfit risk: `True`
Coefficients: `{'A0': 3.2243717587792684, 'a': 3.5005296274400397, 'b_fiber': 4.625517939903549, 'b_base': 1.0161769447426865}`

## Candidate Laws

| Law | RMS | Max abs | Parameters | Overfit risk | Official |
| --- | ---: | ---: | ---: | --- | --- |
| `A_branch_rank_only` | `1.4455346874752366` | `2.543660723891726` | `2` | `False` | `False` |
| `B_branch_rank_plus_type` | `1.327957316462961` | `2.543660723891728` | `4` | `True` | `False` |
| `C_bounded_norm_plus_type` | `0.8432649467827357` | `1.5934776173753837` | `4` | `True` | `False` |
| `D_log_threshold_plus_type` | `0.510697459271581` | `1.0380747597108453` | `4` | `True` | `False` |
| `E_branch_rank_mixed_penalty` | `1.327957316462961` | `2.5436607238917244` | `5` | `True` | `False` |
| `F_orientation_cross` | `0.9440235948328525` | `1.667424771607946` | `5` | `True` | `False` |

## Conclusions

1. Branch-rank threshold alone approximates the existing engine only coarsely.
2. Adding pure-fiber and pure-base branch specialness improves shape in diagnostic laws but increases overfit risk.
3. Bounded/log thresholds are diagnostic alternatives, not official formulas.
4. Remaining error is structured by sector and mode type through hidden response terms.
5. The next derivation target is a branch-aware threshold law plus residual hidden-response terms from boundary dynamics.

## Claim Boundaries

- No official predictions are changed.
- No frozen predictions are changed.
- No new official mass formula is introduced.
- No sector-specific or per-particle coefficients are used.
- `BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived.
- `FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived.
- `RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE` is not upgraded to derived.
