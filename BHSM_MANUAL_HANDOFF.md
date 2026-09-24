# BHSM handoff — 2026-09-20

## Stopping state

All processes in the active reproduction tree were intentionally stopped at
the user's request. No background continuation is intended. Saved midpoint
checkpoints were parsed successfully: 99 JSON files, no empty/truncated file.
The stopped stage is `interval14_midpoint14_refined_chain_repeat`; its final
`record.json` does not yet exist. Do not mistake the intentional stop for a
mathematical failure.

Repository: `C:\Users\carbe\OneDrive\Documents\CODEX\Berger-Hopf-Standard-Model`.
Immutable evidence: sibling directory `BHSM-ae32-crossing-correction`.
Runtime: `C:\Python314\python.exe`, python-flint/Arb at 512 bits.
Work files: `tmp/gate7_vector_20260919/` under the repository.

## Mathematical status

Interval 13 is CLOSED/FROZEN. Combined gain 0.72221510; margin 0.27778490.
Do not recompute/reopen it, shrink the original domain, or add assumptions.

Current target: interval 14, right block, zero-based entry 73 <- 14,
`sup_D |e_a| < 0.000394150` after subtracting the frozen point anchor/first jet.
First-run uniform upper bound: approximately **1.8350773693620786e-5**.
Transverse full-history contribution, including the unbooked TT linear piece:
approximately **5.517875529290355e-12**, below the 10% allocation
**1.1302782276695312e-10**. Exact rationals are in
`interval14_entry_assembly_first.json`.

This is still a first-run entry result, not a completed independent entry
certificate. The ledger is unchanged. Gate 7 and the three full-history
physical inequalities remain OPEN/UNDECIDED.

## Reproduction completed

- Endpoint base reproduced exactly: `interval14_endpoint15_base_taylor_repeat_serial`.
- Midpoint base repaired/reproduced exactly: `interval14_midpoint14_exact_raw_repair_v2`.
- Endpoint directional proof reproduced: `interval14_endpoint15_direction_taylor_repeat`.
- Endpoint descriptor refinement reproduced: `interval14_endpoint_descriptor_refined_repeat`.
  Its numerical refinement is byte-identical; wrapper differences are limited
  to the explicitly checked refinement-file location.

The 14 formerly differing source IDs are response rows
28,30,33,36,38,41,44,46,49,52,54,57,59,61, each named `response_NN_source`.
Their exact first/repeat balls and rational endpoints are listed in
`interval14_midpoint14_exact_14_term_inventory.json`.
Two fresh serial raw-operand runs reproduced all 14 exactly, with identical
complete input hashes: `interval14_midpoint14_raw_serial_first` and `_repeat`.

The issue was cache serialization and overlapping original producer/prefetch
writes, not a physical-domain failure. See
`docs/research_packets/2026-09-20/GATE_7_MIDPOINT14_EXACT_SOURCE_REPAIR.md`.
The repair receipt records the reconstructed cache-read/in-memory schedule.
Schedule recovery used exact equality among rigorous equivalent evaluations;
the selected schedule was fixed before the second accumulation. No numerical
tolerance or canonical certificate coarsening was used. Exact ball restoration
has two passing focused tests.

## Manual continuation

Open PowerShell and run:

```powershell
Set-Location -LiteralPath 'C:\Users\carbe\OneDrive\Documents\CODEX\Berger-Hopf-Standard-Model'
& .\CONTINUE_BHSM_MANUALLY.ps1
```

If script execution policy blocks the local helper, use the direct command:

```powershell
Set-Location -LiteralPath 'C:\Users\carbe\OneDrive\Documents\CODEX\Berger-Hopf-Standard-Model'
& 'C:\Python314\python.exe' scripts/reproduce_n12_gate7_interval14_entry.py --evidence-root ../BHSM-ae32-crossing-correction --work tmp/gate7_vector_20260919 --workers 10 --midpoint-repair tmp/gate7_vector_20260919/interval14_midpoint14_exact_raw_repair_v2 *> tmp/gate7_vector_20260919/manual_resume.log
```

Run only one driver. The driver now skips completed producer executions and
still compares their saved results/source hashes. It resumes midpoint
checkpoints, then runs midpoint scalar refinement and final entry assembly.
Do not edit any proof producer or arithmetic source while this runs: source
hashes deliberately reject such changes. Keep the PowerShell window open.

To watch the newest manual log from a second PowerShell window:

```powershell
Set-Location -LiteralPath 'C:\Users\carbe\OneDrive\Documents\CODEX\Berger-Hopf-Standard-Model'
$bhsmLog = Get-ChildItem tmp/gate7_vector_20260919/manual_resume*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content -LiteralPath $bhsmLog.FullName -Tail 12 -Wait
```

The resume helper and completed-stage skip were syntax-checked but have not
been run after this stop. In particular, restarting a partial producer can
expose another Arb cache-read rounding difference. Any comparison failure
must remain visible: preserve its exact operands, bounds and log; use the
same targeted raw/canonical-ball analysis. Do not loosen equality, delete
evidence, or rerun an entire verification campaign automatically.

Success creates `interval14_entry_reproduction_first.json` and `_repeat.json`.
Confirm `independent_process_recomputation` and the explicit comparison list.
The driver deliberately leaves `transverse_ledger_debited` false. After the
complete entry and transport reproduce, the next mathematical step is the
single-entry budget update/certificate, then remaining TT paths and LL/LT
intervals 70–369. Full Gate-7 closure needs all three full-history inequalities
and remaining physical operator/domain obligations; do not infer it from this
one entry.

## Git and files to preserve

Branch: `codex/g7-vector-endpoint-final-closure`.
Last pushed commit: `684e5a79`; draft PR 442:
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/pull/442

The latest repair, resume change and this handoff are LOCAL/UNCOMMITTED:

- `scripts/diagnose_n12_gate7_midpoint_source_reproduction.py`
- `scripts/repair_n12_gate7_midpoint_source_reproduction.py`
- `scripts/reproduce_n12_gate7_interval14_entry.py` (modified)
- `src/bhsm/interface/exact_arb_ball_restore.py`
- `tests/test_exact_arb_ball_restore.py`
- `docs/research_packets/2026-09-20/GATE_7_MIDPOINT14_EXACT_SOURCE_REPAIR.md`
- `CONTINUE_BHSM_MANUALLY.ps1`, `BHSM_MANUAL_HANDOFF.md`

There are also 15 older dirty historical artifact files from an earlier test
campaign. Do NOT use `git add .` or restore them indiscriminately. They are
outside this repair. Temporary numerical evidence is generally ignored by
Git: preserve the entire work directory locally. Do not delete it as cleanup.
Required invariant/public-readiness audits must run before publishing these
new local changes; no publication/commit was attempted during this stop.

## Text to paste into basic chat

Continue from this handoff and request only specific logs/results needed for
the next step. You cannot inspect my filesystem directly. Interval 13 is
frozen. Interval-14 73<-14 first-run error bound is 1.8350773693620786e-5,
below 3.94150e-4; full independent reproduction is incomplete. Both base
proofs and endpoint directional/descriptor reproduction passed. Fourteen
midpoint source terms were serially reproduced exactly with identical full
input hashes and no tolerance. The process tree is stopped during midpoint
directional reproduction with 99 valid JSON checkpoints. I have a local
CONTINUE_BHSM_MANUALLY.ps1 helper. Help interpret its output conservatively;
do not claim a ledger debit or Gate-7 closure without the required artifacts.
