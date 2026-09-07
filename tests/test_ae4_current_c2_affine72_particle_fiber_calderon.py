import hashlib

import numpy as np
import pytest

from bhsm.interface.ae4_current_c2_affine72_particle_fiber_calderon import (
    attach_preserved_particle_fibers,
    claim_boundary,
    product_dirac_friedrichs_weyl_first_jet,
)
from scripts.materialize_ae4_current_c2_affine72_particle_fiber_calderon import (
    TARGET,
    build_payload,
    main,
)


def _carrier(parameter_count=2):
    return {
        "log_radii": np.asarray((0.0, 0.01, 0.02)),
        "normalized_proper_times": np.asarray((0.0, 0.4, 1.0)),
        "proper_duration": 0.2,
        "log_radius_first_jet": np.ones((3, parameter_count)) * 0.01,
        "proper_duration_first_jet": np.linspace(0.01, 0.02, parameter_count),
    }


def _fiber_rows():
    labels = {
        "charged_lepton": ((0, 0), (5, 2), (9, 3)),
        "up": ((0, 0), (6, 0), (10, 1)),
        "down": ((0, 0), (6, 3), (8, 2)),
    }
    return [
        {
            "sector": sector,
            "slot": slot,
            "mode_label": list(label),
            "projector_rank": 1,
            "parent_stop_event_child_enclosure_child_transport": (
                "PRESERVED_ON_THE_C2_FIBER"
            ),
        }
        for sector, modes in labels.items()
        for slot, label in enumerate(modes)
    ]


def test_product_dirac_first_jet_keeps_spatial_level_separate_from_mass():
    result = product_dirac_friedrichs_weyl_first_jet(
        **_carrier(), spatial_dirac_level=0, chirality=1
    )
    assert result["unit_radius_dirac_eigenvalue_mu_n"] == 1.5
    assert result["D_parameter_Weyl"].shape == (2,)
    assert np.allclose(
        result["D_parameter_Weyl"],
        result["D_parameter_Weyl_radius_part"]
        + result["D_parameter_Weyl_duration_part"],
    )
    assert not result["internal_Berger_family_mode_used_as_spatial_level"]
    assert not result["raw_Dirac_level_identified_as_physical_mass"]


def test_all_existing_fibers_attach_to_one_common_spatial_carrier():
    result = attach_preserved_particle_fibers(
        **_carrier(), frozen_fiber_rows=_fiber_rows(), spatial_dirac_level=0
    )
    assert result["attached_fiber_count"] == 9
    assert result[
        "carrier_response_is_family_central_before_existing_internal_operators"
    ]
    assert not result["index_separation"]["indices_identified_with_each_other"]
    assert not result["particle_spectrum_rebuilt"]
    with pytest.raises(ValueError):
        attach_preserved_particle_fibers(
            **_carrier(), frozen_fiber_rows=_fiber_rows()[:-1]
        )


def test_claim_boundary_is_affine_and_fail_closed():
    boundary = claim_boundary()
    assert boundary[
        "AE4_CURRENT_C2_AFFINE72_PRODUCT_DIRAC_CARRIER_FIRST_JET_EVALUATED"
    ]
    assert boundary[
        "ALL_NINE_EXISTING_CHARGED_PARTICLE_FIBERS_ATTACHED_TO_CARRIER"
    ]
    assert not boundary[
        "AE4_CURRENT_C2_NONLINEAR72_PARTICLE_FIBER_CALDERON_DERIVED"
    ]
    assert not boundary["CURRENT_C2_PHYSICAL_MASS_OPERATOR_DERIVED"]


def test_materialized_particle_fiber_attachment_is_valid_and_deterministic():
    payload = build_payload()
    assert payload["validation_passed"]
    assert payload["scientific_result"]["attached_existing_fiber_count"] == 9
    assert payload["validation"]["internal_and_spatial_mode_indices_not_conflated"]
    assert payload["validation"]["moving_stop_duration_contribution_retained"]
    assert not payload["carrier"]["nonlinear_exact_family_authority"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
