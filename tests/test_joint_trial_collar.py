from pathlib import Path
import sys
import json
import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from checkpoint_n12_gate7_66d_tangent_binding import digest, restore

PACKET = ROOT/'artifacts/flagship_integration/joint_trial_collar_20260928/run2'


def test_trial_collar_uses_current_reset_and_retains_event_defect():
    ctx.prec = 512
    report = json.loads((PACKET/'report.json').read_bytes())
    assert digest(PACKET/'arrays.npz') == report['arrays_SHA256']
    for path, expected in report['source_SHA256'].items():
        assert digest(ROOT/path) == expected, path
    assert report['eigenpair_proof']['validation_passed']
    assert report['eigenpair_proof']['selected_zero_based_index_verified'] == 24
    assert report['domain_inclusion']['state_excursion_upper'] < 1
    assert report['domain_inclusion']['descriptor_excursion_upper'] < 1
    with np.load(PACKET/'arrays.npz') as z:
        defect = restore(z, 'selected_event_descriptor_defect')[0, 0]
        assert defect < 0 and not defect.contains(0)
        assert restore(z, 'independent_event_descriptor')[0, 0] == 0
        assert not restore(z, 'old_prefix_radius_minus_current')[0, 0].contains(0)
        assert restore(z, 'proper_duration')[0, 0] > 0
    assert report['event_root_solved'] is False
    assert report['physical_amplitude_selected'] is False
    assert report['new_Jacobi_columns'] == 0


def test_directed_clock_inclusion_is_derived_from_same_field_domain():
    ctx.prec = 512
    with np.load(PACKET/'arrays.npz') as z:
        speed = restore(z, 'augmented_field_domain')[98, 0]
        norm = restore(z, 'arc_norm_domain')[0, 0]
        lapse = restore(z, 'lapse_domain')[0, 0]
        h = restore(z, 'arc_horizon')[0, 0]
        duration = restore(z, 'proper_duration')[0, 0]
        assert speed > 0 and norm > 0 and lapse > 0
        # This encloses the integral even though the point clock at r=0 is zero.
        recomputed = lapse*speed*h*h/(2*norm)
        assert (duration-recomputed).contains(0)
        assert duration.lower() > 0
