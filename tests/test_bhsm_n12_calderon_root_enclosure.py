import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_CALDERON_ROOT_ENCLOSURE_CHECKPOINT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_n12_calderon_root_enclosure_is_recorded_fail_closed():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = payload["scientific_result"]
    assert payload["validation_passed"] is True
    assert all(
        defect < 1.0
        for defect in result[
            "gauge_fixed_sector_interval_inverse_defects"
        ].values()
    )
    assert result["coupled_graph_symbol_interval_inverse_defect"] >= 1.0
    assert result["retained_action_obstruction_demonstrated"] is False
    assert result["numerical_overenclosure_localized"] is True
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_n12_calderon_root_enclosure_manifest_hashes_reproduce():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for relative, expected in payload["inputs"].items():
        assert _sha256(ROOT / relative) == expected
