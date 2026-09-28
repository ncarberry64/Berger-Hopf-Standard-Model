"""Current base binding and local/history distinction for formation operands."""
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from checkpoint_n12_gate7_66d_tangent_binding import restore,digest
from assemble_n12_current_formation_local_operands import CANDIDATE
from bhsm.interface.aether_forward_boundary_radius import boundary_log_radius,proper_time_log_radius_rate

BASE=ROOT/'artifacts/flagship_integration/formation_op_current_20260928'


def test_exact_current_incoming_half_and_owned_geometry():
    with ctx.workprec(512), np.load(BASE/'local_run1/arrays.npz') as z, np.load(CANDIDATE) as c:
        state=restore(z,'current_incoming_state_raw')
        raw=c['joint_state_raw'][98:196]
        assert all(state[i,0].contains(arb(float(raw[i]))) for i in range(98))
        assert not np.array_equal(raw,c['joint_state_raw'][:98])
        x=float(restore(z,'incoming_log_R4')[0,0].mid())
        v=float(restore(z,'incoming_proper_log_radius_rate')[0,0].mid())
        assert abs(x-boundary_log_radius(12,raw[:37]))<1e-14
        assert abs(v-proper_time_log_radius_rate(12,raw[:37],raw[37:74],raw[74:]))<1e-14


def test_local_sector_sum_replays_original_action_at_current_point():
    r=json.loads((BASE/'local_run1/report.json').read_bytes())
    assert len(r['sectors'])==10
    assert r['replay']['value']['approximate_upper']<1e-140
    assert r['replay']['gradient']['approximate_upper']<1e-140
    assert r['replay']['local_Q66_Hessian']['approximate_upper']<1e-60
    with ctx.workprec(512), np.load(BASE/'local_run1/arrays.npz') as z:
        g=sum((restore(z,n+'_local_gradient_raw') for n in r['sectors']),arb_mat(98,1))
        assert all(v.contains(0) for v in (g-restore(z,'local_action_gradient_raw')).entries())


def test_endpoint_radius_fixed_does_not_freeze_lapse_or_radius_rate():
    with ctx.workprec(512), np.load(BASE/'dependency_run1_complete/arrays.npz') as z:
        dx=restore(z,'endpoint_log_radius_partial_66')
        lapse=restore(z,'endpoint_log_lapse_partial_66')
        rate=restore(z,'endpoint_proper_radius_rate_partial_66')
        assert max(float(abs(v).upper()) for v in dx.entries())<1e-60
        assert any(not v.contains(0) for v in lapse.entries())
        assert any(not v.contains(0) for v in rate.entries())


def test_no_local_operand_promoted_to_reduced_formation_output():
    r=json.loads((BASE/'local_run1/report.json').read_bytes())
    assert not r['complete'] and not r['stationary_solve_attempted']
    for key in ('formation_action_covector_66','formation_physical_hessian_66x66','formation_launch_forcing_66x73'):
        assert r[key] is None
    assert r['local_results_are_not_reduced_formation_derivatives']
    for first,second in (('local_run1','local_run2'),('dependency_run1_complete','dependency_run2')):
        for file in ('arrays.npz','report.json'):
            assert (BASE/first/file).read_bytes()==(BASE/second/file).read_bytes()
        report=json.loads((BASE/first/'report.json').read_bytes())
        assert digest(BASE/first/'arrays.npz')==report['arrays_SHA256']
        for path,sha in report['source_SHA256'].items():assert digest(ROOT/path)==sha
