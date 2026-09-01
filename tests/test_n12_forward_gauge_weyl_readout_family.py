from scripts.derive_n12_forward_gauge_weyl_readout_family import build_payload


def test_forward_resolvent_spectral_family_is_action_owned() -> None:
    payload = build_payload()
    family = payload["operator_family"]
    assert payload["validation_passed"] is True
    assert family["resolvent_pencil"] == "P_C^D-z*I"
    assert family["resolvent"] == "R_C^D(z)=(P_C^D-z*I)^(-1)"
    assert family["physical_resolvent"] == "R_C(z)=(K_C-z*I)^(-1)"
    assert family["physical_spectral_measure"] == "dE_C(lambda)"
    assert family["Dirichlet_reference_operator"] == "P_C^D"
    assert family["spectral_parameter"] == "z_IN_THE_RESOLVENT_SET_OF_P_C^D"
    assert family["z_identified_with_momentum_squared"] is False
    assert family["temporal_Fourier_mode_used"] is False
    assert family["periodic_cycle_restored"] is False


def test_exact_weyl_derivative_identity_closes() -> None:
    payload = build_payload()
    witness = payload["exact_discrete_witness"]
    assert witness["Weyl_value"]["exact"] == "11/4"
    assert witness["Weyl_derivative"]["exact"] == "-17/16"
    assert witness["Poisson_extension_norm_squared"]["exact"] == "17/16"
    assert witness["derivative_identity_exact"] is True


def test_exact_geometry_variation_compresses_the_exterior_force() -> None:
    payload = build_payload()
    witness = payload["exact_geometry_variation_witness"]
    oracle = payload["exterior_oracle_bundle"]
    assert witness["direct_Weyl_geometry_derivative"]["exact"] == "1707/6160"
    assert witness["Poisson_contraction"]["exact"] == "1707/6160"
    assert witness["variation_identity_exact"] is True
    assert oracle["full_pointwise_exterior_history_logically_required"] is False
    assert "D_Phi_M_C" in oracle["zero_source_force_dependency"]


def test_operator_readout_is_defined_without_fabricating_scalar_coupling() -> None:
    payload = build_payload()
    readout = payload["gauge_readout"]
    boundary = payload["claim_boundary"]
    assert readout["inherited_p2_contract_retired"] is True
    assert readout["z_to_p2_map_derived"] is False
    assert readout["single_physical_scalar_evaluated"] is False
    assert boundary["forward_resolvent_spectral_family"] == "DERIVED"
    assert boundary["forward_p2_operator_family"] == "RETIRED_NOT_CONSTRUCTED"
    assert boundary["forward_exterior_Weyl_value"] == "OPEN"
    assert boundary["physical_scalar_gauge_couplings"] == "OPEN"


def test_all_maximal_endpoint_classes_and_gate_locks_are_preserved() -> None:
    payload = build_payload()
    endpoints = payload["endpoint_compatibility"]
    assert endpoints["terminal_reachability_required_to_define_family"] is False
    assert "FRIEDRICHS" in endpoints["infinite_history"]
    assert "FRIEDRICHS" in endpoints["finite_excluded_exit"]
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE_NOT_CLOSED"
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["chord_03_authorized"] is False
