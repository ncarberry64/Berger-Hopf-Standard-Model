"""Regression checks for descriptor identity and the failed frozen fiber value."""
import json
import sys
from pathlib import Path

import numpy as np
from flint import arb,ctx,fmpq

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import adjudicate_n12_gate7_descriptor_fiber as d

OUT=d.ROOT/d.BASE/'gate7_descriptor_fiber_owner_20260926'


def packet():
    r=json.loads((OUT/'report.json').read_bytes())
    with np.load(OUT/'arrays.npz') as z:a={k:z[k] for k in z.files}
    return r,a


def test_same_functional_does_not_imply_center_fiber_membership():
    ctx.prec=512
    r,_=packet()
    assert r['descriptor_identity']=='SAME_EULER_DIRAC_DESCRIPTOR_PROVED'
    assert all(r['identity_checks'].values())
    n=r['node13'];s=fmpq(n['s13_exact'])
    eigen_upper=fmpq(n['lambda_owner']['upper_exact'])
    residual_upper=fmpq(n['residual_physical']['upper_exact'])
    assert eigen_upper < s
    assert residual_upper < 0
    assert abs(float(eigen_upper-s)-n['residual_physical']['midpoint'])<1e-28
    assert not n['center_satisfies_fiber']
    assert not n['binary64_eigensolve_used']
    assert not n['point_or_action_producer_rerun']
    assert arb(n['point_witness_radius_exact']) < arb('1e-120')


def test_null_derivative_comes_only_from_signed_descriptor():
    r,a=packet()
    with np.load(d.NULL/'arrays.npz') as z:
        assert np.all(z['null_endpoints_action_physical'][0,:98]==0)
        lo=fmpq(str(z['unit_null_lower_exact'][0]))
        hi=fmpq(str(z['unit_null_upper_exact'][0]))
    assert fmpq(r['covector']['null_proof_lower_exact']) == -hi
    assert fmpq(r['covector']['null_proof_upper_exact']) == -lo
    assert a['fiber_row_reduced_proof_diagnostic'][-1]==-1
    assert r['covector']['null_physical_midpoint']==-d.SCALE*a['unit_null'][0]


def test_child_and_boundary_row_evaluations_preserve_existing_directions():
    r,a=packet()
    with np.load(d.C/'binding/arrays.npz') as z:child=z['node_013_child_augmented']
    np.testing.assert_array_equal(a['fiber_row_reduced_proof_diagnostic']@child,a['child_replay_diagnostic'])
    np.testing.assert_array_equal(a['fiber_row_reduced_proof_diagnostic']@a['node13_boundary_directions_reduced'],a['boundary_replay_diagnostic'])
    assert a['node13_boundary_directions_reduced'].shape==(74,7)
    assert np.all(a['node13_boundary_directions_reduced'][-1]==0)
    assert r['covector']['boundary_duality_replay']['approximate_upper']<1e-12
    assert not r['covector']['child_tangent_compatibility_proved']


def test_fail_closed_and_source_hashes():
    r,_=packet()
    assert r['status']=='STOP_FROZEN_CENTER_OFF_DESCRIPTOR_FIBER'
    for key in ('row_appended','old_8x8_reextracted','reaction_replay_repeated','center_modified',
                'nonlinear_work_attempted','scientific_producers_run','Gate7_closed','FULL_BHSM_COMPLETE'):
        assert r[key] is False
    assert r['system_75_rank'] is None
    for name,sha in r['source_SHA256'].items():assert d.digest(d.ROOT/name)==sha
    assert d.digest(OUT/'arrays.npz')==r['arrays_SHA256']
