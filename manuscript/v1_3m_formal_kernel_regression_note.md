# BHSM v1.3M Formal-Kernel Regression Note

BHSM v1.3M reruns the finite-basis `H_T` gap and bound audits using the
corrected formal sector-labeled kernel operator
`DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`.

This supersedes coordinate-first Level 2 conclusions where those conclusions
depended on the old protected block `(0,1,2)`.

## Old vs Corrected Baseline

| quantity | coordinate-first Level 2 | corrected formal-kernel Level 2 |
| --- | --- | --- |
| protected coordinates | `(0,1,2)` | `(0,18,36)` |
| protected sectors | lepton, lepton, lepton | lepton, up, down |
| first complement eigenvalue | `1.4630400252994733` | `6.8171156827281205` |
| `H_T` gap | `19586.72266333732` | `19592.076941940737` |
| margin vs `mu_H` | `1.4628370793107024` | `6.81711568272658` |
| sector-coupling spectral norm | `0.4720872031830534` | `0.47208720318305375` |
| structured lower bound | `1.4412292741558648` | `6.729508865520464` |

The corrected formal-kernel baseline clears the required Dirac lower bound
`0.8038064161349437` and restores the finite-basis `H_T` gap under the formal
projector.

## Corrected Convergence Result

The corrected convergence scan covers
`k_max = 4,6,8,10,12,16,20,24,32` and the three anisotropy controls:

- alpha-anchored canonical `a=alpha^{-1}/(12*pi^2)`;
- round control `a=1.0`;
- legacy sensitivity `a=0.573`.

All corrected baseline rows pass. The worst direct `H_T` margin in the scan is
`4.833981204821612`, and the worst Gershgorin margin against the required
Dirac lower bound is `3.949470723972136`.

## Interpretation

The v1.3M regression confirms that the old coordinate-first Level 2 protected
block should not be used for future formal-kernel `H_T` claims. The corrected
formal-kernel scaffold has a stronger finite-basis complement gap in the
baseline and remains stable across the requested convergence scan.

## Limitations

- This does not prove the full `H_T` theorem.
- This remains a finite-basis `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL` audit.
- The full twisted Dirac spectrum, index theorem, and infinite-basis
  complement split remain open.
- Frozen BHSM v1.0/v1.1 predictions are unchanged.
