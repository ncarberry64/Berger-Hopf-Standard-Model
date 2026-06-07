# BHSM v1.3L Corrected Formal-Kernel H_T Gap Report

Theorem complete: `False`
Status: `FORMAL_KERNEL_GAP_RESTORED`

## Old vs New Protected Coordinates

| Variant | Coordinates |
| --- | --- |
| `DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST` | `(0, 1, 2)` |
| `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL` | `(0, 18, 36)` |

## Corrected Formal-Kernel Gap

| Quantity | Value |
| --- | --- |
| Protected sectors | `('lepton', 'up', 'down')` |
| Formal kernel protected | `True` |
| Sector coupling vanishes on formal kernel | `True` |
| First complement eigenvalue | `6.8171156827281205` |
| Required Dirac lower bound | `0.8038064161349437` |
| H_T gap | `19592.076941940737` |
| Margin vs mu_H | `6.81711568272658` |
| Passes mu_H | `True` |

## Sector-Coupling Norms on Formal Complement

| Norm | Value |
| --- | --- |
| Spectral | `0.02105708357088191` |
| Frobenius | `0.10529905521507689` |
| Row-sum | `0.021249999999999998` |

## Legacy vs Formal Gap Table

| Variant | Coordinates | First complement | H_T gap | Margin | Passes |
| --- | --- | --- | --- | --- | --- |
| `DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST` | `(0, 1, 2)` | `1.4630400252994733` | `19586.72266333732` | `1.4628370793107024` | `True` |
| `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL` | `(0, 18, 36)` | `6.8171156827281205` | `19592.076941940737` | `6.81711568272658` | `True` |

## Formal-Kernel Robustness Scan

| k_max | a | Coordinates | First complement | Margin | Passes | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `4` | `1.157054135733433` | `(0, 18, 36)` | `7.2322929398408276` | `7.232292939839681` | `True` | `FORMAL_KERNEL_GAP_RESTORED` |
| `4` | `1.0` | `(0, 18, 36)` | `6.8171156827281205` | `6.81711568272658` | `True` | `FORMAL_KERNEL_GAP_RESTORED` |
| `4` | `0.573` | `(0, 18, 36)` | `4.833981204821929` | `4.833981204821612` | `True` | `FORMAL_KERNEL_GAP_RESTORED` |
| `6` | `1.157054135733433` | `(0, 32, 64)` | `7.232292939840859` | `7.232292939839681` | `True` | `FORMAL_KERNEL_GAP_RESTORED` |
| `6` | `1.0` | `(0, 32, 64)` | `6.817115682727939` | `6.81711568272658` | `True` | `FORMAL_KERNEL_GAP_RESTORED` |
| `6` | `0.573` | `(0, 32, 64)` | `4.833981204821945` | `4.833981204821612` | `True` | `FORMAL_KERNEL_GAP_RESTORED` |
| `8` | `1.157054135733433` | `(0, 50, 100)` | `7.232292939840811` | `7.232292939839681` | `True` | `FORMAL_KERNEL_GAP_RESTORED` |
| `8` | `1.0` | `(0, 50, 100)` | `6.817115682728141` | `6.81711568272658` | `True` | `FORMAL_KERNEL_GAP_RESTORED` |
| `8` | `0.573` | `(0, 50, 100)` | `4.833981204822106` | `4.833981204821612` | `True` | `FORMAL_KERNEL_GAP_RESTORED` |

## Limitations

- The corrected formal-kernel operator is a finite-basis scaffold variant.
- It does not change frozen BHSM v1.0/v1.1 predictions.
- It does not prove the full H_T no-extra-light-state theorem.
- This is a corrected finite-basis Level 2 scaffold.
- Structured, uniform, and basis-convergence audits must be rerun under this formal-kernel variant before stronger H_T claims.
- The full H_T theorem remains open.

## v1.3M Regression and Convergence Update

v1.3M performs those reruns under `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`.

| Quantity | Corrected formal-kernel value |
| --- | --- |
| direct finite-spectrum lower bound | `6.8171156827281205` |
| min-max complement lower bound | `6.8171156827281205` |
| Gershgorin lower bound | `6.721838618515489` |
| sector-coupling structured lower bound | `6.729508865520464` |
| convergence classification | `FORMAL_KERNEL_CONVERGENCE_SUPPORTED` |
| all convergence rows pass | `True` |

Coordinate-first Level 2 conclusions are superseded where they depended on
the old protected block.

## v1.3N Action-Origin / Semi-Analytic Bound Update

v1.3N derives the finite coordinates `(0,18,36)` from:

- sector-labeled protected heavy modes;
- protected chirality `chi=-1`;
- v1.2 sector boundary functional and parent-action reduction;
- Level 2 sector-major basis ordering.

Status: `FORMAL_KERNEL_BASIS_DERIVED`, not
`FORMAL_KERNEL_ACTION_DERIVED`.

The semi-analytic complement-bound scaffold clears the required Dirac lower
bound:

| Bound | Value |
| --- | --- |
| required Dirac lower bound | `0.8038064161349437` |
| diagonal complement lower bound | `6.833527254265818` |
| Gershgorin lower bound | `6.721838618515489` |
| structured relative lower bound | `6.729508865520464` |
| exact finite lower bound | `6.8171156827281205` |
