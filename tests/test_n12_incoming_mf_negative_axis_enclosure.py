from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_incoming_mf_negative_axis_enclosure import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json"
)


def test_incoming_mf_negative_axis_payload_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_all_stored_incoming_responses_are_positive() -> None:
    payload = build_payload()
    for group in ("scalar_and_deRham_rows", "factorized_product_Dirac_rows"):
        for row in payload[group]:
            for probe in row["negative_axis_samples"]:
                lower, upper = probe[
                    "incoming_M_f_interval_at_lambda_box_edge"
                ]
                assert 0.0 < lower <= upper


def test_fermion_joint_seam_is_invertible() -> None:
    payload = build_payload()
    for row in payload["factorized_product_Dirac_rows"]:
        for probe in row["negative_axis_samples"]:
            lower, upper = probe["joint_fermion_seam_interval"]
            assert 0.0 < lower <= upper
            assert probe["joint_seam_inverse_norm_upper"] <= 1.0 / lower
    assert payload["claim_boundary"][
        "fermion_AE2_joint_seam_invertibility"
    ] == "CLOSED"


def test_proof_edge_is_not_selected_history() -> None:
    payload = build_payload()
    assert "NOT_A_PHYSICAL_HISTORY_SELECTION" in payload[
        "proof_edge_crosscheck"
    ]["role"]
    assert payload["claim_boundary"]["exact_joint_spectral_trace"] == "OPEN"
