# BHSM MadGraph Event Generation Path v0.1.0

BHSM v1.0.1 does not currently provide a MadGraph-ready model.

The future MadGraph path is:

```text
validated BHSM 4D Lagrangian
-> validated field-content table
-> validated parameter card
-> validated interaction/vertex table
-> Feynman-rule export
-> UFO model directory
-> MadGraph process definition
-> run card and parameter card
-> LHE event generation
```

## Current Tooling

The repository includes:

- `tools/export_bhsm_ufo_manifest.py`
- `tools/generate_madgraph_run_card_template.py`
- `tools/check_lhe_hepmc_generation_readiness.py`

These tools do not call MadGraph and do not generate events. The run-card
generator creates a structural placeholder warning only.

## Current Blocker

MadGraph generation is blocked by the absence of a real UFO model directory and
the absence of a collider-ready Lagrangian, Feynman rules, parameter card, and
vertex table.

Phase Two-A adds a gated candidate builder and readiness checker. They report
these blockers instead of invoking MadGraph.
