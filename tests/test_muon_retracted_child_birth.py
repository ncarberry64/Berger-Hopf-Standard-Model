import numpy as np
from bhsm.interface.muon_retracted_child_birth import retract_original_birth_rows


def test_retraction_holds_free_coordinates_and_all_original_dependent_rows():
    def app(u,jacobian):
        r=np.array([u[0]**2+u[1]-1,u[1]**2+u[2]-.2],complex)
        return dict(valid=True,residual=r,jacobian=np.array([[2*u[0],1,0],[0,2*u[1],1]],complex),
            all_original_rows=np.r_[r,(2+.3j)*r[0]])
    B=np.array([[0,0,1]],complex);start=np.array([.9,.01,.19],complex)
    a=retract_original_birth_rows(start,np.array([.19]),B,app,max_iterations=12,max_backtracks=6)
    assert a['status']=='ALL_ORIGINAL_BIRTH_ROWS_AND_FIXED_COORDINATES_TOLERANCE'
    assert np.max(abs(a['application']['all_original_rows']))<=2e-10
    assert abs(a['canonical_input'][2]-.19)<2e-15
    assert len(a['history'])>1
