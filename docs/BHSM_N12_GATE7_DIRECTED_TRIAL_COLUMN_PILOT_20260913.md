# Directed trial-column integration pilot — 2026-09-13

The paired center-split calculation reduces the maximum entry radius in the
previously worst tested local column by about 63.5%. This is one column of one
fixed-frame local operator. It does not establish full-path contraction or
physical predictions; Gate7 and FULL_BHSM_COMPLETE remain false.

## Measured numerical result

Interval 13, frozen trial column 14 (zero-based), Arb512. The original paired
local matrices had their maximum-radius entries at row 73, column 14.
All numbers below are enclosure radii, not physical measurements.

| Local column | Paired baseline, restored | Direct interval direction | Center-split direction |
| --- | ---: | ---: | ---: |
| DL | 197.08040928840637 | 161.19533705711365 | 71.96129047870636 |
| DR | 192.63046193122864 | 159.850839138031 | 70.26982593536377 |

Restoring serialized Arb balls can add a small outward rounding increment;
comparisons use the same restored baseline. The center-split result tightens
61 of 74 DL coordinates and 57 of 74 DR coordinates against that baseline.
It is not a statement about all 74 trial columns.

The endpoint directional actions improve in every coordinate: maximum radii
2.6966227144002914 to 0.6004478149116039 (left) and 2.4440038353204727 to
0.5089433398097754 (right). Both independently reproduce.

The first midpoint interval-direction attempt is retained as an adverse result.
Its maximum radii, 51.44666922092438 and 44.55125051736832, are wider than the
existing ambient-matrix products, 16.33421716094017 and 14.166688054800034.
That attempt tightens no midpoint coordinate and selects the older valid bounds.

The center-split midpoint attempt instead reaches 15.330442517995834 and
13.162704527378082 and tightens all 99 coordinates. The large improvement in
local columns is calculated from their full componentwise enclosures, not
inferred from the ratio of these maximum midpoint radii.

## Retained equations and evidence

The new direction evaluator runs the original complete physical variation graph
on the actual frozen trial column, including D3/D4 contractions, both coupled
variations, signed centered residuals, componentwise inverse bounds, and coupled
normalization. The configuration and descriptor input derivatives use the supplied
weighted direction rather than an ambient basis index.

For endpoint action A, the actual HS chain direction is W = E/2 +/- h A/8.
The split variant writes W = w0 + delta, evaluates DF_M w0 directly, and encloses
DF_M delta using the already paired full derivative on the identical old actual
midpoint domain. The tail is included explicitly. Stored center_* variation
proofs apply to w0; the summed action covers W.

The original three primal pairs, lambda, physical domains, fixed frames, time
step, and frozen L/R remain unchanged. Each primal pair is checked against the
exact source hash used by its compared full derivative. This does not certify
a physical quotient or derivatives of state-dependent frames.

Original paired evidence is under
`tmp/bhsm_directed_trial13_pair_20260913/{endpoint_left,endpoint_right,midpoint_left,midpoint_right,local}`.
The split variant reuses the endpoint pairs and independently reproduces
`tmp/bhsm_split_directed_trial13_pair_20260913/{midpoint_left,midpoint_right,local}`.
Every new stage has distinct fresh-process first/repeat output and a byte-identical
receipt. All data, record, and receipt hashes are recorded in
[the companion report](../artifacts/flagship_integration/BHSM_N12_GATE7_DIRECTED_TRIAL_COLUMN_PILOT_20260913.json).

## Reproduction and validation

Use `scripts/diagnose_n12_gate7_directed_trial_hs_column.py` with interval 13,
column 14, explicit stage/side, the matching `--primal-pair`, `--evidence-root`,
and a fresh `--out` directory. Run each endpoint stage in two fresh processes;
compare exact record and data bytes before issuing its receipt. Then do the same
for midpoint stages and `--stage assemble`. The split producer is
`scripts/diagnose_n12_gate7_split_directed_trial_hs_column.py`; it consumes those
paired endpoints and separately reproduces midpoint and assembly stages.
The same immutable baseline prerequisites as the paired full derivatives are
required; this is not a standalone prediction script.

Six directed-HS algebra tests and three direction-split tests pass. They cover
noncommuting matrices, both HS signs, interval uncertainty, incompatible inputs,
and preservation of a signed center action with an exact zero tail. Both
numerical variants additionally verify the complete point derivative is contained
and preserve failed/wider alternatives.

## Next critical step

Retain this improvement, but defer a full 74-column campaign until the remaining
local uncertainty is addressed. The split midpoint center-action maximum radii
are about 1.035 and 1.038; tail-action maxima are about 14.725 and 12.555.
These maxima need not occur in the same rows and do not by themselves attribute
the worst local defect. The next inexpensive comparison should use the already
paired split operands to apply the fixed preconditioner before the uncertain tail
product, and compare equivalent associations at the actual local column.

The six-worker point-curvature campaign resumes after each bounded pilot. No
Museum engine or manuscript completion status changes for this isolated result.
No measured mass or mixing data, fitting, or new physical assumptions enter.
