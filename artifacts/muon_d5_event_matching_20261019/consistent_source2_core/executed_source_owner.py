"""Refine only consumed source fields while the completed V10 stays fixed.

The forcing is the literal original linearized D5 operator on the saved
value and its actual time/radial derivatives. No homogeneous source state,
physical normal mode, or value response is selected by this application.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import lu_factor,lu_solve

from .muon_d5_complement_bulk_response import _collocation_rule,_generator
from .muon_d5_temporal_bulk_refinement import coefficient_rows,time_evaluation_matrix,_factor_at
from .muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory,evaluate_event_normal_source


LABELS=('plus_seed','minus_seed','minus_LR','minus_RL')


def source_forcing_gauss_update(G,forcing,initial,step,A,initializer):
    """Solve the unchanged value-generator matrix for a new source forcing."""
    G,F,v0,A,guess=(np.asarray(a,complex) for a in (G,forcing,initial,A,initializer))
    q,d,k=F.shape
    if G.shape!=(q,d,d) or v0.shape!=(d,k) or A.shape!=(q,q) or guess.shape!=F.shape:
        raise ValueError('explicit complete source Gauss operands required')
    if not all(np.isfinite(a).all() for a in (G,F,v0,A,guess)):
        raise ValueError('finite source Gauss operands required')
    matrix=-step*np.einsum('ij,jab->iajb',A,G)
    for i in range(q):matrix[i,:,i,:]+=np.eye(d)
    matrix=matrix.reshape(q*d,q*d)
    rhs=np.broadcast_to(v0,F.shape)+step*np.einsum('ij,jdk->idk',A,F)
    before=rhs.reshape(q*d,k)-matrix@guess.reshape(q*d,k)
    correction=lu_solve(lu_factor(matrix),before).reshape(q,d,k)
    stage=guess+correction
    slopes=np.einsum('qij,qjk->qik',G,stage)+F
    return slopes,dict(initializer_stage_residual_max=float(np.max(abs(before))),
        corrected_stage_residual_max=float(np.max(abs(matrix@stage.reshape(q*d,k)-rhs.reshape(q*d,k)))),
        initializer_correction_norm=float(np.linalg.norm(correction)),value_equations_resolved=False)


def original_source_forcing(R,T,K,Rx,Tx,Kx,value,radial,time):
    """-R^-1[(delta R)V_r+(delta T)V_t+(delta K)V], without R V_r=-TV_t-KV."""
    R,T,K,Rx,Tx,Kx,V,Vr,Vt=(np.asarray(a,complex) for a in (R,T,K,Rx,Tx,Kx,value,radial,time))
    if R.shape!=T.shape or R.shape!=K.shape or R.shape!=Rx.shape or R.shape!=Tx.shape or R.shape!=Kx.shape:
        raise ValueError('same original coefficient/carrier axes required')
    if V.shape!=Vr.shape or V.shape!=Vt.shape or V.shape[:-1]!=R.shape[:-1]:
        raise ValueError('same saved value and actual derivative axes required')
    vertex=Rx@Vr+Tx@Vt+Kx@V
    forcing=-np.linalg.solve(R,vertex)
    substituted_radial=-np.linalg.solve(R,T@Vt+K@V)
    substituted=-np.linalg.solve(R,Rx@substituted_radial+Tx@Vt+Kx@V)
    return forcing,forcing-substituted


def _saved_value_block(saved,label,branch_index,op,bi,newtimes,rho):
    base=op+'_block'+str(bi)+'_';indices=saved[base+'indices'];d=len(indices);oldn=len(saved['times'])
    w=np.concatenate([saved[label+'_wall'][:,(2*family+branch_index)*64+indices].reshape(oldn*d,108)
        for family in range(3)],axis=1)
    H,Hr,_,_=_factor_at(saved,base,[rho])[0]
    V=time_evaluation_matrix(saved['times'],newtimes)
    Dt=time_evaluation_matrix(saved['times'],newtimes,1)
    values=[]
    for weights,a in ((V,H@w),(V,Hr@w),(Dt,H@w)):
        values.append((weights@a.reshape(oldn,-1)).reshape(len(newtimes),d,324))
    return values


def _saved_source_block(source,label,op,bi,newtimes,rho):
    base=label+'_'+op+'_block'+str(bi)+'_';indices=source[base+'indices'];d=len(indices)
    bounds=source['radial_boundaries'];order=int(source['radial_order']);_,_,integral,_=_collocation_rule(order)
    step=min(np.searchsorted(-bounds,-rho,side='right')-1,len(bounds)-2);step=max(step,0)
    h=bounds[step+1]-bounds[step];theta=(rho-bounds[step])/h
    a=source[base+'source_initial'][step]+h*np.einsum('q,qdk->dk',integral(theta),source[base+'source_slopes'][step])
    oldn=len(source['times']);P=time_evaluation_matrix(source['times'],newtimes)
    return (P@a.reshape(oldn,-1)).reshape(len(newtimes)*d,324)


def refine_consumed_event_source(saved_value,completed_source,history,psi_e1,*,radial_steps=2):
    """Solve four consistent source fields, holding value10/time10 unchanged.

    Only the declared consumed labels are refined. The old homogeneous value
    family remains an independent saved operand; its new source is None.
    """
    if len(saved_value['times'])!=10 or not np.array_equal(saved_value['times'],completed_source['times']):
        raise ValueError('this explicit source application holds the completed ten-time grid fixed')
    if radial_steps not in (2,4):raise ValueError('explicit consistent-two or targeted-four radial partition required')
    if complex(completed_source['provisional_constant_psi_E1'])!=complex(psi_e1):
        raise ValueError('source initializer has a different event-normal direction')
    newhistory=ProvisionalNormalSourceHistory(history,psi_e1)
    oldt=saved_value['times'];t=oldt.copy();n=len(t);D=saved_value['time_derivative'].copy()
    oldbounds=saved_value['radial_boundaries']
    bounds=np.linspace(oldbounds[0],oldbounds[-1],radial_steps+1);order=int(saved_value['radial_order'])
    cn,_,integral,A=_collocation_rule(order)
    radii=np.concatenate([a+(b-a)*cn for a,b in zip(bounds[:-1],bounds[1:])])
    coefficients,_,_=coefficient_rows(newhistory,t,radii)
    actual_sources=np.array([newhistory.source(ti)[0] for ti in t])
    if not np.array_equal(actual_sources,completed_source['source_Xi268_nodes']):
        raise ValueError('completed wall/source inputs do not match the declared same-Xi application')
    out=dict(times=t,source_times=t.copy(),value_times=oldt.copy(),radial_boundaries=bounds.copy(),
        radial_order=np.array(order),source_label_codes=np.arange(4,dtype=np.int64),
        provisional_constant_psi_E1=np.array(psi_e1),
        source_Xi268_nodes=actual_sources)
    endpoint_value_difference=0.
    for label in LABELS:
        out[label+'_wall_source']=completed_source[label+'_wall_source'].copy(order='K')
        out[label+'_wall']=completed_source[label+'_wall'].copy(order='K')
        endpoint_value_difference=max(endpoint_value_difference,float(np.max(abs(
            out[label+'_wall'][-1]-saved_value[label+'_wall'][-1]))))
    for key,a in completed_source.items():
        if key.startswith('wall_'):out[key]=a.copy(order='K')
    reports={};forcing_difference=temporal_value_derivative_difference=0.
    original_source_value_defect_transfer=original_value_stage_defect=0.
    for side in ('plus','minus'):
      labels=[label for label in LABELS if label.startswith(side+'_')]
      for branch_index,branch in enumerate(('particle','conjugate')):
        op=side+'_'+branch;c=coefficients[op]
        for bi in range(int(saved_value[op+'_block_count'])):
            base=op+'_block'+str(bi)+'_';indices=saved_value[base+'indices'];d=len(indices)
            initial=np.concatenate([out[label+'_wall_source'][:,(2*family+branch_index)*64+indices].reshape(n*d,108)
                for label in labels for family in range(3)],axis=1)
            initial_records=[];slope_records=[];stage_reports=[]
            for si,(left,right) in enumerate(zip(bounds[:-1],bounds[1:])):
                gs=[];forces=[];guesses=[]
                for j,rho in enumerate(left+(right-left)*cn):
                    ci=si*order+j
                    args=[c[key][ci][:,indices][:,:,indices] for key in ('time','radial','body','time_source','radial_source','body_source')]
                    T,R,K,Tx,Rx,Kx=args
                    G,_=_generator(T,R,K,Tx,Rx,Kx,D)
                    pieces=[_saved_value_block(saved_value,label,branch_index,op,bi,t,rho) for label in labels]
                    V,Vr,Vt=[np.concatenate([piece[ki] for piece in pieces],axis=-1) for ki in range(3)]
                    F,difference=original_source_forcing(R,T,K,Rx,Tx,Kx,V,Vr,Vt)
                    forcing_difference=max(forcing_difference,float(np.max(abs(difference))))
                    original_source_value_defect_transfer=max(original_source_value_defect_transfer,
                        float(np.max(abs(R@difference))))
                    original_value_stage_defect=max(original_value_stage_defect,
                        float(np.max(abs(R@Vr+T@Vt+K@V))))
                    temporal_value_derivative_difference=max(temporal_value_derivative_difference,
                        float(np.max(abs((D@V.reshape(n,-1)).reshape(V.shape)-Vt))))
                    gs.append(G);forces.append(F.reshape(n*d,-1))
                    guesses.append(np.concatenate([_saved_source_block(completed_source,label,op,bi,t,rho)
                        for label in labels],axis=-1))
                initial_records.append(initial)
                slopes,check=source_forcing_gauss_update(np.array(gs),np.array(forces),initial,
                    right-left,A,np.array(guesses))
                slope_records.append(slopes);stage_reports.append(check)
                initial=initial+(right-left)*np.einsum('q,qdk->dk',integral(1.),slopes)
            for li,label in enumerate(labels):
                sl=slice(li*324,(li+1)*324);prefix=label+'_'+base
                out[prefix+'indices']=indices.copy()
                out[prefix+'source_initial']=np.array(initial_records)[...,sl]
                out[prefix+'source_slopes']=np.array(slope_records)[...,sl]
            reports[base]=stage_reports
        out[op+'_block_count']=np.array(int(saved_value[op+'_block_count']))
    report=dict(classification='PROVISIONAL_CONSISTENT_ORIGINAL_CONSUMED_SOURCE_WITH_HELD_VALUE10',
        value_time_count=10,source_time_count=10,source_initializer_time_count=10,
        value_radial_steps=len(oldbounds)-1,source_radial_steps=radial_steps,
        source_initializer_direction='same executed normal-corrected Xi; not the old uncorrected Xi',
        original_source_equation='R S_r+T S_t+K S=-(R_Xi V10_r+T_Xi V10_t+K_Xi V10)',
        actual_saved_value_derivatives_used=True,value_equations_resolved=False,
        source_forcing_difference_from_substituted_value_equation_max=forcing_difference,
        original_R_Xi_times_saved_value_radial_equation_defect_max=original_source_value_defect_transfer,
        original_saved_value_stage_equation_defect_max=original_value_stage_defect,
        D10_of_saved_V10_minus_actual_V10_time_derivative_max=temporal_value_derivative_difference,
        original_E1_wall_value_identity_difference_max=endpoint_value_difference,
        completed_same_input_wall_source_cache_reused=True,
        stage_checks=reports,source_constant_psi_E1=float(np.real(psi_e1)),
        physical_psi_time_coordinate_assigned=False,physical_mode_selected=False,
        homogeneous_value_coordinates_per_time_node=366,homogeneous_value_family_refined=False,
        homogeneous_bulk_source_response=None,physical_g_and_normal_profiles_assigned=False,
        full_physical_derivative=False,physical_admission=False,continuum_error_bound=False)
    return out,report,newhistory


def evaluate_consumed_source_refinement(arrays,label,times,radii):
    """Reuse the completed generic dense source evaluator with explicit axes."""
    return evaluate_event_normal_source(arrays,label,times,radii)
