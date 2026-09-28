from pathlib import Path
import sys
import json
import numpy as np
from flint import ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from checkpoint_n12_gate7_66d_tangent_binding import restore,digest

BASE=ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928'


def test_fixed_s_direction_is_fiber_tangent_and_internal_response_replays():
    ctx.prec=512
    folder=BASE/'directional1'; report=json.loads((folder/'report.json').read_bytes())
    assert digest(folder/'arrays.npz')==report['arrays_SHA256']
    with np.load(folder/'arrays.npz') as z:
        assert restore(z,'augmented_rate')[98,0]>0
        assert restore(z,'fixed_s_direction')[98,0]==1
        assert restore(z,'fixed_s_curve_second')[98,0].contains(0)
        A=restore(z,'local_internal_jacobian');D=restore(z,'local_internal_first')
        X=restore(z,'local_internal_input_partial')
        assert all(v.contains(0) for v in (A*D+X).entries())
        assert restore(z,'replay_selected_fiber_tangent')[0,0].contains(0)
    assert report['uniform_correlated_remainder'] is None
    assert not report['prefix_overlap_certified']


def test_failed_chart_is_not_promoted_to_an_overlap_or_physical_failure():
    folder=BASE/'entry1099511627776'
    report=json.loads((folder/'report.json').read_bytes())
    assert report['status']=='LOCAL_COLLAR_FIELD_CHART_FAILED'
    assert report['error']=='descriptor speed does not exclude zero'
    assert report['first_initial_failure']['coordinate']==0
    assert len(report['initial_target_domain_failures'])==99
    assert not report['physical_failure_claim']
    assert report['prefix_cells_rebuilt']==0
