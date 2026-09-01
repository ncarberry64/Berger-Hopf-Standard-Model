import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_CORRELATED_SPECTRAL_DOMAIN.json"
)


def test_same_center_blocks01_correlated_spectral_domain() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["status"] == (
        "BLOCKS01_ROOT_CONTAINING_CORRELATED_BRANCH24_DOMAIN_CERTIFIED__"
        "LOCAL_RATE_JACOBIAN_VARIATION_REMAINS"
    )
    assert payload["local_domain"]["two_block_Newton_coordinate_norm_upper"] < (
        payload["local_domain"]["action_coordinate_radius"]
    )
    assert payload["summary"]["certified_locations"] == 5
    assert payload["summary"]["minimum_negative_selected_gap_lower"] > 0.0
    assert payload["summary"]["minimum_selected_positive_gap_lower"] > 0.0
    assert payload["summary"]["minimum_descriptor_lower"] > 0.0
    assert all(row["selected_branch"] == 24 for row in payload["rows"])
    assert all(
        row["correlated_spectral_domain_closed"] for row in payload["rows"]
    )
    boundary = payload["claim_boundary"]
    assert boundary["correlated_branch24_spectral_domain_blocks01"] == "CERTIFIED"
    assert boundary["same_center_outward_local_rate_Jacobian_variation"] == "OPEN"
    assert boundary["local_Y_Z1_Z2_Krawczyk_inequality"] == "OPEN"
    assert boundary["Gate7"] == "OPEN"
