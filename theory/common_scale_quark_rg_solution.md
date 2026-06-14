# Common-scale quark RG validation

Issue: `P1-2`
Status: `CLOSED_SOLVED`
Classification: `COMMON_SCALE_RG_VALIDATED_WARNING`
Blocker: `None`

## Pass/Fail Criteria

- Validated common-scale u/t, c/t, d/b, s/b references must be available.
- Mixed-scale PDG-style values cannot be used as a precision verdict.

## Evidence

- Common-scale input validated: True.
- Reference scale: M_Z = 91.1876 GeV.
- Reference scheme: MSbar running quark masses at M_Z in SM convention.
- Dressed c/t improves versus bare: True.
- Warning-level dressed ratios: ('u/t',).
- Precision quark matching remains warning-level because uncertainties are not propagated and u/t remains outside tolerance.

## Unchanged Quantities

- quark ratios unchanged
- dressed c/t unchanged

## Next Action

propagate common-scale uncertainties and investigate the remaining u/t tension without retuning
