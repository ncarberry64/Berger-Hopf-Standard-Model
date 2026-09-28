"""Real trace owner, differential flux map, and four-direction contractions."""
import ast
import json
from pathlib import Path
import sys

import mpmath as mp
import numpy as np
import pytest
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.geometric_material_port import (
    geometric_trace_jet,required_material_jet,heat_pair_4x73,reduce_material_mixed)
from bind_n12_gate7_geometric_material_port import source_functions,radial_from_current_state,OWNER
from certify_n12_gate7_coupled_center_neighborhood import load
from checkpoint_n12_gate7_66d_tangent_binding import digest

OUT=ROOT/'artifacts/flagship_integration/gate7_geometric_material_port_20260927'


def test_actual_complete_child_producer_has_three_geometric_rows():
    trace,definitions=source_functions()
    function=ast.parse(definitions['_child_rows_at_order']['text']).body[0]
    # Execute the actual assembler with controlled component dependencies;
    # this tests row ownership/signs, not a substitute physical solution.
    n=37
    namespace=dict(np=np,dimensions=lambda order:{'coordinates':37},
        _trace_jacobian_at_order=trace,
        _canonical_pair_at_order=lambda *a,**kw:(np.array([2.,3.]),np.array([7.,11.]),np.eye(37,2),np.eye(37,2)),
        _metric_radial_flux_covector_at_order=lambda *a:np.r_[13.,17.,np.zeros(35)],
        _exact_full_jet_euler_dirac_acceleration=lambda *a,**kw:dict(acceleration=np.zeros(n),multiplier_rate=np.zeros(24)),
        _complex_step_canonical_momentum_rate=lambda *a,**kw:np.array([19.,23.]),
        constraint_residual=lambda *a,**kw:np.zeros(25))
    exec(compile(ast.Module(body=[function],type_ignores=[]),str(OWNER),'exec'),namespace)
    state=np.zeros(98);state[0]=1;event=np.zeros(37);event[1]=0.25
    r=namespace['_child_rows_at_order'](12,state,event,np.array([29.,31.]),np.array([37.,41.]),points=1,flux_derivative_method='complex_step')
    assert np.array_equal(r[:3],trace(12)@(state[:37]-event))
    assert np.array_equal(r[28:30],np.array([2.,3.])-np.array([29.,31.]))
    assert np.array_equal(r[30:],np.array([13.,17.])+np.array([19.,23.])-np.array([7.,11.])+np.array([37.,41.]))


def test_all_three_current_trace_rows_and_rank_replay():
    ctx.prec=512
    a=load(OUT/'arrays.npz');d=json.loads((OUT/'report.json').read_bytes())
    assert a['geometric_trace_3x73'].shape==(3,73)
    assert all(x.contains(0) for x in a['trace_overlap_replay'].flat)
    assert d['trace_overlap_replay']['approximate_upper']<2e-14
    assert d['trace_rank']==3 and d['trace_rank_inverse_defect']['approximate_upper']<1
    assert all(x.contains(0) for x in a['trace_radius_replay'].flat)
    for name in ('trace_fixed_section_explicit_shape_3x73','trace_explicit_attachment_3x73','trace_direct_action_increment_3x73'):
        assert all(x.is_zero() for x in a[name].flat)


def test_trace_shape_motion_must_be_explicit_and_counted_once():
    T=arb_mat([[1,0],[0,1],[1,-1]]);J=arb_mat([[2],[3]])
    shape=arb_mat([[5],[7],[11]])
    got=geometric_trace_jet(T,J,shape)
    assert got==arb_mat([[7],[10],[10]])
    with pytest.raises(ValueError,match='shape term'):geometric_trace_jet(T,J,None)


def test_dynamic_flux_requires_rate_and_conormal_not_four_by_four_basis():
    p=arb_mat([[2],[3]]);f=arb_mat([[7],[11]]);g=arb_mat([[13],[17]])
    h=arb_mat([[19],[23]]);rate=arb_mat([[29],[31]])
    got=required_material_jet(p,f,g,h,rate)
    assert got==arb_mat([[2],[3],[-54],[-60]])
    # Same four canonical contractions, different momentum-rate jet.
    other=required_material_jet(p,f,g,h,arb_mat(2,1))
    assert other!=got
    with pytest.raises(ValueError,match='five owned'):required_material_jet(p,f,g,None,rate)


def test_current_force_to_flux_difference_is_real_and_replayed():
    a=load(OUT/'arrays.npz');d=json.loads((OUT/'report.json').read_bytes())
    assert d['force_to_flux_nonzero_entry_lower']>1500
    assert all(x.contains(0) for x in a['value_decomposition_replay'].flat)
    assert all(x.contains(0) for x in a['material_overlap_replay'].flat)
    assert d['force_to_flux_is_static_basis_change'] is False
    order=arb_mat(a['canonical_order_change_4x4'].tolist())
    assert order*order==arb_mat(np.eye(4,dtype=int).tolist())


def test_radial_formula_replays_actual_source_at_control_state():
    # Independent binary64 value check of the explicit Arb geometry formula.
    trace,definitions=source_functions()
    tree=ast.parse(definitions['_metric_radial_flux_covector_at_order']['text'])
    from derive_n12_gate7_slaved_interface import A
    namespace=dict(np=np,dimensions=lambda n:{'coordinates':37},RADIUS0=A.RADIUS0)
    exec(compile(tree,str(OWNER),'exec'),namespace)
    Y=np.linspace(-0.02,0.02,98)
    expected=namespace['_metric_radial_flux_covector_at_order'](12,Y[:37],Y[74:])
    actual=radial_from_current_state([arb(float(x)) for x in Y])
    assert np.allclose([float(x.mid()) for x in actual.entries()],expected,rtol=3e-14,atol=0)


def test_four_material_heat_pair_matches_noncommuting_action():
    ctx.prec=512
    B=[arb_mat(2,2) for _ in range(4)];P=[arb_mat(2,2) for _ in range(73)]
    B[2]=arb_mat([[1,2],[2,-1]]);P[5]=arb_mat([[2,-1],[-1,3]])
    got=heat_pair_4x73([arb(2),arb(3)],B,P)
    with mp.workdps(100):
        def action(b,p):
            a=2+b+2*p;d=3-b+3*p;off=2*b-p
            mid=(a+d)/2;gap=mp.sqrt((a-d)**2/4+off**2)
            return -(mp.e1(mid-gap)+mp.e1(mid+gap))/2
        truth=mp.diff(lambda b:mp.diff(lambda p:action(b,p),0),0)
        assert got[2,5].overlaps(arb(mp.nstr(truth,90))+arb(0,arb('1e-89')))
    assert all(got[i,j].is_zero() for i in range(4) for j in range(73) if (i,j)!=(2,5))
    with pytest.raises(ValueError,match='four material'):heat_pair_4x73([arb(2),arb(3)],B+[arb_mat(2,2)],P)


def test_four_direction_general_objective_adjoint_against_implicit_truth():
    ctx.prec=512
    # n=bp, Gamma=n^2/2+3n+bn+2pn+7bp at b=p=0.
    # eta=3, so L_bp=7-3*(-1)=10; Gamma_red,bp=10.
    Lbp=arb_mat(4,73);Lbp[0,0]=10
    Lbn=arb_mat(4,1);Lbn[0,0]=1
    Lnp=arb_mat(1,73);Lnp[0,0]=2
    moving=arb_mat(4,73);moving[0,0]=5
    got=reduce_material_mixed(L_bp=Lbp,L_bn=Lbn,L_np=Lnp,L_nn=arb_mat([[1]]),
        F_n=arb_mat([[1]]),F_b=arb_mat(1,4),F_p=arb_mat(1,73),moving_seed=moving)
    assert got['fixed_seed'][0,0]==10 and got['total'][0,0]==15
    assert all(x.is_zero() for x in got['adjoint_replay'].entries())
    assert all(x.is_zero() for x in got['boundary_replay'].entries())


def test_nonzero_internal_response_four_direction_adjoint():
    # Constant symmetric quadratic objective; F=n+2b+3p.
    # Reduced mixed Hessian: 7 - 3*1 - 2*2 + (-2)*5*(-3)=30.
    Lbp=arb_mat(4,73);Lbp[0,0]=7
    Lbn=arb_mat(4,1);Lbn[0,0]=1
    Lnp=arb_mat(1,73);Lnp[0,0]=2
    Fb=arb_mat(1,4);Fb[0,0]=2
    Fp=arb_mat(1,73);Fp[0,0]=3
    got=reduce_material_mixed(L_bp=Lbp,L_bn=Lbn,L_np=Lnp,L_nn=arb_mat([[5]]),
        F_n=arb_mat([[1]]),F_b=Fb,F_p=Fp,moving_seed=arb_mat(4,73))
    assert got['total'][0,0]==30


def test_trace_is_not_added_twice_and_history_remains_explicitly_open():
    d=json.loads((OUT/'report.json').read_bytes())
    assert d['classification_dimensions']==[3,4]
    assert d['seven_action_seed_requirement_retired']
    assert d['R_trace_history_3x73'] is None
    assert d['R_history_7x73'] is None and d['R_complete_7x73'] is None
    assert d['trace_explicit_action_correction_zero']
    assert not d['material_response_promoted'] and not d['current_material_history_4x73_materialized']
    assert not d['prefix_rebuilt'] and not d['Stage_B_rerun'] and d['action_producers_run']==0
    assert [r['type'] for r in d['rows']]==['GEOMETRIC_COMPATIBILITY']*3+['MATERIAL_ACTION_REACTION']*4
    assert not d['Gate7_closed'] and not d['FULL_BHSM_COMPLETE']


def test_packet_source_hashes_and_deterministic_replay():
    d=json.loads((OUT/'report.json').read_bytes())
    for p,h in d['source_SHA256'].items():assert digest(ROOT/p)==h
    assert digest(OUT/'arrays.npz')==d['arrays_SHA256']
    r=json.loads((OUT/'reproduction.json').read_bytes())
    assert r['byte_identical']
    for name,h in r['SHA256'].items():assert digest(OUT/name)==h
