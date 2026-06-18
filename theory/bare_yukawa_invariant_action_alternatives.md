# Bare Yukawa Invariant-Action Alternatives

Status: `BARE_YUKAWA_INVARIANT_ACTION_VARIANTS_CANDIDATE`

The raw integer eigenvalue may be incomplete because the previous scan preferred the largest epsilon tested and zeroed the fourth-order and focusing terms. This note audits invariant alternatives without sector-specific tuning.

## Variants

| Variant | Status | Control only | Rationale |
| --- | --- | --- | --- |
| `A_raw` | `RAW_BARE_ACTION_TIER_C_ORDERING_ONLY_CONFIRMED` | `False` | Raw integer-coordinate action from the previous numerical gate. |
| `B_target_degree_normalized` | `DEGREE_NORMALIZED_ACTION_CANDIDATE` | `False` | Sheet-coordinate action using q/N_f and j/N_f. |
| `C_mixed_raw_degree` | `MIXED_RAW_DEGREE_ACTION_CANDIDATE` | `False` | Raw eigenvalue divided by target degree N_f. |
| `D_channel_dimension_normalized` | `CHANNEL_DIMENSION_NORMALIZED_ACTION_CANDIDATE` | `False` | Raw eigenvalue divided by active channel count N_f^2-1. |
| `E_branch_relative` | `BRANCH_RELATIVE_ACTION_STRUCTURAL_CANDIDATE_CONTROL` | `True` | Sector-relative subtraction by the minimum selected nonzero branch. |

Degree normalization tests whether suppression should depend on normalized sheet coordinates. Channel-dimension normalization tests whether active operator channel space dilutes spectral cost. Branch-relative subtraction is dangerous because it subtracts a sector minimum; it is therefore `BRANCH_RELATIVE_ACTION_STRUCTURAL_CANDIDATE_CONTROL` only.

## Variant Results

| Variant | Response | Verdict | RMS log error | Max abs log error | Ordering | Evidence allowed |
| --- | --- | --- | ---: | ---: | --- | --- |
| `A_raw` | `bare_only` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY` | `2.650470675424182` | `4.721337722933362` | `True` | `True` |
| `A_raw` | `current_candidate_responses` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY` | `2.7321527735934024` | `4.759226970704423` | `True` | `True` |
| `B_target_degree_normalized` | `bare_only` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY` | `3.1075738561160615` | `6.102463009393552` | `True` | `True` |
| `B_target_degree_normalized` | `current_candidate_responses` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY` | `3.0686322603607583` | `6.102463009393552` | `True` | `True` |
| `C_mixed_raw_degree` | `bare_only` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY` | `2.658330119417409` | `5.168810786151742` | `True` | `True` |
| `C_mixed_raw_degree` | `current_candidate_responses` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY` | `2.724729616918709` | `5.230402065422447` | `True` | `True` |
| `D_channel_dimension_normalized` | `bare_only` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY` | `3.242428941083313` | `6.0976067545372965` | `True` | `True` |
| `D_channel_dimension_normalized` | `current_candidate_responses` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY` | `3.2141370234701894` | `6.12456373568821` | `True` | `True` |
| `E_branch_relative` | `bare_only` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_D_FAIL` | `3.1214607962810095` | `4.912481179126079` | `True` | `False` |
| `E_branch_relative` | `current_candidate_responses` | `BARE_YUKAWA_INVARIANT_VARIANT_TIER_D_FAIL` | `2.998821658798196` | `4.219333998566134` | `True` | `False` |

## Guardrails

- `NO_SECTOR_SPECIFIC_TUNING_GUARDRAIL_REINFORCED`
- `QUARK_RATIO_SCHEME_SENSITIVITY_GUARDRAIL`
- No sector-specific parameters are used in variants A-D.
- Variant E is not used as primary evidence.
- No official frozen output is updated.
