# BHSM claim/input/completion consistency v6.30.8

## Result

The v6.30.7 scalar calculation is retained, but its completion consequence
is corrected. The invariant

\[
\lambda_5=\frac{\kappa_1 G_5}{Z_5^2}
\]

is an unfitted `INDEPENDENT_THEORY_INPUT` of the parameterized reduced
scalar family. BHSM does not predict its numerical value or sign. The
canonical quartic and local-stability statement therefore remain functions
of \(\lambda_5\), not parameter-free numerical predictions.

The exact verdict is
`BHSM_SCALAR_QUARTIC_PARAMETERIZED_NOT_PREDICTED`. The associated
classification is
`BHSM_LAMBDA5_RECLASSIFIED_AS_PARAMETER_FREE_EXTENSION_BLOCKER`.

## Frozen-output dependency audit

Every scalar leaf in both branches of
`theory/bhsm_v1_frozen_prediction_set.json` has an explicit computation
path and direct/transitive input ledger in
`artifacts/BHSM_frozen_prediction_dependency_graph_v6_30_8.json`.
Neither \(\lambda_5\), \(G_5\), \(Z_5\), nor \(\kappa_1\) occurs in those
paths, and no frozen output can vary with \(\lambda_5\).

This is not a promotion of the frozen screens to fully action-derived
predictions. The audit records alpha-anchored geometry, supplied mode
selection, CKM screen rules, gauge normalization, and the scale screen as
open provenance obligations. The `Zvirt=1/2` dressed branch remains
`CANDIDATE_NOT_OFFICIAL`. Published measurements remain comparison data and
do not become parent-action inputs.

## Parameterized versus parameter-free

BHSM 1.0 may contain an independent dimensionless theory input only when it
is explicitly typed, unfitted, and never advertised as a prediction. A
parameter-free scalar extension would additionally require an internal
selection or derivation of \(\lambda_5\). That extension is not the present
BHSM 1.0 release contract.

No value, sign, unit convention, scale, fit, or empirical inverse is chosen
in this campaign. The conditional local-stability inequality is retained;
unconditional and global stability remain unsupported.

## Completion and scale consequences

`RB-02` is removed from the BHSM 1.0 release-blocking set and retained as a
parameter-free-extension blocker. Fifteen scientific/release blockers
remain open. BHSM Core Complete, Physical Complete, and Tier C are not
satisfied.

The scale phase remains closed independently of \(\lambda_5\). A unified
canonically normalized parent action, boundary measure/transport,
action-level scalar attachment, physical scale bridge, and common
observable/scheme map remain unresolved. The exact scale verdict is
`BHSM_SCALE_PHASE_STILL_BLOCKED_INDEPENDENTLY_OF_LAMBDA5`.

The rebuilt dependency DAG selects
`RB-01_UNIFIED_PARENT_ACTION_PROVENANCE` as the next highest-upstream
scientific target. No v6.31 scientific work is performed here.

## Integrity

The frozen Markdown and JSON hashes are unchanged. The materializer is
deterministic UTF-8/LF, comparison data are excluded from action inputs, and
all scientific-integrity guards remain false.
