import math

import numpy as np

from bhsm.interface import aether_diagonal_sp1_m4_attachment_v15_50 as attachment


def test_diagonal_metric_completion_and_global_quotient():
    residual = attachment.metric_completion_residual(
        2.0, 1.3, np.array([0.2, -0.4, 0.7]), np.array([-0.1, 0.8, 0.3])
    )
    assert abs(residual) < 1e-13
    contract = attachment.diagonal_quotient_contract()
    assert contract["action_is_free_at_regular_pole"]
    assert contract["boundary_quotient"].endswith("=S3")


def test_radius_and_connection_normalization_are_coefficient_locked():
    row = attachment.diagonal_quotient_geometry(1.7, 1.2)
    assert row["M4_spatial_radius"] == 1.7 * 1.2 / math.sqrt(1.7**2 + 1.2**2)
    assert abs(row["radius_ratio_M4_to_fiber"] - row["radius_ratio_from_x"]) < 1e-14
    assert row["connection_kinetic_coefficient"] > 0.0
    assert row["canonical_geometric_coupling_squared"] > 0.0


def test_attachment_is_not_a_second_classical_energy():
    payload = attachment.completion_payload()
    assert payload["validation_passed"]
    assert payload["action_ownership"]["background_curvature_already_in_parent_R8"]
    assert payload["action_ownership"]["add_connection_background_energy_again"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_payload_json_is_deterministic():
    payload = attachment.completion_payload()
    assert attachment.deterministic_json(payload) == attachment.deterministic_json(
        attachment.completion_payload()
    )
