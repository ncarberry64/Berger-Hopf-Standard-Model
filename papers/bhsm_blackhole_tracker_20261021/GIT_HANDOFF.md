# Git and publication handoff

## Formal reviewer repository

The authoritative reviewer repository is [Berger-Hopf-Standard-Model](https://github.com/ncarberry64/Berger-Hopf-Standard-Model), on branch `codex/blackhole-tracker-real-data-20261022`, in [draft PR #471](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/pull/471).

Reviewer paths in that branch are:

- `products/blackhole_tracker/`: installable product, launcher, notebooks, tests and release evidence.
- `papers/bhsm_blackhole_tracker_20261021/`: manuscript, theory replay, provenance and reviews.

The external delivery receipt binds the final formal code commit, review status and artifact hashes. No formal code SHA is inferred here from a workspace commit or a theory-source pin. The interpretation manifest pins the dated scientific amendment at `3c820fee74a5c715ef58bf30998edb1d7b26fe78`; this is a source revision, not the final product/paper delivery commit.

## Current RC7 review candidate

The current product is `0.2.0rc7`, pinned in the formal repository at
`f90c9dc4a9eed262ca3b2291b3320f47bb4a5333`, with 373 exact imported product
source files from workspace commit `648fad552dfe1ee45b1c139b61423fdf22b997d1`.
The final delivery receipt separately binds the reviewed paper and later formal
integration head. The BHSM repository remains the canonical researcher source.

Source and minimum-supported installed environments each pass 338 tests and
66 subtests. The compact source distribution separately replays 49 research
controls and the original 16 ideal algebra controls. A fresh installed-browser
run imports all 734 native rows of OGLE3-ULENS-0585, fits, exports and replays
with zero prediction difference; the original data and unavailable quantities
remain intact, and manifest tampering is refused.

The new frozen synthetic experiment retains all 4,608 datasets and 4,736 fits.
Its independent saved-only audit confirms three uncertainty-calibration failures.
The separate normalized-Student 2023 known-system experiment remains numerically
unresolved. Software verification does not clear these scientific limits:
accepted independent known-black-hole recoveries and established new black-hole
identifications both remain zero, and scientific publication remains on HOLD.

The product contains the versioned protocols, compact findings and three bounded
public evidence parts with assembly/hash verification. Native observations
excluded from that public transport retain their hashes, source-row provenance,
official retrieval information and separate access/rights requirements. The
compact source distribution includes retrieval and replay helpers rather than
silently substituting generated measurements for observations. The legal
notices, software citation and historical preprint identifier remain distinct.

## Historical corrected rc3 and frozen real observations

The runtime is pinned in the formal repository at `002b9ecfe2f1a778b68b7558581997c05919ae93`, imported from development commit `aa1759d07c97e25a2fb1a7ad24a053aa553d602a`. The reviewed F4/F5 theory source is independently pinned at `705d4c7e2f9a832b457f63ff975e7d4dc8008645`. This is a review candidate; no new merge, Pages publication or journal submission is performed.

All 182 product tests pass. The clean installed wheel and actual local native app pass fit/export/replay with native row identities and BHSM interpretation preserved; unidentified motion covariance remains null. All three notebooks execute through the installed wheel outside the checkout. The corrected manuscript is 36 pages and includes the actual two archival follow-up light curves and the complete pilot interpretation.

`real_data_pilot_20261022/` preserves the internally frozen protocol, original numerical tables and later literature annotations separately, all 100 residual plots and diagnostic files, original software bytes and external raw hashes/refetch instructions. Its 100 events / 76,344 measurements yield 89 inadequate and 11 non-rejected simple-model fits, two historical archival follow-ups, and zero mass-supported black-hole candidates. The historical 2022 benchmark remains inadequate under five photometric variants and its specific HST time/frame gaps remain unresolved. The user's subsequent request for known-black-hole mass validation is being investigated on a separate branch and later-data protocol; it does not replace these frozen results.

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
