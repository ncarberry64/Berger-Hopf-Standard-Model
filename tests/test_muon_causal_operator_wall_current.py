"""Actual finite source/return identities; no physical state is selected."""
from pathlib import Path
import json
import subprocess
import sys

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'artifacts/muon_causal_operator_wall_current_20261018'


@pytest.mark.parametrize('side',['incoming','outgoing'])
def test_new_operator_current_consumes_forced_scalar_response_and_endpoint(side):
    with np.load(DATA/'run_A'/f'{side}_causal_operator_current.npz',allow_pickle=False) as z:
        assert z['Higgs_current_stage_hat'].shape==(4,16,30,30)
        assert np.max(abs(z['Higgs_current_stage_hat']))>1e-14
        assert np.max(abs(z['scalar_forced_final']))>1e-14
        np.testing.assert_allclose(z['scalar_forced_stages'],z['original_DAE_stages'],atol=1e-26,rtol=1e-13)
        causal=z['actual_direct_plus_causal_wall134_hat']
        pull=z['matter_pullback574_hat'][440:]
        endpoint=z['scalar_symplectic_endpoint166_hat'][32:]
        assert np.max(abs(endpoint))>1e-15
        np.testing.assert_allclose(causal,pull+endpoint,atol=2e-21,rtol=1e-13)
        assert np.max(abs(causal-pull))>1e-15
        np.testing.assert_allclose(z['wall_gauge_Euler_return_hat']+z['wall_gauge_temporal_endpoint_hat'],
                                   z['scalar_causal_wall_return134_hat'],atol=1e-28,rtol=1e-13)
        assert np.max(abs(causal-causal.conj().swapaxes(-1,-2)))<2e-21


@pytest.mark.parametrize('side',['incoming','outgoing'])
def test_current_operator_contracts_linearly_without_choosing_physical_occupation(side):
    with np.load(DATA/'run_A'/f'{side}_causal_operator_current.npz',allow_pickle=False) as z:
        # Two explicit matrix probes check operator linearity only; neither is a physical density.
        first=np.diag(np.linspace(-.1,.1,30))
        second=np.diag(np.cos(np.arange(30))*.03)
        load=lambda state:np.einsum('ij,cji->c',state,z['actual_direct_plus_causal_wall134_hat'])
        np.testing.assert_allclose(load(first+second),load(first)+load(second),atol=1e-21,rtol=1e-13)
        assert np.max(abs(z['matter_pullback574_hat'][:408]))==0
    result=json.loads((DATA/'run_A/result.json').read_text())
    assert not result['physical_flags']['density_or_reference_selected']
    assert not result['physical_flags']['physical_full_derivative_admitted']
    assert result['physical_flags']['coupled_physical_corrections']==0


def test_completed_current_arms_resume_without_recomputing_or_rewriting():
    target=DATA/'run_A/result.json'
    original=target.read_bytes()
    head=json.loads((DATA/'PHASE_A_PUBLICATION.json').read_text())['commit']
    process=subprocess.run([sys.executable,'-B','scripts/evaluate_muon_causal_operator_wall_current.py',
        '--output',str(DATA/'run_A'),'--phase-a-published-head',head,'--resume'],
        cwd=ROOT,capture_output=True,text=True,check=True)
    assert process.stdout.count('reused completed hash-verified')==2
    assert target.read_bytes()==original


@pytest.mark.parametrize('side',['incoming','outgoing'])
def test_current_is_consumed_in_common_classical_wall_and_endpoint_maps(side):
    from bhsm.interface.retained_response.operator_current_system import hermitian_coordinates
    with np.load(DATA/'common_system_A'/f'{side}_known_current_open_system.npz',allow_pickle=False) as joint, \
         np.load(DATA/'run_A'/f'{side}_causal_operator_current.npz',allow_pickle=False) as current, \
         np.load(ROOT/'artifacts/muon_retained_response_20261018/run_A'/f'{side}_joint_open_response.npz',allow_pickle=False) as classical:
        raw=np.sin(np.arange(900).reshape(30,30))+1j*np.cos(np.arange(900).reshape(30,30)+.31)
        operand=.001*(raw+raw.conj().T)
        eta=.01*np.cos(np.arange(574));n=hermitian_coordinates(operand)
        assert joint['known_wall_map'].shape==(134,1474)
        assert joint['known_final_map'].shape==(440,1474)
        direct=classical['classical_wall_map']@eta+np.einsum('ij,cji->c',operand,current['actual_direct_plus_causal_wall134_hat'])
        np.testing.assert_allclose(joint['known_wall_map']@np.r_[eta,n],direct,atol=3e-16,rtol=0)
        final=classical['classical_final_map']@eta
        final=final.astype(complex)
        final[408:]+=np.einsum('ij,cji->c',operand,current['scalar_forced_final'])
        np.testing.assert_allclose(joint['known_final_map']@np.r_[eta,n],final,atol=3e-16,rtol=0)
