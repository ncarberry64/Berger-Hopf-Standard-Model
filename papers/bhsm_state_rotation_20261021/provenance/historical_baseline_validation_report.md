# Final local validation

**Historical manuscript-pass record.** This report describes the pre-sightline snapshot and its 39-page PDF. The later 41-page manuscript and observational package are covered by [SN sightline validation V1](SN_SIGHTLINE_VALIDATION_V1.md). Canonical `code/`, `tests/` and `preregistration/` hashes remain unchanged; the earlier full-suite result is not represented as a new run.

The scientific snapshot is identified by SHA-256 **ac34e2f45e3eab1e9317db88d97288cd8fcfac7595b436cd4b1438a2b50039a2** in SUBMISSION_SCIENTIFIC_SNAPSHOT_v1.json. The final intended review commit is HEAD on theory/cosmology-universe-manuscript-final; resolve with git rev-parse HEAD. No scientific source changed during the full run; subsequent edits concern prose, typesetting and packaging.

- Full repository pytest: **87 passed, 1 strict expected failure**, 6699.65 seconds. No unexpected failures or skipped tests.
- The JUnit test identities match the complete recorded collection; subsets, duplicate replacements and inconsistent failure counters are rejected.
- Existing expected failure: curved-EFT DAE constraint preservation. It was not added or weakened by this pass.
- Focused gate/optical checks: **25 passed**.
- Canonical clean LaTeX build and isolated ZIP rebuild: **PASS**, without force flags.
- Undefined controls/references/citations, natbib/fatal warnings and overfull boxes: **none**.
- PDF: **39 pages**, visually inspected; numerical notation and figure layout checked after edits.
- Abstract: **200 words** using the recorded whitespace convention; eight keywords.
- Original frozen R1 manifest and historical numerical-result artifacts: unchanged.

Machine-readable evidence: [validation JSON](../artifacts/UNIVERSE_FINAL_VALIDATION_v1.json), [scientific file hashes](../artifacts/SUBMISSION_SCIENTIFIC_SNAPSHOT_v1.json), [JUnit report](../artifacts/submission_pytest.xml), [source ZIP](../submission/universe-source.zip).

These are software and build checks, not new observational validation. The Gaussian gate artifact is synthetic. Historical raw/derived input hashes and the original homogeneous localization statistic are missing. Action normalization/coherence and complete matter/radiation closure remain conditional/open.

**Not ready for actual submission:** complete the [author/submission checklist](UNIVERSE_MDPI_SUBMISSION_CHECKLIST.md). The generic source follows the free-format route. Native current MDPI template retrieval was blocked and is a separate optional/final-stage conversion. Local success does not certify remote CI; inspect the draft PR.
