"""Ensure reaction projection cannot hide intrinsic shooting/history response."""
import json
import sys
from pathlib import Path

import numpy as np
from flint import arb,ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import compare_n12_gate7_reduced_fiber_tangents as d

OUT=d.ROOT/d.BASE/'gate7_reduced_fiber_tangents_20260926'


def packet():
    r=json.loads((OUT/'report.json').read_bytes())
    with np.load(OUT/'arrays.npz') as z:a={k:z[k] for k in z.files}
    return r,a


def test_full_schur_response_contains_intrinsic_component():
    ctx.prec=512;r,a=packet()
    np.testing.assert_allclose(a['reduced_Schur']@a['p_response'],-a['intrinsic_forcing'],rtol=0,atol=1e-18)
    np.testing.assert_allclose(a['intrinsic_component']+a['reaction_component'],a['full_response'],rtol=0,atol=1e-18)
    assert arb(r['intrinsic_coordinate_response_lower_exact'])>arb('9e-6')
    assert arb(r['intrinsic_Schur_forcing_lower_exact'])>arb('9e-6')
    assert r['full_linearized_shooting_change']['approximate_upper']<1e-140


def test_vertical_replay_error_is_not_full_response():
    r,a=packet()
    assert r['raw_error_lift_intrinsic_residual']['approximate_upper']<1e-140
    assert r['fixed_p_q_only_p_equation_residual']['approximate_upper']>9e-6
    np.testing.assert_allclose(a['right_projector']@a['raw_reaction_error_lift'],0,rtol=0,atol=1e-17)
    assert np.linalg.norm(a['right_projector']@a['full_response'])>9e-6


def test_endpoint_agreement_does_not_imply_history_agreement():
    r,a=packet()
    x=a['original_reduced_pair'];y=a['owner_consistent_reduced_pair']
    np.testing.assert_allclose(x[:98],y[:98],rtol=0,atol=1e-14)
    assert np.linalg.norm(x[98:]-y[98:])>9e-6
    assert d.comparison(x,y)==r['paired_history_reduced_tangent_comparison']
    assert r['endpoint_reduced_tangent_comparison']['projector_operator_residual']<1e-13
    assert r['paired_history_reduced_tangent_comparison']['projector_operator_residual']>2e-6
    assert arb(r['paired_projector_Frobenius_lower_exact'])>arb('2.9e-6')
    assert r['paired_history_reduced_tangent_comparison']['owner_consistent_rank']==66


def test_authority_and_stop_flags():
    r,_=packet()
    assert r['status']=='STOP_INTRINSIC_HISTORY_TANGENT_COMPONENT_REMAINS'
    assert r['frozen_owner_classification']=='EULER_DIRAC_DESCRIPTOR_FIBER_OWNER_RECOVERED'
    old=json.loads((d.ROOT/d.BASE/d.PACKETS['appended']/'report.json').read_bytes())
    assert r['frozen_allowance_exact']==old['descriptor_allowance_exact']
    for name in ('center_certificate_promoted','representation_only_reclassification_allowed',
                 'Layer_C_rebound','nonlinear_work_performed','scientific_producers_run',
                 'tolerances_changed','center_relocated','Gate7_closed','FULL_BHSM_COMPLETE'):
        assert r[name] is False
    for name,sha in r['source_SHA256'].items():assert d.digest(d.ROOT/name)==sha
    assert d.digest(OUT/'arrays.npz')==r['arrays_SHA256']
