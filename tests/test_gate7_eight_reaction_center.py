"""Cheap frozen-algebra regressions; run with --noconftest."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from flint import arb, ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import diagnose_n12_gate7_eight_reaction_center as c


def load():
    report=json.loads((c.OUTPUT/'report.json').read_bytes())
    with np.load(c.OUTPUT/'arrays.npz') as z:
        arrays={k:z[k] for k in z.files}
    return report,arrays


def test_frozen_sources_and_saved_array_hash():
    report,_=load()
    for name,expected in report['source_SHA256'].items():
        with (c.ROOT/name).open('rb') as stream:
            assert hashlib.sha256(stream.read()).hexdigest().upper()==expected
    assert c.digest(c.OUTPUT/'arrays.npz')==report['arrays_SHA256']


def test_hessian_lift_does_not_substitute_euclidean_complement():
    ctx.prec=512
    H=c.amat(np.diag([2,5,7]))
    A=c.amat(np.array([[1,1,0]]))
    _,L=c.action_hessian_lift(c.identity(3),H,A)
    assert (L[0,0]-arb('5/7')).contains(0)
    assert (L[1,0]-arb('2/7')).contains(0)
    assert not (L[0,0]-arb('1/2')).contains(0)
    assert (A*L-c.identity(1))[0,0].contains(0)


def test_saved_transform_replays_original_center():
    ctx.prec=512
    report,z=load()
    with np.load(c.CAPSULE/'newton/M_13.npz') as source:
        M=c.amat(source['M_13'])
    N=c.amat(np.block([[z['M_pp'],z['M_pq']],[z['M_qp'],z['M_qq']]]))
    residual=c.frob(c.amat(z['trial_transform'])*N*c.amat(z['trial_transform_inverse'])-M)
    assert residual<=arb(report['stored_transform_roundtrip_error']['exact_upper'])
    assert z['M_pp'].shape==(66,66)
    assert z['M_pq'].shape==(66,8)
    assert z['M_qp'].shape==(8,66)
    assert z['M_qq'].shape==(8,8)
    assert z['Dphi_0_candidate'].shape==(8,66)


def test_stored_reaction_inverse_has_neumann_certificate():
    ctx.prec=512
    report,z=load()
    Q,R=map(c.amat,(z['M_qq'],z['M_qq_inverse']))
    assert c.frob(c.identity(8)-R*Q)<1
    assert c.frob(c.identity(8)-Q*R)<1
    for name in ('child','boundary','combined'):
        assert report['ranks'][name]['full_column_rank']


def test_descriptor_replay_failure_blocks_nonlinear_authority():
    ctx.prec=512
    report,_=load()
    assert arb(report['descriptor_replay_difference_lower'])>arb(report['descriptor_reprojection_allowance_upper'])
    assert report['status']=='STOP_CENTER_REACTION_REPLAY_FAILED'
    for key in ('center_slaving_validated','nonlinear_attempted','Gate7_closed','FULL_BHSM_COMPLETE'):
        assert report[key] is False
