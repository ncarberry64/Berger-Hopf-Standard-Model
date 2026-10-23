"""Independent finite-field evidence for the restricted operator derivative."""
from pathlib import Path
import json

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'artifacts/muon_causal_operator_wall_current_20261018/derivative_run_A'


@pytest.mark.parametrize('side',['incoming','outgoing'])
def test_current_derivative_agrees_with_independent_affine_propagations(side):
    result=json.loads((DATA/side/'result.json').read_text())
    with np.load(DATA/side/'analytic_affine_current_derivative.npz',allow_pickle=False) as z:
        assert np.max(abs(z['tangent_UE_final']))>1e-7
        assert np.max(abs(z['actual_direct_plus_causal_wall134_hat']))>1e-12
        np.testing.assert_allclose(z['scalar_forced_stages'],z['original_DAE_stages'],atol=1e-31,rtol=1e-12)
        np.testing.assert_allclose(z['actual_direct_plus_causal_wall134_hat'],
            z['direct_matter_pullback166_hat'][32:]+z['scalar_matter_pullback166_hat'][32:]
            +z['scalar_symplectic_endpoint166_hat'][32:],atol=1e-26,rtol=1e-12)
    errors=[row['errors']['actual_direct_plus_causal_wall134_hat'] for row in result['independent_finite_field']]
    assert all(e['maximum_entry_absolute']<3e-21 for e in errors)
    assert all(e['maximum_entry_absolute']<e['finite_difference_roundoff_scale'] for e in errors)
    # Retain the actual smaller-step roundoff trend; no convergence order is asserted.
    assert errors[-1]['maximum_entry_absolute']>errors[0]['maximum_entry_absolute']
    assert not result['physical_flags']['physical_total_derivative_admitted']
    assert not result['physical_flags']['state_or_reference_selected']
