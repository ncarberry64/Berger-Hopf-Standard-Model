from __future__ import annotations

from bhsm.interface.envelopment import radion_variation_v10_2 as radion


def test_exact_hopf_radion_derivative_has_no_positive_static_root():
    row = radion.symbolic_radion_variation()
    assert row["dR7_da_F_formula"] == "-12/a_F^3-24 a_F/a_H^4"
    assert row["vertical_derivative_strictly_negative"] is True
    assert row["positive_static_solution"] is False


def test_gravitational_kinetic_indefiniteness_is_not_called_a_ghost_theorem():
    row = radion.symbolic_radion_variation()
    assert row["kinetic_determinant"] == -72
    assert row["kinetic_indefinite"] is True
    assert row["ghost_conclusion"] is None


def test_radion_rho_and_proxy_R_remain_distinct():
    row = radion.radion_ownership_ledger()
    assert row["rho"]["identified_with_a_F"] is False
    assert row["R"]["identified_with_a_F"] is False
    assert row["R"]["gauge_invariant_map_R_of_a_F_psi_G_sigma_eta"] is None
    assert row["physical_buoyancy_radion"] is None


def test_radion_payload_is_valid_and_adds_no_potential():
    payload = radion.radion_payload()
    assert payload["validation_passed"] is True
    assert payload["equation"]["independent_radion_potential_added"] is False
