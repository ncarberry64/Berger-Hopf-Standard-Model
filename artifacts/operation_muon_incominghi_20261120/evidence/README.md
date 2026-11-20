# Operation Muon: incoming-hi held-probe integration checkpoint

**Objective:** match a physical weak probe to the formed charged spin response on one native background. The bundled data are finite conditional diagnostics, not a physical outgoing exterior, admitted muon pole, magnetic moment or uncertainty. No formation replay and no fit to measured g are needed for this handoff.

## Replay from clean extraction

Python 3.12, NumPy 2.3.5 and SciPy 1.17.0 were used. Run from the extracted root; use OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1. No online calls or repository needed for the replay.

1. Verify the shipped initial files: `sha256sum -c SHA256SUMS` (or `python verify_package.py --hashes` on Windows).
2. Run `python verify_package.py`. It checks initial hashes, replays seven curated calculations and checks scientific ordinates. It updates several result files in its own extracted directory; perform another hash check only on a fresh extraction. It does not launch Codex or use any network.
3. Optional original finite action reassembly: run `python verify_package.py --rebuild-action` **on another fresh extraction**. This checks M84, B84, K84 and KH20, plus the physically relevant condensed D20 against the frozen seeds. The saved spin-pair/current arrays remain inputs in both modes.

## What is actually here

- **Native baseline:** incoming hi raw268 history, same-clock H84, saved constant-angle near-charge spin pair and current (see independent_review seeds), precisely the K84/M84/B84, KH20, D20 and lift used in these replays. Optional action source dependencies included.
- **Held probe transfer:** `FORMED_N0_HELD_PROBE_WALL_TRANSFER.md`; both native ports couple to the candidate gap. With one proven rank-one exterior, delta_gap = tau j/(1+Lambda chi). j is an independently normalized incident affine force, not given here.
- **Equal local field:** `FORMED_N0_EQUAL_LOCAL_FIELD_TEST.md`; both trial force families reproduce the same full reduced magnetic vector, but coordinate gap slopes differ by .261755713738; proper slopes .655359189316 and .419208627793.
- **Minimal unknown:** `FORMED_N0_MINIMAL_EXTERIOR_ADJOINT.md`; in this finite held-temporal chart one scalar force projection suffices for this gap once the local field is specified. It survives interior Gauss and extra zero wall-temporal/scalar forcing tests. It is not a physical error bar.
- **Gauge-completed fourth row:** `FORMED_HIGGS_INVARIANT_COMPANION.md`. The normalized axial companion is -sqrt(5) J3, where J=Im(H† D H)/|H|². Receives the appropriate phase term; six-force residual about 8e-14 and full-16 relative residual about 1.35e-7. The latter is not established zero. `neutral_higgs_surface_current_identity` verifies the tangential Higgs torque/current attachment, not a radial Higgs boundary law.
- **Exterior controls:** `FROZEN_NATIVE_CENTRAL_HALFLINE.md` and `OUTGOING_SPHERE_AND_NATIVE_TRACTION.md`. The constant-coefficient central half-line is intentionally artificial. Its static return differs from the required target and can be altered with a remote angular tail while preserving the same local wall. Both the high-frequency native impedance and the flat-sphere solver control are diagnostics only.

## Suggested continuation, not a numerical result

Stay in the actual formed incoming-hi chart. Recover the action-selected retarded exterior and independently held incident trace plus action conormal projected onto the gap-visible direction (particularly the neutral Higgs current companion, if a regular nonzero-H receiving chart exists). Combine exterior and interior on their common gauge/scalar/complement trace **before** reducing shared directions. Do not add a separately condensed exterior as if the released modes were independent. Preserve outgoing/retarded orientation, time/field units, Higgs-frame contacts, and the difference between prescribed incident drive and held total wall trace. Document original boundary and adjoint residuals and any controlled error estimate. If only a finite direct gap is available, do not present it as on-shell F2(0); physical normalized legs, soft source and residue remain requirements.

## Earlier assets intentionally not duplicated

- Existing exact action/moving trace provenance and candidate branch: [pinned 4a650a61 repo](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/4a650a61a6e0e4cd3674650c399b435c106d66c3). Relevant interface owners and constraints are identified in the included APPLIED_FIELD and SAME_DOMAIN notes.
- [V64 native Higgs-frame photon and Schur insertion](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/1ef75378916644c34229da5c24148b85d9fba868/artifacts/muon_reconnection_magnetic_vertex_20261102/RECONNECTION_MAGNETIC_VERTEX.md); not a same-domain outer solution.
- Earlier complete 134×1474 current-extended wall maps, 574-coordinate open-wall histories, 47-segment inherited chronology, D5 formation/C1 prefix, weak daughter kernels and older matching candidates are not bundled. Their scope and locate-by-name links are in the related notes. Only retrieve an older artifact if the present projection demonstrably needs it and matches its action, background, trace/clock and continuation. The same-branch D5 forcing successors exist, but are not physical present-state exterior data.
- This small ZIP intentionally does not contain the larger historical workspace or imply all omitted operands were absent from it.
