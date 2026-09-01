# Light-Up Ratio Tension Audit

## Problem

The validated common-scale M_Z audit leaves `u/t` as the only dressed-branch quark-ratio warning while dressed `c/t`, `s/b`, and `d/b` pass the declared scheme-aware band.

## Common-Scale Quark RG Result

Classification: `U_T_WARNING_CONFIRMED`
BHSM `u/t`: `1.2690463017606151e-05`
M_Z reference `u/t`: `7.328332371609925e-06`
Relative error: `0.7316986149221621`
Absolute error: `5.362130645996226e-06`

## Why u/t Is Special

The numerator is an extremely light quark. Small absolute changes in a common-scale light-quark reference produce large ordinary relative errors. This does not erase the residual, but it argues for warning-level treatment unless uncertainty propagation is added.

## Existing Official BHSM Status

- `BHSM_BARE_V1` is unchanged.
- `BHSM_DRESSED_V1_CANDIDATE` is unchanged.
- Official `u/t` is unchanged.
- The dressed branch still changes only `c/t`.

## Whether The Tension Is A Failure Or Warning

u/t warning confirmed: `True`
Recommendation: Keep u/t as a common-scale warning. Do not alter official frozen outputs. A light-up-only factor near 1/sqrt(3) is numerically suggestive but remains candidate-only and would change official u/t and CKM sin(theta_13).

## Possible Structural Explanations

| Candidate | Factor | Corrected u/t | Relative Error | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `no_correction` | `1.0` | `1.2690463017606151e-05` | `0.7316986149221621` | `BASELINE` | Baseline frozen value. |
| `required_factor_diagnostic_only` | `0.5774676906148296` | `7.328332371609926e-06` | `1.155833147710002e-16` | `EXPLORATORY_CANDIDATE` | Computed after seeing the reference; diagnostic only, not an allowed derivation. |
| `coframe_amplitude_1_over_sqrt3` | `0.5773502691896258` | `7.326842239355902e-06` | `0.00020333851938751296` | `EXPLORATORY_CANDIDATE` | Simple triplet-amplitude factor; structurally suggestive but not derived. |
| `weak_doublet_probability_1_over_2` | `0.5` | `6.3452315088030755e-06` | `0.13415069253891893` | `EXPLORATORY_CANDIDATE` | Borrowed from existing middle-up dressing family; not derived for light-up mode. |
| `weak_doublet_amplitude_1_over_sqrt2` | `0.7071067811865475` | `8.973512456146406e-06` | `0.22449583358281275` | `EXPLORATORY_CANDIDATE` | Simple two-component amplitude factor; not derived for light-up mode. |
| `alpha_sqrt` | `0.08542454313184122` | `1.0840770054105326e-06` | `0.8520704369782321` | `EXPLORATORY_CANDIDATE` | Alpha-suppressed candidate; included as exploratory stress test only. |

## Rejected Explanations

- Global rescale allowed: `False`
- Damaged ratios under global rescale: `('c/t', 's/b', 'd/b')`
- Mixed-scale masses are not used as precision truth.

## Candidate Repair Criteria

- Any light-up dressing must be derived before adoption.
- It must be frozen before future external comparison.
- It must not damage official CKM, c/t, s/b, d/b, gauge, or electroweak screens.

## Recommendation

Keep `u/t` as a warning-level common-scale tension. The closest simple factor is exploratory only and not official.
