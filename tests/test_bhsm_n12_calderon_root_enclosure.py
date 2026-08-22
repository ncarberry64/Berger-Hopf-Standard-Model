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


def test_n12_correlated_root_and_finite_core_close_fail_closed():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = payload["scientific_result"]
    assert payload["validation_passed"] is True
    assert result["correlated_exact_root_graph_gap_lower"] > 0.0
    assert result["whole_action_ball_graph_gap_lower"] > 0.0
    assert result["whole_action_ball_radius"] > 0.0
    assert result["c_M0_observation_norm_lower"] > 0.0
    assert result["C_r_event_child_product"] > 0.0
    assert result["that_cutoff_is_not_a_continuum_certificate"] is True
    assert result["retained_action_obstruction_demonstrated"] is False
    assert len(payload["localized_open_operator_blocks"]) == 4
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_n12_calderon_root_enclosure_manifest_hashes_reproduce():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for relative, expected in payload["inputs"].items():
        assert _sha256(ROOT / relative) == expected, relative
