import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_QXI_RELATIVE_ENERGY_REUSE_TABLE.json"
)


def test_qxi_reuse_table_preserves_the_continuum_gate() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["Q_xi_evaluated"] is False
    assert payload["Delta_H_evaluated"] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
    rows = {row["object"]: row for row in payload["reuse_table"]}
    assert rows["matched_parent_restriction_R_P"][
        "event_side_may_be_substituted"
    ] is False
    assert rows["complete_Q_xi_contract"]["current_implementation"] is None
    assert rows["matched_parent_positive_duration_history"][
        "current_implementation"
    ] is None
    assert rows["matched_parent_stationary_section"][
        "N12_normal_inverse_may_be_substituted"
    ] is False
    assert rows["local_canonical_energy"]["scope"] == (
        "NOT_Q_xi_NOT_DeltaH_NOT_MASS"
    )
