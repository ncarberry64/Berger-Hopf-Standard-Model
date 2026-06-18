# BHSM Mixing-Dressed v1 Candidate Audit

Status: `CANDIDATE_NOT_OFFICIAL` / `CANDIDATE_EXPONENT`

This candidate is not part of the official frozen release. It is a clean repair candidate for the CKM 2-3 pressure point and requires derivation of the 1/16 exponent before promotion.

This audit compares the official frozen CKM baseline to the candidate CKM 2-3 mixing dressing. It does not change the official released `BHSM_BARE_V1` or `BHSM_DRESSED_V1_CANDIDATE` outputs.

## Candidate Check

| Check | Result |
| --- | --- |
| Improves `Vcb` | `True` |
| Improves `Vts` | `True` |
| Non-2-3 damage flag | `False` |
| `J_CKM` damage flag | `False` |

## Pressure-Point Residuals

| Quantity | Baseline | Candidate | Reference | Baseline rel. err. | Candidate rel. err. |
| --- | ---: | ---: | ---: | ---: | ---: |
| `Vcb` | `0.0438676646377` | `0.0420078195737` | `0.0411` | `0.0673398` | `0.0220881` |
| `Vts` | `0.0430867199483` | `0.0412751148982` | `0.0415` | `0.0382342` | `0.00541892` |
| `J_CKM` | `3.10117029454e-05` | `2.96992845105e-05` | `3e-05` | `0.0337234` | `0.0100238` |

## Full Residual Table

| State | Quantity | Predicted | Reference | Relative Error |
| --- | --- | ---: | ---: | ---: |
| `BHSM_FROZEN_CKM_BASELINE` | `Vud` | `0.974209560072` | `0.97367` | `0.000554151` |
| `BHSM_FROZEN_CKM_BASELINE` | `Vus` | `0.225617026399` | `0.22431` | `0.00582688` |
| `BHSM_FROZEN_CKM_BASELINE` | `Vub` | `0.00356236761405` | `0.00382` | `0.067443` |
| `BHSM_FROZEN_CKM_BASELINE` | `Vcd` | `0.225466485395` | `0.221` | `0.0202103` |
| `BHSM_FROZEN_CKM_BASELINE` | `Vcs` | `0.973262807243` | `0.975` | `0.00178174` |
| `BHSM_FROZEN_CKM_BASELINE` | `Vcb` | `0.0438676646377` | `0.0411` | `0.0673398` |
| `BHSM_FROZEN_CKM_BASELINE` | `Vtd` | `0.0089775847469` | `0.0086` | `0.0439052` |
| `BHSM_FROZEN_CKM_BASELINE` | `Vts` | `0.0430867199483` | `0.0415` | `0.0382342` |
| `BHSM_FROZEN_CKM_BASELINE` | `Vtb` | `0.999030999287` | `1.01` | `0.0108604` |
| `BHSM_FROZEN_CKM_BASELINE` | `J_CKM` | `3.10117029454e-05` | `3e-05` | `0.0337234` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `Vud` | `0.974209560072` | `0.97367` | `0.000554151` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `Vus` | `0.225617026399` | `0.22431` | `0.00582688` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `Vub` | `0.00356236761405` | `0.00382` | `0.067443` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `Vcd` | `0.225481752711` | `0.221` | `0.0202794` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `Vcs` | `0.973341318495` | `0.975` | `0.00170121` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `Vcb` | `0.0420078195737` | `0.0411` | `0.0220881` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `Vtd` | `0.00858558434191` | `0.0086` | `0.00167624` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `Vts` | `0.0412751148982` | `0.0415` | `0.00541892` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `Vtb` | `0.999110931094` | `1.01` | `0.0107813` |
| `BHSM_MIXING_DRESSED_V1_CANDIDATE` | `J_CKM` | `2.96992845105e-05` | `3e-05` | `0.0100238` |

## Frozen Branch Check

```json
{
  "BHSM_BARE_V1_unchanged": true,
  "BHSM_DRESSED_V1_CANDIDATE_unchanged": true,
  "dressed_branch_changes_only_c_over_t": true,
  "u_over_t_unchanged": true,
  "ckm_sin_theta_13_unchanged": true,
  "changed_rows": [
    {
      "quantity": "c/t",
      "bare": 0.008310500554068288,
      "dressed": 0.004155250277034144,
      "changed": true
    }
  ]
}
```

## Limitations

- `1/16` is not proven and remains a derivation target.
- The candidate is not part of the official frozen release.
- Future adoption requires freezing the rule before future external comparisons.
