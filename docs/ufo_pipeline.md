# BHSM UFO Pipeline Phase One v0.1.0

Current pipeline stage: `PHASE_ONE_SCAFFOLD`.

```text
pipeline_stage = PHASE_ONE_SCAFFOLD
ufo_export_ready = false
event_generation_ready = false
```

BHSM v1.0.1 remains a status-reconciled internal boundary no-fit package. This
phase-one UFO pipeline scaffold defines the files, schemas, validators, and
readiness checks needed before a future explicit BHSM 4D Lagrangian can be
translated into collider software inputs.

## Future Chain

```text
BHSM boundary/operator artifacts
-> explicit 4D BHSM Lagrangian
-> field-content table
-> parameter card
-> interaction/vertex table
-> Feynman-rule export
-> UFO model directory
-> MadGraph-compatible process generation
-> LHE event output
-> optional showering/HepMC
-> detector simulation handoff
-> Athena/CMSSW integration only after experiment-specific review
```

## Phase-One Scope

This sprint adds:

- JSON schemas for a future Lagrangian, field table, parameter card, vertex
  table, and UFO export manifest;
- structural templates marked incomplete;
- validators that distinguish schema validity from physics readiness;
- a manifest exporter that reports blockers instead of inventing a UFO model;
- a MadGraph run-card template generator that does not call MadGraph;
- an LHE/HepMC readiness checker that exits cleanly when blockers remain.

## Current Blockers

- No complete collider-ready 4D physical Lagrangian is exported.
- No collider-ready Feynman rules are exported.
- No UFO/FeynRules model directory is exported.
- No real mass/width parameter card is exported.
- No validated vertex table is exported.
- No MadGraph process generation is enabled.
- No LHE or HepMC event files are generated.
- No Athena or CMSSW integration is claimed.

## Claim Boundary

The UFO pipeline scaffold is an interface roadmap and validation harness. It is
not a physical Lagrangian, not a Feynman-rule derivation, not a UFO model, and
not a collider event generator.

## Phase Two-A Analytical Export Layer

Phase Two-A adds source-derived analytical export ledgers for field content,
parameter-card entries, and vertex-source categories. These ledgers use existing
BHSM artifacts only. They remain blocked from UFO export until a complete 4D
collider-ready Lagrangian and Feynman-rule layer are supplied.

## Phase Three-A 4D Projection Gate

Phase Three-A adds a candidate effective Lagrangian term ledger plus field,
vertex, mass/width, and renormalization gate ledgers. This is still not a
production UFO model. The FeynRules translation gate remains false until the
boundary-to-4D projection theorem, gauge fixing, field normalization, vertex
normalization, complete vertex table, mass/width scheme, renormalization
scheme, and production parameter-card conventions are supplied.
