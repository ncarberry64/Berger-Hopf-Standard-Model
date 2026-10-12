import numpy as np
from bhsm.interface.muon_stored_admission_correction import bounded_stored_admission_correction


def test_general_nonsymmetric_stage_and_independent_literal_transpose():
    rng=np.random.default_rng(957)
    n=9; A=rng.normal(size=(n,n))+.4j*rng.normal(size=(n,n))+6*np.eye(n)
    C=rng.normal(size=(2,n)); E=rng.normal(size=(n,2))+.2j
    K=np.block([[A,E],[C,np.zeros((2,2))]])
    rhs=rng.normal(size=n+2)+.3j*rng.normal(size=n+2)
    target=rng.normal(size=n+2)+.2j*rng.normal(size=n+2)
    start=np.linalg.solve(K,rhs); left_start=np.linalg.solve(K.T,target)
    right=bounded_stored_admission_correction(K,rhs,start,n,correction_count=1)
    left=bounded_stored_admission_correction(K.T,target,left_start,n,correction_count=1)
    assert right['exact_stored']['bordered_residual_upper']<1e-45
    assert left['exact_stored']['bordered_residual_upper']<1e-45
    r=right['arrays']['correction_solution_high']; p=left['arrays']['correction_solution_high']
    np.testing.assert_allclose(p@rhs,target@r,atol=3e-15)
    assert abs(p.conj()@rhs-target@r)>1e-3
    assert not right['rounded_original_rows_guard_passed']
    assert not left['rounded_original_rows_guard_passed']
