from math import isclose, isfinite, sqrt

import numpy as np

from bhsm_config import (
    available_geometry_configs,
    legacy_low_a_config,
    round_geometry_config,
)
from bhsm_model import build_bhsm_model, compute_yukawa_ratios
from claims import ClaimStatus, build_claims_ledger
from constants import S_OVERLAP
from flavor_matrix import (
    canonical_ckm_angles,
    canonical_ckm_delta,
    canonical_ckm_matrix,
    canonical_flavor_report,
    canonical_mass_ratios,
    jarlskog_invariant,
)
from mode_selection import hopf_charge
from prediction_ledger import CKM_REFERENCES, build_prediction_ledger


def test_default_model_uses_alpha_anchored_geometry():
    model = build_bhsm_model()

    assert model.geometry_config.name == "ALPHA_ANCHORED"
    assert isclose(model.geometry_config.a, 1.157054135733433)


def test_canonical_mass_ratios_match_model_outputs():
    model = build_bhsm_model()

    assert canonical_mass_ratios(model) == compute_yukawa_ratios(model)


def test_ckm_angles_are_computed_from_canonical_bhsm_ratios():
    model = build_bhsm_model()
    ratios = canonical_mass_ratios(model)
    angles = canonical_ckm_angles(model)

    assert isclose(angles["sin_theta_12"], sqrt(ratios["down_quarks"]["light"] / ratios["down_quarks"]["middle"]))
    assert isclose(angles["sin_theta_23"], 2.0 * ratios["down_quarks"]["middle"])
    assert isclose(angles["sin_theta_13"], sqrt(ratios["up_quarks"]["light"]))
    assert not isclose(angles["sin_theta_13"], CKM_REFERENCES["sin_theta_13"])


def test_ckm_delta_uses_hopf_charges_and_s_not_empirical_input():
    model = build_bhsm_model()
    delta = canonical_ckm_delta(model)
    q_u = hopf_charge(10, 1)
    q_d = hopf_charge(8, 2)

    assert delta["q_u"] == q_u
    assert delta["q_d"] == q_d
    assert delta["delta_q"] == q_u - q_d
    assert isclose(delta["S"], S_OVERLAP)
    assert isclose(delta["delta"], (q_u - q_d) * sqrt(S_OVERLAP))
    assert not isclose(delta["delta"], CKM_REFERENCES["delta_cp"])


def test_jarlskog_is_finite_and_nonzero():
    model = build_bhsm_model()
    angles = canonical_ckm_angles(model)
    delta = canonical_ckm_delta(model)
    value = jarlskog_invariant(
        angles["sin_theta_12"],
        angles["sin_theta_23"],
        angles["sin_theta_13"],
        float(delta["delta"]),
    )

    assert isfinite(value)
    assert value > 0


def test_ckm_matrix_magnitudes_are_finite():
    matrix = canonical_ckm_matrix(build_bhsm_model())

    assert matrix.shape == (3, 3)
    assert np.all(np.isfinite(matrix))
    assert np.all(matrix >= 0)
    assert np.all(matrix <= 1)


def test_canonical_flavor_report_contains_cp_screen():
    report = canonical_flavor_report(build_bhsm_model())

    assert report["status"] == "BHSM_CANONICAL_FLAVOR_SCREEN"
    assert report["cp_phase_status"] == "HOPF_PHASE_CP_SCREEN"
    assert report["delta"]["formula"] == "delta_CKM = (q_u - q_d) * sqrt(S)"
    assert report["jarlskog"] > 0


def test_round_and_legacy_low_a_remain_controls():
    configs = available_geometry_configs()

    assert round_geometry_config() in configs
    assert legacy_low_a_config() in configs
    assert round_geometry_config().status == "BASELINE_CONTROL"
    assert legacy_low_a_config().status == "LEGACY_SENSITIVITY"


def test_prediction_ledger_uses_computed_cp_not_placeholder():
    ledger = build_prediction_ledger(build_bhsm_model())
    rows = {row.id: row for row in ledger}

    assert rows["ckm.delta_cp"].status == "HOPF_PHASE_CP_SCREEN"
    assert rows["ckm.delta_cp"].predicted == canonical_ckm_delta(build_bhsm_model())["delta"]
    assert rows["ckm.delta_cp"].metadata["formula"] == "delta_CKM = (q_u - q_d) * sqrt(S)"
    assert "placeholder" not in rows["ckm.delta_cp"].metadata


def test_claim_status_does_not_upgrade_to_final_proof():
    claims = {claim.id: claim for claim in build_claims_ledger()}

    assert claims["ckm_screen"].status == ClaimStatus.DERIVED_CONDITIONAL
    assert claims["forbidden_numerical_predictions"].status == ClaimStatus.FORBIDDEN
