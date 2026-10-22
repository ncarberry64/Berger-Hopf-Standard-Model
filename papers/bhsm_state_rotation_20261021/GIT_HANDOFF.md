# Separate new-paper Git handoff

Repository: https://github.com/ncarberry64/Manuscript-Generation
Base: 5fd65ea18a6055dbc6028839c2918415e3c00f71 (origin/main at recovery)
Local branch: codex/bhsm-state-rotation-20261021
Local worktree: C:/Users/carbe/Manuscript-Generation/.worktrees/bhsm-state-rotation-20261021

The branch adds the new Hopf-charge paper and preserves the exact recovered
angular starting paper as its sibling. It also adds a small pytest import-path
conftest and scoped papers/.gitattributes to preserve archived hashes across
Git line-ending conversion. Existing scientific equations, tests, frozen
predictions, unrelated dirty checkouts and PR #23 are not changed.

The release ZIP contains both paper directories and their complete offline
scientific reproduction inputs. GIT_HANDOFF, RESULT_STATEMENT, CHAIN_AND_FREEDOMS,
VALIDATION and review/ describe the claims and limits. The separate output patch
includes all Git changes and binary PDFs/figures.

For a fresh checkout at the stated base, apply the supplied format-patch with:

    git switch -c codex/bhsm-state-rotation-20261021 5fd65ea18a6055dbc6028839c2918415e3c00f71
    git am <path-to-BHSM_Hopf_Nodal_Lensing.patch>

For the already prepared local branch, publish without touching PR #23:

    git push -u origin codex/bhsm-state-rotation-20261021

Then create a **new draft** pull request to main using the title/body in
PR_DESCRIPTION.md. No journal submission, merge or message to another person
is authorized by this handoff. Remote publication status and the exact final
commit/patch hash are supplied in the external delivery receipt, avoiding a
self-referential commit identity inside the commit.

The GitHub connector rejected branch creation with 403 Resource not accessible
by integration. The existing authenticated Git CLI dry-run succeeded; actual
push and draft-PR outcome are recorded in the final delivery receipt.
