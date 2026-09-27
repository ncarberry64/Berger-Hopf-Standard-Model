"""Scope, transversality and reproducibility of the new signed covector."""
import json
import sys
from pathlib import Path

import numpy as np
from flint import arb, ctx, fmpq

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_point_fiber_covector as c

OUT=c.BASE/'gate7_fiber_covector_20260927'


def packet():
    r=json.loads((OUT/'report.json').read_bytes())
    with np.load(OUT/'arrays.npz') as z:a={k:z[k] for k in z.files}
    return r,a


def balls(a,key):
    return [arb(str(m))+arb(0,arb(str(r))) for m,r in
            zip(a[key+'_mid_q'].flat,a[key+'_rad_q'].flat,strict=True)]


def test_signed_covector_and_uniform_transversality():
    ctx.prec=512;r,a=packet()
    point=balls(a,'gradient_action');tube=balls(a,'affine_tube_gradient_action')
    assert a['gradient_action_mid_q'].shape==(1,98)
    assert all(x.contains(y) for x,y in zip(tube,point,strict=True))
    assert tube[86]>0 and point[86]>0
    assert fmpq(r['affine_tube_coordinate86']['lower_exact'])>fmpq(2,10**6)
    assert r['covector_radius_Frobenius_upper']['approximate_upper']<1e-120


def test_covector_matches_independent_owned_contraction():
    r,_=packet()
    assert r['point_cpsi_contained_in_saved_uniform_contraction']
    cp=r['point_cpsi']
    assert fmpq(cp['lower_exact'])>fmpq(6,10**11)
    assert fmpq(cp['upper_exact'])<fmpq(8,10**11)
    assert r['branch_index']==24
    assert r['nonzero_derivative']['action_coordinate_zero_based']==86


def test_point_certificate_does_not_promote_history_or_enlarge_domain():
    r,_=packet()
    assert r['graph_center']['Y13_unchanged']
    assert r['graph_center']['shooting_root_certified'] is False
    assert r['graph_center']['constraints_root_certified'] is False
    for k in ('hessian_or_eigenpair_producer_rerun','finite_difference_used',
              'uniform_recentered_covector_certified','full_history_jet_certified',
              'Layer_C_rebound','tolerances_changed','Gate7_closed','FULL_BHSM_COMPLETE'):
        assert r[k] is False


def test_sources_and_replay_receipt():
    r,_=packet()
    for p,sha in r['source_SHA256'].items():assert c.digest(Path(p))==sha
    assert c.digest(OUT/'arrays.npz')==r['arrays_SHA256']
    receipt=json.loads((OUT/'reproduction.json').read_bytes())
    assert receipt['fresh_processes']==2
    for name,item in receipt['files'].items():
        assert item['byte_identical']
        assert c.digest(OUT/name)==item['SHA256']
