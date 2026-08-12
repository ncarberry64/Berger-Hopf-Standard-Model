import math

import numpy as np

from bhsm.interface.aether_common_quantum_superdeterminant_v15_96 import (
    completion_payload,
    joint_quantum_derivative_contract,
    periodic_proper_laplacian,
    proper_cycle_lattice,
    regulated_superdeterminant_seed,
    scale_force_finite_difference,
)


def test_proper_cycle_lattice_and_periodic_laplacian():
    lattice = proper_cycle_lattice(16)
    operator = periodic_proper_laplacian(16, lattice["proper_step"])
    assert lattice["proper_duration"] > 0.0
    assert np.linalg.norm(operator @ np.ones(16)) < 1.0e-10
    assert np.linalg.eigvalsh(operator)[0] > -1.0e-10


def test_common_regulated_seed_is_finite_and_brist_quotiented():
    result = regulated_superdeterminant_seed(16)
    assert all(math.isfinite(value) for value in result["components"].values())
    assert result["BRST_longitudinal_ghost_net"] == 0.0
    assert result["same_operator_family_for_all_derivatives"]


def test_scale_force_frechet_identity():
    result = scale_force_finite_difference(16)
    assert result["relative_residual"] < 2.0e-7


def test_gauge_and_yukawa_are_derivatives_of_one_quantum_functional():
    result = joint_quantum_derivative_contract()
    assert result["gauge_coefficients"].startswith("K_E,K_B")
    assert "D_Hdagger_D_H_Gamma_q" in result["Higgs_residue"]
    assert "D_barPsi_D_Psi_D_H_Gamma_q" in result["Yukawa_vertex"]
    assert result["independent_gauge_counterterm_allowed"] is False
    assert result["independent_Yukawa_insertion_allowed"] is False


def test_payload_validates_without_overclaiming_saddle():
    result = completion_payload()
    assert result["validation_passed"]
    assert result["claim_boundary"]["common_quantum_operator_formulated"]
    assert result["claim_boundary"]["coupled_quantum_event_saddle_solved"] is False
