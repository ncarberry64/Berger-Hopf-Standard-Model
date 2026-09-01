import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "artifacts"
    / "flagship_integration"
    / "BHSM_INTEGRATED_LINEAGE_REDUCTION.json"
)


def test_all_recorded_bhsm_lineages_are_integrated() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["status"] == (
        "ALL_FETCHED_BHSM_LINEAGES_INTEGRATED__SEMANTIC_REDUCTION_ACTIVE"
    )
    assert payload["counts"]["refs_unmerged"] == 0
    assert payload["unmerged_refs"] == []
    assert payload["counts"]["refs_examined"] == payload["counts"]["refs_integrated"]
    assert all(row["is_ancestor_of_main"] for row in payload["ref_inventory"])


def test_reduction_preserves_assets_without_rebuilding_particles() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    policy = payload["integration_policy"]
    reduction = payload["canonical_reduction"]
    assert policy["all_lineages_are_bhsm_assets"] is True
    assert policy["unique_files_are_imported"] is True
    assert policy["particle_spectrum_is_not_rebuilt"] is True
    assert "family or mode may manifest as an SM particle" in reduction["manifestation_rule"]
    assert len(reduction["forbidden_equivalences"]) == 3
