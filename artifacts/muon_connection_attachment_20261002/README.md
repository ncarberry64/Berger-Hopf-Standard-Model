# Current BHSM connection-attachment handoff

Start HEAD bc27b082542ccb3c4c64fadc7b894430d71292a6; scientific reference 524ed90689bd5923c249bba2e699abf627e703cd.

Read theory/muon_current_connection_attachment_20261002.md, checkpoint.json and missing_operand.json. The zero mechanical-sector amplitude is explicitly declared a fluctuation. The current action-to-carrier background substitution is still absent from the inspected equation chain. New exact Higgs compatibility identities and an eight-source conditional mixed Higgs row are evaluated; no physical anomaly or exterior response is produced.

replay_reference contains the final executed result, receipt, AST equation evidence and conditional_higgs_source_actions.npz. run_1 and run_2 preserve earlier passes from this continuation. The older mechanical packet and all previous shared caches are unchanged.

From the retained PR worktree, run into a fresh directory:

```powershell
python C:\Users\carbe\Downloads\BHSM_muon_connection_attachment_524ed906_20261002\replay.py --output C:\Users\carbe\Downloads\BHSM_muon_connection_attachment_replay_new
python -m pytest --noconftest -q tests/test_muon_connection_attachment.py
```

The standalone replay uses input_refs.json and the existing repository's source and saved inputs, not a duplicate generic engine. It verifies 23 source/data hashes before deriving the new result. Native physical directions, finite-E1 contractions and exterior returns remain zero executions, not zero contributions.

The one next operand is the action-owned horizontal internal connection value A_hor^(0), or its sufficient contracted current M5/M4 attachment equation, recorded in missing_operand.json. No new vacuum, Higgs profile, interpolating coefficient, endpoint or history is authorized by this packet.
