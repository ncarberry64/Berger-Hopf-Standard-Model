import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_SAME_CENTER_BLOCKS01_LOCAL_KRAWCZYK.json"
)


def test_same_center_blocks01_local_krawczyk() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["result"] == (
        "LOCAL_OWNER_NOT_CERTIFIED__"
        "CORRELATED_CANCELLED_RATE_TAYLOR_MODEL_REQUIRED"
    )
    assert payload["directive_terminal_classification"] == (
        "B_LOCAL_OWNER_FAILS_TO_CERTIFY"
    )
    assert payload["requested_B_curvature_label_not_claimed"] is True
    segment = payload["segment"]
    assert segment["block_intervals"] == [0, 1]
    assert segment["endpoint_nodes"] == [0, 1, 2]
    assert segment["spectral_containment_margin"] > 0.0
    outward = payload["outward_operands"]
    assert outward["local_Y_Euclidean_upper"] > 0.0
    assert outward["local_Z1"] is None
    assert outward["local_Z2"] is None
    assert outward["Krawczyk_self_map"] is None
    assert payload["failed_enclosure"]["stage"] == "tube_endpoint_1"
    boundary = payload["claim_boundary"]
    assert boundary["correlated_branch24_spectral_domain_blocks01"] == "CERTIFIED"
    assert boundary["blocks01_local_root"] == "OPEN"
    assert boundary["local_Z1_Z2_Krawczyk_inequality"] == "NOT_CERTIFIED"
    assert boundary["root_nonexistence_claim"] is False
    assert boundary["physical_instability_claim"] is False
    assert boundary["Gate7"] == "OPEN"
