"""Whole-history pullback of the existing real two-arm classical action.

All temporal endpoint positions and cell algebraic variables remain. The
default joint source owner requires the SAME coordinate-time step per arm;
its proper lapses remain independent. Unequal steps need a caller-owned
source-clock pullback evaluator, not merely different action weights.
There is no native force, boundary load or reset constraint inferred as zero.
"""
from __future__ import annotations
import numpy as np


def _real(value, shape, name):
    a = np.asarray(value)
    if not np.isrealobj(a) or a.shape != shape or not np.isfinite(a).all():
        raise ValueError('complete finite real ' + name + ' required')
    return np.asarray(a, float)


def paired_temporal_layout(coordinate_lift, parent_times, child_times):
    """Build supplied h*L(midpoint x,Delta x/h,y) numerical incidence.

    The supplied node pairing is numerical action incidence. It is not a
    physical equality of the clocks or an inferred event correspondence.
    Both signed orientations are recorded without abs(h). The default
    action consumer separately rejects unequal arm coordinate steps.
    """
    P = np.asarray(coordinate_lift)
    if not np.isrealobj(P) or P.shape != (268,252) or not np.isfinite(P).all():
        raise ValueError('actual complete raw268/master252 real lift required')
    if not np.array_equal(P.T@P,np.eye(252)):
        raise ValueError('the exact retained coefficient lift is required')
    tp,tc = (np.asarray(t) for t in (parent_times,child_times))
    if tp.ndim != 1 or len(tp)<2 or tc.shape!=tp.shape:
        raise ValueError('both explicit paired coordinate-time node lists required')
    tp=_real(tp,tp.shape,'parent times');tc=_real(tc,tp.shape,'child times')
    steps=np.column_stack((np.diff(tp),np.diff(tc)))
    if np.any(steps==0) or any(np.any(s[:-1]*s[1:]<=0) for s in steps.T):
        raise ValueError('each supplied arm must have nonzero consistently oriented steps')
    nodes=len(tp);n=106;m=40;position_size=nodes*2*n
    return dict(lift=np.asarray(P,float),times=np.column_stack((tp,tc)),steps=steps,
        nodes=nodes,cells=nodes-1,dynamic_per_arm=n,algebraic_per_arm=m,
        position_size=position_size,size=position_size+(nodes-1)*2*m,
        x_shape=(nodes,2,n),y_shape=(nodes-1,2,m),
        master_order='each arm x106,v106,y40; full pair x212,v212,y80',
        temporal_rule='supplied coordinate h*L((x0+x1)/2,(x1-x0)/h,y_mid)',
        shared_proper_clock_inferred=False,physical_pairing_incidence_selected=False)


def pack_temporal_state(layout, positions, algebraic):
    x=_real(positions,layout['x_shape'],'all temporal endpoint positions')
    y=_real(algebraic,layout['y_shape'],'all cell multiplier/Gauss variables')
    return np.r_[x.ravel(),y.ravel()]


def _local_maps(state, layout, cell):
    n=106;m=40;nodes=layout['nodes'];size=layout['size'];sx=layout['position_size']
    x=state[:sx].reshape(nodes,2,n);y=state[sx:].reshape(nodes-1,2,m)
    eta=np.empty((2,252));T=np.zeros((504,size));I=np.eye(n)
    for arm,h in enumerate(layout['steps'][cell]):
        eta[arm]=np.r_[(x[cell,arm]+x[cell+1,arm])/2,
                      (x[cell+1,arm]-x[cell,arm])/h,y[cell,arm]]
        base=arm*252;left=(cell*2+arm)*n;right=((cell+1)*2+arm)*n
        T[base:base+n,left:left+n]=I/2;T[base:base+n,right:right+n]=I/2
        T[base+n:base+2*n,left:left+n]=-I/h;T[base+n:base+2*n,right:right+n]=I/h
        alg=sx+(cell*2+arm)*m;T[base+2*n:base+252,alg:alg+m]=np.eye(m)
    P=layout['lift'];raw=np.array([P@e for e in eta]);R=np.zeros((536,504))
    R[:268,:252]=P;R[268:,252:]=P
    return raw,R@T,T


def real_two_arm_temporal_action(state,layout,reference_pairs,representation,*,
        nu_squared_action,surface_gamma=None,coordinate_action_weights=None,
        joint_action_evaluator=None,parent_action_evaluator=None,
        source_clock_incidence_bound=False,
        native_application=None,boundary_application=None,constraint_application=None,
        constraint_multipliers=None):
    """Assemble with no additional g(x)-g(0) background subtraction.

    Per cell w_c*L_pair+(w_p-w_c)*L_parent applies each arm's supplied
    coordinate measure exactly once, preserving the child's dependence on
    BOTH states. This measure split is NOT a source-clock pullback. The
    default owner inserts parent lambda_tau in the common coordinate clock
    and therefore requires h_parent=h_child. Custom paired evaluators must
    already own any different source-rate/clock pullback and all its jets.
    Unknown exterior/native/reset applications remain explicit.
    Optional native/boundary callbacks must supply value/gradient/Hessian.
    Optional constraint callback supplies residual/Jacobian and the Hessian
    of its multiplier contraction; no moving incidence contact is omitted.
    """
    z=_real(state,(layout['size'],),'whole two-arm temporal state')
    refs=_real(reference_pairs,(layout['cells'],2,268),'supplied reference pairs')
    weights=layout['steps'] if coordinate_action_weights is None else _real(
        coordinate_action_weights,(layout['cells'],2),'separate coordinate action weights')
    if type(source_clock_incidence_bound) is not bool:
        raise ValueError('explicit boolean source-clock incidence assertion required')
    default_owner=joint_action_evaluator is None and parent_action_evaluator is None
    if joint_action_evaluator is None or parent_action_evaluator is None:
        if joint_action_evaluator is not None or parent_action_evaluator is not None:
            raise ValueError('both literal action owners must be supplied together')
        if not np.array_equal(layout['steps'][:,0],layout['steps'][:,1]):
            raise ValueError('default profile owner requires equal coordinate-time steps; unequal arm clocks need an explicit source-rate pullback evaluator')
        from bhsm.interface.muon_birth_finite_normal_trace_graph import (
            finite_normal_trace_graph_action_two_jet,pointwise_finite_normal_action)
        params=dict(nu_squared_action=nu_squared_action,surface_gamma=surface_gamma)
        joint_action_evaluator=lambda raw,ref:finite_normal_trace_graph_action_two_jet(raw,ref,representation,**params)
        parent_action_evaluator=lambda raw:pointwise_finite_normal_action(raw,representation,**params)
    elif (not np.array_equal(layout['steps'][:,0],layout['steps'][:,1])
          and not source_clock_incidence_bound):
        raise ValueError('unequal-clock custom evaluators must explicitly assert their already-bound source-clock incidence')
    size=layout['size'];g=np.zeros(size);H=np.zeros((size,size));value=0.
    initial=[];final=[];raws=[];cell_values=[]
    for k,(wp,wc) in enumerate(weights):
        raw,J,T=_local_maps(z,layout,k);a=joint_action_evaluator(raw,refs[k]);p=parent_action_evaluator(raw[0])
        ag=_real(a['raw_gradient'],(536,),'joint action gradient')
        ah=_real(a['raw_hessian'],(536,536),'joint action Hessian')
        pg=_real(p['raw_gradient'],(268,),'parent action gradient')
        ph=_real(p['raw_hessian'],(268,268),'parent action Hessian')
        localg=wc*ag;localH=wc*ah
        localg[:268]+=(wp-wc)*pg;localH[:268,:268]+=(wp-wc)*ph
        cellvalue=wc*float(a['value'])+(wp-wc)*float(p['value'])
        value+=cellvalue;g+=J.T@localg;H+=J.T@localH@J
        P=layout['lift'];masterg=np.array([P.T@localg[268*s:268*(s+1)] for s in range(2)])
        first=[];last=[]
        for arm,h in enumerate(layout['steps'][k]):
            gx=masterg[arm,:106];gv=masterg[arm,106:212]
            first.append(gx/2-gv/h);last.append(gx/2+gv/h)
        initial.append(first);final.append(last);raws.append(raw);cell_values.append(cellvalue)
    classical_value=value;classical_gradient=g.copy();classical_hessian=H.copy()
    extras={}
    for name,callback in (('native',native_application),('boundary',boundary_application)):
        if callback is None:extras[name]=None;continue
        a=callback(z)
        eg=_real(a['gradient'],(size,),name+' whole-history gradient')
        eh=_real(a['hessian'],(size,size),name+' whole-history Hessian')
        ev=float(a['value'])
        if not np.isfinite(ev):raise ValueError('finite '+name+' value required')
        value+=ev;g+=eg;H+=eh;extras[name]=a
    constraints=None
    if constraint_application is not None:
        if constraint_multipliers is None:raise ValueError('explicit reset/frame multipliers required')
        lam=np.asarray(constraint_multipliers)
        if lam.ndim!=1:raise ValueError('explicit multiplier vector required')
        lam=_real(lam,lam.shape,'constraint multipliers');a=constraint_application(z,lam)
        c=_real(a['residual'],lam.shape,'all caller constraint rows')
        C=_real(a['jacobian'],(len(lam),size),'all constraint derivative rows')
        hc=_real(a['multiplier_hessian'],(size,size),'full moving-incidence multiplier Hessian')
        constraints=dict(residual=np.r_[g+C.T@lam,c],
            jacobian=np.block([[H+hc,C.T],[C,np.zeros((len(lam),len(lam)))]]),
            supplied_constraint_residual=c,supplied_constraint_jacobian=C)
    elif constraint_multipliers is not None:raise ValueError('constraint application required with multipliers')
    sx=layout['position_size']
    return dict(value=value,gradient=g,hessian=H,classical_value=classical_value,
        classical_gradient=classical_gradient,classical_hessian=classical_hessian,
        position_cotangents=classical_gradient[:sx].reshape(layout['x_shape']),
        algebraic_rows=classical_gradient[sx:].reshape(layout['y_shape']),
        cell_initial_cotangents=np.asarray(initial),cell_final_cotangents=np.asarray(final),
        cell_raw_pairs=np.asarray(raws),cell_values=np.asarray(cell_values),
        coordinate_action_weights=np.asarray(weights).copy(),constraint_KKT=constraints,
        source_clock_binding='literal common coordinate-time owner' if default_owner else 'supplied evaluator; unequal steps require explicit source-clock assertion',
        native_application=extras['native'],boundary_application=extras['boundary'],
        supplied_combined_mean_residual=None if native_application is None or boundary_application is None or constraint_application is None else constraints['residual'],
        complete_physical_mean_residual=None,
        native_quantum_force_computed=native_application is not None,
        endpoint_or_reset_conditions_inferred=False,background_gradient_subtracted=False,
        all_x212_v212_y80_and_source_crossblocks_retained=True,
        physical_outgoing_or_stationary_mean_claimed=False,coupled_matching_corrections=0)
