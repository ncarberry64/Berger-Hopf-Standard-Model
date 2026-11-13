from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_electromagnetic_source_photon_action import executed_electromagnetic_photon_quadratic_action

ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('side',['incoming','outgoing'])
def test_actual_em_full_action_matches_canonical_temporal_minus_boundary_work(side):
    a=executed_electromagnetic_photon_quadratic_action(
        f'artifacts/muon_primal_electromagnetic_source_20261011/{side}_run_1',repository=ROOT)
    assert a['source_Higgs_aligned_electromagnetic']
    assert a['full_raw_vs_reduced_action_relative_difference']<3e-13
    assert np.linalg.norm(a['scalar_source_quadratic_action'])>0
    assert np.linalg.norm(a['Maxwell_source_quadratic_action'])>0
    assert np.array_equal(a['source_quadratic_action'],a['source_quadratic_action'].T)
    assert a['coordinate_time_interval']==([-1e-5,0.] if side=='incoming' else [0.,1e-5])
    assert not a['source_mode_or_soft_transfer_selected']


def test_old_transported_covectors_cannot_be_relabeled_electromagnetic():
    with pytest.raises(ValueError,match='executed complete same-background'):
        executed_electromagnetic_photon_quadratic_action(
            'artifacts/muon_attached_reached_action_20261011/incoming_run_1',repository=ROOT)
