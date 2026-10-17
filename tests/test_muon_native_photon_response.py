"""Targeted checks of NEW actual-current component responses, not native g-2."""
import json
from pathlib import Path
import sys
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_native_photon_response import require_native_photon_action

RUN=ROOT/'artifacts/muon_native_photon_response_20261006/run_1'


def arrays(path):
    with np.load(path,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def test_actual_source_dual_and_reference_coexact_pairing():
    d=arrays(RUN/'component_action_and_current.npz')
    S=d['source_inclusion'];G=d['flat_reference_gradient']
    assert S.shape==(240,8)
    assert np.linalg.norm(G.conj().T@S)<2e-14
    assert np.linalg.norm(S.conj().T@d['reached_current_dual']-d['mode_current_covector'])<2e-14
    assert d['mode_current_covector'].shape==(8,224)
    # Reference coexactness does not remove the real background constraint.
    assert np.linalg.norm(G.conj().T@d['K_per_kappa1']@S)>1e3


def test_complete_primitive_rows_agree_and_keep_lorentz_sign():
    d=arrays(RUN/'component_action_and_current.npz')
    old=arrays(ROOT/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz')
    expected=np.vstack([old[f'weak_angular_row_n{n}'][-1].reshape(8,-1).T for n in (1,3)])
    actual=d['K_per_kappa1']@d['source_inclusion']
    assert np.linalg.norm(actual-expected)<5e-12
    assert np.linalg.norm(actual[48:])>1e3  # n3 kept before consumption
    S=d['source_inclusion']
    assert np.all(np.diag(S.conj().T@d['K_per_kappa1']@S).real<0)


def test_all_current_columns_residual_and_postsolve_return_bounds():
    d=arrays(RUN/'component_action_and_current.npz')
    for i in range(3):
        row=arrays(RUN/f'response_{i}.npz')
        cert=json.loads((RUN/'return_certificate_completion'/f'certificate_{i}.json').read_text())
        H=d['K_per_kappa1']+cert['zeta_over_kappa1']*float(d['M_geometric_scalar'])*np.eye(240)
        residual=np.linalg.norm(H@row['current_response']-d['reached_current_dual'],axis=0)
        bounds=np.asarray(cert['current_residual_absolute_upper'])
        # NumPy residual contains subtraction rounding; certificate bounds
        # exact frozen products and also includes current-product rounding.
        assert np.all(residual<=bounds+5e-15)
        assert len(cert['current_residual_relative_upper'])==224
        assert max(x for x in cert['current_residual_relative_upper'] if x is not None)<4e-10
        assert cert['current_return_frobenius_error_upper']<1.6e-14
        assert cert['coercivity_lower']>0
        assert cert['physical_or_native_error_bound'] is False


def test_residual_driven_enrichment_controls_consumed_component():
    result=json.loads((RUN/'result.json').read_text())
    assert [x['dimension'] for x in result['enrichment']]==[8,16,24,32]
    assert result['enrichment'][0]['maximum_consumed_basis_error_estimate']>1e-8
    assert result['enrichment'][-1]['maximum_consumed_basis_error_estimate']<1e-12
    d=arrays(RUN/'component_action_and_current.npz')
    V=arrays(RUN/'enriched_frame.npz')['M_orthonormal_frame']
    assert np.linalg.norm(float(d['M_geometric_scalar'])*V.conj().T@V-np.eye(32))<5e-14
    for i,shift in enumerate(result['shifts']):
        cert=json.loads((RUN/'return_certificate_completion'/f'certificate_{i}.json').read_text())
        assert shift['ambient_return_difference_norm']<cert['basis_consumed_return_error_upper']


def test_index_and_source_frame_reused_once_in_actual_load():
    d=arrays(RUN/'component_action_and_current.npz')
    old=arrays(ROOT/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz')
    geom=arrays(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    family=arrays(ROOT/'artifacts/muon_native_family_difference_20261006/run_1/family_source_actions.npz')
    R=geom['boundary_radius'][0];fR=float(old['T_b'])/R
    assert np.array_equal(d['mode_current_covector'],fR*family['Gamma_bar_complete'].reshape(8,-1))
    m=geom['proper_lapse'][0,-1]*geom['C_rho'][0,-1]*geom['base_radius'][0,-1]/R
    assert float(d['M_geometric_scalar'])==m
    assert np.linalg.norm(d['source_inclusion'].conj().T@d['source_inclusion']-(16/3)*np.eye(8))<5e-14


def test_component_cannot_be_promoted_to_native_heat_or_transfer():
    result=json.loads((RUN/'result.json').read_text())
    assert result['operator']['Lorentz_angular_sign']==-1
    assert result['requested_native_target_reached'] is False
    assert result['execution']['full_native_shifted_solves']==0
    assert result['heat_consumer']['invocations']==0
    assert result['heat_consumer']['ell_star_numerical'] is None
    assert result['physical_a_mu'] is None and result['physical_g_mu'] is None
    assert all(x['spectral_parameter_only'] for x in result['shifts'])
    with pytest.raises(NotImplementedError,match='polarization action'):
        require_native_photon_action()
