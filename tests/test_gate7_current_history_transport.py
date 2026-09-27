import json
from pathlib import Path
import sys
import numpy as np
import mpmath as mp
import pytest
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from bhsm.interface.arb_current_history_transport import flow_certificate,flow_at,flow_span
from bhsm.interface.arb_weyl_first_pullback import local_map,first_pullback
from bhsm.interface.aether_forward_c2_weyl_riccati import _map
from certify_n12_gate7_coupled_center_neighborhood import load
from checkpoint_n12_gate7_66d_tangent_binding import digest

OUT=ROOT/'artifacts/flagship_integration/gate7_current_history_20260927'


def test_picard_and_first_variation_enclose_exact_nonlinear_flow():
    ctx.prec=512
    # y'=y^2, y(0)=1; y(t)=1/(1-t), J(t)=1/(1-t)^2.
    domain=arb(1)+arb(0,arb(1)/4)
    c=flow_certificate([arb(1)],np.array([[arb(1)]],dtype=object),
        [domain*domain],np.array([[2*domain]],dtype=object),[arb(1)/4],arb(1)/16)
    y,J=flow_at(c,arb(1)/16)
    assert y[0].contains(arb(16)/15) and J[0,0].contains((arb(16)/15)**2)
    _,tube=flow_span(c,0,arb(1)/16)
    assert tube[0,0].contains(1) and tube[0,0].contains((arb(16)/15)**2)
    with pytest.raises(ArithmeticError,match='leaves'):
        flow_certificate([arb(1)],np.array([[arb(1)]],dtype=object),
            [domain*domain],np.array([[2*domain]],dtype=object),[arb(1)/4],arb(1))


@pytest.mark.parametrize('channel,value,chi',[('scalar',3,1),('product_Dirac',1.5,1),('product_Dirac',1.5,-1)])
def test_interval_weyl_jet_against_independent_owned_mpmath_law(channel,value,chi):
    ctx.prec=512
    with mp.workdps(110):
        inputs=[mp.mpf('2'),mp.mpf('-0.1'),mp.mpf('0.2')]
        f=lambda L,x,h:_map(L,x,h,channel=channel,value=value,z=-1,chirality=chi)
        v,d=local_map(arb(2),arb('-0.1'),arb('0.2'),channel=channel,value=arb(value),z=-1,chirality=chi)
        # mpmath is a high-precision oracle, not an interval proof input.
        assert abs(mp.mpf(str(v.mid().fmpq()))-f(*inputs))<mp.mpf('1e-100')
        for i in range(3):
            def partial(x):
                args=inputs.copy();args[i]=x;return f(*args)
            assert abs(mp.mpf(str(d[i].mid().fmpq()))-mp.diff(partial,inputs[i]))<mp.mpf('1e-100')


def test_weyl_cotangent_composes_signed_radius_and_duration_motion():
    ctx.prec=512
    x=[arb('-0.1')]*3;h=[arb('0.2'),arb('0.3')]
    dx=arb_mat([[1,-1],[2,-2],[3,-3]]);dh=arb_mat([[4,-4],[-5,5]])
    r=first_pullback(x,h,dx,dh,channel='scalar',value=3,z=-1)
    assert all(v.contains(0) for v in r['replay'].entries())
    assert (r['first'][0,0]+r['first'][0,1]).contains(0)
    assert not r['first'][0,0].contains(0)


def test_new_flow_box_certifies_index_and_positive_clocks():
    ctx.prec=512
    d=json.loads((OUT/'flow_box/report.json').read_bytes())
    assert d['eigenpair']['validation_passed']
    assert d['eigenpair']['selected_zero_based_index_verified']==24
    assert d['descriptor_rate_positive']
    core=load(OUT/'core/arrays.npz')
    assert core['proper_clock'][0,0]>0
    assert all(v>0 for v in core['proper_durations'])
    # Retained is not the same as resolved: the current uniform enclosure is
    # broad and contains zero, but must not be replaced by identically zero.
    assert any(not v.is_zero() for v in core['proper_duration_first_73'].flat)


def test_current_core_does_not_relabel_old_actions_or_complete_joint_response():
    d=json.loads((OUT/'core/report.json').read_bytes())
    assert d['historical_certificates_inherited']==0 and d['historical_actions_recomputed']==0
    assert d['new_flow_boxes']==1 and d['current_core_mesh_segments']==1222
    assert d['R_history_7x73'] is None and d['R_complete_7x73'] is None
    assert not d['material_response_promoted'] and not d['Gate7_closed']
    assert not d['negative_axis_checks_are_graded_heat_outputs']


def test_current_history_sources_and_reproduction():
    for sub in ('flow_box','core'):
        d=json.loads((OUT/sub/'report.json').read_bytes())
        assert digest(OUT/sub/'arrays.npz')==d['arrays_SHA256']
        for p,h in d['source_SHA256'].items():assert digest(ROOT/p)==h
    receipt=json.loads((OUT/'reproduction.json').read_bytes())
    for name,entry in receipt['files'].items():
        assert entry['byte_identical'] and digest(OUT/name)==entry['SHA256']
