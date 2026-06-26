# BHSM v1.1.0 - Institutional HEP handoff and bounded collider-interface package

## Summary

BHSM v1.1.0 packages the status-reconciled internal boundary no-fit release and the Phase Three bounded collider-interface HEP handoff chain.

## What Is Included

- Internal boundary no-fit package.
- Frozen prediction integrity checks.
- Minimal bounded collider-interface subset.
- CKM/PMNS charged-current target structures sourced by BHSM artifacts.
- FeynRules-prep documentation and disabled minimal FeynRules draft.
- Runtime preflight, Wolfram/FeynRules mapping, UFO export, and MadGraph smoke-test runners.
- Institutional HEP handoff manifest and validation protocol.

## What Is Not Claimed

BHSM v1.1.0 is not an officially integrated CERN software package, not complete BHSM 4D Lagrangian export, not FeynRules/UFO/MadGraph validated, not Athena-ready, not CMSSW-ready, and not empirically validated.

## Runtime Requirements

Python is required for repository tests. Live FeynRules validation requires licensed Wolfram/WolframScript or Mathematica plus a legal FeynRules installation. MadGraph smoke testing requires a loadable UFO export and a legal MadGraph installation.

## How To Review

Start with `docs/hep_review_quickstart.md` and `docs/institutional_hep_handoff_index.md`.

## How To Validate Locally

Run:

```powershell
python -m pytest -q
python scripts/setup/check_bhsm_hep_environment.py
```

Then follow the Wolfram/FeynRules and MadGraph mapping guides.

## Current Gate Status

Institutional HEP handoff package ready: yes. Official CERN software integration: no. Complete BHSM 4D Lagrangian: no. Minimal collider-interface subset: yes. FeynRules, UFO, MadGraph, event, Athena, and CMSSW runtime gates remain closed.

## Remaining Blockers

- Licensed Wolfram/FeynRules runtime mapping.
- Live FeynRules validation.
- UFO export and loadability.
- MadGraph smoke test.
- Event-generation evidence.
- Complete BHSM 4D Lagrangian export.
- Charged-boundary, neutral-kernel, and standalone CP-holonomy production-vertex closure.

## Claim Boundaries

See `docs/bhsm_v1_1_0_claim_status.md`.

## Citation

Use `CITATION.cff`. Zenodo DOI is pending/unknown for v1.1.0.
