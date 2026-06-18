# GitHub Cleanup Report

Current branch: `github-pr-stack-cleanup-v1`

Current public status: structural architecture integrated conditional; numerical closure open.

This cleanup report is documentation-only. It does not change scientific
content, theorem conclusions, frozen predictions, official predictions, or
public claim status.

## Open PRs Inspected

Inspected PRs #2 through #11 with GitHub CLI.

- PR #2: `CLOSED` during this sprint as superseded by PR #3.
- PR #3: `OPEN`, `MERGEABLE`.
- PR #4: `OPEN`, `MERGEABLE`.
- PR #5: `OPEN`, `MERGEABLE`.
- PR #6: `OPEN`, `MERGEABLE`.
- PR #7: `OPEN`, `MERGEABLE`.
- PR #8: `OPEN`, `MERGEABLE`.
- PR #9: `OPEN`, `MERGEABLE`.
- PR #10: `OPEN`, `MERGEABLE`.
- PR #11: `OPEN`, `MERGEABLE`.

## Superseded PRs

PR #2 was verified as superseded by PR #3.

Verification:

```text
PR2_HEAD_IS_ANCESTOR_OF_PR3_HEAD=true
```

Action taken:

- Posted a supersession comment on PR #2.
- Closed PR #2 as superseded by PR #3.

## Recommended Close Action

No further PR closures are recommended at this time.

## Stack Order

Correct active stack:

```text
#3 -> #4 -> #5 -> #6 -> #7 -> #8 -> #9 -> #10 -> #11
```

PR #3 is based on `main`. PRs #4 through #11 are stacked branch-to-branch.

## Mergeability

All active PRs #3 through #11 were reported by GitHub CLI as `MERGEABLE` at the
time of inspection.

## Tests Run

```text
python -m pytest -q
```

Result:

```text
1376 passed
```

## Audits Run

```text
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
```

Results:

- forbidden-claims audit: passed
- BHSM status audit: passed
- frozen prediction integrity audit: passed

## Frozen Predictions Changed

No.

Evidence:

- `docs/frozen_predictions.md`: hash matched expected value.
- `docs/frozen_predictions.json`: hash matched expected value.
- PR diff-name audit for #3 through #11 found no `docs/frozen_predictions.*`
  changes.

## Official Predictions Changed

No.

Evidence:

- `tools/audit_bhsm_status.py` passed with `official_predictions_unchanged`.
- No frozen prediction file changes were detected in the active PR stack.

## Risky Files / Secrets Scan

Changed-file audit across PRs #3 through #11 found:

- no `.env` files;
- no private-key file names;
- no token/credential-like file names;
- no frozen prediction file changes.

Secret-like content scan across the active stack diff found no matches for:

```text
OPENAI_API_KEY
GITHUB_TOKEN
password
secret
BEGIN PRIVATE KEY
api_key
```

## Status Phrase Check

Required status phrase remains present:

```text
structural architecture integrated conditional; numerical closure open
```

No cleanup change strengthened claims. Existing "replacement" and FTL language
appears in guarded, negated, or explicitly conditional contexts, such as "not
yet a completed replacement" or "No claim of experimental FTL is made."

## Recommended Merge Order

Do not merge automatically without explicit user authorization.

Recommended order when authorized:

```text
Merge PR #3 first.
Update/rebase or retarget PR #4 onto updated main if needed.
Merge PR #4.
Repeat for #5, #6, #7, #8, #9, #10, and #11.
```

Because the active PRs are currently stacked branch-to-branch, avoid retargeting
unless the owner wants a linear main-merge workflow after each merge.

## Branches Safe To Delete After Merge

Only after the corresponding PR is merged and the owner confirms cleanup:

- `bhsm-s-nu-topo-local-closure-v1`
- `bhsm-delta-y-nu-localization-v1`
- `bhsm-s-eff-nu-localization-v1`
- `bhsm-subsurface-projection-geometry-v1`
- `bhsm-neutral-boundary-tensors-v1`
- `bhsm-boundary-variation-v1`
- `bhsm-normal-coupling-collar-v1`
- `bhsm-collar-geometry-package-v1`
- `bhsm-complete-collar-action-v1`

Do not delete the superseded PO-BH-47 branch without explicit owner approval.

## Unresolved Cleanup Items

- Decide whether to merge the active stack branch-to-branch or retarget each PR
  to `main` after its predecessor merges.
- After each merge, rerun tests/audits on the updated base before merging the
  next PR.
- Keep PR #11 in the stack plan because PO-BH-56 is now open and mergeable.
