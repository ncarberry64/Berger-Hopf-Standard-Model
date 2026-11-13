import numpy as np
from bhsm.interface.muon_inherited_normal_readout_frame import phase_normal_readout_frame
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_corrected_profile_magnetic_response import corrected_wall_reference


def test_actual_child_frame_retains_explicit_inherited_value_time_radial_application():
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    frame=phase_normal_readout_frame(phase,family=1,electric_charge=.30282212073695486)
    expected=corrected_wall_reference(frame['raw_fields'],phase['representation'],coordinate_time=0.,
        initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
    np.testing.assert_array_equal(frame['arguments']['wall_connection'],expected['background_values'][0])
    np.testing.assert_array_equal(frame['inherited_profile_value_time_radial'],expected['inherited_profile_value_time_radial'])
    assert frame['inherited_parent_and_reference_explicit']


def test_actual_parent_frame_does_not_add_a_child_profile_or_select_a_mass():
    phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1')
    frame=phase_normal_readout_frame(phase,family=2,electric_charge=.30282212073695486)
    assert not frame['inherited_parent_and_reference_explicit']
    assert not frame['physical_pole_or_unit_selected']
    np.testing.assert_array_equal(frame['arguments']['family_indices'],[4,5,10,11,16,17])
