# CKM Mixing Dressing Candidate Audit

Status: `EXPLORATORY_CANDIDATE`

This audit tests whether fractional powers of the existing `Z_virt^{u,2}=1/2` dressing factor suppress only the CKM 2-3 mixing channel. It does not modify `BHSM_BARE_V1`, `BHSM_DRESSED_V1_CANDIDATE`, frozen prediction files, or released CKM outputs.

Any adopted mixing-dressing rule must be frozen before future external comparisons.

## Inputs

- `Z_virt^{u,2} = 0.5`
- Tested candidates: `no_correction`, `Z^(1/4)`, `Z^(1/8)`, `Z^(1/16)`
- Dressing scope: multiply only `sin_theta_23`; leave `sin_theta_12`, `sin_theta_13`, and Hopf-phase `delta_CKM` unchanged.
- CKM reconstruction: standard CKM parameterization using matrix magnitudes.
- Reference set: PDG-style direct CKM magnitudes plus existing repository `J_CKM = 3.0e-5` reference.

## Candidate Summary

| Candidate | Factor | sin(theta_23) | Vcb rel. err. | Vts rel. err. | J rel. err. | Improves Vcb/Vts | Damages rest | Conclusion |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `no_correction` | `1` | `0.0438679429909` | `0.0673398` | `0.0382342` | `0.0337234` | `False` | `False` | baseline frozen CKM screen; no mixing dressing applied |
| `Z^(1/4)` | `0.840896415254` | `0.0368883960056` | `0.102478` | `0.125581` | `0.1305` | `False` | `True` | does not improve both Vcb and Vts relative to the baseline |
| `Z^(1/8)` | `0.917004043205` | `0.0402270810897` | `0.0212451` | `0.0472208` | `0.051926` | `False` | `True` | does not improve both Vcb and Vts relative to the baseline |
| `Z^(1/16)` | `0.957603280699` | `0.0420080861256` | `0.0220881` | `0.00541892` | `0.0100238` | `True` | `False` | improves Vcb/Vts without material damage to non-2-3 rows in this audit |

## Full Residual Table

| Candidate | Quantity | Predicted | Reference | Relative Error |
| --- | --- | ---: | ---: | ---: |
| `no_correction` | `Vud` | `0.974209560072` | `0.97367` | `0.000554151` |
| `no_correction` | `Vus` | `0.225617026399` | `0.22431` | `0.00582688` |
| `no_correction` | `Vub` | `0.00356236761405` | `0.00382` | `0.067443` |
| `no_correction` | `Vcd` | `0.225466485395` | `0.221` | `0.0202103` |
| `no_correction` | `Vcs` | `0.973262807243` | `0.975` | `0.00178174` |
| `no_correction` | `Vcb` | `0.0438676646377` | `0.0411` | `0.0673398` |
| `no_correction` | `Vtd` | `0.0089775847469` | `0.0086` | `0.0439052` |
| `no_correction` | `Vts` | `0.0430867199483` | `0.0415` | `0.0382342` |
| `no_correction` | `Vtb` | `0.999030999287` | `1.01` | `0.0108604` |
| `no_correction` | `J_CKM` | `3.10117029454e-05` | `3e-05` | `0.0337234` |
| `Z^(1/4)` | `Vud` | `0.974209560072` | `0.97367` | `0.000554151` |
| `Z^(1/4)` | `Vus` | `0.225617026399` | `0.22431` | `0.00582688` |
| `Z^(1/4)` | `Vub` | `0.00356236761405` | `0.00382` | `0.067443` |
| `Z^(1/4)` | `Vcd` | `0.22551973916` | `0.221` | `0.0204513` |
| `Z^(1/4)` | `Vcs` | `0.973539989296` | `0.975` | `0.00149745` |
| `Z^(1/4)` | `Vcb` | `0.0368881619394` | `0.0411` | `0.102478` |
| `Z^(1/4)` | `Vtd` | `0.00752198866871` | `0.0086` | `0.12535` |
| `Z^(1/4)` | `Vts` | `0.0362883816222` | `0.0415` | `0.125581` |
| `Z^(1/4)` | `Vtb` | `0.999313050573` | `1.01` | `0.0105811` |
| `Z^(1/4)` | `J_CKM` | `2.60849922009e-05` | `3e-05` | `0.1305` |
| `Z^(1/8)` | `Vud` | `0.974209560072` | `0.97367` | `0.000554151` |
| `Z^(1/8)` | `Vus` | `0.225617026399` | `0.22431` | `0.00582688` |
| `Z^(1/8)` | `Vub` | `0.00356236761405` | `0.00382` | `0.067443` |
| `Z^(1/8)` | `Vcd` | `0.225495639442` | `0.221` | `0.0203423` |
| `Z^(1/8)` | `Vcs` | `0.973413334137` | `0.975` | `0.00162735` |
| `Z^(1/8)` | `Vcb` | `0.0402268258388` | `0.0411` | `0.0212451` |
| `Z^(1/8)` | `Vtd` | `0.008212773995` | `0.0086` | `0.0450263` |
| `Z^(1/8)` | `Vts` | `0.0395403379271` | `0.0415` | `0.0472208` |
| `Z^(1/8)` | `Vtb` | `0.999184223264` | `1.01` | `0.0107087` |
| `Z^(1/8)` | `J_CKM` | `2.84422185756e-05` | `3e-05` | `0.051926` |
| `Z^(1/16)` | `Vud` | `0.974209560072` | `0.97367` | `0.000554151` |
| `Z^(1/16)` | `Vus` | `0.225617026399` | `0.22431` | `0.00582688` |
| `Z^(1/16)` | `Vub` | `0.00356236761405` | `0.00382` | `0.067443` |
| `Z^(1/16)` | `Vcd` | `0.225481752711` | `0.221` | `0.0202794` |
| `Z^(1/16)` | `Vcs` | `0.973341318495` | `0.975` | `0.00170121` |
| `Z^(1/16)` | `Vcb` | `0.0420078195737` | `0.0411` | `0.0220881` |
| `Z^(1/16)` | `Vtd` | `0.00858558434191` | `0.0086` | `0.00167624` |
| `Z^(1/16)` | `Vts` | `0.0412751148982` | `0.0415` | `0.00541892` |
| `Z^(1/16)` | `Vtb` | `0.999110931094` | `1.01` | `0.0107813` |
| `Z^(1/16)` | `J_CKM` | `2.96992845105e-05` | `3e-05` | `0.0100238` |

## Best 2-3 Residual Candidate

`Z^(1/16)` has the lowest combined `Vcb`/`Vts` relative error among the pre-declared candidates.

This is not an adopted BHSM rule. It is an exploratory candidate for a future freeze decision only.

## Limitations

- This audit is not part of the frozen release.
- The CKM frozen values remain unchanged.
- No parameter, mode, tolerance, or prediction output is retuned.
- Matrix references are PDG-style comparison inputs, not fitting targets.
- Any adopted mixing-dressing rule must be specified and frozen before future external comparisons.
