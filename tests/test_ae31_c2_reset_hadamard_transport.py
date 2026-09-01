import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_reset_hadamard_transport import (
    claim_boundary,
    finite_reset_transport_witness,
    reset_hadamard_transport_theorem,
    transport_self_dual_covariance,
)
from scripts.materialize_ae31_c2_reset_hadamard_transport import (
    TARGET,
    build_payload,
    main,
)


def test_nontrivial_reset_transport_preserves_self_dual_pure_covariance():
    result = finite_reset_transport_witness()
    assert result["positivity_and_order_preserved"]
    assert result["self_dual_CAR_constraint_preserved"]
    assert result["purity_preserved"]
    assert result["transport_is_bijective"]
    assert result["event_purity_residual"] < 1.0e-12
    assert result["child_purity_residual"] < 1.0e-12
    assert result["event_conjugation_involution_residual"] < 1.0e-12
    assert result["child_conjugation_involution_residual"] < 1.0e-12
    child = np.asarray(result["covariance_child_real"]) + 1.0j * np.asarray(
        result["covariance_child_imag"]
    )
    assert not np.allclose(child, np.diag([1.0, 0.0, 0.0, 1.0]))


def test_invalid_non_self_dual_covariance_is_rejected():
    identity = np.eye(2, dtype=complex)
    with pytest.raises(ValueError, match="self-dual CAR"):
        transport_self_dual_covariance(
            np.diag([1.0, 1.0]), identity, identity, identity
        )


def test_noninvolutive_CAR_conjugation_is_rejected():
    identity = np.eye(2, dtype=complex)
    noninvolutive = np.asarray([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)
    with pytest.raises(ValueError, match="antiunitary involutions"):
        transport_self_dual_covariance(
            0.5 * identity,
            identity,
            noninvolutive,
            noninvolutive,
        )


def test_reset_theorem_carries_state_without_selecting_it():
    result = reset_hadamard_transport_theorem()
    assert result["quasifree_state_class_transport_bijective"]
    assert result["future_null_covectors_map_to_future_null_covectors"]
    assert result["Hadamard_wavefront_and_polarization_preserved"]
    assert result["commutes_with_frozen_family_projectors"]
    assert result["upstream_Hadamard_particle_state_reaches_child_enclosure"]
    assert result["statement_is_conditional_on_an_upstream_state"]
    assert not result["one_upstream_or_child_state_selected"]
    assert not result["Bogoliubov_particle_number_derived"]


def test_claim_boundary_closes_transport_not_dressed_poles():
    result = claim_boundary()
    assert result["AE2_RESET_HADAMARD_STATE_CLASS_TRANSPORT_DERIVED"]
    assert result[
        "UPSTREAM_HADAMARD_PARTICLE_STATE_CARRIED_INTO_CURRENT_C2_ENCLOSURE"
    ]
    assert result["RESET_TRANSPORT_PRESERVES_FROZEN_FAMILY_IDENTITY"]
    assert not result["RESET_SELECTS_UNIQUE_PHYSICAL_FERMION_STATE"]
    assert not result["CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED"]
    assert not result["MUON_MAGNETIC_MOMENT_DERIVED"]


def test_materialized_reset_hadamard_transport_is_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
