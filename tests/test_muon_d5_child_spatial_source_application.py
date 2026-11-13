"""Pure gauge source linearity on the retained original child background."""
from pathlib import Path
import json
import numpy as np
import pytest
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_child_spatial_source_application import evaluate_child_spatial_source

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def child_inputs():
    folder=ROOT/'artifacts/muon_retained_response_20261018/inputs'
    metadata=json.loads((folder/'history_metadata.json').read_bytes())['sides']['outgoing']
    with np.load(folder/'outgoing_history.npz',allow_pickle=False) as z:
        t=np.array([s['time'] for s in metadata])
        raw=np.array([z[s['label']+'_raw_fields'] for s in metadata])
        rate=np.array([z[s['label']+'_raw_coordinate_time_derivative'] for s in metadata])
    history=recovered_export_history(ROOT,'outgoing',t,raw,rate)[0]
    with np.load(ROOT/'artifacts/muon_d5_valid_domain_application_20261019/domain_core/arrays.npz',allow_pickle=False) as z:
        child={key:z[key].copy(order='K') for key in z.files}
    return history,child


def test_wall_gauge_append_preserves_geometry_and_retains_every_free_rotation(child_inputs):
    history,child=child_inputs;rng=np.random.default_rng(901)
    field=np.zeros((4,268));free=np.zeros((4,268,6))
    field[:,168:180]=rng.normal(size=(4,12))*1e-4
    free[:,168:180]=rng.normal(size=(4,12,6))*1e-3
    result,report=evaluate_child_spatial_source(history,child,field,free)
    doubled,_=evaluate_child_spatial_source(history,child,field*2,free*2)
    assert report['additional_geometry_density_chart_source_from_pure_gauge_exact_max']==0
    assert report['normal_or_birth_domain_recomputed'] is False
    assert report['candidate_selected_as_physical_map'] is False
    assert result['child_field_source_columns268'].shape==(268,14)
    for candidate in (2,3):
      for side in ('plus','minus'):
       for branch in ('particle','conjugate'):
        prefix='candidate'+str(candidate)+'_child_'+side+'_'+branch+'_'
        for key in ('time','normal'):
            np.testing.assert_array_equal(result[prefix+key+'_spatial_field_additional_source64'],0)
        body=result[prefix+'body_spatial_field_additional_source64']
        assert body.shape==(7,64,64)
        assert np.count_nonzero(np.sum(abs(body),axis=(1,2)))==7
        np.testing.assert_allclose(doubled[prefix+'body_spatial_field_additional_source64'],body*2,atol=0,rtol=0)
        np.testing.assert_allclose(result[prefix+'body_corrected_particular_source64'],child['child_'+side+'_'+branch+'_body_source64']+body[0])


def test_geometry_or_velocity_change_is_not_silently_a_wall_gauge_append(child_inputs):
    history,child=child_inputs;field=np.zeros((4,268));free=np.zeros((4,268,6))
    field[2,98]=1e-8
    with pytest.raises(ValueError,match='only the original12'):
        evaluate_child_spatial_source(history,child,field,free)
