# BHSM Collider Readiness Audit v0.1.0

Current BHSM release basis: `v1.0.1`.

Current public status:

```text
BHSM v1.0.1 status-reconciled release: internal boundary no-fit package complete/exported; external empirical comparison layer separate/open.
```

This document accepts the collider-software critique as a valid readiness
standard. It does not treat that critique as invalidating BHSM v1.0.1. BHSM
v1.0.1 is a released internal boundary no-fit prediction package, not a
collider production software stack.

## Readiness Verdict

| Interface target | Current status |
| --- | --- |
| Complete collider-ready 4D physical Lagrangian | Not exported |
| Gauge-fixed interaction vertices | Not exported |
| Feynman rules | Not exported |
| UFO/FeynRules model | Not exported |
| Mass/width parameter card | Not exported |
| LHE/HepMC event output | Not supported |
| MadGraph/Pythia/Herwig generation | Not supported |
| Athena integration | Not ready |
| CMSSW integration | Not ready |
| PDG validation plots | Schema/tool scaffold only; requires pinned targets |

BHSM v1.0.1 exports boundary/operator-level no-fit artifacts, not a production
event-generator model. No empirical values are used to derive BHSM constants or
boundary predictions.

## What Exists

- Internal boundary no-fit package: `COMPLETE_EXPORTED`.
- Profile scale, charged boundary outputs, neutral/PMNS/CKM/CP boundary outputs,
  and boundary-scale transport identity are exported as machine-readable
  artifacts.
- External empirical comparison layer: implemented as a separate one-way
  comparison layer and still open.
- Falsification/comparison guardrails: empirical data cannot feed back into
  derivation constants or boundary predictions.

## What Is Missing For Collider Software

Before any collider experiment software interface can be considered, BHSM would
need:

- an explicit collider-ready 4D physical Lagrangian;
- gauge fixing and interaction vertices;
- Feynman rules with conventions and units;
- a UFO/FeynRules or equivalent model export;
- a mass/width parameter card;
- event-generator cards for a concrete generator;
- generated and validated LHE or HepMC samples;
- detector simulation compatibility checks;
- collaboration-specific software, physics, and institutional review.

## Relation To Athena And CMSSW

Official experiment software integration is out of scope for BHSM v1.0.1. The
repository is not an official ATLAS or CMS software component and does not claim
compatibility with Athena, CMSSW, or experiment production workflows.

## Roadmap

| Future layer | Required milestone |
| --- | --- |
| BHSM-HEP v0.2 | Pinned PDG target table and generated comparison plots from real targets |
| BHSM-HEP v0.3 | Explicit collider-ready Lagrangian draft with claim boundaries |
| BHSM-HEP v0.4 | Feynman-rule/UFO export scaffold with validation gates |
| BHSM-HEP v1.0 | Validated event-generator model and documented event samples |

None of these future layers are claimed by BHSM v1.0.1.
