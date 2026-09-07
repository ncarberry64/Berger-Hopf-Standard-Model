import hashlib
from math import pi

import numpy as np
import pytest

from bhsm.interface.ae31_c2_composite_lorentzian_kinetic_pole import (
    chiral_bubble_principal_part,
    claim_boundary,
    clifford_trace_witness,
    combined_composite_hessian_structure,
    current_c2_lorentzian_principal_symbol,
    exact_remaining_owner,
    historical_mass_derivative_adjudication,
)
from scripts.materialize_ae31_c2_composite_lorentzian_kinetic_pole import (
    TARGET,
    build_payload,
    main,
)


def test_one_pair_bubble_has_positive_external_momentum_pole():
    result = chiral_bubble_principal_part()
    assert result["scaleless_tadpoles_in_dimensional_regularization"] == 2
    assert result["one_pair_pole_coefficient_without_epsilon"] == pytest.approx(
        1.0 / (16.0 * pi**2)
    )
    assert not result["finite_part_selected"]
    trace = clifford_trace_witness(
        q=np.asarray((0.7, -1.1, 0.3, 0.9)),
        p=np.asarray((0.2, 0.4, -0.5, 1.3)),
    )
    assert trace["residual"] < 1.0e-13
    assert trace["Euclidean_Clifford_residual"] < 1.0e-13
    with pytest.raises(ValueError):
        clifford_trace_witness(np.ones(3), np.ones(4))


def test_current_c2_symbol_uses_one_lorentzian_residue_and_trace_counts():
    result = current_c2_lorentzian_principal_symbol(
        omega=0.5, spatial_eigenvalue=1.25, epsilon_uv=2.0
    )
    assert result["pairing_multiplicities"] == [9, 9, 3]
    assert result["Lorentzian_covector_square"] == 1.0
    assert result["same_temporal_and_spatial_residue_per_channel"]
    diagonal = np.diag(np.asarray(result["pole_residue_matrix"]))
    assert diagonal[0] == diagonal[1]
    assert diagonal[0] == pytest.approx(3.0 * diagonal[2])
    with pytest.raises(ValueError):
        current_c2_lorentzian_principal_symbol(
            omega=0.0, spatial_eigenvalue=-1.0
        )


def test_pole_does_not_select_the_up_down_direction():
    result = combined_composite_hessian_structure()
    assert result["bare_inverse_curvature_over_G_C2"] == ["5/14", "5/13", "5/3"]
    assert result["derivative_pole_relative_to_up"] == ["1", "1", "1/3"]
    assert result["up_down_derivative_pole_degenerate"]
    assert not result["up_down_bare_curvature_degenerate"]
    assert not result["pole_alone_selects_up_down_direction"]


def test_old_mass_derivative_is_not_relabelled_wavefunction_residue():
    result = historical_mass_derivative_adjudication()
    assert not result["same_functional_derivative"]
    assert not result["historical_numeric_Z_H_promoted_to_current_C2_kinetic_residue"]
    assert not result["historical_gap_branch_revived"]
    assert not result["global_EC_eliminated_action_used"]


def test_claim_boundary_and_artifact_are_conservative_and_deterministic():
    claims = claim_boundary()
    assert claims["CURRENT_C2_COMPOSITE_LORENTZIAN_PRINCIPAL_POLE_DERIVED"]
    assert claims["CURRENT_C2_COMPOSITE_TEMPORAL_SPATIAL_POLE_RESIDUE_MATCH_DERIVED"]
    assert not claims["CURRENT_C2_FINITE_COMPOSITE_KINETIC_RESIDUE_DERIVED"]
    assert not claims["CURRENT_C2_COMPOSITE_GAP_DERIVED"]
    assert not exact_remaining_owner()["cutoff_fitted_residue_or_old_EC_number_allowed"]
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
