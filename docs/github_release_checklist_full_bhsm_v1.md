# GitHub Release Checklist: Full BHSM v1 Candidate

This checklist is for a future release action. It does not publish a release.

## Pre-Release Checks

- [ ] Confirm branch and tag target with author.
- [ ] Run focused status-refresh tests.
- [ ] Run full test suite.
- [ ] Run safety scan.
- [ ] Run frozen prediction diff check.
- [ ] Run official prediction diff check.
- [ ] Confirm README is updated.
- [ ] Confirm Zenodo metadata is checked.
- [ ] Confirm no auth material is handled.
- [ ] Confirm no release publication unless explicitly instructed by the user.

## Commands

```powershell
python -m pytest -q
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
git diff -- docs/frozen_predictions.md docs/frozen_predictions.json
```

## Guardrails

- Do not change official predictions.
- Do not change frozen predictions.
- Do not create a new official mass formula.
- Do not claim completed Standard Model derivation.
- Do not claim dark matter is solved.
