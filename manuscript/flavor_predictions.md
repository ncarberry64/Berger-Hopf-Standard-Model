# Flavor Predictions

The frozen flavor outputs are generated from the fixed mode ledger and overlap
rule. The term prediction here means frozen model-output ledger entry, not a
claim of a completed first-principles derivation.

## Charged Fermion Ratios

| Sector | Heavy | Middle | Light |
| --- | --- | --- | --- |
| charged leptons | `1.0` | `0.06007447093260976` | `0.00029729106456492414` |
| up quarks, bare | `1.0` | `0.008310500554068288` | `1.2690463017606151e-05` |
| down quarks | `1.0` | `0.021933971495439474` | `0.0011165200546001757` |

In the mixed-default residual audit, charged lepton rows are scheme-stable,
while quark rows are marked scheme-sensitive. The worst mixed-default charged
fermion residual is `mass_ratio.up_quarks.middle`, with relative error
`0.13003176431657681`, and is classified as `SCHEME_SENSITIVE`.

## PMNS Effective Extension

The PMNS rows are effective-extension screens:

| Quantity | BHSM Output |
| --- | --- |
| `sin2_theta_13` | `0.021892057707851405` |
| `sin2_theta_12` | `0.3114412756254819` |
| `sin2_theta_23` | `0.5437841154157028` |
| `delta_m2_21_over_delta_m2_31` | `0.029189410277135206` |

These entries are not minimal-Standard-Model predictions. They are included as
effective neutrino-sector screens with explicit limitations.
