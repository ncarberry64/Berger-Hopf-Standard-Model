"""Actual temporal/reset rows of a supplied complex two-arm action pair.

This retains the historical represented velocity-trial cotangent map and
its explicit scope. It does not turn a held affine parent into a solved
canonical parent, or select a physical formation reference/first hit.
"""
from __future__ import annotations
import numpy as np
from .aether_exact_radial_schur_lift_v15_83 import Jet
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from .muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt,holomorphic_geometry_rows
from .muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from .muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_parent_maxwell_full_weak import M,FIELD_ORDER
from .aether_full_reset_action_jacobian import _attachment_jacobian_at_order,_trace_jacobian_at_order,_symmetric_power


def _log(a):
    return Jet(np.log(a.value),a.gradient/a.value,a.hessian/a.value-np.outer(a.gradient,a.gradient)/a.value**2)


def holomorphic_moving_trace(raw):
    q,v,m,delta,dr,wall,Cstar=_geometry_variables(np.asarray(raw,complex)[:100]);F=_fields(12,q,v,m,wall)
    C,A,B=(F[k]for k in ('C','A','B'));R=A*B/_sqrt(A*A+B*B)
    trace=[_log(C)-np.log(RADIUS0),_log(A)-np.log(RADIUS0)+np.log(2)/2,_log(B)-np.log(RADIUS0)+np.log(2)/2]
    q0=Jet.affine(np.asarray(raw,complex)[0],np.eye(100)[0]);qw=_log(2*R/RADIUS0);attachment=[qw,q0-qw]
    values=trace+[attachment[1]]
    return dict(value=np.array([a.value for a in values]),first=np.array([a.gradient for a in values]),
        second=np.array([a.hessian for a in values]),attachment_first=np.array([a.gradient for a in attachment]),
        attachment_second=np.array([a.hessian for a in attachment]))


def holomorphic_reference_work_first(raw,rep,action):
    """Differentiate the owned anchored reference-clock work, not L_t."""
    raw=np.asarray(raw,complex);fields=action['branch_fields'][1]
    geo=holomorphic_geometry_rows(raw[1,:100],rep['rho']);parent=holomorphic_geometry_rows(raw[0,:100],rep['rho'],connection_only=True)
    keys=('electric','radial','angular','electric_radial','shift')
    density=np.array([[a[k].value for k in keys]for a in geo['rows']])
    A,At,Ar=(fields[k]for k in ('A','At','Ar'));local=analytic_constant_maxwell_batch(A,At,Ar,density)
    gd=np.empty((len(A),60,5),complex)
    for k in range(4):
        c=np.zeros_like(density);c[:,k]=1;c[:,4]=density[:,4];gd[:,:,k]=analytic_constant_maxwell_batch(A,At,Ar,c)['gradient']
    p=density.copy();m=density.copy();p[:,4]+=1;m[:,4]-=1
    gd[:,:,4]=(analytic_constant_maxwell_batch(A,At,Ar,p)['gradient']-analytic_constant_maxwell_batch(A,At,Ar,m)['gradient'])/2
    gb=np.asarray(rep['gauge_basis'])[:,:,0].reshape(len(A),80,20);gr=np.asarray(rep['gauge_radial_basis'])[:,:,0].reshape(len(A),80,20)
    gradient=np.zeros(536,complex)
    for j,w in enumerate(rep['radial_quadrature']):
        J=np.zeros((60,536),complex);J[:20,368:448]=gb[j].T;J[20:40,448:528]=gb[j].T;J[40:,368:448]=gr[j].T
        for k,key in enumerate(('connection_lambda','lambda_tau','lambda_rho')):
            J[k*20+8:(k+1)*20,:100]=M.reshape(12,1)*parent['rows'][j][key].gradient[None,:]
        test=np.zeros(60,complex);test[28:40]=M.reshape(-1)*action['profile_reference_difference'][j,1]
        dg=J.T@local['hessian'][j]@test
        density_first=np.array([geo['rows'][j][k].gradient for k in keys])
        dg[268:368]+=density_first.T@gd[j].T@test
        gradient+=w*MAXWELL_TO_CAP*dg
    return action['master_lift'].T@gradient


def holomorphic_two_arm_reset(raw_pair,reference_pair,rep,state_weights,normalization_coordinates,*,
        nu_squared_action=4,surface_gamma=None,compute_projected_derivative=False,difference_step=2e-5):
    raw=np.asarray(raw_pair,complex);a=holomorphic_two_arm_action(raw,reference_pair,rep,
        nu_squared_action=nu_squared_action,surface_gamma=surface_gamma)
    R=a['master_lift'];P=a['one_lift'];n=106;nm=252;vi=a['velocity_indices'];yi=a['algebraic_indices'];G=a['gradient'];H=a['hessian']
    traces=[holomorphic_moving_trace(x)for x in raw];xi=np.r_[np.arange(n),252+np.arange(n)]
    B=np.zeros((6,212),complex);DB=np.zeros((504,6,212),complex)
    for arm,tr in enumerate(traces):
        r=arm*268+np.arange(100)
        B[2*arm:2*arm+2]=tr['attachment_first']@R[np.ix_(r,xi)]
        DB[:,2*arm:2*arm+2]=np.einsum('aki,kj,il->jal',tr['attachment_second'],R[r],R[np.ix_(r,xi)],optimize=True)
    B[4,37]=B[5,n+37]=1
    A=H[np.ix_(vi,vi)];C=H[np.ix_(yi,vi)];Q=np.vstack((B,C))
    K=np.block([[A,Q.T],[Q,np.zeros((86,86),complex)]])
    scale=1/np.sqrt(np.maximum(np.max(abs(K),axis=1),np.finfo(float).tiny))
    rhs=np.zeros((298,6),complex);rhs[212:218]=np.eye(6)
    solution=scale[:,None]*np.linalg.solve(scale[:,None]*K*scale[None,:],scale[:,None]*rhs)
    ell=solution[:212];theta=a['temporal_cotangent'];theta_first=a['temporal_cotangent_first']
    dual_rhs=np.r_[theta,np.zeros(86,complex)];adjoint=scale*np.linalg.solve(scale[:,None]*K.T*scale[None,:],scale*dual_rhs)
    common=np.zeros((6,3));common[[0,2],0]=1;common[[1,3],1]=1;common[[4,5],2]=1
    projected=common.T@(ell.T@theta)
    ag=a['area_gradient_per_gamma'];ah=a['area_Hessian_per_gamma'];Ca=ah[np.ix_(yi,vi)];dQ=np.vstack((np.zeros((6,212)),Ca))
    dK=np.block([[ah[np.ix_(vi,vi)],dQ.T],[dQ,np.zeros((86,86))]])
    projected_area=common.T@(ell.T@a['area_temporal_cotangent_per_gamma']-adjoint@dK@solution)
    projected_first=np.zeros((3,504),complex);directional=[]
    if compute_projected_derivative:
        # Exact analytic transpose placement; only these third-action
        # contractions use centered holomorphic Hessian differences.
        av=np.zeros(504,complex);av[vi]=adjoint[:212];av[yi]=adjoint[218:]
        ay=np.zeros(504,complex);ay[yi]=adjoint[218:]
        b=np.zeros((504,6),complex);b[vi]=ell;b[yi]=solution[218:]
        by=np.zeros_like(b);by[yi]=solution[218:]
        rawweights=np.tile(np.r_[state_weights,np.ones(170)],2);mw=abs(R.T)@rawweights
        eta=R.T@raw.reshape(-1)
        def derivative(d):
            magnitude=float(np.max(abs(mw*d)))
            if magnitude==0:return np.zeros_like(H)
            unit=d/magnitude
            plus=holomorphic_two_arm_action((R@(eta+difference_step*unit)).reshape(2,268),reference_pair,rep,
                nu_squared_action=nu_squared_action,surface_gamma=surface_gamma)['hessian']
            minus=holomorphic_two_arm_action((R@(eta-difference_step*unit)).reshape(2,268),reference_pair,rep,
                nu_squared_action=nu_squared_action,surface_gamma=surface_gamma)['hessian']
            directional.append(dict(unit=unit,magnitude=magnitude,step=difference_step))
            return magnitude*(plus-minus)/(2*difference_step)
        third=derivative(av)@b-derivative(ay)@by
        contact=np.empty((504,6),complex)
        for j,db in enumerate(DB):contact[j]=adjoint[:212]@db.T@solution[212:218]+adjoint[212:218]@db@ell
        projected_first=common.T@(theta_first.T@ell-third-contact).T
    rows=[];jac=[];area_source=[];groups={}
    def add(name,value,first,source):
        value=np.atleast_1d(value);start=len(rows);rows.extend(value);jac.extend(np.atleast_2d(first));area_source.extend(np.atleast_1d(source));groups[name]=list(range(start,len(rows)))
    for arm,name in enumerate(('incoming','child')):
        indices=yi[arm*40:(arm+1)*40];s=np.r_[1/np.asarray(state_weights)[74:98],np.ones(16)]
        add(name+'_constraints',s*G[indices],s[:,None]*H[indices],s*ag[indices])
    eta=R.T@raw.reshape(-1);v=np.zeros(504,complex);v[vi]=eta[vi]
    E=v@G-a['value'];dE=H.T@v-G;dE[vi]+=G[vi]
    pg=a['parent']['gradient'];ph=a['parent']['hessian'];pv=np.zeros(252,complex);pv[n:2*n]=eta[n:2*n]
    Ep=pv@pg-a['parent']['value'];dEp=np.zeros(504,complex);dEp[:252]=ph.T@pv-pg;dEp[n:2*n]+=pg[n:2*n]
    area_parent=ag[:252];area_parent_value=original_endpoint_area_value(raw[0],P)
    Ep_area=pv@area_parent-area_parent_value;Earea=v@ag-a['area_value_per_gamma']
    work_first=holomorphic_reference_work_first(raw,rep,a)
    add('incoming_energy',Ep,dEp,Ep_area);add('child_energy',E-Ep-a['reference_clock_work'],dE-dEp-work_first,Earea-Ep_area)
    dynamic=a['constant_profile_child']['coordinates']['dynamic_gauge_indices'];labels=rep['gauge_labels'];affine=np.zeros(64)
    for j,i in enumerate(dynamic):
        label=labels[i];f=FIELD_ORDER.index(label['field'])
        if f>=2 and label['internal']==f-2:affine[j]=np.sqrt(8)*rep['affine_difference_coefficients'][label['radial']]
    for name,ids,offset,positions in (('gauge',100+dynamic,affine,np.arange(38,102)),('Higgs',np.arange(260,264),np.zeros(4),np.arange(102,106))):
        T=np.zeros((len(ids),536),complex);T[:,ids]=-np.eye(len(ids));T[:,268+ids]=np.eye(len(ids))
        add(name+'_trace',raw[1,ids]-raw[0,ids]-offset,T@R,np.zeros(len(ids)))
        add(name+'_temporal_dual',theta[positions]+theta[106+positions],theta_first[positions]+theta_first[106+positions],
            a['area_temporal_cotangent_per_gamma'][positions]+a['area_temporal_cotangent_per_gamma'][106+positions])
    baseB=_attachment_jacobian_at_order(12,normalization_coordinates);T0=np.vstack((_trace_jacobian_at_order(12),baseB[1]))
    norm=_symmetric_power(T0@np.diag(1/np.asarray(state_weights)[:37]**2)@T0.T,-.5)
    T=np.zeros((4,536),complex);T[:,:100]=-traces[0]['first'];T[:,268:368]=traces[1]['first']
    add('moving_geometric_trace',norm@(traces[1]['value']-traces[0]['value']),norm@T@R,np.zeros(4))
    T=np.zeros(536,complex);T[366]=1;T[98]=-1
    add('normal_position_trace',raw[1,98]-raw[0,98],T@R,0)
    attachment_norm=_symmetric_power(baseB@baseB.T,.5)
    add('common_attachment_temporal_dual',attachment_norm@projected[:2],attachment_norm@projected_first[:2],attachment_norm@projected_area[:2])
    add('common_normal_temporal_dual',projected[2],projected_first[2],projected_area[2])
    return dict(residual=np.asarray(rows),jacobian=np.asarray(jac),area_parameter_source=np.asarray(area_source),groups=groups,action=a,
        projected_cotangent=projected,projected_area_cotangent=projected_area,projected_saddle=K,projected_solution=solution,
        projected_adjoint=adjoint,projected_saddle_residual=K@solution-rhs,projected_adjoint_residual=K.T@adjoint-dual_rhs,
        reference_clock_work_first=work_first,trace_B=B,trace_DB=DB,trace_values=np.array([tr['value']for tr in traces]),
        parent_energy=Ep,child_energy=E-Ep-a['reference_clock_work'],full_Jacobian_evaluated=compute_projected_derivative,
        projected_third_action_directions=directional,held_pair_full_reset_stationarity_claimed=False,
        projection_scope='historical constrained velocity trial A=Lvv,C=Lyv with y held; not replacement of full true-Lyy temporal Legendre response')


def original_endpoint_area_value(raw,P):
    from .muon_complex_endpoint_area_action import original_endpoint_area_coefficient
    return original_endpoint_area_coefficient(raw,P)['value']
