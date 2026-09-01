import hashlib

import pytest

from bhsm.interface.ae31_c2_quark_vertex_contact_projection import (
    abstract_sector_projection,
    claim_boundary,
    descriptor_channel_incidence,
    exact_missing_incidence_map,
    projection_nonidentifiability_theorem,
    unit_probe_scaling_theorem,
)
from scripts.materialize_ae31_c2_quark_vertex_contact_projection import (
    TARGET,
    build_payload,
    main,
)


def test_unit_probe_vertex_and_contact_scaling_is_exact():
    theorem = unit_probe_scaling_theorem()
    assert theorem["scaling_verified"]
    assert theorem["vertex_scaling_residual"] < 1.0e-14
    assert theorem["contact_scaling_residual"] < 1.0e-14
    assert not theorem["q_selected_by_unit_probe_derivation"]


def test_descriptor_chirality_is_not_up_down_incidence():
    incidence = descriptor_channel_incidence(
        [
            "product_Dirac_lambda1_5_chirality_plus__K_diagonal",
            "product_Dirac_lambda1_5_chirality_minus__K_diagonal",
        ]
    )
    assert incidence["chirality_plus_present"]
    assert incidence["chirality_minus_present"]
    assert not incidence["explicit_up_down_sector_axis_present"]
    assert not incidence["descriptor_can_distinguish_up_from_down"]


def test_nonfinite_sector_coefficient_fails_closed():
    with pytest.raises(ValueError):
        abstract_sector_projection(q_up=float("nan"), q_down=1.0)


def test_sector_projectors_split_support_but_not_coefficients():
    theorem = projection_nonidentifiability_theorem()
    assert theorem["both_obey_same_projector_algebra"]
    assert theorem["same_structural_projection_different_residue_ratio"]
    assert theorem["representation_projectors_select_block_support"]
    assert not theorem["representation_projectors_select_block_coefficients"]


def test_missing_incidence_map_forbids_unit_or_fitted_substitution():
    missing = exact_missing_incidence_map()
    assert missing["existing_projectors_and_family_operators_reused"]
    assert not missing["unit_probe_may_be_declared_both_sector_coefficients"]
    assert not missing["independent_q_up_q_down_allowed"]
    assert not missing["quark_mass_fit_allowed"]


def test_claim_boundary_promotes_only_structural_projection():
    boundary = claim_boundary()
    assert boundary["CURRENT_C2_UNIT_PRODUCT_DIRAC_SOURCE_SCALING_DERIVED"]
    assert boundary["CURRENT_C2_QUARK_VERTEX_CONTACT_BLOCK_PROJECTION_STRUCTURALLY_DEFINED"]
    assert not boundary["CURRENT_C2_PRODUCT_DIRAC_DESCRIPTOR_UP_DOWN_INCIDENCE_PRESENT"]
    assert not boundary["CURRENT_C2_QUARK_VERTEX_CONTACT_COEFFICIENTS_ACTION_DERIVED"]
    assert not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]


def test_materialized_vertex_projection_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
