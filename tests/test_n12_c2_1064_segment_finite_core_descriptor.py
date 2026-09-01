from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from assemble_n12_c2_1064_segment_finite_core_descriptor import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
)


def test_1064_segment_descriptor_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_actual_coefficient_core_is_assembled_without_endpoint_promotion() -> None:
    payload = build_payload()
    path = payload["coefficient_path"]
    partition = payload["endpoint_event_child_partition"]
    assert path["node_count"] == 1065
    assert path["segment_count"] == 1064
    assert partition["far_core_edge_is_physical_endpoint"] is False
    assert partition["terminal_load_imposed"] is False
    assert all(
        row["generalized_gap_lower"] > 0.0
        and row["explicit_matrix_inverse_formed"] is False
        for row in payload["descriptor_pencils"].values()
    )


def test_missing_reset_jacobi_and_maximal_tail_are_not_fabricated() -> None:
    payload = build_payload()
    assert payload["derivative_interface"]["actual_reset_quotient_coefficient_Jacobi"] == "OPEN"
    assert payload["adjudication"]["actual_maximal_history_coefficient_oracle"] == "OPEN_BEYOND_THIS_PREFIX"
    assert payload["claim_boundary"]["zero_source_force"] == "OPEN"
