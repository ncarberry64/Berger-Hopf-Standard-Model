# Operation Muon: formed-envelope probe matching

This milestone preserves the verified November 20 offline incoming-hi package and adds a bounded force-space test. It concerns the present formed candidate's weak-field spin response. It does not reconstruct formation, fit the measured anomaly, or establish a physical muon magnetic moment.

The original 58-file package is byte-preserved under `evidence/`. Its `SHA256SUMS` covers the other 57 files. The source ZIP was 243875 bytes with SHA-256 `7bb4693da8ba459c918ef38197d64ad63acd660afeb3e3a923aa18dc344c7833`. The ZIP, transfer metadata, private identifiers and unrelated historical work are not included.

## Verified finite results

The saved 84-coordinate interior action condenses to 20 wall coordinates. Holding the four temporal gauge traces leaves 16 spatial-gauge/Higgs coordinates. These are a finite n=0, fixed-geometry candidate and saved spin/current pair, not admitted physical external legs.

| Quantity | Value | Scope |
|---|---:|---|
| Held central trace spin-gap derivative | 1.2603788642488865 | per unit archived trace |
| Held Higgs-aligned trace derivative | 1.0013228590975443 | same finite chart |
| Central-force slope at matched three-component field | 0.726417973549738 | coordinate units |
| Higgs-aligned-force slope at the same field | 0.4646622598116612 | coordinate units |
| Difference at the same local field | 0.2617557137380767 | diagnostic, not physical uncertainty |

The phase current is `J = Im(H† D H)/|H|²`; in the aligned nonzero-H frame the normalized axial companion is `Z·A = -sqrt(5) J3`. Its complete variation includes the Higgs-frame and local phase contacts. The intrinsic angular Higgs equation contains the derivative of the weighted `|H|² J3`. These two readouts differ because the latter also varies `|H|²`.

The new calculation uses the original central axial row of `KH20`, without adding a second Higgs surface force. Let `A` be the held-temporal action, `g` the spin-gap covector, `f=A u`, and `R` the chosen readout rows. Solve `t=A^-T g` and `F=R A^-1`, then decompose `t=F.T c+r`. For every vector in this **finite chart**,

```
gap = c.T (R u) + r.T f.
```

| Readouts R | Remaining force-covector norm | Relative to norm(t) |
|---|---:|---:|
| Three local field components | 0.3327001972297203 | 0.9991838846723088 |
| Field + phase-current companion | 1.60797913989628e-6 | 4.8291731019451245e-6 |
| Field + weighted Higgs sheet current | 0.2886931224877626 | 0.867019370614708 |
| Field + both currents | 2.3226498456511595e-8 | 6.97551223244045e-8 |

The last row has rank 5; its smallest singular value is about 0.2682 and `cond2(A)=433.4272`. The reconstructed identity error is 2.22e-16. For the saved equal-field difference, the last remaining contraction is 2.54877904315632e-8. Thus the excellent six-force fit does not justify dropping the full-space remainder. An arbitrary algebraic force is not thereby an admissible physical source.

## What the numbers do not establish

- The archived Higgs potential uses `lambda = 1.1663774240217167e-5 * 125.11**2 / sqrt(2)` and `nu2=4`; these calibrated/declared inputs are preserved, not reclassified as a native scalar prediction. No scalar Pauli correction is added here.
- All reported remainder norms use the archived coordinate norm. They are method diagnostics, not physical error bars. The original physical `2e-10` criterion is unchanged and has not been passed by a completed physical state.
- No same-background retarded exterior, normalized held incident photon, admitted muon pole/residue, or full native-relative magnetic response is supplied. Neither `a_mu` nor `g_mu` nor their total uncertainty is computed.
- The artificial half-line and flat-sphere controls in the evidence are retained as controls. They do not select the physical exterior.

## Exact next physical application

On the same formed background and full shared trace space, the held-incident matching equation is

```
(K + Lambda_R) w = Lambda_R w_inc + t_inc - P z - Q b.
```

`Lambda_R`, `w_inc` and its oriented action conormal `t_inc` must be evaluated together before reducing shared gauge/Higgs/complement directions. A zero external force is not a held applied field. The new finite reduction identifies which projections are needed: the field, both current readouts, and `r.T f_ext`. The inequality `|r.T f_ext| <= ||r|| ||P_kernel(F) f_ext||` is conditional; no physical bound for its second factor is presently available.

The focused source reconciliation confirms that the unified M5/M4 owner defines the fixed-trace functional and its mixed current derivatives, and AE4 selects the relative spectral owner and future/retarded orientation. They do not instantiate the incoming-hi common stratified domain, source incidence and conormal return. The older exterior-face source explicitly leaves the radial field derivative unevaluated and distinguishes it from temporal momentum. Local wall data and the chosen domain class do not supply this derivative. This is the remaining mathematical construction, not a request to choose an arbitrary source, impedance, occupation or formation history.

The smallest useful next solve is one action-owned receiving adjoint/current-incidence contraction on this formed background, with the independently normalized incident trace/conormal and common gauge constraints. A full exterior inverse is unnecessary. Until its operator/domain and source lift are instantiated, a guessed half-line or extra intrinsic Higgs traction would change the problem. Sources are pinned in `PROVENANCE.json` and the two focused owner/exterior audits under `evidence/`.

## Reproduction

Use an inspected Python installation. The integration replay used Python 3.14.3, NumPy 2.4.3 and SciPy 1.17.1, compared with the producer's Python 3.12, NumPy 2.3.5 and SciPy 1.17.0. Both integration replays passed all seven calculations and produced byte-identical `LOCAL_REPLAY_RECEIPT.json` files, SHA-256 `3e8de96fa138e320fb6c1b27fc7f19d7769ae80000c3917ae5b0b676364a36c1`. The optional action rebuild was reported by the producer and was not rerun here.

From this directory, replace the inspected package-root argument with the global site-packages under your interpreter's own prefix:

```
python -I -S replay_isolated.py --source evidence --destination /fresh/replay-directory --site-packages /inspected/python/Lib/site-packages
python -I -S verify_weighted_current.py --site-packages /inspected/python/Lib/site-packages --output /fresh/weighted-result.json
```

The runner verifies hashes before making a fresh copy, inspects NPZ arrays with pickle disabled, limits numerical threads to one, blocks network and subprocesses, and checks import origins. It never executes the producer's non-isolated child-launch wrapper. The new force test ran twice with identical result SHA-256 `2cdafbdb5cd7b83ea86b9116a0b3e75c63b616726a0900d7b13773ce77fe90dc`.

The original evidence includes a few inherited text-rendering defects; its bytes are preserved for provenance. The equations and scope above use corrected readable notation. All changes are confined to this artifact directory; old dirty research worktrees and frozen predictions are untouched.

All five repository publication audits pass. `REPOSITORY_AUDITS.json` records their scope: the checkout is sparse, so historical content hygiene covers materialized files; `REVIEW.json` separately covers every new payload file. The isolated audit launcher runs the original audits unchanged and routes their CLI help check through a bounded `-I -S` child. The evidence-only Git whitespace exception preserves seven inherited final blank lines rather than invalidating the archive hashes. No scientific tolerance is affected.
