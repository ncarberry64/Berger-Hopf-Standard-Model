import hashlib

import pytest

from bhsm.interface.energetically_admissible_encapsulation_carrier_adjudication import (
    admissible_carrier_family,
    available_event_energy_status,
    boundary_operator_package,
    carrier_selection_verdict,
    claim_boundary,
    conservation_firewall,
    energetic_feasibility,
    envelopment_requirement_status,
    multiple_child_status,
    n12_rank_ledger,
    oriented_energy_balance_residual,
    recovered_energy_geometry_candidates,
    response_and_active_differential_status,
    rho_status,
    scale_status,
    stabilizer_spectral_incidence_status,
)
from scripts.materialize_energetically_admissible_encapsulation_carrier_adjudication import (
    TARGET,
    build_payload,
    main,
)


def test_recovered_candidate_ledger_has_requested_metadata_and_fail_closed_energy_sources():
    rows = recovered_energy_geometry_candidates()
    assert len(rows) >= 9
    required = {
        "candidate_id",
        "energy_quantity",
        "geometry_quantity",
        "locality",
        "covariance",
        "relevant_stratum_domain",
        "units",
        "scale_dependence",
        "historical_envelopment_role",
        "current_status",
    }
    assert all(required == set(row) for row in rows)
    by_id = {row["candidate_id"]: row for row in rows}
    assert "INVALIDATED_AS_AVAILABLE_ENERGY" in by_id["N12_LEGENDRE_ENERGY"]["current_status"]
    assert "POSITIVE_AVAILABLE_ENERGY" in by_id["CLOSED_S7_HAMILTONIAN_CONSTRAINT"]["current_status"]
    assert by_id["AE4_IMPEDANCE_CORE_CROSSING"]["current_status"].startswith("OPEN")


def test_available_and_required_energy_are_typed_but_not_invented():
    available = available_event_energy_status()
    requirement = envelopment_requirement_status()
    assert not available["defined"]
    assert available["E_avail_equals_E_mode"] == "NOT_DERIVED"
    assert "mode_projector" in available["missing_map"]
    assert not requirement["defined"]
    assert not requirement["universal_price_per_volume"]
    assert not requirement["global_envelopment_fixture_is_E_envlp"]


def test_owner_feasibility_helper_is_diagnostic_and_rejects_unphysical_inputs():
    assert energetic_feasibility(5.0, 5.0)
    assert not energetic_feasibility(5.0, 5.1)
    assert energetic_feasibility(5.0, 5.1, compensating_source=0.1)
    for bad in (-1.0, float("inf"), float("nan")):
        with pytest.raises(ValueError):
            energetic_feasibility(bad, 1.0)


def test_oriented_balance_accounts_for_seam_flux_and_separate_children():
    residual = oriented_energy_balance_residual(
        10.0,
        4.0,
        1.0,
        additional_children=(2.0, 1.0),
        outward_flux=2.0,
    )
    assert residual == pytest.approx(0.0)
    firewall = conservation_firewall()
    assert not firewall["reset_may_supply_missing_energy"]
    assert firewall["independent_energy_bearing_actualization"] == "SEPARATE_CHILD_CANDIDATE"
    assert len(firewall["scalar_form_conditions"]) == 4


def test_rho_and_scale_classifications_do_not_insert_a_threshold():
    rho = rho_status()
    scale = scale_status()
    assert rho["classification"] == "RHO5"
    assert not rho["privileged_scalar_derived"]
    assert rho["regime_audit"]["C_A"] == "ORDINARY_ENERGY_NOT_EVALUATED_ON_THE_SINGULAR_STRATUM"
    assert rho["closest_recovered_hypothesis"]["promotion"] == "NOT_EVALUATED_OR_ACTION_DERIVED"
    assert not scale["manual_Planck_threshold_inserted"]
    assert "2.0232708255441265" in scale["R_star_relation"]
    assert any(row["trigger"] == "lambda_phys=0" for row in scale["candidate_triggers"])


def test_local_CARR1_scope_does_not_promote_full_CARR5_carrier():
    family = admissible_carrier_family()
    selection = carrier_selection_verdict()
    local = family["local_AE3_subsystem_carrier"]
    assert local["surface"] == "Sigma_enc={sigma=0}"
    assert local["classification"].startswith("CARR1")
    assert not local["terminal_reset_boundary"]
    assert not local["energy_selected"]
    assert family["full_event_to_child_carrier"]["classification"] == "CARR5"
    assert selection["full_classification"] == "CARR5"
    assert not selection["saturation_derived"]
    assert not selection["first_positive_return_selects_geometry"]
    assert "integrable E_avail" in selection["exact_blocking_map"]


def test_multiple_child_boundary_and_representation_packages_fail_closed():
    branching = multiple_child_status()
    package = boundary_operator_package()
    symmetry = stabilizer_spectral_incidence_status()
    response = response_and_active_differential_status()
    assert not branching["action_owned_branching_dynamics"]
    assert not branching["one_child_with_internal_modes_is_multiple_children"]
    assert not package["AE3_local_partial_package"]["six_sector_closure"]
    assert package["physical_Calderon_or_DtN_operators"] == "NOT_INSTANTIATED"
    assert symmetry["spectral_projectors"] == "OPEN"
    assert symmetry["event_to_child_incidence"] == "OPEN_AT_FULL_PHYSICAL_LEVEL"
    assert response["response_classification"] == "RSP5"
    assert not response["F_B_selected"]


def test_n12_rank_and_claim_boundaries_remain_conservative():
    ledger = n12_rank_ledger()
    boundary = claim_boundary()
    assert ledger["actual_new_rank"] == 0
    assert ledger["residual_before_time_quotient"] == 67
    assert ledger["residual_after_time_quotient"] == 66
    assert all(row["independent_rank"] == 0 for row in ledger["rows"])
    assert boundary["AE3_SIGMA_ZERO_LOCAL_MATERIAL_CARRIER_ACTION_OWNED"]
    assert not boundary["AE3_SIGMA_ZERO_IS_TERMINAL_RESET_BOUNDARY"]
    assert not boundary["ENCAPSULATION_RESPONSE_FUNCTION_SELECTED"]
    assert not boundary["FROZEN_PREDICTIONS_MODIFIED"]
    assert not boundary["GATE7_PROMOTED"]
    assert not boundary["FULL_BHSM_COMPLETE"]


def test_materialized_artifact_is_valid_and_byte_deterministic():
    payload = build_payload()
    assert payload["validation_passed"]
    assert all(payload["validation"].values())
    assert payload["AE3_local_regular_carrier_certificate"]["regular_level_set"]
    assert len(payload["source_hashes_sha256"]) >= 15
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
