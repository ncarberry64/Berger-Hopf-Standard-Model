import importlib.util
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.universal_precision_form_factor import project_electromagnetic_form_factors
from bhsm.interface.ae31_c2_local_em_ward_identity import pauli_transversality_witness, local_ward_identity_witness

spec = importlib.util.spec_from_file_location("pauli_audit", Path(__file__).parents[1] / "audits/muon_pauli_sufficient_readout.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
readout = module.pauli_readout


def test_reduced_projection_agrees_with_existing_complex_vertex_solver():
    rng = np.random.default_rng(417)
    for _ in range(20):
        d, p, v = rng.normal(size=(3, 20)) + 1j * rng.normal(size=(3, 20))
        reduced = readout(v, d, p)
        existing = project_electromagnetic_form_factors(v, d, p, q_squared=-0.2)
        assert reduced['F2'] == pytest.approx(existing.F2, abs=1e-13)
        assert reduced['F1'] == pytest.approx(existing.F1, abs=1e-13)
        assert reduced['relative_remainder'] == pytest.approx(existing.relative_projection_residual)


def test_dirac_changes_do_not_change_pauli_coefficient_but_remainder_is_retained():
    d = np.array([1, 0, 0], dtype=complex)
    p = np.array([2j, 1, 0], dtype=complex)
    a = readout(d + 0.003 * p, d, p)
    b = readout(7 * d + 0.003 * p + np.array([0, 0, 5]), d, p)
    assert a['F2'] == pytest.approx(b['F2'])
    assert a['relative_remainder'] < 1e-14
    assert b['relative_remainder'] > 0.1


@pytest.mark.parametrize('p', [[0, 0], [2, 0]])
def test_zero_transfer_or_dependent_basis_is_not_a_physical_readout(p):
    with pytest.raises(ValueError, match='independent Pauli'):
        readout([1, 0], [1, 0], p)


def test_existing_action_identity_cannot_fix_transverse_correction():
    ward = local_ward_identity_witness()
    transverse = pauli_transversality_witness()
    assert ward['Ward_Takahashi_residual'] < 1e-12
    assert transverse['q_sigma_q_residual'] < 1e-14
    assert transverse['minimal_tree_vertex_F2'] == 0
    assert transverse['Ward_identity_determines_F2'] is False
    # Arbitrary coefficients are an identifiability witness, never predictions.
    for coefficient in [0, 0.1, -0.2]:
        assert abs(coefficient * transverse['q_sigma_q_residual']) < 1e-14
