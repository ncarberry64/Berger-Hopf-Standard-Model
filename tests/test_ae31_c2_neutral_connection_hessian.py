import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_neutral_connection_hessian import (
    ACTION_VERSION,
    claim_boundary,
    higgs_neutral_charge_ledger,
    lorentzian_photon_promotion_gate,
    neutral_connection_hessian,
    neutral_field_current_rotation,
)
from scripts.materialize_ae31_c2_neutral_connection_hessian import (
    TARGET,
    build_payload,
    main,
)


def test_higgs_vacuum_selects_qem_without_gauge_inputs():
    result = higgs_neutral_charge_ledger()
    assert ACTION_VERSION == "BHSM-AE-3.1.0"
    assert result["T3_on_vacuum"] == -0.5
    assert result["Y_BH_on_vacuum"] == 0.5
    assert result["Q_em_on_vacuum"] == 0.0
    assert not result["independent_g2_or_g1_inserted"]


def test_neutral_connection_hessian_has_one_exact_null_direction():
    result = neutral_connection_hessian()
    assert result["rank"] == 1
    assert result["nullity"] == 1
    assert result["Q_em_null_residual_exact"] == 0.0
    assert result["Q_em_null_residual_floating"] < 2.0e-12
    assert result["unique_neutral_null_direction"]
    assert result["broken_curvature_positive"]
    assert not result["measured_Higgs_VEV_used"]
    assert not result["canonically_normalized_physical_field_result"]


def test_neutral_hessian_rejects_invalid_saddle():
    with pytest.raises(ValueError):
        neutral_connection_hessian(0.0)
    with pytest.raises(ValueError):
        neutral_connection_hessian(np.nan)


def test_fields_and_currents_rotate_together_in_connection_coordinates():
    result = neutral_field_current_rotation()
    assert result["orthogonal_coordinate_transform"]
    assert result["same_current_C2_source_domain"]
    assert result["Q_em_current"] == "J_Q proportional_to J3+JY"
    assert not result["canonical_kinetic_rotation_claimed"]
    assert not result["Weinberg_angle_derived"]


def test_lorentzian_residue_mismatch_still_blocks_physical_photon():
    result = lorentzian_photon_promotion_gate()
    assert result["neutral_Higgs_curvature_null_direction_derived"]
    assert not result["single_Lorentzian_Maxwell_residue_available"]
    assert not result["physical_transverse_A_Q_pole_derived"]
    assert not result["physical_photon_promoted"]


def test_claim_boundary_promotes_structure_not_physical_photon():
    result = claim_boundary()
    assert result["CURRENT_C2_NEUTRAL_CONNECTION_HESSIAN_DERIVED"]
    assert result["CURRENT_C2_UNIQUE_QEM_CONNECTION_NULL_DIRECTION_DERIVED"]
    assert result["CURRENT_C2_STRUCTURAL_JQ_CURRENT_DERIVED"]
    assert not result["CURRENT_C2_CANONICAL_WEINBERG_ROTATION_DERIVED"]
    assert not result["CURRENT_C2_PHYSICAL_PHOTON_DERIVED"]
    assert not result["MUON_MAGNETIC_MOMENT_DERIVED"]


def test_materialized_neutral_hessian_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
