import hashlib
from math import pi, sqrt

from bhsm.interface.ae31_c2_r2_electron_capture_selection_rule import (
    capture_vertex_and_hessian_gate,
    claim_boundary,
    electron_metric_incidence_contract,
    normalized_s3_rank2_witness,
    recovered_r2_provenance,
    scientific_decision,
)
from scripts.materialize_ae31_c2_r2_electron_capture_selection_rule import (
    TARGET,
    build_payload,
    main,
)


def test_exact_s3_rank2_selection_rule():
    result = normalized_s3_rank2_witness()
    assert abs(result["rank2_normalization"] - sqrt(3.0) / pi) < 1.0e-15
    assert result["diagonal_Gaunt_000_to_2"] == 0.0
    assert abs(result["off_diagonal_Gaunt_0_2_2"] - 1.0 / (pi * sqrt(2.0))) < 1.0e-15
    assert result["rank0_to_rank2_mixing_allowed"]


def test_historical_r2_is_not_relabelled_as_capture_orbital():
    result = recovered_r2_provenance()
    assert result["current_stationary_branch_Delta_A"] == "ZERO"
    assert result["current_stationary_branch_shear_operator"] == "ZERO"
    assert not result["r2_is_a_capturable_electron_state_derived"]


def test_metric_incidence_is_owned_but_intertwiner_is_missing():
    result = electron_metric_incidence_contract()
    assert not result["new_electron_shear_coefficient_required"]
    assert not result["historical_full_preimage_H2_to_current_M4_metric_intertwiner_derived"]
    assert not result["therefore_current_C2_numeric_mixed_block_derived"]


def test_capture_current_is_structural_while_composite_blocks_remain_open():
    gate = capture_vertex_and_hessian_gate()
    decision = scientific_decision()
    boundary = claim_boundary()
    assert gate["leptonic_weak_representation_attached"]
    assert gate["quark_weak_representation_attached"]
    assert not gate["physical_hadronic_weak_matrix_element_derived"]
    assert not gate["capture_Hessian_derived"]
    assert decision["r2_may_dress_a_capture_state"]
    assert not decision["r2_may_be_renamed_the_capture_orbital"]
    assert boundary[
        "CURRENT_C2_ELL2_ISOTROPIC_LOWEST_TRACE_SELECTION_RULE_DERIVED"
    ]
    assert not boundary["CURRENT_C2_FULL_LOWEST_SPINOR_ELL2_BLOCK_DERIVED"]
    assert not boundary["CURRENT_C2_OUTGOING_NEUTRINO_BOUNDARY_MODE_DERIVED"]


def test_artifact_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
