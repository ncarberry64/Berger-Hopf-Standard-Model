# Historical muon first-order artifact retention

This publication-hygiene review starts at
`00fa89d62e4c74ee9fd0b41611b3468ad035b5db` on
`codex/muon-parent-maxwell-density-review`. The scientific reference remains
`524ed90689bd5923c249bba2e699abf627e703cd`.

The existing [retention registry](../data/retained_large_research_artifacts.json)
uses schema `BHSM_RETAINED_LARGE_RESEARCH_ARTIFACTS_V1`. The public-readiness
audit accepts a registered NPZ only when its exact byte size and SHA-256 match;
it gives no exemption to changed bytes or other unlisted large files. The
original public-main review anchor is preserved, and the new entry records its
own branch review and historical introduction commit.

The preserved artifact is
[first_order_compact_reduction.npz](../artifacts/muon_first_order_complement_20261006/run_2/first_order_compact_reduction.npz):

| Field | Reviewed value |
| --- | --- |
| Repository path | `artifacts/muon_first_order_complement_20261006/run_2/first_order_compact_reduction.npz` |
| Exact bytes | `11125650` |
| SHA-256 | `f35ae512a03639ccc887bdeead0350a8cdec147b15db5b66ed6f94da794bfdb2` |
| Historical introduction | `b0b5cdec48735f6e2ae40051a32662297882b7e4` |
| Classification | `HISTORICAL_SCIENTIFIC_EVIDENCE` |

The hash agrees with the retained
[run_2 output receipt](../artifacts/muon_first_order_complement_20261006/run_2/output_hashes.json).
The [scientific milestone](muon_first_order_complement_20261006.md) records a
domain-valid compact first-order Galerkin reduction for the proposed seam.
That proposal remains unadopted; the artifact does not establish the full
retarded or native complementary response, global domain, or a physical muon
observable. Preserving its original matrices and reduction supports inspection
and reproducibility of that historical, explicitly restricted calculation.

The artifact was neither regenerated nor altered and was not consumed as new
physical data. This change only adds an exact preservation entry and records
the public-readiness audit before and after the entry. No artifact-generation
script, scientific equation, physical source, control calculation, or
public-readiness threshold was changed.

Receipts are retained in
[the hygiene evidence directory](../artifacts/muon_first_order_artifact_retention_20261007/).
The initial audit reports this single 11,125,650-byte artifact as the hygiene
blocker. The post-entry audit is materialized twice and compared byte for byte;
the preserved NPZ hash and size are checked again after validation. The
two post-entry runs pass with `BHSM_REPOSITORY_PUBLIC_REVIEW_READY` and classify
this artifact as `EXACT_REVIEWED_HASH`. The
existing exact-retention guard test still checks rejection of changed or
unlisted large files; the added entry-integrity test checks this artifact's
bytes and historical metadata.
