"""Canonical lift normalization and the missing variational port identity."""
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from flint import arb, arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.canonical_boundary_material_seeds import differentiated_lift, moving_action_contraction
from certify_n12_gate7_coupled_center_neighborhood import load
from checkpoint_n12_gate7_66d_tangent_binding import digest
from derive_n12_gate7_slaved_interface import attachment, attachment_variation

OUT=ROOT/'artifacts/flagship_integration/gate7_material_seeds_20260927'


def test_current_lifts_retain_their_actual_two_channel_normalization():
    ctx.prec=512
    a=load(OUT/'arrays.npz')
    for name in ('canonical_q_attachment_replay','canonical_v_attachment_replay'):
        assert a[name].shape==(2,2)
        assert all(x.contains(0) and abs(x)<arb('1e-40') for x in a[name].flat)
    d=json.loads((OUT/'report.json').read_bytes())
    assert d['canonical_four_rank']==4
    assert d['canonical_four_rank_inverse_defect']['approximate_upper']<1e-40
    # Raw canonical virtual directions preserve their own 24 KKT constraints,
    # not automatically the full 25-row state/energy kernel.
    assert d['canonical_four_lie_in_K73'] is False
    assert d['constraint_leakage_entry_absolute_lower']>1


def test_historical_seven_duality_is_kept_in_its_historical_scope():
    d=json.loads((OUT/'report.json').read_bytes())
    assert d['historical_seven_duality']['approximate_upper']<1e-130
    assert d['material_seed_change_of_basis_7x7'] is None
    assert 'frozen Stage-B' in d['historical_seven_scope']


def test_attachment_material_derivative_against_exact_curve():
    ctx.prec=512
    q=[arb(0)]*37; q[25]=arb('0.2')
    U=np.full((98,1),arb(0),dtype=object);U[25,0]=arb(3)
    _,signs,t,sech=attachment(q)
    got=attachment_variation(U,signs,t,sech)
    # d/dp[-tanh(2*(0.2+3p))] = -6 sech^2(0.4).
    expected=-arb(6)/(arb('0.4').cosh()**2)
    for j in range(12):
        assert (got[0,25+j,0]-expected*((-1)**j)).contains(0)
        assert (got[1,25+j,0]+expected*((-1)**j)).contains(0)
    assert all(got[a,i,0].is_zero() for a in range(2) for i in range(25))


def test_lift_motion_includes_moving_target_and_preserves_kkt_equation():
    ctx.prec=512
    K=arb_mat([[2,1],[1,3]]);E=arb_mat([[1],[0]]);L=K.solve(E)
    dK=arb_mat([[1,2],[2,-1]]);dE=arb_mat([[3],[-2]])
    dl=differentiated_lift(K,L,[dK],[dE])[0]
    assert all(x.contains(0) for x in (K*dl+dK*L-dE).entries())
    with pytest.raises(ValueError,match='material derivatives'):
        differentiated_lift(K,L,[dK],None)


def test_ordinary_material_reaction_uses_plus_sign():
    ctx.prec=512
    # L(p)=(1+2p,3-p), g(p)=(4+5p,6+7p).
    # derivative of the actual contraction is 4*2-6 + 5+3*7=28.
    r=moving_action_contraction(arb_mat([[1],[3]]),arb_mat([[4],[6]]),
        arb_mat([[5],[7]]),[arb_mat([[2],[-1]])])
    assert r['fixed_seed'][0,0]==26
    assert r['moving_seed'][0,0]==2
    assert r['total'][0,0]==28
    with pytest.raises(ValueError,match='material lift derivative'):
        moving_action_contraction(arb_mat([[1]]),arb_mat([[2]]),arb_mat([[3]]),None)


def test_boundary_duality_does_not_identify_output_with_action_derivative():
    # Logical counterexample only, not a substituted BHSM state/model.
    beta=arb_mat([[1,0]]);L=arb_mat([[1],[0]])
    assert (beta*L)[0,0]==1
    y=arb_mat([[2],[3]]);gradient=arb_mat([[4],[6]])  # Gamma=||y||^2
    assert (beta*y)[0,0]==2
    assert (L.transpose()*gradient)[0,0]==4
    # Same beta-right-inverse condition permits adding a kernel direction.
    other=arb_mat([[1],[1]])
    assert (beta*other)[0,0]==1
    assert (other.transpose()*gradient)[0,0]==10


def test_packet_does_not_turn_missing_history_rows_into_zeros():
    d=json.loads((OUT/'report.json').read_bytes())
    assert d['R_history_7x73'] is None and d['R_complete_7x73'] is None
    assert not d['material_response_promoted'] and not d['prefix_rebuilt']
    assert not d['Gate7_closed'] and not d['FULL_BHSM_COMPLETE']
    assert not d['canonical_seed_motion_materialized'] and d['action_producers_run']==0
    assert [r['event_balance_sign'] for r in d['rows']]==[-1]*5+[1]*2
    assert all(r['history_launch_derivative'] is None for r in d['rows'])


def test_source_binding_and_byte_identical_replay():
    d=json.loads((OUT/'report.json').read_bytes())
    assert digest(OUT/'arrays.npz')==d['arrays_SHA256']
    for path,h in d['source_SHA256'].items():
        assert digest(ROOT/path)==h
    r=json.loads((OUT/'reproduction.json').read_bytes())
    assert r['byte_identical']
    for name,h in r['SHA256'].items():
        assert digest(OUT/name)==h
