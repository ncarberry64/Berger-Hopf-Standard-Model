import numpy as np
from bhsm.interface.muon_fixed_parent_fiber_admission import propagated_fiber_admission


def test_border_reaction_does_not_hide_incompatible_original_jacobi_rows():
    # The singular phase quadratic has a named border. An arbitrary
    # canonical momentum produces a genuine original algebraic defect.
    H=np.array([[2,0,0],[0,1,1],[0,1,1]],complex)
    a=propagated_fiber_admission([H],np.array([[0,1]],complex),[.1],np.eye(2,dtype=complex))
    assert np.max(abs(a['bordered358_tangent_rows']))<2e-15
    assert np.max(abs(a['named_frame_tangent_rows']))<2e-15
    assert np.max(abs(a['original_unbordered358_tangent_rows'][:,3:]))>.9
    assert np.max(abs(a['named_frame_reactions']))>.9
    assert a['original_unbordered_rows_cannot_be_replaced_by_bordered_success']
