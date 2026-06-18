# GitHub PR Stack Status

Current public status: structural architecture integrated conditional; numerical closure open.

This file records the GitHub PR stack inspection performed from branch
`github-pr-stack-cleanup-v1`. It is a repo-hygiene document only. It does not
change theorem conclusions, frozen predictions, official predictions, or
scientific statuses.

## Summary

PR #2 was verified as superseded by PR #3 because the head of PR #2
(`bhsm-theorem-discharge-numerical-input-closure-map-v1`) is an ancestor of the
head of PR #3 (`bhsm-s-nu-topo-local-closure-v1`). PR #2 was closed with a
supersession comment.

PRs #3 through #11 form a clean branch-to-branch stack after the main-based
PR #3.

## Stack Table

| PR | Title | Head branch | Base branch | State | Mergeable | Stacked correctly | Frozen prediction changes | Official prediction changes | Recommended action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #2 | PO-BH-47: Numerical Input Closure Map and Claim-Status Cleanup | `bhsm-theorem-discharge-numerical-input-closure-map-v1` | `main` | `CLOSED` | `MERGEABLE` before close | superseded by #3 | no detected frozen-file changes | no detected official-output changes; status audit passed on stack tip | Keep closed as superseded by #3. |
| #3 | PO-BH-47/48: Closure Map and Neutral Topographic Suppression Localization | `bhsm-s-nu-topo-local-closure-v1` | `main` | `OPEN` | `MERGEABLE` | yes, first active stack PR | no `docs/frozen_predictions.*` changes detected | no detected official-output changes; status audit passed on stack tip | Merge first after final review/tests. |
| #4 | PO-BH-49: Neutral Saddle Displacement Localization | `bhsm-delta-y-nu-localization-v1` | `bhsm-s-nu-topo-local-closure-v1` | `OPEN` | `MERGEABLE` | yes | no `docs/frozen_predictions.*` changes detected | no detected official-output changes; status audit passed on stack tip | Merge after #3 or retarget to updated `main` after #3 merges. |
| #5 | PO-BH-50: Neutral Effective Action Localization | `bhsm-s-eff-nu-localization-v1` | `bhsm-delta-y-nu-localization-v1` | `OPEN` | `MERGEABLE` | yes | no `docs/frozen_predictions.*` changes detected | no detected official-output changes; status audit passed on stack tip | Merge after #4 or retarget to updated `main` after #4 merges. |
| #6 | PO-BH-51: Subsurface Neutral Projection Geometry Localization | `bhsm-subsurface-projection-geometry-v1` | `bhsm-s-eff-nu-localization-v1` | `OPEN` | `MERGEABLE` | yes | no `docs/frozen_predictions.*` changes detected | no detected official-output changes; status audit passed on stack tip | Merge after #5 or retarget to updated `main` after #5 merges. |
| #7 | PO-BH-52: Neutral Boundary Tensors and Boundary Condition Localization | `bhsm-neutral-boundary-tensors-v1` | `bhsm-subsurface-projection-geometry-v1` | `OPEN` | `MERGEABLE` | yes | no `docs/frozen_predictions.*` changes detected | no detected official-output changes; status audit passed on stack tip | Merge after #6 or retarget to updated `main` after #6 merges. |
| #8 | PO-BH-53: Scalar/Topographic Boundary Variation | `bhsm-boundary-variation-v1` | `bhsm-neutral-boundary-tensors-v1` | `OPEN` | `MERGEABLE` | yes | no `docs/frozen_predictions.*` changes detected | no detected official-output changes; status audit passed on stack tip | Merge after #7 or retarget to updated `main` after #7 merges. |
| #9 | PO-BH-54: Normal-Coupling Collar Convention | `bhsm-normal-coupling-collar-v1` | `bhsm-boundary-variation-v1` | `OPEN` | `MERGEABLE` | yes | no `docs/frozen_predictions.*` changes detected | no detected official-output changes; status audit passed on stack tip | Merge after #8 or retarget to updated `main` after #8 merges. |
| #10 | PO-BH-55: Collar Geometry Package Localization | `bhsm-collar-geometry-package-v1` | `bhsm-normal-coupling-collar-v1` | `OPEN` | `MERGEABLE` | yes | no `docs/frozen_predictions.*` changes detected | no detected official-output changes; status audit passed on stack tip | Merge after #9 or retarget to updated `main` after #9 merges. |
| #11 | PO-BH-56: Complete Scalar/Topographic Collar Action Audit | `bhsm-complete-collar-action-v1` | `bhsm-collar-geometry-package-v1` | `OPEN` | `MERGEABLE` | yes | no `docs/frozen_predictions.*` changes detected | no detected official-output changes; status audit passed on stack tip | Merge after #10 or retarget to updated `main` after #10 merges. |

## Recommended Merge Order

```text
#3 -> #4 -> #5 -> #6 -> #7 -> #8 -> #9 -> #10 -> #11
```

Do not merge automatically unless explicitly authorized, tests/audits are
current, and frozen prediction integrity still passes.

## Branches Safe To Delete After Merge

After the corresponding PR is merged and the branch is no longer needed:

- `bhsm-s-nu-topo-local-closure-v1`
- `bhsm-delta-y-nu-localization-v1`
- `bhsm-s-eff-nu-localization-v1`
- `bhsm-subsurface-projection-geometry-v1`
- `bhsm-neutral-boundary-tensors-v1`
- `bhsm-boundary-variation-v1`
- `bhsm-normal-coupling-collar-v1`
- `bhsm-collar-geometry-package-v1`
- `bhsm-complete-collar-action-v1`

Do not delete `bhsm-theorem-discharge-numerical-input-closure-map-v1` until the
owner confirms it is no longer needed beyond the closed superseded PR #2.
