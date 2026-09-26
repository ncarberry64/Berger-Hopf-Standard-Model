"""Frozen null, owner separation, and fail-closed classification regressions."""
import ast
import json
import sys
from pathlib import Path

import numpy as np
from flint import arb, ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import classify_n12_gate7_local_null as c

OUT = c.ROOT/c.BASE/'gate7_local_null_classification_20260926'


def packet():
    r = json.loads((OUT/'report.json').read_bytes())
    with np.load(OUT/'arrays.npz') as z:
        arrays = {k:z[k] for k in z.files}
    return r, arrays


def test_unit_null_and_exact_source_identity():
    ctx.prec = 512
    r,a = packet()
    with np.load(c.LOCAL/'arrays.npz') as z:
        K = z['K_cut']
    error = c.bound(c.amat(K)*c.amat(a['unit_null'][:,None]))
    assert arb(error['exact_upper']) <= arb(r['stored_unit_null_replay']['exact_upper'])
    assert abs(np.linalg.norm(a['unit_null'])-1) < 1e-15
    assert a['unit_null'][0] > 0
    assert np.all(a['null_endpoints_action_physical'][0,:98] == 0)
    assert r['exact_unit_normalization_replay']['approximate_upper'] < 1e-140
    assert r['exact_unit_null_replay']['approximate_upper'] < 1e-140
    for name,sha in r['source_SHA256'].items():
        assert c.digest(c.ROOT/name) == sha
    assert c.digest(OUT/'arrays.npz') == r['arrays_SHA256']


def test_flow_projection_cannot_be_relabelled_as_lift():
    r,a = packet()
    f = a['flow_pair_reduced']
    dropped = np.r_[f[0,:73],np.zeros(75)]
    projected = np.r_[np.zeros(73),a['projected_flow_75_diagnostic']]
    np.testing.assert_array_equal(f.ravel(),projected+dropped)
    assert np.linalg.norm(dropped) > 0.99
    result = c.line_comparison(a['null_pair_reduced'],f.ravel())
    assert result == r['stored_forward_flow_comparison']['full_148_reduced_pair_comparison']
    assert result['unit_projection_residual'] > 0.99
    assert r['quotient_owner']['known_coupled_generator_angle'] is None
    assert not r['stored_forward_flow_comparison']['exact_lift_into_75_slice_exists']


def test_event_is_not_independent_descriptor_covector():
    r,a = packet()
    endpoints = a['null_endpoints_action_physical']
    event = np.einsum('ij,ij->i',a['diagnostic_event_covectors'],endpoints[:,:98])
    np.testing.assert_array_equal(event,r['event']['Dlambda_unit_null'])
    assert event[0] == 0 and endpoints[0,98] > 0
    np.testing.assert_array_equal((event-endpoints[:,98])/c.SCALE,
                                 r['event']['diagnostic_fiber_covector_on_null_proof_units'])
    # Regression of stored centers, NOT an outward transversality allowance.
    np.testing.assert_allclose(r['event']['Dlambda_Fs'],[1,1],rtol=1e-8,atol=0)
    assert r['environment']['E_on_null'] is None
    # Source-level independence of the actual interface from a carried s.
    source = c.ROOT/'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    owner = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_child_rows_at_order')
    assert [arg.arg for arg in owner.args.args] == ['order','child','event_coordinates','event_momentum','event_flux']
    assert not any(isinstance(n,ast.Name) and n.id in ('signed_descriptor','descriptor') for n in ast.walk(owner))


def test_child_boundary_split_reconstructs_without_discarding_reactions():
    r,a = packet()
    with np.load(c.SPLIT/'arrays.npz') as z:
        P = z['trial_transform']
    np.testing.assert_allclose(P@a['null_right_split'],a['unit_null'][1:],rtol=0,atol=2e-13)
    combined = a['null_state_child_oblique_component']+a['null_state_boundary_oblique_component']
    np.testing.assert_allclose(combined,a['null_endpoints_action_physical'][1,:98],rtol=0,atol=2e-13)
    assert r['projections']['right_boundary_oblique_action_norm'] > 5
    assert r['projections']['right_child_oblique_action_norm'] > 5
    assert r['classification'] == 'UNRESOLVED'
    assert r['status'] == 'UNRESOLVED_OWNER_SCALAR'
    assert r['quotient_matrix_rank'] is None and r['quotient_condition'] is None
    for name in ('quotient_or_environment_condition_imposed','old_8x8_extraction_repeated',
                 'center_reaction_replay_repeated','nonlinear_work_attempted',
                 'scientific_producers_run','Gate7_closed','FULL_BHSM_COMPLETE'):
        assert r[name] is False
