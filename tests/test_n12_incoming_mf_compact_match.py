from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_forward_channel_transfer import (
    restrict_two_boundary_weyl_to_dirichlet_birth_jets,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_INCOMING_MF_COMPACT_MATCH.json"


def test_dirichlet_birth_restriction_extracts_terminal_blocks() -> None:
    base = np.asarray([
        [2.0, 0.1, 0.2, 0.3],
        [0.1, 3.0, 0.4, 0.5],
        [0.2, 0.4, 5.0, 0.7],
        [0.3, 0.5, 0.7, 6.0],
    ])
    jets = {
        "base": base,
        "first_left": 0.2 * base,
        "first_right": -0.1 * base,
        "mixed_second": 0.03 * base,
    }
    result = restrict_two_boundary_weyl_to_dirichlet_birth_jets(jets)
    for key, matrix in jets.items():
        assert np.array_equal(result[key], matrix[2:, 2:])
    assert result["response"] == "M_f=M11"
    assert result["explicit_matrix_inverse_formed"] is False
    assert result["endpoint_load_imposed"] is False


def test_incoming_mf_match_certificate() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["incoming_Mf_operator_identity"].startswith("CLOSED")
    assert payload["claim_boundary"]["incoming_Mf_action_owned_Laurent_germ"] == "CLOSED"
    assert payload["claim_boundary"]["complete_finite_duration_incoming_Mf_family"].startswith("OPEN")
    assert payload["action_amplitude"]["positive_lambda_0_selected"] is False
    assert payload["exact_match"]["explicit_matrix_inverse_formed"] is False
