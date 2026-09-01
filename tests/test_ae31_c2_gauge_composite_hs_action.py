import hashlib

import pytest

from bhsm.interface.ae31_c2_gauge_composite_hs_action import (
    action_owned_gauge_hs_contract,
    claim_boundary,
    current_c2_domain_and_trace_transport,
    exact_hs_completion_witness,
    exact_inverse_coefficients,
    intrinsic_higgs_mixing_boundary,
    odd_composite_endomorphism_attachment,
)
from scripts.materialize_ae31_c2_gauge_composite_hs_action import (
    TARGET,
    build_payload,
    main,
)


def test_exact_hs_completion_closes_without_new_coefficient():
    result = exact_hs_completion_witness(1.7)
    assert result["completion_residual"] < 1.0e-12
    assert result["stationary_residual"] < 1.0e-12
    with pytest.raises(ValueError):
        exact_hs_completion_witness(0.0)
    contract = action_owned_gauge_hs_contract()
    assert contract["bare_LR_vertices"] == {"up": 1.0, "down": 1.0}
    assert not contract["new_continuous_coefficient"]
    assert not contract["new_elementary_scalar"]


def test_inverse_coefficients_are_exact():
    result = exact_inverse_coefficients()
    assert result == {
        "up": "5/14",
        "down": "5/13",
        "up_minus_down": "-5/182",
        "mean": "135/364",
        "sigma3": "-5/364",
    }


def test_composite_attachment_is_odd_and_preserves_current_c2_domain():
    result = odd_composite_endomorphism_attachment()
    assert result["grading_residuals"] == {"up": 0.0, "down": 0.0}
    assert result["supports_disjoint"]
    assert result["composite_HS_odd_endomorphism_action_owned_by_rewrite"]
    assert not result["intrinsic_Higgs_odd_endomorphism_action_owned"]
    domain = current_c2_domain_and_trace_transport()
    assert domain["reset_generated_C2_domain_preserved"]
    assert domain["retained_birth_trace_preserved"]
    assert not domain["Einstein_Cartan_global_kernel_used"]


def test_intrinsic_mixing_and_physical_promotions_remain_open():
    boundary = intrinsic_higgs_mixing_boundary()
    assert not boundary["auxiliary_derivative_kinetic_term_at_bare_level"]
    assert not boundary["M_HS_action_derived"]
    assert not boundary["auxiliary_field_is_physical_Higgs"]
    claims = claim_boundary()
    assert claims["CURRENT_C2_GAUGE_COMPOSITE_HS_REWRITE_DERIVED"]
    assert claims["CURRENT_C2_COMPOSITE_ODD_ENDOMORPHISM_ACTION_OWNED"]
    assert not claims["CURRENT_C2_INTRINSIC_HIGGS_ODD_ENDOMORPHISM_ACTION_OWNED"]
    assert not claims["CURRENT_C2_CANONICAL_QUARK_YUKAWA_RESIDUES_DERIVED"]


def test_materialized_gauge_composite_action_is_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
