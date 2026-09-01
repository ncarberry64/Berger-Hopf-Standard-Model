# BHSM v1.3L Formal-Kernel Level 2 Operator Note

BHSM v1.3L corrects the Level 2 `H_T` scaffold to protect the formal
sector-labeled kernel rather than the legacy coordinate-first block.

The v1.3K audit showed that the legacy Level 2 scaffold protected
coordinates `(0,1,2)`, all in the lepton sector. The formal BHSM protected
kernel is instead the sector-labeled triplet

| sector | protected coordinate at `k_max=4` |
| --- | --- |
| lepton | `0` |
| up | `18` |
| down | `36` |

The corrected variant is labeled
`DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`. It zeros rows and columns for the formal
sector-labeled block `(0,18,36)` and leaves the old lepton-only coordinates
`(1,2)` in the complement.

## Corrected Gap Audit

| quantity | value |
| --- | --- |
| status | `FORMAL_KERNEL_GAP_RESTORED` |
| protected coordinates | `(0,18,36)` |
| protected sectors | `lepton, up, down` |
| first complement eigenvalue | `6.8171156827281205` |
| required Dirac lower bound | `0.8038064161349437` |
| `H_T` gap | `19592.076941940737` |
| margin vs `mu_H` | `6.81711568272658` |
| passes `mu_H` | `True` |

The corrected formal-kernel sector-coupling block vanishes on the formal
protected states. The finite-basis projector is rank three, idempotent, and
orthogonal to its complement.

## Interpretation

The v1.3L result repairs the finite Level 2 kernel bookkeeping exposed by
v1.3K. The old coordinate-first protected block should not be used for future
Level 2 `H_T` gap claims. The corrected formal-kernel variant restores the
finite-basis gap under the sector-labeled projector.

## Limitations

- This is still a finite-basis Level 2 scaffold.
- The full twisted Dirac / `H_T` theorem is not proven.
- The formal-kernel projection is not yet derived uniquely from the full
  Berger-Hopf internal action.
- Structured, uniform, and basis-convergence audits should be rerun under
  `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`.
- Frozen BHSM v1.0/v1.1 predictions are unchanged.
