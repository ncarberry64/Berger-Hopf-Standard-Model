from bhsm.interface.common_16 import audit_common_16_provenance


def test_provenance_gates_retain_action_and_transport_blockers() -> None:
    result = audit_common_16_provenance()
    assert result.status == "CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE"
    assert result.omega_f_source_status == "STRUCTURALLY_INTEGRATED_NOT_ACTION_DERIVED"
    assert result.rho_ch_source_status == "OPEN_MISSING_RHO_CH_ACTION_DERIVATION"
    assert result.ckm_exponent_final_status == "OPEN_MISSING_CKM_EXPONENT_DERIVATION"
    assert "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM" in result.open_blockers
