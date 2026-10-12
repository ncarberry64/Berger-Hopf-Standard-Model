"""Resumable original226 reset equations with full v/y phase response.

Two dependent rows are identified by the exact central gauge identities,
never by numerical singular vectors. Every original residual is exported
and checked after a nonlinear trial. The coordinate minimum-norm choice
is computational and is not a physical mode or formation selector.
"""
from __future__ import annotations
from itertools import combinations
import numpy as np
from .muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from .muon_holomorphic_two_arm_reset import holomorphic_two_arm_reset
from .muon_coupled_phase_trace_projection import coupled_phase_trace_projection,coupled_phase_trace_parameter
from .muon_complex_canonical_compatibility import canonical_central_frame
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .aether_full_reset_action_jacobian import _attachment_jacobian_at_order,_symmetric_power


def coupled_reset_application(raw,reference,rep,weights,normalization,*,
        action_parameters,compute_jacobian=True,difference_step=2e-5):
    base=holomorphic_two_arm_reset(raw,reference,rep,weights,normalization,**action_parameters)
    a=base['action'];R=a['master_lift'];phase=np.r_[a['velocity_indices'],a['algebraic_indices']]
    F=np.zeros((4,292),complex);Z=np.zeros((292,4),complex)
    for arm,x in enumerate(raw):
        frame=canonical_central_frame(x,rep);ids=np.r_[arm*106+np.arange(106),212+arm*40+np.arange(40)]
        F[np.ix_(arm*2+np.arange(2),ids)]=frame['named_frame_covectors'];Z[np.ix_(ids,arm*2+np.arange(2))]=frame['literal_generators']
    common=np.zeros((6,3));common[[0,2],0]=1;common[[1,3],1]=1;common[[4,5],2]=1
    projection=coupled_phase_trace_projection(a['hessian'][np.ix_(phase,phase)],np.c_[base['trace_B'],np.zeros((6,80))],F,
        np.r_[a['temporal_cotangent'],np.zeros(80)],common)
    parameter=coupled_phase_trace_parameter(projection,a['area_Hessian_per_gamma'][np.ix_(phase,phase)],
        np.r_[a['area_temporal_cotangent_per_gamma'],np.zeros(80)])
    groups=base['groups'];ai=groups['common_attachment_temporal_dual'];ni=groups['common_normal_temporal_dual']
    B=_attachment_jacobian_at_order(12,normalization);bn=_symmetric_power(B@B.T,.5)
    rows=base['residual'].copy();rows[ai]=bn@projection['common_trace_cotangent'][:2];rows[ni]=projection['common_trace_cotangent'][2]
    gamma=base['area_parameter_source'].copy();gamma[ai]=bn@parameter['common_trace_cotangent_parameter'][:2];gamma[ni]=parameter['common_trace_cotangent_parameter'][2]
    J=base['jacobian'].copy();direction=None;magnitude=0.
    if compute_jacobian:
        av=np.zeros(504,complex);av[phase]=projection['adjoint'][:292]
        b=np.zeros((504,6),complex);b[phase]=projection['phase_lift']
        mw=abs(R.T)@np.tile(np.r_[weights,np.ones(170)],2);magnitude=float(np.max(abs(mw*av)))
        eta=R.T@np.asarray(raw,complex).reshape(-1);direction=av/magnitude
        hp=holomorphic_two_arm_action((R@(eta+difference_step*direction)).reshape(2,268),reference,rep,**action_parameters)['hessian']
        hm=holomorphic_two_arm_action((R@(eta-difference_step*direction)).reshape(2,268),reference,rep,**action_parameters)['hessian']
        third=magnitude*(hp-hm)/(2*difference_step)@b
        theta_first=np.zeros((292,504),complex);theta_first[:212]=a['temporal_cotangent_first']
        contact=np.empty((504,6),complex)
        for j,db in enumerate(base['trace_DB']):
            de=np.c_[db,np.zeros((6,80))]
            contact[j]=projection['adjoint'][:292]@de.T@projection['port_reactions']+projection['adjoint'][292:298]@de@projection['phase_lift']
        port_first=common.T@(theta_first.T@projection['phase_lift']-third-contact).T
        J[ai]=bn@port_first[:2];J[ni]=port_first[2]
    return dict(residual=rows,jacobian=J,area_parameter_source=gamma,groups=groups,action=a,projection=projection,
        area_projection=parameter,literal_generators=Z,named_frame_map=F,
        full_phase_generator_image=projection['phase_Hessian']@Z,
        third_action_direction=direction,third_action_magnitude=magnitude,
        full_Jacobian_evaluated=compute_jacobian,historical_projection_used_as_full_phase_response=False)


def central_reset_Ward_rows(application,raw,rep):
    """Exact two central first-action identities in original reset rows.

    theta.GAt_p-theta.GAt_c +theta_r.(PiAr_p-PiAr_c)
    -theta_wall.(G Hp).(PiH_p-PiH_c)
    +theta_wall.(G.T PiH_c).(Hc-Hp)=0.
    """
    a=application;groups=a['groups'];profiles=enriched_central_profiles(rep);coordinates=a['action']['constant_profile_child']['coordinates']
    labels=rep['gauge_labels'];At=[j for j,i in enumerate(coordinates['At_indices'])if labels[i]['internal']==3]
    Ar=[j for j,i in enumerate(coordinates['dynamic_gauge_indices'])if labels[i]['field']=='A_rho'and labels[i]['internal']==3]
    theta=profiles['theta_coefficients'];D=profiles['radial_derivative_coefficients']
    wall=rep['wall_trace_map'][0,3,np.array(coordinates['At_indices'])[At]]@theta
    T=higgs_u2_real_representation()['real_generators'][3];L=np.zeros((2,226),complex)
    for sign,name in ((1,'incoming_constraints'),(-1,'child_constraints')):
        ids=np.array(groups[name])[24+np.array(At)];L[:,ids]=sign*theta.T
    L[:,np.array(groups['gauge_temporal_dual'])[Ar]]=D.T
    L[:,groups['Higgs_temporal_dual']]=-wall[:,None]*(T@np.asarray(raw)[0,260:264])[None,:]
    pchild=-a['action']['temporal_cotangent'][106+102:212]
    L[:,groups['Higgs_trace']]=wall[:,None]*(T.T@pchild)[None,:]
    candidates=np.array(groups['incoming_constraints'])[24+np.array(At)]
    pair=max(combinations(candidates.tolist(),2),key=lambda ids:abs(np.linalg.det(L[:,ids])))
    if abs(np.linalg.det(L[:,pair]))<1e-12:raise ValueError('named central profile minor must have structural rank2')
    keep=np.array([j for j in range(226)if j not in pair])
    return dict(rows=L,dependent_original_rows=np.array(pair),independent_original_rows=keep,
        original_nonlinear_identity=L@a['residual'],named_minor=L[:,pair],
        numerical_singular_vectors_used_to_choose_dependent_rows=False)


def complex_reset_chart(raw):
    from .muon_holomorphic_normal_geometry import _geometry_variables,_fields,anchored_holomorphic_chart
    records=[]
    for x in np.asarray(raw,complex):
        q,v,m,delta,dr,wall,C=_geometry_variables(x[:100],differentiate=False);F=_fields(12,q,v,m,wall)
        chart=anchored_holomorphic_chart(delta.value);U=F['C'].value*(dr.value+F['beta'].value)/F['N'].value
        records.append(dict(abs_delta=float(abs(delta.value)),monotonicity_margin=float(1-2*abs(chart['coefficients'][0])-6*abs(chart['coefficients'][1])),
            implicit_residual_max=float(np.max(abs(chart['implicit_residual']))),wall_velocity_real=float(U.real),wall_velocity_imag=float(U.imag)))
    return records
