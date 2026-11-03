import importlib.util,json,sys
from hashlib import sha256
from pathlib import Path
import numpy as np
import pytest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import projected_current as p

@pytest.fixture(scope='module')
def data():return p.calculate()

def test_original_source_recovered_without_history_replay():
    q=json.loads((HERE/'evidence/provenance.json').read_text())
    assert sha256((HERE/'evidence/original_angular_source.npz').read_bytes()).hexdigest()=='146435df28178967c321c0aa7e89a1511395d196f96b8715532aa98e3e312c2b'
    assert q['source_recovered_from_existing_Git'] and not q['new_quadrature'] and not q['new_resolution']
    for name,h in q['owned_extraction_sha256'].items():assert sha256((HERE/'evidence'/name).read_bytes()).hexdigest()==h

def test_actual_photon_source_and_original_curvature(data):
    op,r=data
    assert r['checks']['owned_original_magnetic_variation']<2e-11
    np.testing.assert_allclose(op['neutral_Gram8'],48*np.eye(8),rtol=0,atol=2e-11)
    assert op['magnetic_curvature'].shape==(3,4,20,8)

def test_charged_connection_is_retained(data):
    op,r=data
    np.testing.assert_allclose(op['magnetic_Gram8'],op['neutral_Gram8']+op['charged_Gram8'],rtol=0,atol=2e-11)
    assert np.linalg.eigvalsh(op['charged_Gram8']).min()>2
    assert r['D_source_s_norm']>2

def test_coexact_does_not_imply_full_Gauss_compatibility(data):
    op,r=data
    assert r['checks']['coexact_divergence']<2e-11
    assert r['checks']['projected_angular_Gauss_zero']<2e-11
    assert np.linalg.svd(op['covariant_angular_divergence'].reshape(80,8),compute_uv=False).min()>.8
    assert r['boundary_Higgs_not_used_to_cancel_bulk']

def test_direct_Higgs_and_neutral_contacts_scope(data):
    _,r=data
    for name in ('classical_Higgs_photon_current','classical_Higgs_total_H_contact','neutral_second_curvature_zero','neutral_charged_contact_one_insertion_zero'):
        assert r['checks'][name]<2e-11
    assert not r['complete_projected_current_evaluated']

def test_new_189_coordinate_chain_rule(data):
    op,r=data
    assert op['magnetic_Gram_gradient189'].shape==(189,8,8)
    assert op['covariant_divergence_gradient189'].shape==(189,4,20,8)
    for axis in (6,11,16):assert r['checks'][f'new_gauge_Gram_derivative_{axis}']<2e-11

def test_physical_admission_and_observable_remain_open(data):
    _,r=data
    assert r['physical_guard']==2e-10 and r['admitted_temporal_strength']==2**-9
    assert not r['physical_state_admitted'] and not r['physical_reconnection_demonstrated']
    assert all(r[k] is None for k in ('a_mu','g_mu','total_physical_uncertainty'))
