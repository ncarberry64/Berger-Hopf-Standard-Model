# Optional live PDG adapter

The adapter checks for optional PDG support and otherwise returns curated
fallback references. Cache files live under `.cache/bhsm_pdg/` and are not
committed by default.

Live PDG values are comparison references only and are never BHSM derivation inputs.

Electron-neutrino fallback data retain upper-limit semantics.

Reference values, including PDG values, are comparison inputs only and are never BHSM derivation inputs. Artifact-backed commands do not invoke the live PDG adapter.
