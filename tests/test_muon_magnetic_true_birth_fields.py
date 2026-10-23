"""CONTROL_ONLY exact constitutive checks; no new physical source selection."""
import numpy as np
import pytest
from bhsm.interface.muon_magnetic_true_birth_fields import birth_constitutive_response
from bhsm.interface.muon_parent_maxwell_full_retarded import constrained_gauss_schur


def test_sourced_legendre_and_all_gauss_rows_match_literal_uneliminated_action():
    # CONTROL_ONLY finite literal action with temporal gauge/value/source mix.
    M=np.zeros((488,488));M[80:,80:]=np.diag(np.linspace(1,3,408))
    B=np.zeros_like(M);K=np.eye(488);B[:80,80:160]=.1*np.eye(80)
    B[80:480,480:]=.03*np.arange(3200).reshape(400,8)/3200
    K[:80,480:]=.01*np.arange(640).reshape(80,8)/640;K[480:,:80]=K[:80,480:].T
    r=constrained_gauss_schur(M,B,K,80)
    state=np.arange(6400).reshape(800,8)/6400
    out=birth_constitutive_response({'reduced':r},state)
    z=np.r_[out['A_tau'],state[:400],np.eye(8)]
    zd=np.r_[np.zeros((80,8)),out['velocity'],np.zeros((8,8))]
    np.testing.assert_allclose((M@zd+B.T@z)[80:480],state[400:],atol=2e-16)
    np.testing.assert_allclose((K@z+B@zd)[:80],0,atol=2e-16)
    assert np.max(abs(out['Gauss_residual']))<2e-16
    assert not out['velocities_transferred_across_birth']


def test_source_momentum_contact_is_not_dropped_and_missing_state_rejected():
    r={'M':np.eye(408),'B':np.zeros((408,408)),
       'At_value_map':np.zeros((80,408)),'At_velocity_map':np.zeros((80,408)),
       'Gauss_matrix':np.eye(80),'Gauss_value_row':np.zeros((80,408)),'Gauss_velocity_row':np.zeros((80,408))}
    r['B'][400:,:400]=.2
    state=np.zeros((800,8))
    out=birth_constitutive_response({'reduced':r},state)
    np.testing.assert_array_equal(out['velocity'],np.full((400,8),-.2))
    with pytest.raises(ValueError):birth_constitutive_response({'reduced':r},np.zeros((400,8)))
