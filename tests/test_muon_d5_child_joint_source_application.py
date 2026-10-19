import numpy as np
import pytest
from bhsm.interface.muon_d5_child_joint_source_application import append_joint_child_source


def test_joint_phase_bulk_source_requires_a_new_application_if_nonzero():
    joint=dict(initial_candidate_index=[2],child_raw_field_Higgs_source_correction=np.zeros((1,268)),
        child_raw_field_Higgs_free_rotation_phase_coefficients=np.zeros((1,268,7)))
    joint['child_raw_field_Higgs_free_rotation_phase_coefficients'][0,168,6]=1.
    spatial=dict(child_raw_field_source_corrections=np.zeros((4,268)),
        child_raw_field_free_rotation_coefficients=np.zeros((4,268,6)))
    with pytest.raises(ValueError,match='phase changes a bulk gauge source'):
        append_joint_child_source(None,None,None,spatial,joint)
