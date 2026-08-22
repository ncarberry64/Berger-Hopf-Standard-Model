import hashlib
import json
from pathlib import Path

from bhsm.interface.n12_source_restricted_positive_duration import (
    source_restricted_positive_duration_theorem,
)


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "artifacts" / "n12_source_restricted_positive_duration"


def test_source_restricted_positive_duration_theorem_closes_only_its_scope():
    result = source_restricted_positive_duration_theorem()
    conclusions = result["conclusions"]

    assert result["validation_passed"] is True
    assert conclusions[
        "source_restricted_soft_Cauchy_family_is_strong_graph_precompact"
    ] is True
    assert conclusions[
        "nonzero_normal_zero_observation_limit_excluded"
    ] is True
    assert conclusions[
        "source_restricted_positive_duration_observation_bound_exists"
    ] is True
    assert conclusions["source_restricted_normal_right_inverse_exists"] is True
    assert conclusions["arbitrary_unrestricted_Jacobi_data_covered"] is False
    assert conclusions["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert conclusions["FULL_BHSM_COMPLETE"] is False


def test_static_and_finite_probe_shortcuts_remain_invalid():
    result = source_restricted_positive_duration_theorem()

    assert result["finite_diagnostics"]["used_as_the_uniform_bound"] is False
    assert result["validation"]["static_shifted_inverse_not_used"] is True
    assert "NUMERICAL_CONSTANTS" in result["promotion_boundary"]


def test_checkpoint_manifest_hashes_and_fails_closed():
    manifest = json.loads((
        CHECKPOINT
        / "BHSM_N12_SOURCE_RESTRICTED_POSITIVE_DURATION_CHECKPOINT_MANIFEST.json"
    ).read_text(encoding="utf-8"))
    for item in manifest["files"]:
        payload = (ROOT / item["path"]).read_bytes()
        assert hashlib.sha256(payload).hexdigest().upper() == item["SHA256"]
    status = manifest["scientific_status"]
    assert status["SOURCE_RESTRICTED_NORMAL_RIGHT_INVERSE_PROVED"] is True
    assert status["ARBITRARY_JACOBI_DATA_COVERED"] is False
    assert status["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert status["FULL_BHSM_COMPLETE"] is False
