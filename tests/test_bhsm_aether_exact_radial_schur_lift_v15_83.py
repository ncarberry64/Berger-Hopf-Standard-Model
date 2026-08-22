import json

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    angular_selection_theorem,
    completion_payload,
    deterministic_json,
    exact_radial_rows,
    identity_response_localization,
)


def test_exact_hessian_sequence_keeps_every_near_null_direction():
    rows = exact_radial_rows()
    assert [row["order"] for row in rows] == list(range(2, 13))
    assert all(abs(row["full_half_J_Dinv_J"]) < 2.0 for row in rows)
    assert all("smallest_mode_source_projection" in row for row in rows)


def test_lowest_killing_spinor_has_no_nonaxisymmetric_source_tail():
    theorem = angular_selection_theorem()
    assert theorem["non_axisymmetric_Schur_tail"] == 0.0
    assert theorem["cohomogeneity_one_sector_complete_for_this_quadratic_source"]


def test_payload_is_valid_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    encoded = deterministic_json(payload)
    assert encoded == deterministic_json(completion_payload())
    assert json.loads(encoded)["version"] == "v15.83"


def test_identity_response_localization_uses_exact_normalized_integral():
    chi = np.linspace(0.0, np.pi / 4.0, 1001)
    raw = np.sin(chi) ** 2 * np.cos(chi) ** 2
    increments = 0.5 * (raw[1:] + raw[:-1]) * np.diff(chi)
    cumulative = np.concatenate(([0.0], np.cumsum(increments)))
    cumulative *= 0.5 / cumulative[-1]
    numerical = 1.0 - 4.0 * (-0.5 + cumulative) ** 2
    exact = identity_response_localization(chi)
    assert exact[0] == 0.0
    assert exact[-1] == 1.0
    assert np.max(np.abs(exact - numerical)) < 1.0e-6
