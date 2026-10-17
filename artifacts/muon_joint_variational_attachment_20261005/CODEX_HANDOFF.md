# BHSM current joint variation handoff

Read report.md, checkpoint.json and run_2/coupled_variation.json.
The prescribed source is the photon connection b_A. p is its insertion image
on a computational probe, subsequently used as a diagnostic parent load.
Do not demand a separate physical Theta_p or Dom(D) membership of the load.
Keep the independent wall response psi4 unknown in the joint variation.

New objects: known principal Green columns/time jet and known bulk Euler
contractions on cached node3 directions. These are not native R4, a strong
P conormal, a new stationary response, or a physical magnetic anomaly.
run_1 preserves a new failed array-layout attempt; run_2 is accepted.
Three new targeted checks passed; prior seven and production actions were
not rerun. The accepted parent-bulk solution and frozen locals are unchanged.

One next operand: the current first-order joint interface variation c45,
or the equivalent owned joint variation graph/output equation, restricted
to the reached trace/source directions. Differentiate that SAME equation
under the photon source. The displayed action equations do not supply it;
this is not an exhaustive absence theorem for all retained sources.

This focused ZIP requires the existing PR465 repository/input artifacts.
Reproduce into a fresh output directory:

    C:\Python314\python.exe replay_muon_joint_variational_attachment.py --repository <PR465-checkout> --output <fresh-dir>

From that checkout, with PYTHONPATH=src if needed:

    C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_joint_variational_attachment.py

Use input/source hashes and exact executed snapshots. Canonical-LF source
hashes are recorded separately from executed bytes. No old production or
whole-tail reference calculation is required to resume this checkpoint.
