# Branch Threshold Candidate Laws

Status: `BRANCH_RANK_THRESHOLD_DIAGNOSTIC`

This note describes candidate branch-threshold laws. They are diagnostics only and remain unofficial.

| Law | Formula | Parameter count | Overfit risk |
| --- | --- | ---: | --- |
| `A_branch_rank_only` | `log_pred=A0-a*branch_rank_by_N` | `2` | `False` |
| `B_branch_rank_plus_type` | `log_pred=A0-a*branch_rank_by_N+b_fiber*pure_fiber+b_base*pure_base` | `4` | `True` |
| `C_bounded_norm_plus_type` | `log_pred=A0-a*N/(1+N)+b_fiber*pure_fiber+b_base*pure_base` | `4` | `True` |
| `D_log_threshold_plus_type` | `log_pred=A0-a*log(1+N)+b_fiber*pure_fiber+b_base*pure_base` | `4` | `True` |
| `E_branch_rank_mixed_penalty` | `log_pred=A0-a*branch_rank_by_N+b_fiber*pure_fiber+b_base*pure_base-c_mixed*mixed` | `5` | `True` |
| `F_orientation_cross` | `log_pred=A0-a*branch_rank_by_N+b_fiber*pure_fiber+b_base*pure_base+gamma*orientation_product` | `5` | `True` |

Pure-fiber and pure-base specialness are tested as universal coefficients, not sector-specific tuning. Mixed-branch penalties and orientation/cross terms are diagnostic only. Forbidden tuning rules: no sector-specific parameters, no per-particle response factors, no retrofitting frozen predictions.

Guardrail: `NO_NEW_OFFICIAL_MASS_FORMULA_GUARDRAIL`.
