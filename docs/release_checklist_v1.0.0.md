# BHSM v1.0.0 Release Checklist

Release title: Berger-Hopf Standard Model v1.0.0: Complete Internal Boundary
No-Fit Package.

## Package Checks

- [x] README updated for v1.0.0 status.
- [x] Release notes created.
- [x] Citation metadata created/updated.
- [x] Zenodo metadata created/updated.
- [x] Authors file present.
- [x] License preserved as all rights reserved.
- [x] Manuscript Markdown created.
- [x] Release manifest created.
- [x] External comparison layer documented as separate/open.
- [x] DOI not invented.

## Tests And Audits

- [x] Focused release tests passed: 8 passed.
- [x] Adjacent stack tests passed: 120 passed.
- [x] Full test suite passed: 1776 passed.
- [x] Forbidden-claims audit passed.
- [x] BHSM status audit passed.
- [x] Frozen prediction integrity audit passed.
- [x] Safety scan completed; only benign checklist/test wording and variable-name hits.
- [x] Manuscript PDF generated:
  `manuscript/BHSM_v1_complete_internal_boundary_no_fit_package.pdf`.

## Post-Merge Release Commands

Do not run these commands until the branch is merged and release creation is
explicitly authorized.

```bash
git checkout main
git pull
git tag -a v1.0.0 -m "BHSM v1.0.0: Complete internal boundary no-fit package"
git push origin v1.0.0
gh release create v1.0.0 \
  --title "Berger-Hopf Standard Model v1.0.0: Complete Internal Boundary No-Fit Package" \
  --notes-file RELEASE_NOTES_v1.0.0.md
```

## Zenodo Note

After the GitHub release is published, Zenodo should archive the release if the
repository is enabled in the Zenodo GitHub integration. Wait for processing,
then update `CITATION.cff`, `README.md`, and `docs/how_to_cite.md` with the DOI
if a new DOI is assigned.
