Manual RC6 preparation — publication HOLD

This directory prepares a local author-review packet for Galaxies. It performs no upload, portal action, final author attestation, journal agreement or payment. `ready_for_submission` remains `false` even when every byte check passes. Gaia18ajz is a previously published primary investigation target; no new engine BH interpretation or accepted known-BH recovery is established. Packaging does not remove the scientific publication hold.

Only this README and `prepare_submission.py` are authored at this stage. Final `submission_metadata.json` and `cover_letter_draft.md` must wait for the final formal BHSM code commit, visually reviewed PDF hash and page count, installed-product validation and notebook/browser/replay receipts. Do not copy RC5 pins, counts or a preliminary RC6 PDF into final metadata. All RC5 files remain historical records in `../rc5/`.

After those final bindings are supplied, run from the paper directory:

```text
python submission/rc6/prepare_submission.py /path/to/a/fresh/external/manual-files-rc6-held
```

The output directory must be new and outside the paper source tree. The checker requires an exact normalized abstract of at most 200 words, the final 40-character formal BHSM code citation for `bhsm-blackhole-tracker 0.2.0rc6`, a valid PDF whose bytes match the reviewed SHA-256, positive reviewed page-count metadata and the final wheel/validation binding. It verifies every focused LaTeX ZIP member, copies the PDF/metadata/held cover draft byte-for-byte and checks that its inputs did not change. Existing output directories are refused. Failed newly created packets retain a failure receipt; they never become submission-ready.

The final metadata retains the existing RC5 author/declaration provenance where applicable, `manual_submission_only: true`, `ready_for_submission: false` and `submission_actions_performed: []`. Its `local_release_validation` must name product version `0.2.0rc6`, the actual final wheel SHA-256 and `scientific_acceptance: "NOT_ESTABLISHED"`. Keep the following explicit evidence facts in `publication_hold`:

```json
{
  "status": "HOLD",
  "primary_investigation_target": "Gaia18ajz",
  "primary_candidate_previously_published": true,
  "new_engine_BH_interpretation_established": false,
  "native_candidate_analysis_adequate": false,
  "known_black_hole_recovery_validated": false
}
```

The held cover-letter draft must identify Gaia18ajz as previously published and explicitly retain the publication hold. Literature-dependent mass alternatives, the primary research target, the published positive BH reference and non-BH comparison keep their different roles. A candidate category or successful software test is not a physical identification. The common BHSM interpretation uses one shared exterior response counted once; it adds no extra optical potential or measured microscopic core state.

PDF pages and validation results originate in the separate final review receipts. This stdlib packager verifies the PDF byte hash and reports the reviewed page count; it does not independently render or count pages, rerun scientific analyses or assert hosted CI success. No journal deadline or charge is reverified by this source preparation. Any future release of the publication hold requires a separate explicit evidence/status revision and author decision.

Formal reviewer repository and code citation: [Berger–Hopf Standard Model](https://github.com/ncarberry64/Berger-Hopf-Standard-Model). The manuscript Git remains a workspace.
