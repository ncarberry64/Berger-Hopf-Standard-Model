from __future__ import annotations

import numpy as np

from bhsm.interface.envelopment import floquet


def test_generic_monodromy_audit_classifies_instability_and_marginality():
    unstable = floquet.monodromy_audit(np.diag([0.8, 1.2]))
    marginal = floquet.monodromy_audit(np.array([[0.0, -1.0], [1.0, 0.0]]))
    assert unstable["classification"] == "UNSTABLE"
    assert marginal["classification"] == "MARGINAL"
    assert unstable["physical_orbit_claimed"] is False


def test_charged_orbit_gate_fails_closed_before_floquet_promotion():
    row = floquet.relative_periodic_orbit_gate()
    assert row["action_selected_orbit"] is None
    assert row["Floquet_operator"] is None
    assert row["Floquet_classification"] == "NOT_EVALUABLE_NO_PHYSICAL_ORBIT"
    assert row["collective_radius_proxy_is_particle"] is False
    assert row["numerical_search_executed"] is False
    assert row["numerical_evidence"]["residual_norm"] is None
    assert len(row["ansatz_audit"]) == 3
    assert row["status"] == "BLOCKED_EXACT_OBJECT_PROVED"


def test_stationary_cycle_reduces_exactly_to_v89_lens_inputs():
    Gu = np.diag([1.0, 2.0, 3.0])
    Qu = np.diag([1.0, 4.0, 9.0])
    Gd = np.diag([1.5, 2.5, 3.5])
    Qd = np.diag([0.5, 3.0, 8.0])
    K = np.eye(3)
    row = floquet.static_cycle_reduction(Gu, Qu, K, Gd, Qd)
    assert row["identity_exact"] is True
    assert row["physical_promotion"] is False
    assert np.allclose(row["cycle_average_G_u"], Gu)
    assert row["static_v8_9_result"]["current_unitarity_residual"] < 1.0e-12


def test_dynamic_forms_and_all_downstream_matrices_remain_null():
    payload = floquet.family_and_floquet_payload()
    forms = payload["cycle_forms"]
    assert forms["A_f"] is None
    assert forms["physical_K_ud"] is None
    assert forms["physical_V_BHSM"] is None
    assert payload["physical_CKM"] is None
    assert payload["physical_PMNS"] is None
    assert payload["matrices_printed"] is False


def test_quark_neutrino_measurement_and_4d_routes_name_exact_objects():
    gates = floquet.downstream_sector_gates()
    assert gates["quark"]["color_neutral_parent"] is None
    assert "COLOR_NEUTRAL_PARENT" in gates["quark"]["status"]
    assert gates["neutrino"]["monodromy_sectors"] is None
    assert gates["neutrino"]["PMNS"] is None
    assert gates["measurement"]["normalized_probabilities"] is None
    assert gates["four_dimensional"]["runtime"] is None
