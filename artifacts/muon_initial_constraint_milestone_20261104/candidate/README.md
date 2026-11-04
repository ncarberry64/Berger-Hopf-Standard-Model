# Muon continuation: initial constraints and the event-domain boundary

This is a selected preservation milestone after commit
`eef2b40e0d49c89f57132dadc1c0d4df89819378`. It records concrete local
calculations and the exact limit of their physical interpretation. It is
not a muon magnetic-moment prediction, a completed event map or a demonstrated
reconnection event.

The selected payload belongs on branch
`codex/muon-reconnection-magnetic-vertex-20261102` in
`ncarberry64/Berger-Hopf-Standard-Model`. It does not include the surrounding
working tree's modified modules, tests, archives or unrelated artifacts.

## What is preserved

1. The initial multiplier and temporal-gauge constraint application on two
   saved nonzero-normal trial germs, with the matching stationary native18
   derivatives kept separate from the complete native/relative force.
2. The exact canonical intrinsic pair-current coefficients, including the
   charge-conjugate e_R sign and the distinction between the real-base pair
   density and the independent Green/source dual.
3. The local Dirac principal/current identities on these same regular germs.
   They establish a pointwise prerequisite for retarded evolution, not
   hyperbolicity of the complete coupled action through formation.
4. A source-hashed ledger of the intervening bordered-source, edge, joint
   trace, carrier, force and domain work. That ledger preserves provenance;
   it does not claim those entire historical computations are replayed here.

The first lapse-row native18 pieces are **0.929514564715928** and
**0.591020030322905**. They are components, not total physical residuals.
The complete initial constraint and full charged event Green balance remain
unevaluated. `DERIVATION.md` identifies the missing application precisely.

## Reproduce the selected applications

From this directory, run a supported Python 3 interpreter in isolation:

```text
python -I -S verify_milestone.py --out replay_1
python -I -S verify_milestone.py --out replay_2
```

Use fresh output directories. The verifier uses only the Python standard
library, rejects non-isolated/site-enabled invocation, checks every input
hash and permits no imported custom package. The pure coefficient functions
are extracted from reviewed owned sources; their module top level is not
executed. Both results must match the bundled `result.json` byte for byte.
`REPLAY_RECEIPT.json` records the actual preservation replay.

`OPERANDS.json` contains sufficient exact numeric operands for these local
applications. It does not require the unselected local files or private
archives. It includes saved native gradients as inputs. Replaying this
package **does not recompute their heat integrals**, certify their physical
uncertainty, generate physical columns, or solve a carrier history.

## Files and dependencies

- `DERIVATION.md`, `SCOPE.json`: result, assumptions and open physical rows.
- `PROVENANCE.json`, `SOURCE_EXCERPTS.txt`: exact original paths/hashes,
  extraction rules and scoped owned-action excerpts.
- `POST_CHECKPOINT_LEDGER.json`: selected intervening local reports and
  receipt hashes, including corrected/superseded-result receipts where saved.
- `OPERANDS.json`, `OWNED_COEFFICIENTS.py`, `verify_milestone.py`:
  self-contained numerical replay dependencies.
- `result.json`, `REPLAY_RECEIPT.json`: deterministic replay evidence.
- `REVIEW.json`, `INVENTORY.json`: payload review and content manifest.
- `NEXT_CALCULATION.md`: a distinct bounded local-principal test, proposed
  but not executed by this preservation operation.

The method tolerance remains `2e-11`; physical admission remains `2e-10`.
The last admitted temporal-only stage is `t=2^-9`. The later conditional wall
diagnostic remains a separate object. Neither supplies a full physical
Cauchy state, calibrated c_F, physical a_mu/g_mu or total uncertainty.

There is no new state, attachment or occupation selection. The fixed
stationary-past preparation and the action-selected envelope/new child-boundary
interpretation are retained. Magnetic reconnection remains a mechanism to
test, not an established consequence of the calculations preserved here.
