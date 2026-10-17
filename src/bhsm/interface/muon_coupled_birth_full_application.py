"""All-row birth application and complete signed common-geometry ports.

The port basis has two attachment amplitudes and one proper-normal
amplitude. It is a computational basis, not an action-selected event
mode. Its frozen coefficient form is not a chronological H_form.
"""
import numpy as np
from .muon_complex_paired_normal_action import (
    _balanced_solver, analytic_frequency_polynomial, complex_proper_normal_trace,
)


def trace_action_forms(action_matrix, trace_map, named_frames, common, sectors, parameter):
    """Full bordered response with independently solved transpose left.

    All prescribed ports remain a matrix. Natural attachment elimination
    is exported separately; no zero traction is imposed on the base.
    """
    A, E, F, C, dA = [np.asarray(x, complex) for x in
                       (action_matrix, trace_map, named_frames, common, parameter)]
    n = len(A)
    if A.shape != (n,n) or dA.shape != A.shape or E.ndim != 2 or F.ndim != 2:
        raise ValueError('complete signed matrix and original trace/frame rows required')
    if E.shape[1] != n or F.shape[1] != n or C.shape[0] != len(E):
        raise ValueError('same-domain common trace and named frame maps required')
    Q = np.vstack((E,F)); K = np.block([[A,Q.T],[Q,np.zeros((len(Q),len(Q)),complex)]])
    rhs = np.zeros((len(K), C.shape[1]), complex); rhs[n:n+len(E)] = C
    solve, balance = _balanced_solver(K)
    right, left = solve(rhs), solve(rhs, True)
    dK = np.zeros_like(K); dK[:n,:n] = dA
    dr, dl = solve(-dK@right), solve(-dK.T@left, True)
    u, v = right[:n], left[:n]
    forms = {name:v.T@np.asarray(matrix,complex)@u for name,matrix in sectors.items()}
    total = v.T@A@u
    derivative = dl[:n].T@A@u + v.T@dA@u + v.T@A@dr[:n]
    return dict(saddle=K,rhs=rhs,right=right,left=left,
        original_right_rows=K@right-rhs,original_left_rows=K.T@left-rhs,
        common_action_form=total,common_action_parameter=derivative,
        right_parameter=dr,left_parameter=dl,
        parameter_right_rows=K@dr+dK@right,parameter_left_rows=K.T@dl+dK.T@left,
        border_action_identity=total+C.T@right[n:n+len(E)],
        sector_forms=forms,sector_sum_difference=sum(forms.values())-total,
        trace_map=E,named_frames=F,common_trace_map=C,
        balanced_condition=float(np.linalg.cond(balance)),analytic_dual_conjugated=False)


def attachment_schur(form):
    """Conditional free-attachment reduction of the complete 3-port form."""
    A=np.asarray(form,complex)
    if A.shape!=(3,3):raise ValueError('complete attachment2 plus normal1 matrix required')
    lift=np.r_[-np.linalg.solve(A[:2,:2],A[:2,2]),1+0j]
    return dict(normal_form=lift.T@A@lift,normal_lift=lift,
                attachment_natural_rows=(A@lift)[:2],physical_section_selected=False)


def complete_birth_geometry_ports(application,raw_pair,representation):
    """Keep proper traces, all fields/Lyy, and parent drive separately."""
    a=application['action']; raw=np.asarray(raw_pair,complex)
    P=a['one_lift']; H=a['hessian']; Ha=a['area_Hessian_per_gamma']
    n,m=106,40; order=np.r_[np.arange(n),252+np.arange(n),n+np.arange(n),
                            252+n+np.arange(n),2*n+np.arange(m),252+2*n+np.arange(m)]
    Ho=H[np.ix_(order,order)]; Hao=Ha[np.ix_(order,order)]
    Hp=np.zeros_like(H);Hp[:252,:252]=a['parent']['hessian'];Hp=Hp[np.ix_(order,order)]
    traces=[complex_proper_normal_trace(x,P) for x in raw]
    B=np.zeros((6,212),complex)
    B[:3,:106]=traces[0]['trace'];B[3:,106:]=traces[1]['trace']
    E=np.c_[B,np.zeros((6,80),complex)]
    common=np.vstack((np.eye(3),np.eye(3)))
    phase=np.r_[a['velocity_indices'],a['algebraic_indices']]
    D=H[np.ix_(phase,phase)];Da=Ha[np.ix_(phase,phase)]
    Dp=np.zeros_like(D)
    local=np.r_[np.arange(106,212),np.arange(212,252)]
    pphase=np.r_[np.arange(106),212+np.arange(40)]
    Dp[np.ix_(pphase,pphase)]=a['parent']['hessian'][np.ix_(local,local)]
    kinetic=trace_action_forms(D,E,application['named_frame_map'],common,
                             dict(parent=Dp,inherited_child=D-Dp),Da)
    static=np.zeros((8,292),complex)
    coordinates=a['constant_profile_child']['coordinates'];labels=representation['gauge_labels']
    Ar=[j for j,i in enumerate(coordinates['dynamic_gauge_indices'])
        if labels[i]['field']=='A_rho' and labels[i]['internal']==3]
    if len(Ar)!=4:raise ValueError('original four central radial coordinates per arm required')
    for arm in range(2):static[arm*4+np.arange(4),arm*106+38+np.asarray(Ar)]=1
    pol=analytic_frequency_polynomial(Ho,212);pa=analytic_frequency_polynomial(Hao,212)
    pp=analytic_frequency_polynomial(Hp,212)
    restoring=trace_action_forms(pol[0],E,static,common,
                               dict(parent=pp[0],inherited_child=pol[0]-pp[0]),pa[0])
    lapse=traces[1]['induced_lapse']
    I=lapse*kinetic['common_action_form'];R=-restoring['common_action_form']/lapse
    return dict(kinetic=kinetic,restoring=restoring,ordering=order,
        proper_inertia_matrix=I,proper_restoring_matrix=R,
        proper_inertia_parameter=lapse*kinetic['common_action_parameter'],
        proper_restoring_parameter=-restoring['common_action_parameter']/lapse,
        proper_parent_inertia=lapse*kinetic['sector_forms']['parent'],
        proper_child_inertia=lapse*kinetic['sector_forms']['inherited_child'],
        proper_parent_drive=restoring['sector_forms']['parent']/lapse,
        proper_child_resistance=-restoring['sector_forms']['inherited_child']/lapse,
        parent_trace=traces[0],child_trace=traces[1],child_readout_lapse=lapse,
        conditional_attachment_inertia=attachment_schur(I),
        conditional_attachment_restoring=attachment_schur(R),
        coefficient_freezing=True,formation_section_or_physical_domain_selected=False)
