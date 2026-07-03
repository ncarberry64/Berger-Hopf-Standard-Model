import json
from pathlib import Path

from bhsm.interface.gauge_coupling_spectral_residue import INVALIDATIONS, OPEN_GATES

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = "BHSM should not interpret w=(1,2,7) as gauge-boson counts. Gauge algebra dimensions remain (1,3,8)."


def test_v4_5_artifacts_are_parseable_guarded_and_incomplete():
    paths = sorted((ROOT / "artifacts").glob("BHSM_*_v4_5.json"))
    v45 = [path for path in paths if any(token in path.name for token in ("casimir_shell", "spectral_density", "whitened_boundary", "inverse_covariance", "open_gates"))]
    assert len(v45) == 5
    for path in v45:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["physics_validation_claimed"] is False
    open_payload = json.loads((ROOT / "artifacts" / "BHSM_open_gates_v4_5.json").read_text(encoding="utf-8"))
    assert open_payload["status"] == "FULL_BHSM_NOT_COMPLETE"
    assert set(OPEN_GATES).issubset(open_payload["open_gates"])


def test_docs_reject_boson_counts_projectors_raw_covariance_and_naive_running():
    docs = [
        ROOT / "docs" / "bhsm_casimir_shell_spectral_residue_v4_5.md",
        ROOT / "docs" / "bhsm_whitened_boundary_fluctuation_v4_5.md",
        ROOT / "docs" / "bhsm_inverse_covariance_placement_v4_5.md",
        ROOT / "docs" / "bhsm_relative_boundary_spectral_running_v4_5.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in docs)
    assert DOCTRINE in text
    for invalidation in INVALIDATIONS:
        assert invalidation in text
    assert "does not close `OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION`" in text


def test_public_claim_ledgers_preserve_the_action_gate():
    text = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in ("STATUS.md", "CLAIMS.md"))
    assert DOCTRINE in text
    assert "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT" in text
    assert "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    assert "λ_i=w_i/(6π²)" in text
    assert "before α_i is claimed as derived" in text
