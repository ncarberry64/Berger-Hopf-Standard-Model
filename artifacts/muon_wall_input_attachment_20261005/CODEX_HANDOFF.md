# Focused node3 wall-input handoff

Read report.md and checkpoint.json. The parent response and frozen locals are unchanged.
Newly evaluated objects are in run_1 and principal_run_1. They are intrinsic
kinetic-reference actions on actual normalized radial inputs, NOT Pi4 D_strat iota.

The one next operand is Theta_p^(3)=Pi4 iota_p^(3), with its action-owned
first-order joint trace/normal-output rule on the12 supplied source columns.
Known B_rad p is nonzero despite zero geometric material trace. A bounded
B graph is not a dense domain in the independent canonical H5+H4 direct sum.
Do not silently choose that graph, a new boundary law, or a new coefficient.
The report corrects the earlier checkpoint's overdefinite assembly label.

No old production calculations or tests were rerun. No new stationary solve,
native heat action, physical soft-transfer evaluation, a_mu or g_mu is claimed.
The six original new checks and separately added seventh check passed.

This ZIP is a focused handoff, not a self-contained physics runtime. It uses
the existing PR465 repository and unchanged input artifacts. Executed source
snapshots retain exact bytes; committed source may use canonical LF endings.
input_hashes.json and source_hashes.json distinguish these identities.

To reproduce into NEW directories (no overwrite):

    C:\Python314\python.exe replay_muon_wall_input_attachment.py --repository <PR465-checkout> --output <fresh-dir>
    C:\Python314\python.exe contract_muon_wall_input_time_jet.py --source <fresh-dir> --output <another-fresh-dir>

Targeted checks from that checkout:

    C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_wall_input_attachment.py

Set PYTHONPATH=src if required by the checkout. These checks read saved
artifacts and do not run old production producers. Last-bit BLAS differences
are assessed on matrix scale, not by a byte-reproduction campaign.
