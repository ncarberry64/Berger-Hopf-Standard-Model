"""Canonical row signs, differentiated lift, and shared material composition."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from flint import arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
import derive_n12_gate7_event_conormal_jet as e
from bhsm.interface.complete_child_flux_response import dynamic_flux_first_jet, pullback_sector_five

OUT = ROOT/'artifacts/flagship_integration/gate7_event_conormal_20260927'


def packet():
    ctx.prec = 512
    return json.loads((OUT/'report.json').read_bytes()), e.r.load(OUT/'arrays.npz')


def zero(x):
    return all(v.contains(0) for v in x.entries())


def test_canonical_complete_child_source_assigns_event_flux_once():
    # Execute the actual canonical assembler with polynomial controls for its
    # dependencies: catches wrong side/sign/duplicate momentum-rate ownership.
    path = ROOT/'src/bhsm/interface/aether_n3_complete_child_chart_reconstruction_v18_24.py'
    node = next(x for x in ast.parse(path.read_text()).body
                if isinstance(x, ast.FunctionDef) and x.name == '_child_rows')
    env = dict(np=np, _unpack_child=lambda z:(z[:2], z[2:4], z[4:]),
        _canonical_pair=lambda q,v,m:(q*q+v*m, np.array([7.,11.]), np.eye(2), np.eye(2)),
        _metric_radial_flux_covector=lambda q,m:(np.array([13.,17.]), {}),
        exact_euler_dirac_acceleration=lambda *a,**kw:dict(acceleration=np.array([3.,5.]),multiplier_rate=np.array([2.,4.])),
        _trace_jacobian=lambda:np.eye(2), constraint_residual=lambda *a,**kw:np.zeros(7))
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), env)
    z=np.array([1.,2.,3.,4.,5.,6.]); event=np.array([19.,23.])
    rows=env['_child_rows'](z,np.zeros(2),np.zeros(2),event)
    dp=2*z[:2]*z[2:4]+np.array([3.,5.])*z[4:]+z[2:4]*np.array([2.,4.])
    assert np.allclose(rows[-2:], np.array([13.,17.])+dp-np.array([7.,11.])+event, rtol=0, atol=1e-8)
    shifted=env['_child_rows'](z,np.zeros(2),np.zeros(2),event+np.array([2.,-3.]))
    assert np.allclose(shifted[-2:]-rows[-2:], [2.,-3.], rtol=0, atol=1e-12)


def test_dynamic_chain_keeps_both_momentum_rate_terms():
    blocks=[arb_mat([[v],[2*v]]) for v in (2,3,5,7,11)]
    result=dynamic_flux_first_jet(*blocks)
    assert result == arb_mat([[22],[44]])
    with pytest.raises(ValueError):
        dynamic_flux_first_jet(*blocks[:4], arb_mat(2,2))


def test_sector_pullback_preserves_cancellation_and_counts_trace_once():
    trace=arb_mat([[1,2],[3,4],[5,6]])
    sectors={'plus':arb_mat([[100,2],[3,100]]), 'minus':arb_mat([[-99,-2],[-3,-99]])}
    material=arb_mat([[1,2,3],[4,5,6]])
    shape=arb_mat([[1,0,0],[0,2,0],[0,0,3],[4,0,0],[0,5,0]])
    total, parts=pullback_sector_five(trace,sectors,material,shape)
    expected=arb_mat((trace*material).tolist()+material.tolist())+shape
    assert total == expected and sum(parts.values(),arb_mat(2,3)) == material
    with pytest.raises(ValueError):
        pullback_sector_five(trace,sectors,material,arb_mat(5,2))


def test_native_event_conormal_uses_both_covector_and_lift_motion():
    report,a=packet(); mat=e.r.mat
    assert a['native_event_7x98'].shape == (7,98)
    direct=mat(a['event_conormal_derivative'])
    assert zero(direct-mat(a['conormal_lift_contribution'])-mat(a['conormal_covector_contribution']))
    assert zero(mat(a['adjoint_direct_replay']))
    assert report['replay']['inverse']['approximate_upper'] < 1e-110
    assert report['replay']['adjoint_direct']['approximate_upper'] < 1e-110
    assert report['replay']['differentiated_lift']['approximate_upper'] < 1e-110
    assert report['lift_contribution_norm']['approximate_upper'] > 0
    prior=e.r.load(e.BASE/'arrays.npz')
    assert zero(mat(a['native_event_7x98'][:5])-mat(prior['native_trace_momentum_jet']))


def test_point_scope_and_owner_signs_are_not_promoted_to_material_map():
    report,_=packet()
    assert report['dynamic_flux_owner_exists']
    assert not report['event_momentum_rate_added']
    assert not report['material_response_7x73_derived']
    assert not report['current_environment_identified']
    assert report['new_environment_inputs'] == 0
    assert not report['Gate7_closed'] and not report['FULL_BHSM_COMPLETE']


def test_source_hashes_and_byte_identical_reproduction():
    report,_=packet(); h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
    assert h(OUT/'arrays.npz') == report['arrays_SHA256']
    for path,sha in report['source_SHA256'].items(): assert h(Path(path)) == sha
    for path,item in report['provenance'].items(): assert h(Path(path)) == item['SHA256']
    for name,item in json.loads((OUT/'reproduction.json').read_bytes())['files'].items():
        assert item['byte_identical'] and h(OUT/name) == item['SHA256']
