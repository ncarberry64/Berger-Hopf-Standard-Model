"""Owner-row replay, pure chart derivative and fixed-side null checks."""
import ast
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import audit_n12_gate7_two_sided_null_owner as d

OUT=d.ROOT/d.BASE/'gate7_two_sided_null_owner_20260926'


def packet():
    r=json.loads((OUT/'report.json').read_bytes())
    with np.load(OUT/'arrays.npz') as z:a={k:z[k] for k in z.files}
    return r,a


def test_attachment_derivative_and_depth_identity():
    _,jacobian,coordinates=d.chart_helpers()
    with np.load(d.ROOT/d.FIXED) as z:q=z['projected_states'][13,:37]
    direction=np.linspace(-0.3,0.2,37)
    derivative=np.imag(coordinates(12,q.astype(complex)+1e-20j*direction))/1e-20
    np.testing.assert_allclose(derivative,jacobian(12,q)@direction,atol=2e-15,rtol=2e-14)
    pair=coordinates(12,q)
    assert abs(-q[0]+pair.sum())<1e-15
    np.testing.assert_allclose(jacobian(12,q).sum(axis=0),np.eye(37)[0],atol=0,rtol=0)


def test_reset_signs_and_row_replay():
    r,a=packet()
    with np.load(d.RESET) as z:J=z['analytic_full_reset_jacobian']
    np.testing.assert_allclose(a['reset_boundary_normalizer']@a['reset_configuration_rows_raw_action'],J[26:30],atol=2e-14,rtol=2e-14)
    raw=a['reset_configuration_rows_raw_action']
    np.testing.assert_array_equal(raw[:3,:37],-raw[:3,98:135])
    assert np.all(a['stored_reset_rows_on_fixed_state_direction']==0)
    assert r['reset_rows']['canonical_momentum']==[55,57]
    assert r['reset_rows']['child_constraints']==[30,55]


def test_descriptor_has_no_direct_state_only_boundary_slot():
    r,a=packet()
    assert np.all(a['endpoint_boundary_on_null'][0]==0)
    assert a['endpoint_lapse_on_null'][0]==0
    assert a['endpoint_proper_time_density_on_null'][0]>0
    assert r['right_attachment_on_complete_child_norm_diagnostic']>0.06
    assert abs(r['right_attachment_on_null_diagnostic'])>4e-5
    source=d.ROOT/'src/bhsm/interface/aether_full_reset_action_jacobian.py'
    tree=ast.parse(source.read_text(encoding='utf-8'))
    owner=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='full_reset_residual')
    # The selected event eigenvalue is computed from the event state; no carried
    # independent descriptor is an input to the existing paired reset residual.
    assert 'joint_state' in [a.arg for a in owner.args.args]
    assert not any(isinstance(n,ast.Name) and n.id in ('signed_descriptor','independent_signed_descriptor') for n in ast.walk(owner))
    assert r['candidate_evaluations'][-1]['DB'] is None


def test_sources_and_stop_are_frozen():
    r,_=packet()
    assert r['status']=='TWO_SIDED_SCALAR_OWNER_NOT_YET_DERIVED'
    assert r['center_75_rank'] is None and r['inverse_replay'] is None
    for name in ('center_75_system_formed','physical_child_tangent_changed','boundary_split_changed',
                 'reaction_replay_repeated','nonlinear_work_attempted','scientific_producers_run',
                 'Gate7_closed','FULL_BHSM_COMPLETE'):
        assert r[name] is False
    for name,sha in r['source_SHA256'].items():assert d.digest(d.ROOT/name)==sha
    assert d.digest(OUT/'arrays.npz')==r['arrays_SHA256']
