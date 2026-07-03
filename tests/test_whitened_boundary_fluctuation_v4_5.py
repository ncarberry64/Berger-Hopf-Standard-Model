from bhsm.interface.gauge_coupling_spectral_residue import build_artifact_payloads, status_table


def test_weyl_density_attaches_to_whitened_modes_not_raw_green_covariance():
    payload = build_artifact_payloads()["whitened_boundary_operator"]
    assert payload["status"] == "WHITENED_BOUNDARY_FLUCTUATION_CONDITIONAL"
    assert payload["whitened_variable"] == "B_i=L_i(rho)^(1/2) A_i"
    assert "not the raw Green covariance" in payload["claim_boundary"]
    assert "OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_L_i" in payload["open_gates"]


def test_inverse_covariance_and_coupling_placement_remain_conditional():
    payload = build_artifact_payloads()["inverse_covariance_placement"]
    assert payload["kinetic_stiffness_candidate"] == "K_i proportional to 1/lambda_i"
    assert payload["coupling_candidate"] == "alpha_i proportional to lambda_i"
    assert payload["is_action_derived"] is False
    assert payload["alpha_i_action_status"] == "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION"
    assert status_table()["full_completion"] == "FULL_BHSM_NOT_COMPLETE"
