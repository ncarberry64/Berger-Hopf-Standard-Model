# BHSM Event Generation Interface v0.1.0

BHSM v1.0.1 does not currently provide a validated event generator.

BHSM v1.0.1 does not currently provide LHE/HepMC event samples.

BHSM v1.0.1 does not currently provide Athena or CMSSW integration.

## Required Future Chain

```text
BHSM collider-ready Lagrangian
-> Feynman rules
-> UFO/FeynRules or equivalent model export
-> MadGraph/Pythia/Herwig-compatible generation
-> LHE or HepMC event output
-> detector simulation bridge
-> Athena/CMSSW-specific integration only after experiment collaboration standards are met
```

## Current Boundary

The current repository exports internal boundary/operator-level artifacts. Those
artifacts are not event samples, generator cards, detector cards, or a validated
collider model.

## Non-Physical Placeholder Policy

No toy LHE or HepMC events are created in this sprint. If a future schema-only
placeholder is introduced, it must be disabled by default and labeled:

```text
NON-PHYSICAL STRUCTURAL PLACEHOLDER - NOT FOR ANALYSIS
```

## Promotion Criteria

Before a future event-generation interface can be promoted, it must include:

- a collider-ready Lagrangian;
- Feynman rules;
- a generator-compatible model export;
- parameter cards;
- event-generator cards;
- validation against pinned external targets;
- explicit claim boundaries preventing empirical feedback into BHSM derivation.
