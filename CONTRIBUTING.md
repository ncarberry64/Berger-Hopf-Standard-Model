# Contributing

Thank you for taking an interest in the Berger-Hopf Standard Model repository.

## Before You Start

- Read `STATUS.md` and `CLAIMS.md` before proposing scientific changes.
- Search existing issues and discussions for related work.
- Open a research-source issue before a substantial theory or status change.
- Do not use measured values, fitted targets, or frozen outputs as derivation inputs.

## Pull Requests

Keep each pull request focused and identify:

- the source or artifact supporting the change;
- the exact claim status and remaining blockers;
- whether frozen predictions or official prediction logic change;
- the tests and audits run.

Run the focused tests plus:

```bash
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
```

The repository is publicly reviewable but remains all rights reserved. Opening an issue or pull request does not alter the terms in `LICENSE.md`.
