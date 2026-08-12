from bhsm.interface import aether_diagonal_fiber_dirac_lift_v15_55 as lift


def test_round_diagonal_fiber_blocks_and_scaling_commute():
    block = lift.reset_block_validation()
    assert block["maximum_round_block_residual"] < 2e-13
    assert block["commutator_n3_two_radii"] < 2e-13
    assert lift.diagonal_fiber_dirac_contract()["anisotropic_Berger_monodromy_active"] is False


def test_every_family_mode_has_exact_internal_dirac_seed():
    seed = lift.family_dirac_seed()
    assert set(seed["sectors"]) == {"Q_L", "L_L", "u_c", "d_c", "e_c", "nu_c"}
    assert seed["sectors"]["Q_L"]["upper"]["R_F_times_positive_Dirac_eigenvalue"] == [1.5, 7.5, 11.5]
    assert seed["sectors"]["L_L"]["lower"]["R_F_times_positive_Dirac_eigenvalue"] == [1.5, 6.5, 10.5]


def test_spinor_incidence_keeps_yukawa_pairing_separate_from_internal_level():
    incidence = lift.spinor_lift_incidence()
    assert len(incidence["gauge_invariant_pairings"]) == 4
    assert incidence["bare_internal_eigenvalue_called_physical_SM_mass"] is False
    payload = lift.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["physical_SM_masses_derived"] is False


def test_payload_json_is_deterministic():
    payload = lift.completion_payload()
    assert lift.deterministic_json(payload) == lift.deterministic_json(
        lift.completion_payload()
    )
