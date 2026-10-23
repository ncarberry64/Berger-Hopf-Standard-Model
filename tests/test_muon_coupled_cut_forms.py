"""New actual-cut form checks; no old producer or replay is executed."""
import json
from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_coupled_cut_forms import (
    require_exterior_history_action, ExteriorActionUnavailable)


ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'artifacts/muon_coupled_cut_forms_20261004'


@pytest.fixture(scope='module')
def saved():
    def load(p):
        with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
    return (load(REF/'run_1/coupled_cut_source_actions.npz'),
            load(REF/'run_2/coupled_complement_blocks.npz'),
            json.loads((REF/'run_2/result.json').read_text()))


def test_actual_source_quotient_retains_all_columns(saved):
    a,_,r=saved;G=a['source_Haar_Gram'];S=a['independent_source_map']
    assert S.shape==(32,12)
    np.testing.assert_allclose(G@S@S.conj().T@G,G,rtol=0,atol=4e-15)
    assert r['actual_source_quotient_reconstruction_residual']<1e-14


def test_bulk_orthogonality_does_not_replace_Cauchy_pairing(saved):
    _,b,_=saved;d=12
    assert np.linalg.norm(b['local_cut_M_Wchi'][:d,d:])<1e-14
    assert np.linalg.norm(b['local_cut_Cauchy_Wchi'][:d,d:])>.01


def test_full_material_trace_cancels_without_zero_complement(saved):
    _,b,r=saved
    assert r['material_complement_trace_norm']>0
    for n in (1,3):
        assert np.linalg.norm(b[f'chi_trace_n{n}'])>0
        assert np.linalg.norm(b[f'total_trace_n{n}']) <= (
            2*np.finfo(float).eps*np.linalg.norm(b[f'chi_trace_n{n}']))


def test_retained_source_cotangent_agrees_with_full_output_form(saved):
    a,_,r=saved;d=12;c=a['source_coordinates'];w=a['radial_weights']*a['volume_density']
    energy=sum(float(w@np.sum(abs(a[f'Dp_n{n}'].reshape(len(w),-1))**2,axis=1)) for n in (1,3))
    assert abs(energy-np.vdot(c,a['rhs_K'][d:2*d]).real)<1e-12
    assert r['omission_of_B_tau_action_weighted_norm']>1e11
    # This is a source form value, not a P_strat application or heat value.
    assert r['physical_a_mu'] is None


def test_cut_blocks_cannot_fill_missing_history_action(saved):
    a,_,_=saved
    with pytest.raises(ExteriorActionUnavailable,match='K_ext,chi-chi'):
        require_exterior_history_action(dict(cut_K=a['local_cut_K_Wp_timejet'],
                                            cut_M=a['local_cut_M_Wp']))
