# Preconditioned split-tail comparison — 2026-09-13

The same paired local column improves by only another 0.24–0.32% when the fixed
preconditioner and shared endpoint uncertainty are combined before interval
multiplication. Both independent runs agree byte for byte. Retain the result,
but stop pursuing reordering alone as the path to full uniform contraction.

| Column, interval 13 / trial 14 | Restored paired split baseline | Preconditioned tail | Combined endpoint tail |
| --- | ---: | ---: | ---: |
| DL | 71.96129059791565 | 71.78827059268951 | 71.78772759437561 |
| DR | 70.26982605457306 | 70.12230157852173 | 70.04334008693695 |

These are maximum entry radii of one 74-row column. Both associations improve
all 74 coordinates. The combined endpoint association is selected in every
coordinate. Restoring Arb balls adds small outward rounding increments; every
comparison uses the restored paired baseline. These are numerical enclosures,
not experimental measurements or physical interaction strengths.

With P = R_frozen^-1 T_frozen and Q = P DF_M, the first association multiplies
Q by the uncertain chain-direction tail. The second combines its shared
endpoint coefficient as h P/6 +/- h^2 Q/12. It explicitly includes the residual
between the exact stored direction center and E/2 +/- h a0/8. The formulas use
only derivative linearity and the original HS chain rule. No action derivative
is recomputed, no uncertainty tail is dropped, and no domain, primal pair,
lambda, frame, step, or preconditioner is changed.

Three focused tests pass, including both signs with interval corner actions
and a deliberately shifted exact center. The numerical producer verifies the
paired center-split operands, their original full derivative dependencies, and
all frozen geometry before comparing equivalent enclosures. Distinct fresh
processes produce identical record and data bytes. Evidence is retained under
`tmp/bhsm_preconditioned_split_trial13_pair_20260913/value`; hashes are in the
[companion report](../artifacts/flagship_integration/BHSM_N12_GATE7_PRECONDITIONED_SPLIT_TRIAL_COLUMN_20260913.json).

Reproduce with `scripts/diagnose_n12_gate7_preconditioned_split_trial_column.py`
using `--interval 13 --column 14`, the paired center-split evidence root, and
separate fresh output directories. Compare exact record/data bytes before
issuing a receipt. The immutable physical baseline prerequisites remain required.

Next, distinguish actual variation of the physical derivative from excess
interval width before paying for more uniform-bound refinements or all 74
columns. Verified point samples inside the existing tube can establish observed
variation and a lower bound on the necessary enclosure width; they cannot supply
a uniform upper bound or prove full local/global contraction.

This remains a single-column, fixed-frame result. Physical quotient and frame
derivatives, complete causal contraction, Gate7, and full BHSM completion remain
open. No measured data, parameter fitting, Museum completion update, or manuscript
completion claim is introduced.
