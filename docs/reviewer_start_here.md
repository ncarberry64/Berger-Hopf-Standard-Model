# Reviewer start here

This route is designed to orient a technical reviewer in about five minutes
before deeper reproduction.

## 1. Read the verdict

Open the [canonical status](current_bhsm_status.md) and confirm the three
fail-closed flags in [machine form](current_bhsm_status.json). Gate 7 is open;
the reduced branch-24 event is not a physical encapsulation.

## 2. Fix the vocabulary

Use the [public terminology](public_terminology.md). In particular, keep
implemented machinery, numerical behavior, and physical prediction separate.

## 3. Inspect the newest owner artifacts

1. [Correlated branch-24 spectral domain](../artifacts/flagship_integration/BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_CORRELATED_SPECTRAL_DOMAIN.json)
2. [Fail-closed local Krawczyk adjudication](../artifacts/flagship_integration/BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_LOCAL_KRAWCZYK.json)
3. [Full-field attachment requirement](../artifacts/flagship_integration/BHSM_NEUTRINO_CHARGED_CURRENT_2PI_CLOSURE_RECONCILIATION.json)
4. [Action attachment audit](../theory/bhsm_current_full_field_action_attachment.md)

Check each artifact's claim boundary, exact missing operand, provenance hashes,
and `FULL_BHSM_COMPLETE` value before interpreting numerical fields.

## 4. Run the minimum audit

```bash
python -m pip install -e ".[benchmark]"
python tools/audit_public_surfaces.py
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
python -m pytest -q tests/test_public_surface_consistency.py tests/test_bhsm_museum_facade.py tests/test_cern_open_data_benchmark.py
```

For the wider retained suite, follow [QUICKSTART.md](../QUICKSTART.md) and the
[reviewer reproduction guide](reviewer_reproduction_guide.md).

## 5. Trace a public claim

For any museum placard or README sentence, require a direct route to source,
test, artifact, and stated limit. The
[claim-to-evidence matrix](BHSM_1_0_CLAIM_TO_EVIDENCE_MATRIX.md) and
[artifact index](../ARTIFACT_INDEX.md) are the main maps.

For the CMS exhibit, begin with the
[CERN source record](https://opendata.cern.ch/record/303), then compare the
[sample manifest](assets/pr98_cms_open_data_animation/pr98_cms_sample_manifest.json),
[benchmark result](../artifacts/cern_open_data_benchmark/results.json), and
[tests](../tests/test_cern_open_data_benchmark.py). That route validates the
coordinate engine only.

## 6. Report a discrepancy

Open a GitHub issue or follow [CONTRIBUTING.md](../CONTRIBUTING.md). Include:

- the exact claim and file;
- the commit and environment;
- the reproduction command and complete output;
- the artifact/provenance field that disagrees; and
- whether the problem affects machinery, numerical evidence, or physical
  promotion.

The repository should fail closed while a material contradiction is unresolved.
