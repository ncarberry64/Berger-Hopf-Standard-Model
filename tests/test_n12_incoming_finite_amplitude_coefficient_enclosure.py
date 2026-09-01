from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_incoming_finite_amplitude_coefficient_enclosure import (  # noqa: E402
    build_payload,
)


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
)


def test_finite_amplitude_coefficient_enclosure_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_finite_enclosure_contains_quadratic_germ() -> None:
    payload = build_payload()
    for row in payload["uniform_normalized_path"]["sampled_interval_rows"]:
        assert row["finite_enclosure_contains_germ_interval"] is True
        finite = row["finite_log_radius_lambda_squared_coefficient_interval"]
        assert finite[0] <= finite[1] <= 0.0
        scalar = row["scalar_log_relative_potential_per_lambda_squared_interval"]
        dirac = row[
            "factorized_Dirac_log_relative_superpotential_per_lambda_squared_interval"
        ]
        assert 0.0 <= scalar[0] <= scalar[1]
        assert 0.0 <= dirac[0] <= dirac[1]


def test_amplitude_box_is_parametric_not_selected() -> None:
    payload = build_payload()
    family = payload["amplitude_family"]
    assert family["parameter_domain"].startswith("0<lambda<=")
    assert family["positive_member_selected"] is False
    assert family["D_lambda_log_R4_absolute_upper_on_box"] > 0.0
    assert payload["claim_boundary"][
        "uniform_inverse_free_finite_amplitude_incoming_remainder"
    ] == "CLOSED"
