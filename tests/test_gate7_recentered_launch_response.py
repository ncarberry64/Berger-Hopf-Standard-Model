"""Base-point separation, chart transport, and exact native composition."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
import bind_n12_gate7_recentered_launch_response as b

OUT=b.BASE/'gate7_launch_response_20260927'


def packet():
    ctx.prec=512
    return json.loads((OUT/'report.json').read_bytes()),b.r.load(OUT/'arrays.npz')


def zero(a):return all(v.contains(0) for v in a.entries())


def test_disjoint_event_center_forbids_reuse_of_old_native_derivative():
    report,a=packet()
    assert not report['historical_event_center_agrees']
    assert report['disjoint_coordinate_lower']>1
    delta=b.r.mat(a['historical_event_state_action']-a['corrected_state_action'])
    assert any(not v.contains(0) for v in delta.entries())
    assert report['old_node13_to_current']['approximate_upper']<3e-14
    assert report['first_five_reused_at_identical_certified_domain']


def test_exact_launch_reconstruction_and_new_constraint_tangent():
    report,a=packet();mat=b.r.mat
    with np.load(b.OLD/'arrays.npz') as old:
        assert zero(mat(a['historical_launch_state'])-b.amat(old['node_013_launch_state']))
    T=mat(a['launch_action']);DC=mat(a['constraint_derivative'])
    assert (T.nrows(),T.ncols())==(98,73)
    assert zero(DC*T)
    assert report['chart_constraint_replay']['approximate_upper']<1e-10
    assert report['chart_rank_certified']==73
    assert report['chart_rank_inverse_defect']['approximate_upper']<1
    defect=b.identity(73)-mat(a['chart_left_inverse_proposal'])*T
    assert b.bound(defect)['approximate_upper']<1


def test_transported_labels_and_slaved_descriptor():
    report,a=packet();mat=b.r.mat
    N=mat(a['constraint_normal']);Ci=mat(a['constraint_normal_inverse'])
    DC=mat(a['constraint_derivative']);old=mat(a['historical_launch_action'])
    first72=b.block(old,range(98),range(72))
    assert zero(b.block(mat(a['launch_action']),range(98),range(72))-(first72-N*Ci*DC*first72))
    local=b.r.load(b.CENTER/'uniform_inputs/left.npz')
    assert zero(mat(a['launch_descriptor'])-mat(local['covector'][None,:])*mat(a['launch_action']))
    assert 'NOT 66+7' in report['chart_parameter_order']


def test_full_native_chain_and_signed_sector_sum():
    report,a=packet();mat=b.r.mat
    J=mat(a['native_event_7x98']);T=mat(a['launch_action']);R=mat(a['response_7x73'])
    assert (R.nrows(),R.ncols())==(7,73)
    assert zero(R-J*T-mat(a['native_explicit_shape_7x73']))
    sectors=sum((mat(a[n+'_pulled_momentum']) for n in b.e.s.NAMES),arb_mat(2,73))
    assert zero(sectors-b.block(R,[3,4],range(73)))
    assert zero(mat(a['flux_replay']))
    assert report['conormal_replay']['inverse_defect']['approximate_upper']<1
    assert report['conormal_lift_vs_frozen_child']['approximate_upper']<1e-20


def test_no_material_environment_identity_inferred_from_recentering():
    report,a=packet()
    assert not report['material_environment_identity_proved']
    assert not report['historical_72_family_uniform_transport_proved']
    assert not report['boundary_reactions_solved']
    assert not report['Layer_C_rebound'] and not report['Gate7_closed']
    assert not report['FULL_BHSM_COMPLETE'] and not report['frozen_tolerances_changed']


def test_sources_and_repeat_hashes():
    report,_=packet();h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
    assert h(OUT/'arrays.npz')==report['arrays_SHA256']
    for p,sha in report['source_SHA256'].items():assert h(Path(p))==sha
    for name,item in json.loads((OUT/'reproduction.json').read_bytes())['files'].items():
        assert item['byte_identical'] and h(OUT/name)==item['SHA256']
