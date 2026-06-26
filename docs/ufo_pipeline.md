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

## Phase Three-C Field Dictionary and Vertex Target Map

Phase Three-C imports `artifacts/BHSM_phase_three_c_analytical_working_packet_v0_5.json`
and exports an explicit candidate 4D field dictionary, gauge-field target
dictionary, candidate BHSM parameter card, boundary-source matrices, and
vertex-source target map. These exports identify collider targets with
provenance, but they do not complete vector/fermion normalization, full
gauge/Lorentz structures, mass-width schemes, or renormalization conventions.

## Phase Three-D Canonical Current Interface

Phase Three-D exports canonical field target conventions and chiral current
attachment maps for CKM/PMNS sectors. It preserves `Z_H = 1` as a BHSM profile
source and marks `Z_A,target = 1` and `Z_psi,target = 1` as standard target
conventions rather than BHSM dynamical predictions. Production FeynRules/UFO
readiness remains blocked by mass-width and renormalization schemes, complete
4D Lagrangian export, and validation gates.

## Phase Three-E Normalization And Scheme Status

Phase Three-E exports explicit vector/fermion normalization theorem-status
ledgers plus gauge-fixing/coupling, mass-width, and renormalization candidate
scheme ledgers. `Z_A,target = 1` and `Z_psi,target = 1` remain standard HEP
target conventions, not BHSM-derived dynamical field-strength predictions.

The candidate gauge couplings are scheme-conditional and not production UFO
couplings. No fake masses, fake widths, fake Feynman rules, fake LHE/HepMC
files, MadGraph readiness, Athena readiness, or CMSSW readiness are claimed.

## Phase Three-F Production Basis And Runtime Parameters

Phase Three-F defines a canonical production basis for future FeynRules/UFO
interfaces. In that basis `Z_A,prod = 1` and `Z_psi,prod = 1` are basis
definitions rather than BHSM dynamical wavefunction-renormalization
predictions. This clears the interface normalization gate only.

Phase Three-F also separates `BHSM_PURE_NOFIT` from
`BHSM_COLLIDER_INTERFACE`. Runtime empirical masses, widths, and cards may be
allowed only in collider-interface comparison mode and do not modify BHSM
constants, boundary coefficients, mixing matrices, or frozen predictions.

## Phase Three-G Vertex Table And Lagrangian Candidate

Phase Three-G exports a candidate production vertex table, symbolic 4D
Lagrangian assembly ledger, vertex readiness matrix, FeynRules blocker table,
and runtime dependency table. CKM/PMNS charged-current target structures are
identified using BHSM-derived mixing sources, but all production FeynRules/UFO
readiness gates remain closed.
