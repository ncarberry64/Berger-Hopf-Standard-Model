"""Fresh sourced fixed-Y mass and full angular source-order applications."""
import numpy as np
import pytest
from bhsm.interface.muon_native_reached_response_heat import retained_current_reached_response,reached_fixed_y_source_vertices,reached_first_response_heat_core
from bhsm.interface.muon_native_coupled_source_heat import corrected_first_response_heat_application


def test_new_actual_scalar_response_and_current_normalization_are_consumed():
    response=retained_current_reached_response();v=reached_fixed_y_source_vertices(response,-.00088)
    assert np.linalg.norm(v['scalar'])>0
    assert np.linalg.norm(v['gauge'])>0
    assert v['source_motion_count']==1
    assert v['scalar_response_is_from_fresh_full_action']
    assert not response['old_original_Q8_H_response_used']
    np.testing.assert_allclose(v['scalar'],v['scalar'].conj().transpose(0,1,3,2),atol=1e-30)
    with pytest.raises(ValueError,match='extrapolation'):reached_fixed_y_source_vertices(response,.001)


def test_contact_and_both_orders_keep_actual_fresh_LR_response():
    response=retained_current_reached_response();core=reached_first_response_heat_core(response,time_nodes=np.linspace(-.001,0,5),quadrature_order=3,family_indices=(1,))
    packet=corrected_first_response_heat_application(core,4.7240808471919143e-8,integrate_cutoff=True)
    components=packet['families']['1']['components']
    assert np.linalg.norm(components['scalar']['reached_first_response_pair'])>0
    assert np.linalg.norm(components['interference']['reached_first_response_pair'])>0
    for row in components.values():
        np.testing.assert_allclose(row['reached_first_response_pair'],row['source_square_contact']+row['ordered_two_insertion']+row['opposite_order_two_insertion'],atol=1e-36,rtol=1e-14)
    assert packet['families']['1']['genuine_mixed_scalar_mean_contact'] is None
    assert not core['complete_native_heat_or_Pauli_evaluated']
