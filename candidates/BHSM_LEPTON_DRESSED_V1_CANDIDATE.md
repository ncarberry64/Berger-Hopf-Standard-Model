# Charged-Lepton Precision Closure

## Problem

BHSM charged-lepton ratios survive at hierarchy/pattern level, but the sprint asks whether one fixed mode-dependent rule can improve both `mu/tau` and `e/tau` without per-particle fitting.

## Official Frozen Lepton Status

- Official frozen lepton ratios are unchanged.
- The candidate is not part of `BHSM_BARE_V1` or `BHSM_DRESSED_V1_CANDIDATE`.

## Why Ordinary Running Failed

Charged-lepton pole ratios are scheme-stable at this audit level; ordinary running is not used as a precision repair.

## Why Time/Location Variation Is Rejected

The sprint uses no time, location, or environment variation. Any such rule would violate the fixed frozen-output discipline.

## Candidate Fixed Mode-Dressing Rule

Formula: `Z_l(k,j)=exp[-eta_l*(q^2+j^2)]`
Fit input: `mu/tau`
Held-out row: `e/tau`
eta_l: `0.0020443439144236667`

## Held-Out Prediction Logic

| Rank | Mode | Norm | Baseline Error | Dressed Error | Improved | Fitted Input | Held Out |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `middle` | `(5, 2)` | `5` | `0.010274139803682273` | `0.0` | `True` | `True` | `False` |
| `light` | `(9, 3)` | `18` | `0.03374889710210006` | `0.0035997951408065676` | `True` | `False` | `True` |

## Damage Checks

Extension allowed: `False`
The candidate is explicitly charged-lepton scoped. Extending the fitted eta_l to quarks or CKM would change official frozen outputs without a derivation.

## Closure Verdict

Classification: `LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL`
Candidate status: `CANDIDATE_NOT_OFFICIAL`
Lepton precision blocker closed: `False`

The candidate improves both rows, but it remains non-official because `eta_l` is fit from `mu/tau`, not derived.

## Promotion Criteria

- derive eta_l independently from BHSM internal dynamics
- pre-freeze the rule before future external comparisons
- show the charged-lepton scope follows from the action rather than convenience
- show no damage to quark, CKM, gauge, Higgs, or H_T screens

## Rejection Criteria

- eta_l remains fitted from mu/tau
- the held-out e/tau row fails under updated references
- the rule requires separate electron and muon factors
- extension outside charged leptons damages frozen outputs

## Recommendation

Keep official lepton ratios frozen. The one-parameter mode-norm candidate improves mu/tau and the held-out e/tau row, but eta_l is fit from mu/tau rather than derived, so the candidate remains non-official.
