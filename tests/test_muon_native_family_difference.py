"""Targeted checks of new family jets on retained actual source arrays."""
from pathlib import Path
from decimal import Decimal,localcontext
import json
import numpy as np
import pytest
from flint import arb

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/muon_native_family_difference_20261006/run_1'

@pytest.fixture(scope='module')
def evidence():
    with np.load(OUT/'family_source_actions.npz') as z:a={k:np.array(z[k]) for k in z.files}
    return a,json.loads((OUT/'outward_display_fix/result.json').read_text())

def test_typed_mass_source_and_dual_conventions(evidence):
    a,r=evidence
    with np.load(ROOT/'artifacts/muon_source_jet_20261002/replay_reference/local_source_actions.npz') as z:
        G=z['gamma0_output'];V=z['V_complete'];Xi=z['Xi_complete']
        assert V.shape==(8,56,20)
        assert np.linalg.norm(G@a['B_H_mass_jet_per_kappa_Delta_r']-a['D_cov_mass_jet_per_kappa_Delta_r'])==0
        assert np.linalg.norm(np.einsum('oi,aij->aoj',G,V)-Xi)==0
        for p in (a['typed_input_embedding'],a['typed_output_embedding']):
            assert np.linalg.norm(p.conj().T@p-np.eye(p.shape[1]))==0
    assert r['proof']['neutrino_mass_block_norm']==0
    assert r['proof']['family_centrality_residual']==0
    assert r['proof']['saved_open_pair_source_residual']==0
    assert r['proof']['bare_upper_mass_composition_norm']>5.6

def test_square_contact_by_bilinear_polarization(evidence):
    a,r=evidence
    with np.load(ROOT/'artifacts/muon_source_jet_20261002/replay_reference/local_source_actions.npz') as z:V=z['V_complete']
    mass=a['B_H_mass_jet_per_kappa_Delta_r']
    # Polarization of the norm form uses complete20->56 source outputs;
    # it is independent of the direct product expression in the producer.
    for k,v in enumerate(V):
        plus=mass+v;minus=mass-v
        polarized=(plus.conj().T@plus-minus.conj().T@minus)/2
        assert np.linalg.norm(polarized-a['K_sb_canonical_per_kappa_Delta_r'][k])<8e-15
    assert np.linalg.norm(a['K_sb_covariant_per_kappa_Delta_r']-a['K_sb_canonical_per_kappa_Delta_r'])==0
    assert r['proof']['direct_typed_weak_K_sb_norm']<4e-15
    assert r['proof']['weak_mass_background_form_norm']>3.99
    assert np.linalg.norm(a['weak_mass_background_form']-a['weak_mass_background_form'].conj().T)<1e-14
    P=a['weak_mass_squared_form']
    assert np.linalg.norm(P@P-P)==0

def test_endpoint_vs_integral_with_retained_decimal_inputs(evidence):
    a,r=evidence;q=r['form_family_quadrature'];rat=q['ratios']
    with localcontext() as c:
        c.prec=80;e,m=Decimal(rat['r_e']),Decimal(rat['r_mu'])
        assert str(m-e)==rat['Delta_r']
        assert str(m+e)==rat['sum_r']
        assert str(m*m-e*e)==q['difference_squared_from_exact_retained_decimals']
    assert arb(q['endpoint_minus_integral_kappa_background']['arb']).contains(0)
    assert arb(q['endpoint_minus_integral_kappa_squared']['arb']).contains(0)
    for term in ('kappa_background','kappa_squared'):
        assert np.array_equal(a['endpoint_coefficient_'+term],a['integral_coefficient_'+term])
    for key in ('Delta_r','difference_squared','integral_mass_squared_coefficient'):
        lo,hi=q[key]['interval']
        assert lo<hi
        assert arb(lo)<=arb(q[key]['arb']).lower()
        assert arb(hi)>=arb(q[key]['arb']).upper()
    assert q['native_heat_quadrature'] is None and q['kappa_numerical'] is None

def test_fixed_form_scope_and_native_three_point_guard(evidence):
    a,r=evidence
    assert not np.count_nonzero(a['source_M_s']) and not np.count_nonzero(a['source_M_sb'])
    assert r['proof']['native_M_s'] is None and r['proof']['native_M_sb'] is None
    assert r['native_heat']['invocations']==0 and not r['native_heat']['default_length_used']
    assert 'K_0,Q(v,w)=delta_A^2' in r['native_heat']['first_missing_operand']['equation']
    assert r['signed_transfer']['native_directions']==0
    assert all(x['classification']=='UNEVALUATED' and x['paired_contribution'] is None for x in r['contributions'].values())
    assert not r['preserved']['seam_campaign_run'] and r['preserved']['electron_QED_difference_not_added']
    assert r['physical_a_mu'] is None and r['physical_g_mu'] is None
