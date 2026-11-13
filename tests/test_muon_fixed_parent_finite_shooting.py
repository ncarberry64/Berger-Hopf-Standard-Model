import numpy as np
from bhsm.interface.muon_fixed_parent_finite_shooting import complete_finite_action_work


def test_complete_boundary_action_keeps_initial_term_and_all_tail_rows():
    T=np.array([[1.2,.3],[.7,1.0083333333333333]],complex)
    E=np.eye(2,dtype=complex);N=np.eye(2,dtype=complex)
    x=np.array([.4]);p=np.array([.8]);end=T@np.r_[x,p];Y=np.array([[.15j]]);s=np.array([.2])
    supplied=np.array([.03j,-.01])
    a=complete_finite_action_work(T,E,N,x,p,end[:1],end[1:],Y,s,supplied)
    literal=T[:1].T@(end[1:]-Y@end[:1]-s)-np.array([p[0],0])+supplied
    assert np.max(abs(a['full_action_work']-literal))<1e-15
    assert np.linalg.norm(a['initial_cotangent_work'])>.5
    assert np.linalg.norm(a['terminal_only_work']-a['full_action_work'])>.5
    assert a['terminal_fiber_rank']==1
    assert a['projected_work_does_not_imply_full_tail_zero']
