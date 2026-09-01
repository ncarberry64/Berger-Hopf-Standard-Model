import hashlib
import math

import pytest

from bhsm.interface.ae31_c2_v1566_dynamic_dtn_recovery import (
    claim_boundary,
    exact_round_cap_residue,
    round_cap_frequency_dtn,
    v1566_current_c2_recovery_classification,
)
from scripts.materialize_ae31_c2_v1566_dynamic_dtn_recovery import (
    TARGET,
    build_payload,
    main,
)


def test_static_round_cap_dtn_is_recovered():
    assert abs(round_cap_frequency_dtn(2) - 2.0) < 2.0e-8
    with pytest.raises(ValueError):
        round_cap_frequency_dtn(1)


def test_exact_continuous_frequency_residue_fails_maxwell_equality():
    result = exact_round_cap_residue(2)
    assert result["exact_electric_formula_residual"] < 1.0e-13
    assert result["exact_ratio_formula_residual"] < 1.0e-13
    assert abs(
        result["temporal_to_spatial_residue_ratio"]
        - (6.0 - 8.0 * math.log(2.0))
    ) < 1.0e-13
    assert abs(
        result["centered_difference_derivative"]
        + result["minus_d_DtN_d_q_squared_exact"]
    ) < 2.0e-7
    assert not result["one_Lorentzian_Maxwell_residue"]


def test_recovered_predecessor_is_reusable_but_not_additive_repair():
    result = v1566_current_c2_recovery_classification()
    assert len(result["reusable_upstream_assets"]) == 4
    assert not result["round_cap_dynamic_Maxwell_residue"]
    assert not result["same_geometry_as_current_AE3_weighted_reciprocal_profile"]
    assert not result["may_be_added_to_current_AE3_trace_without_double_counting"]
    assert not result["v1566_supplies_missing_noncommon_current_C2_correction"]
    assert result["v1569_common_parent_subtraction_still_required"]


def test_claim_boundary_keeps_photon_and_muon_open():
    result = claim_boundary()
    assert result["V1566_ROUND_CAP_CONTINUOUS_FREQUENCY_DTN_DERIVED"]
    assert result["V1566_STATIC_FULL_GAUGE_KERNEL_PROVENANCE_REUSABLE"]
    assert not result["V1566_ADDITIVE_CURRENT_C2_BOUNDARY_CORRECTION_AUTHORIZED"]
    assert not result["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]
    assert not result["MUON_MAGNETIC_MOMENT_DERIVED"]


def test_artifact_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
