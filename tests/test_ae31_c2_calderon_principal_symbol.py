import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_calderon_principal_symbol import (
    claim_boundary,
    conditional_massive_to_principal_limit,
    family_dirac_projectors,
    gauge_brst_characteristic_symbol,
    local_boundary_symbol_theorem,
    reset_equivariance_witness,
    self_dual_principal_covariance,
)
from scripts.materialize_ae31_c2_calderon_principal_symbol import (
    TARGET,
    build_payload,
    main,
)


def test_family_dirac_energy_projectors_and_principal_symbol():
    result = family_dirac_projectors((0.4, -0.7, 1.1), (1.7, 0.1, 0.0005))
    assert result["Hamiltonian_square_residual"] < 1.0e-12
    assert result["positive_Hermitian_residual"] < 1.0e-12
    assert result["positive_idempotence_residual"] < 1.0e-12
    assert result["complement_residual"] < 1.0e-12
    assert result["principal_idempotence_residual"] < 1.0e-12
    assert result["positive_rank"] == 6
    assert result["principal_rank"] == 6
    assert result["family_independent_homogeneous_principal_symbol"]
    with pytest.raises(ValueError, match="nonzero momentum"):
        family_dirac_projectors((0.0, 0.0, 0.0), (1.0,))


def test_self_dual_principal_covariance_is_pure_and_half_rank():
    result = self_dual_principal_covariance((0.4, -0.7, 1.1))
    assert result["Hermitian_residual"] < 1.0e-12
    assert result["purity_residual"] < 1.0e-12
    assert result["self_dual_CAR_residual"] < 1.0e-12
    assert result["rank"] * 2 == result["dimension"]


def test_principal_covariance_intertwines_nontrivial_reset_spin_lift():
    result = reset_equivariance_witness()
    assert result["spin_lift_unitarity_residual"] < 1.0e-12
    assert result["principal_covariance_intertwining_residual"] < 1.0e-12
    assert result["CAR_conjugation_intertwining_residual"] < 1.0e-12
    assert result["family_projectors_preserved"]
    assert result["AE2_reset_equivariant"]


def test_existing_family_masses_are_lower_order_in_the_symbol():
    result = conditional_massive_to_principal_limit()
    differences = np.asarray(result["operator_norm_differences"])
    assert np.all(differences > 0.0)
    assert result["strictly_decreasing"]
    assert not result["mass_changes_homogeneous_principal_symbol"]
    assert not result["measured_mass_used"]


def test_gauge_and_ghost_characteristic_symbols_match_without_repair():
    result = gauge_brst_characteristic_symbol()
    assert result["transverse_projector_rank"] == 2
    assert result["transverse_projector_residual"] < 1.0e-12
    assert result["BRST_characteristic_matching_residual"] < 1.0e-12
    assert not result["one_Maxwell_metric_residue"]
    assert not result["principal_symbol_repairs_residue_mismatch"]


def test_claim_boundary_and_artifact_are_conservative_and_deterministic():
    theorem = local_boundary_symbol_theorem()
    claims = claim_boundary()
    assert theorem["all_admissible_Hadamard_completions_share_spinor_symbol"]
    assert not theorem["physical_outer_projector_constructed"]
    assert claims["CURRENT_C2_SPINOR_HADAMARD_CALDERON_PRINCIPAL_SYMBOL_DERIVED"]
    assert not claims["CURRENT_C2_PHYSICAL_GAUGE_SPINOR_GHOST_CALDERON_PROJECTOR_DERIVED"]
    assert not claims["MUON_MAGNETIC_MOMENT_DERIVED"]
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
