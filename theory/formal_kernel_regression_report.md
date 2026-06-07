# BHSM v1.3M Formal-Kernel H_T Regression Audit

Theorem complete: `False`
Corrected gap stable: `True`

BHSM v1.3M reruns the H_T gap and bound audits using the corrected formal sector-labeled kernel. It supersedes coordinate-first Level 2 conclusions where those depended on the old protected block.

## Old vs Corrected Lower-Bound Table

| Variant | Coordinates | Sectors | Direct lower | Min-max lower | Gershgorin lower | H_T gap | Margin | Passes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST` | `(0, 1, 2)` | `('lepton', 'lepton', 'lepton')` | `1.4630400252994733` | `1.4630400252994733` | `1.4366234871740744` | `19586.72266333732` | `1.4628370793107024` | `True` |
| `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL` | `(0, 18, 36)` | `('lepton', 'up', 'down')` | `6.8171156827281205` | `6.8171156827281205` | `6.721838618515489` | `19592.076941940737` | `6.81711568272658` | `True` |

## Sector-Coupling Regression Table

| Variant | Coordinates | Spectral norm | Frobenius norm | Row-sum norm | Weyl lower | a_K | Structured lower | Classification | Finite pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST` | `(0, 1, 2)` | `0.4720872031830534` | `1.5673539133570085` | `0.47862045138889886` | `0.9920127968169465` | `0.3224419118796895` | `1.4412292741558648` | `NORM_BOUND_SUFFICIENT` | `True` |
| `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL` | `(0, 18, 36)` | `0.47208720318305375` | `1.582154927031561` | `0.47862045138889886` | `6.361440051082765` | `0.015221771257357651` | `6.729508865520464` | `RELATIVE_BOUND_CANDIDATE` | `True` |

## Revised Conclusions

- Coordinate-first protected block `(0,1,2)` is superseded for formal-kernel H_T audits.
- Corrected formal-kernel first complement eigenvalue is larger than the legacy coordinate-first value.
- Corrected sector-coupling norms are recomputed on the formal complement and are much smaller in the baseline row.
- Theorem status remains incomplete because the full action, index theorem, and infinite-basis split remain open.

## Limitations

- All rows are finite-basis Level 2 scaffold rows.
- The full H_T theorem remains open.
- Coordinate-first conclusions are superseded only where they depended on the old protected block.

## v1.3N Action-Origin / Semi-Analytic Update

v1.3N constrains the formal-kernel projector from the BHSM sector,
boundary-functional, parent-action, and basis-ordering scaffolds.

| Quantity | Value |
| --- | --- |
| projector derivation status | `FORMAL_KERNEL_BASIS_DERIVED` |
| parent-action status | `REDUCED_FROM_PARENT_ACTION` |
| formal coordinates | `(0,18,36)` |
| semi-analytic bound status | `SEMI_ANALYTIC_BOUND_SCAFFOLD_PASSES` |
| diagonal complement lower bound | `6.833527254265818` |
| structured relative lower bound | `6.729508865520464` |

The corrected formal kernel remains a scaffolded boundary/basis-derived object,
not a completed full-action projector theorem.
