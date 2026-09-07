import hashlib
import json
import math

import pytest

from bhsm.interface.fsc_encapsulation_constitutive_adjudication import (
    EFFECTIVE_MAP_CLASS,
    EM_CLASS,
    EXACT_NEXT_OBJECT,
    GEOMETRIC_CLASS,
    INTERFACE_CLASS,
    LOOP_CLASS,
    PREGEOMETRIC_CLASS,
    PRIMITIVE_CLASS,
    RSP_CLASS,
    SCALE_CLASS,
    adjudication_payload,
    allowed_fsc_power_ledger,
    alpha_from_canonical_g,
    canonical_g_from_alpha,
    canonical_yang_mills_prefactor,
    channel_weight_ledger,
    claim_firewall,
    closure_status,
    constitutive_closure_test,
    effective_coupling_map,
    electromagnetic_proof_of_concept,
    energy_spacetime_ratio_adjudication,
    first_variation_and_rank_status,
    frozen_prediction_cross_check,
    fsc_historical_lineage,
    geometric_pregeometric_result,
    interface_invariant_coefficient_ledger,
    perturbative_hierarchy_adjudication,
    primitive_coupling_definition,
    scale_running_adjudication,
    weak_and_strong_result,
)
from scripts.materialize_fsc_encapsulation_constitutive_adjudication import (
    TARGET,
    build_payload,
    deterministic_json,
    main,
)


def test_lineage_separates_every_authority_level_and_superseded_routes():
    rows = fsc_historical_lineage()
    by_id = {row["id"]: row for row in rows}
    assert {row["classification"] for row in rows} >= {
        "FSC-P3", "FSC-P2", "FSC-P1", "FSC-P0", "SUPERSEDED"
    }
    assert by_id["HISTORICAL_XI_GEOM"]["classification"] == "FSC-P2"
    assert by_id["HISTORICAL_XI_COUPLING_MAP"]["classification"] == "SUPERSEDED"
    assert by_id["HISTORICAL_LOW_ENERGY_DRESSING_FIT"]["classification"] == "SUPERSEDED"
    assert by_id["WEYL_3D_DENSITY"]["classification"] == "FSC-P3"
    assert by_id["WEYL_3D_DENSITY"]["disposition"] == "MATHEMATICAL_DENSITY_IDENTITY_ONLY"
    assert by_id["GAUGE_127_REGISTRY_SCREEN"]["classification"] == "FSC-P2"
    assert by_id["CURRENT_FSC_YARDSTICK"]["classification"] == PRIMITIVE_CLASS == "FSC-P1"
    assert not by_id["CURRENT_FSC_YARDSTICK"]["action_derived"]


def test_primitive_is_symbolic_and_empirical_low_energy_value_is_downstream_only():
    result = primitive_coupling_definition()
    assert result["primitive"] == "alpha_FSC"
    assert result["classification"] == PRIMITIVE_CLASS
    assert result["owner_approximation"] == "alpha_FSC approximately 1/137"
    assert not result["exact_numeric_value_selected"]
    assert not result["reference_scale_selected"]
    assert not result["renormalization_scheme_selected"]
    assert result["observed_value_role"] == "downstream comparison only"
    assert "1/(12*pi^2)" in result["not_the_primitive"]


def test_canonical_alpha_g_conversion_and_inverse_kinetic_power_are_exact():
    for alpha in (1 / 137, 0.01, 0.1):
        g = canonical_g_from_alpha(alpha)
        assert alpha_from_canonical_g(g) == pytest.approx(alpha, rel=1e-15)
        assert canonical_yang_mills_prefactor(alpha) == pytest.approx(1 / (4 * g * g), rel=1e-15)
        assert canonical_yang_mills_prefactor(alpha) == pytest.approx(1 / (16 * math.pi * alpha), rel=1e-15)
    for invalid in (0.0, -1.0):
        with pytest.raises(ValueError):
            canonical_g_from_alpha(invalid)
        with pytest.raises(ValueError):
            canonical_yang_mills_prefactor(invalid)
        with pytest.raises(ValueError):
            alpha_from_canonical_g(invalid)


def test_weights_preserve_conditional_trace_ratio_and_quarantine_127():
    rows = {row["channel"]: row for row in channel_weight_ledger()}
    assert rows["electromagnetic/U1-like"]["classification"] == "W1"
    assert rows["weak"]["classification"] == "W1"
    assert rows["strong/color"]["classification"] == "W1"
    assert rows["weak"]["weight"].startswith("5/3")
    assert rows["strong/color"]["weight"].startswith("5/3")
    assert rows["weak"]["historical_alternative"].startswith("2 from 1:2:7 is W3")
    assert rows["strong/color"]["historical_alternative"].startswith("7 from 1:2:7 is W3")
    assert all(
        rows[channel]["classification"] == "W4" and rows[channel]["weight"] is None
        for channel in ("scalar/topographic", "geometric/gravitational", "pregeometric/emergent")
    )
    assert not any(row["selected_physical_weight"] for row in rows.values())


def test_linear_effective_map_is_not_derived_and_arbitrary_response_remains():
    result = effective_coupling_map()
    assert result["classification"] == EFFECTIVE_MAP_CLASS == "GEFF5"
    assert result["unique_map"] is None
    assert result["linear_candidate"] == "alpha_eff^(r)=alpha_FSC*W_r"
    assert not result["linear_candidate_justified"]
    assert "R_r(" in result["most_specific_current_form"]
    assert "arbitrary" in result["R_r_status"]


def test_scale_running_does_not_promote_the_sm_comparison_scaffold():
    result = scale_running_adjudication()
    assert result["classification"] == SCALE_CLASS == "SCALE4"
    assert not result["interface_running_law_owned"]
    assert not result["event_scale_map_owned"]
    assert result["conditional_SM_subledger"]["shape"] == "SCALE2_LIKE_COMPARISON_SCAFFOLD"
    assert result["conditional_SM_subledger"]["formula_implemented"]
    assert not result["conditional_SM_subledger"]["may_be_used_as_interface_running"]


def test_power_ledger_blocks_a_universal_linear_alpha_action_claim():
    rows = {str(row["power"]): row for row in allowed_fsc_power_ledger()}
    assert {"-2", "-1", "0", "1/2", "1", "2", "other/nonpolynomial"} == set(rows)
    assert "Yang-Mills kinetic" in rows["-1"]["role"]
    assert "vertex" in rows["1/2"]["role"]
    assert rows["1"]["status"].endswith("ACTION_ATTACHMENT_OPEN")
    assert rows["-2"]["status"] == "NOT_SELECTED_FOR_ANY_INTERFACE_TERM"


def test_every_prior_invariant_family_has_no_new_fsc_coefficient():
    rows = interface_invariant_coefficient_ledger()
    by_family = {row["family"]: row for row in rows}
    assert len(rows) == 12
    assert all(row["fsc_power"] is None for row in rows)
    assert all(row["channel_weight"] is None for row in rows)
    assert all(not row["coefficient_selected"] for row in rows)
    assert by_family["owned_GHY_Hayward"]["fsc_status"].startswith("REDUNDANT")
    assert by_family["extrinsic_curvature_or_second_jet"]["fsc_status"].startswith("EXCLUDED")
    assert "TOPOLOGICALLY_QUANTIZED" in by_family["topological_holonomy"]["fsc_status"]


def test_fsc_factorization_is_bijective_bookkeeping_not_constitutive_closure():
    result = constitutive_closure_test()
    assert result["classification"] == INTERFACE_CLASS == "FSC-IF5"
    assert result["selected_interface_density"] is None
    assert result["selected_coefficients"] == 0
    assert result["selected_functions"] == 0
    assert not result["infinite_dimensional_freedom_removed"]
    assert not result["factorization_has_decision_power"]
    assert "bijective" in result["reason"]


def test_em_weak_strong_and_geometric_results_do_not_force_fsc_universality():
    em = electromagnetic_proof_of_concept()
    gauge = weak_and_strong_result()
    geo = geometric_pregeometric_result()
    assert em["classification"] == EM_CLASS == "EM-FSC3"
    assert not em["exact_strength_at_interface_scale_fixed"]
    assert not em["tensor_operator_shape_fixed"]
    assert not em["complete_first_order_response"]
    assert gauge["weak"]["result"] == "NO_UNIQUE_ALPHA_FSC_TIMES_WEIGHT_COUPLING"
    assert gauge["strong"]["result"] == "NO_UNIQUE_ALPHA_FSC_TIMES_WEIGHT_COUPLING"
    assert not gauge["standard_model_running_overwritten"]
    assert geo["geometric_classification"] == GEOMETRIC_CLASS == "GEO-FSC3"
    assert geo["pregeometric_classification"] == PREGEOMETRIC_CLASS == "GEO-FSC4"
    assert geo["derived_geometric_channel_factor"] is None
    assert not geo["forced_universality"]


def test_fsc_does_not_define_rho_or_a_global_perturbation_series():
    rho = energy_spacetime_ratio_adjudication()
    perturbative = perturbative_hierarchy_adjudication()
    assert not rho["multiplication_derived"]
    assert not rho["rho_E/ST_defined_by_FSC"]
    assert not rho["rho_E/ST_dimensionless_after_FSC"]
    assert rho["selected_control"] is None
    assert not perturbative["global_expansion_valid"]
    assert not perturbative["small_parameter_at_relevant_scale_proved"]
    assert perturbative["asymptotic_or_convergent"] is None
    assert perturbative["first_nonzero_allowed_order"] is None


def test_no_variation_rank_cycle_or_physical_interface_object_is_fabricated():
    variation = first_variation_and_rank_status()
    closure = closure_status()
    assert not variation["finite_density_fixed"]
    assert variation["delta_S_enc_explicit"] is None
    assert variation["Delta_enc"] is None
    assert variation["N12_rank_added"] == 0
    assert variation["N12_residual_before_time_quotient"] == 67
    assert variation["N12_residual_after_time_quotient"] == 66
    assert variation["loop"] == LOOP_CLASS == "LOOP3"
    assert variation["RSP"] == RSP_CLASS == "RSP5"
    assert not variation["cycle_rerun"]
    assert all(
        closure[key] is None
        for key in ("selected_S_enc", "selected_carrier", "selected_F_B", "selected_L_s", "selected_Delta_enc")
    )
    assert closure["owner_question"] is None
    assert closure["exact_next_object"] == EXACT_NEXT_OBJECT


def test_frozen_and_claim_firewalls_are_complete_and_false():
    assert not any(frozen_prediction_cross_check().values())
    assert not any(claim_firewall().values())


def test_integrated_payload_and_artifact_are_valid_and_byte_deterministic():
    adjudication = adjudication_payload()
    assert adjudication["constitutive_closure"]["classification"] == "FSC-IF5"
    first = build_payload()
    second = build_payload()
    assert first["validation_passed"]
    assert all(first["validation"].values())
    assert deterministic_json(first) == deterministic_json(second)

    main()
    first_hash = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second_hash = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first_hash == second_hash
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert stored["classification"]["interface"] == "FSC-IF5"
    assert stored["classification"]["effective_map"] == "GEFF5"
    assert stored["validation_passed"]
