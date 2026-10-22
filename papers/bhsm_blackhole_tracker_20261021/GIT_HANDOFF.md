# Git and publication handoff

## Formal reviewer repository

The authoritative reviewer repository is [Berger-Hopf-Standard-Model](https://github.com/ncarberry64/Berger-Hopf-Standard-Model), on branch `codex/norman-core-surface-amendment-20261022`, in [draft PR #470](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/pull/470).

Reviewer paths in that branch are:

- `products/blackhole_tracker/`: installable product, launcher, notebooks, tests and release evidence.
- `papers/bhsm_blackhole_tracker_20261021/`: manuscript, theory replay, provenance and reviews.

The external delivery receipt binds the final formal code commit, review status and artifact hashes. No formal code SHA is inferred here from a workspace commit or a theory-source pin. The interpretation manifest pins the dated scientific amendment at `3c820fee74a5c715ef58bf30998edb1d7b26fe78`; this is a source revision, not the final product/paper delivery commit.

## Completed rc2 verification

Product `0.2.0rc2` carries interpretation schema 2 and the 22 October 2026 attributed core/surface amendment without adding an optical term or fitted core parameter. A clean installed wheel, both executed installed notebooks, actual browser downloads, CLI replay and the four-interface comparison are recorded in release receipts. GUI/API/CLI/notebook supplied values, fit controls and shared interpretation agree, with exactly zero prediction difference. The rc1-to-rc2 replay records changed interpretation/provenance while retaining the same scientific status and zero optical difference.

The independent [rc2 installed review](review/RC2_INSTALLED_USABILITY_REVIEW.md) additionally checks API/CLI/report consistency, six interpretation/adapter source hashes, actual Git-source bytes, legacy rendering and boundary-output suppression. The corrected trajectory labels preserve 2015 and 2025. These scoped checks do not replace final-head CI or turn the retained synthetic calibration into empirical validation. Historical receipts retain their original versions and claims; the fixed 64-draw calibration was not restarted for this metadata update.

The same review's final full-audit addendum records corrected upload integrity, typed-input validation, lost-job recovery and independent-source plotting, plus 133 passing product tests. Its separate full-review receipt binds the rebuilt wheel SHA256 `323bcf675f6fe1c1262e85be49644d3736c2777788ecf2f92568f1cc6ba92ae3`; the earlier rc2 wheel/receipt remains historical. Final installed exports/replay and canonical BHSM citations pass, with unchanged valid-fit numerics. The new formal delivery commit is recorded separately when the complete paper/source snapshot is published.

## Development and historical handoff

[Manuscript-Generation draft PR #24](https://github.com/ncarberry64/Manuscript-Generation/pull/24), branch `codex/bhsm-state-rotation-20261021`, remains the development workspace and historical record. It is not the formal reviewer repository. Its local worktree is `C:/Users/carbe/Manuscript-Generation/.worktrees/bhsm-state-rotation-20261021`.

Existing unrelated dirty checkouts and PR23 were preserved. The first commit preserved the angular source and completed Hopf support result; subsequent commits make the Blackhole Tracker central. The complete source archive contains product/ and all three paper directories under papers/. The paper theory replay imports the preserved angular provider; the independently installable product carries its own six hash-pinned provider inputs. A separate product source ZIP and wheel are also delivered.

The earlier cumulative binary patch belongs to this historical Manuscript-Generation handoff and base `5fd65ea18a6055dbc6028839c2918415e3c00f71`. It must not be applied to the formal BHSM repository. For recovery of that original workspace only:

    git switch -c codex/bhsm-blackhole-tracker-handoff 5fd65ea18a6055dbc6028839c2918415e3c00f71
    git apply --check <path-to-BHSM_Blackhole_Tracker.patch>
    git apply --index <path-to-BHSM_Blackhole_Tracker.patch>

If the historical branch is already present, use it directly rather than applying the patch again. The older connector permission failure and authenticated Git CLI recovery remain provenance for that handoff. Both review PRs remain draft; no merge, journal submission or external communication has been performed. Final review/CI outcomes belong to the delivery receipt for their exact commits.
