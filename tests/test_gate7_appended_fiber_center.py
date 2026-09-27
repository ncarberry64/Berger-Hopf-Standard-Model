"""Appended stored-matrix inverse and fiber-consistent reaction regression."""
import json
import sys
from pathlib import Path

import numpy as np
from flint import arb,ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import test_n12_gate7_appended_fiber_center as d

OUT=d.ROOT/d.BASE/'gate7_appended_fiber_center_20260926'


def packet():
    r=json.loads((OUT/'report.json').read_bytes())
    with np.load(OUT/'arrays.npz') as z:a={k:z[k] for k in z.files}
    return r,a


def test_appended_row_inverse_and_old_null():
    ctx.prec=512;r,a=packet();A=d.amat(a['appended_matrix']);R=d.amat(a['inverse_proposal'])
    for label,product in [('left',R*A),('right',A*R)]:
        defect=d.bound(d.identity(75)-product)
        assert arb(defect['exact_upper'])<=arb(r['inverse_'+label+'_defect']['exact_upper'])<1
    np.testing.assert_array_equal(a['appended_matrix'][-1],np.r_[-1.,np.zeros(74)])
    assert a['old_null_image'][-1,0]==-1
    assert np.linalg.norm(a['old_null_image'][:-1])<1e-15
    assert r['stored_coefficient_rank_certified']==75


def test_fiber_elimination_recovers_reaction_schur_block():
    r,a=packet();Q9=a['reaction9']
    eliminated=Q9[1:,1:]-Q9[1:,:1]@np.linalg.solve(Q9[:1,:1],Q9[:1,1:])
    np.testing.assert_array_equal(eliminated,a['recovered_Schur8'])
    assert r['Schur8_replay_defect']['approximate_upper']<1e-12
    assert not r['old_8x8_modified']


def test_total_left_history_forcing_is_not_silently_frozen():
    r,a=packet()
    np.testing.assert_array_equal(a['left_history_old'][:73],a['left_history_fiber_candidate'][:73])
    np.testing.assert_allclose(a['left_history_fiber_candidate'][73]-a['left_history_old'][73],
                               a['left_history_descriptor_adjustment'][0],rtol=0,atol=1e-17)
    np.testing.assert_allclose(a['forcing_fiber_candidate']-a['forcing_old'],a['forcing_adjustment'],rtol=0,atol=1e-17)
    assert r['original_reaction_replay']['approximate_upper']<1e-15
    assert r['new_reaction_equation_defect']['approximate_upper']<1e-15
    assert not r['descriptor_replay_passes']
    assert r['descriptor_error_exceeds_allowance']
    assert arb(r['descriptor_error_lower_exact'])>arb(r['descriptor_allowance_exact'])
    assert all(x['passes'] for x in r['boundary_rows'])


def test_owner_recovery_is_not_successful_center_certificate():
    r,_=packet()
    assert r['classification']=='EULER_DIRAC_DESCRIPTOR_FIBER_OWNER_RECOVERED'
    assert r['center_adjudication']=='FAIL_FROZEN_FIBER_VALUE_AND_DESCRIPTOR_REACTION_REPLAY'
    assert r['frozen_fiber_value']['upper_exact'].startswith('-')
    assert r['state_child_basis_unchanged'] and r['boundary_complement_unchanged']
    for name in ('exact_center_on_fiber','augmented_child_tangent_exactly_unchanged',
                 'complete_reaction_replay_passes','constant_residual_discarded','recentered',
                 'tolerances_changed','nonlinear_work_performed','scientific_producers_run',
                 'Gate7_closed','FULL_BHSM_COMPLETE'):
        assert r[name] is False
    for name,sha in r['source_SHA256'].items():assert d.digest(d.ROOT/name)==sha
    assert d.digest(OUT/'arrays.npz')==r['arrays_SHA256']
