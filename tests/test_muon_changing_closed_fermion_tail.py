import numpy as np
import pytest
from scipy.linalg import eigh
from scipy.special import exp1
from bhsm.interface.muon_native_even_y_remainder_certificate import certify_generalized_even_pencil,even_y_tail_bounds
from bhsm.interface.muon_changing_closed_fermion_mean import even_y_trace_duals


def test_even_tail_certificate_covers_actual_complete_trace_difference():
    K=np.diag([3.,7.]);C=np.array([[0,1.],[1.,0]]);B=np.diag([1.,2.]);G=np.eye(2)
    ev,U=eigh(K,G)
    c,record=certify_generalized_even_pencil(K,C,B,G,U,ev,[1,-1])
    t=even_y_tail_bounds(c,.2,.1,.03)
    q=even_y_trace_duals(K,C,B,G,.2)['even_Y2_coefficient']
    value=lambda y:sum(exp1(.2*eigh(K+y*C+y*y*B,eigvals_only=True)))
    error=abs(value(.1)-value(.03)-(.1**2-.03**2)*q)
    assert 0<error<t['value_tail_upper']['upper_binary64']
    assert record['exact_stored_Hermitian_and_LR_parity']


def test_even_tail_rejects_forbidden_grading_terms_without_erasing_them():
    K=np.diag([3.,7.]);C=np.eye(2);B=np.eye(2);G=np.eye(2);ev,U=eigh(K,G)
    with pytest.raises(ValueError,match='grading'):
        certify_generalized_even_pencil(K,C,B,G,U,ev,[1,-1])
