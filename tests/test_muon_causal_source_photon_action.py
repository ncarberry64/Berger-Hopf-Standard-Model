from fractions import Fraction
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_causal_source_photon_action import (
    executed_reached_photon_quadratic_action,stable_native_photon_return,
)
ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('side',['incoming','outgoing'])
def test_full_unreduced_action_matches_saved_canonical_boundary_identity(side):
    a=executed_reached_photon_quadratic_action(
        f'artifacts/muon_trace_enriched_reached_action_20261010/{side}_run_1',repository=ROOT)
    assert a['full_raw_vs_reduced_action_relative_difference']<2e-13
    assert np.array_equal(a['source_quadratic_action'],a['source_quadratic_action'].T)
    assert np.linalg.norm(a['scalar_source_quadratic_action'])>0
    assert np.linalg.norm(a['Maxwell_source_quadratic_action'])>0
    assert not a['source_mode_or_soft_transfer_selected']
    assert not a['physical_free_wall_domain_certified']


def test_native_correction_below_binary64_spacing_remains_nonzero_and_enclosed():
    B=np.diag([2.,3.]);R=np.diag([1e-40,-2e-41])
    a=stable_native_photon_return(B,R)
    assert a['native_form_lost_in_binary64_addition']
    assert np.linalg.norm(a['stable_native_return'])>0
    for i in range(2):
        b=Fraction(float(B[i,i]));r=Fraction(float(R[i,i]))
        exact=-r/(b*(b+r))
        assert Fraction(float(a['stable_native_return_real_lower'][i,i]))<=exact<=Fraction(float(a['stable_native_return_real_upper'][i,i]))
    assert a['exact_stored_inverse_residual_upper']<1e-50
    assert not a['spectral_conditioning_shift_added']
    assert not a['current_covariance_or_physical_Pauli_selected']


def test_null_native_is_rejected_and_action_zero_native_has_provenance_scope():
    with pytest.raises(ValueError):stable_native_photon_return(np.eye(2),None)
    a=stable_native_photon_return(np.eye(2),np.zeros((2,2)))
    assert np.array_equal(a['stable_native_return'],np.zeros((2,2)))
    assert not a['native_form_lost_in_binary64_addition']
