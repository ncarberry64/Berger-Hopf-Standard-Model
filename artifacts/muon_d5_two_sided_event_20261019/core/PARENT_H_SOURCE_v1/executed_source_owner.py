"""Corrected-direction source of the retained full homogeneous D5 family.

The saved value factors are held fixed, including their nonpasses.  This
evaluates a new source operator on their full space; it does not choose h,
delta h, a physical mode, or a boundary state.
"""
from __future__ import annotations

import numpy as np

from .muon_d5_complement_bulk_response import _generator
from .muon_d5_temporal_bulk_refinement import (
    coefficient_rows,time_evaluation_matrix,component_offblock_max,_factor_at,
)
from .muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory
from .muon_d5_event_consumed_source_refinement import (
    original_source_forcing,source_forcing_gauss_update,
)
from .muon_d5_event_represented_radial_source import represented_radial_rule


def solve_corrected_homogeneous_source(saved,completed_source,history,psi_e1):
    """Solve R Hx_r+T Hx_t+K Hx=-(Rx H_r+Tx H_t+Kx H).

    Hx(WALL)=0 defines the fundamental matrix, not a physical boundary
    source.  The consumer separately retains Qx h and Q delta h in full.
    Old-Xi source factors initialize this new solve only.
    """
    t=np.asarray(saved['times']);n=len(t);D=saved['time_derivative']
    actual=np.array([history.value(ti)[0] for ti in t])
    if not np.array_equal(actual,saved['raw268_nodes']):
        raise ValueError('original held value history differs')
    newhistory=ProvisionalNormalSourceHistory(history,psi_e1)
    xi=np.array([newhistory.source(ti)[0] for ti in t])
    if not np.array_equal(xi,completed_source['source_Xi268_nodes']):
        raise ValueError('completed corrected source direction differs')
    bounds=saved['radial_boundaries'];theta=completed_source['represented_radial_theta']
    rho=completed_source['represented_radial_rho'];order=int(saved['radial_order'])
    if theta.shape!=(len(bounds)-1,order) or rho.shape!=theta.shape:
        raise ValueError('matching represented source partition required')
    if not np.array_equal((rho-bounds[:-1,None])/np.diff(bounds)[:,None],theta):
        raise ValueError('source stage/dense coordinates differ')
    rules=[represented_radial_rule(row) for row in theta]
    coeff,_,_=coefficient_rows(newhistory,t,rho.ravel())
    E=time_evaluation_matrix(t,t);Et=time_evaluation_matrix(t,t,1)
    out=dict(times=t.copy(),radial_boundaries=bounds.copy(),radial_order=np.array(order),
        represented_radial_theta=theta.copy(),represented_radial_rho=rho.copy(),source_Xi268_nodes=xi)
    reports={};offblock=transfer=0.
    for op,c in coeff.items():
        components=[saved[op+'_block'+str(bi)+'_indices'] for bi in range(int(saved[op+'_block_count']))]
        offblock=max(offblock,component_offblock_max(c,components))
        if offblock!=0:raise ValueError('corrected source couples retained carrier blocks')
        out[op+'_block_count']=np.array(len(components))
        for bi,indices in enumerate(components):
            prefix=op+'_block'+str(bi)+'_';d=len(indices);nd=n*d
            # The source solve has its own zero-forcing initial-data
            # propagator Z. Reusing approximate H10 for Qx*h would carry
            # L(H10*Qx*h) into the checked source equation. H10 stays fixed.
            initial=np.c_[np.zeros((nd,nd),complex),np.eye(nd)]
            initials=[];slopes_all=[];checks=[]
            for si,(left,right) in enumerate(zip(bounds[:-1],bounds[1:])):
                gs=[];forces=[];guesses=[]
                for j,r in enumerate(rho[si]):
                    ci=si*order+j
                    T,R,K,Tx,Rx,Kx=[c[key][ci][:,indices][:,:,indices] for key in (
                        'time','radial','body','time_source','radial_source','body_source')]
                    H,Hr,oldHx,_=_factor_at(saved,prefix,[r])[0]
                    V=(E@H.reshape(n,-1)).reshape(n,d,nd)
                    Vr=(E@Hr.reshape(n,-1)).reshape(n,d,nd)
                    Vt=(Et@H.reshape(n,-1)).reshape(n,d,nd)
                    F,diff=original_source_forcing(R,T,K,Rx,Tx,Kx,V,Vr,Vt)
                    transfer=max(transfer,float(np.max(abs(R@diff))))
                    G,_=_generator(T,R,K,Tx,Rx,Kx,D)
                    gs.append(G);forces.append(np.c_[F.reshape(nd,nd),np.zeros((nd,nd))])
                    guesses.append(np.c_[oldHx,H])
                initials.append(initial)
                slopes,check=source_forcing_gauss_update(np.array(gs),np.array(forces),
                    initial,right-left,rules[si][2],np.array(guesses))
                slopes_all.append(slopes);checks.append(check)
                initial=initial+(right-left)*np.einsum('q,qdk->dk',rules[si][1](1.),slopes)
            out[prefix+'indices']=indices.copy()
            out[prefix+'source_initial']=np.array(initials)[...,:nd]
            out[prefix+'source_slopes']=np.array(slopes_all)[...,:nd]
            out[prefix+'wall_source_initial']=np.array(initials)[...,nd:]
            out[prefix+'wall_source_slopes']=np.array(slopes_all)[...,nd:]
            reports[prefix]=checks
    report=dict(classification='CORRECTED_SOURCE_OPERATOR_ON_FULL_SAVED_HOMOGENEOUS_SPACE',
        equation='R Hx_r+T Hx_t+K Hx=-(Rx H_saved_r+Tx H_saved_t+Kx H_saved)',
        fundamental_wall_source='Hx(WALL)=0; physical wall source Qx*h+Q*delta_h remains explicit',
        homogeneous_coordinates_per_time_node=366,represented_homogeneous_coordinates=366*n,
        homogeneous_state_selected=False,homogeneous_source_state_selected=False,
        background_and_value_factors_resolved=False,temporal_or_radial_refinement=False,
        source_coefficient_offblock_max=offblock,
        saved_value_defect_transfer_max=transfer,stage_checks=reports,
        old_source_used_only_as_initializer=True,
        source_initial_data_propagator='L Z=0,Z(WALL)=I on the represented source stages; source S=Hx W+Z Wx, without transferring the held H10 value residual into boundary-source propagation',
        source_scope='original Xi plus provisional constant parent normal-response extension; free normal-rate, induced field and physical constraint variations remain independent',
        physical_guard=2e-10,physical_admission=False,continuum_error_bound=False)
    return out,report,newhistory


def corrected_source_factor(source,prefix,radii):
    """Return Hx,Hx_r,Z,Z_r on the stored physical-rho source cardinals."""
    bounds=source['radial_boundaries'];r=np.atleast_1d(np.asarray(radii,float))
    if np.any(r>bounds[0]) or np.any(r<bounds[-1]):
        raise ValueError('outside saved incoming source strip')
    rules=[represented_radial_rule(row) for row in source['represented_radial_theta']]
    out=[]
    for rho in r:
        si=min(np.searchsorted(-bounds,-rho,side='right')-1,len(bounds)-2);si=max(si,0)
        h=bounds[si+1]-bounds[si];theta=(rho-bounds[si])/h
        polys,integral,_=rules[si];vals=[]
        for name in ('source','wall_source'):
            slope=source[prefix+name+'_slopes'][si]
            val=source[prefix+name+'_initial'][si]+h*np.einsum('q,qdk->dk',integral(theta),slope)
            radial=np.einsum('q,qdk->dk',np.array([p(theta) for p in polys]),slope)
            vals.extend((val,radial))
        out.append(tuple(vals))
    return out


def apply_corrected_family(saved,source,side,wall,wall_source,*,times,radii):
    """Apply held H W and Hx W+Z Wx, retaining every explicit wall source.

    For W=P*a+Q*h, Wx must include Px*a+P*delta_a+Qx*h+Q*delta_h.
    This routine never supplies missing physical amplitudes or source data.
    """
    if side not in ('plus','minus'):raise ValueError('explicit same-history eta collar required')
    W,Wx=np.asarray(wall,complex),np.asarray(wall_source,complex)
    t=saved['times'];n=len(t);r=np.atleast_1d(np.asarray(radii,float));p=np.atleast_1d(np.asarray(times,float))
    if W.ndim!=3 or W.shape[:2]!=(n,384) or Wx.shape!=W.shape:
        raise ValueError('full wall values/source at every saved time node required')
    if not np.isfinite(W).all() or not np.isfinite(Wx).all():raise ValueError('finite explicit wall operands required')
    E=time_evaluation_matrix(t,p);Et=time_evaluation_matrix(t,p,1)
    out={k:np.zeros((len(r),len(p),384,W.shape[-1]),complex) for k in (
        'value','radial','time','source','radial_source','time_source')}
    for branch_index,branch in enumerate(('particle','conjugate')):
        op=side+'_'+branch
        for bi in range(int(saved[op+'_block_count'])):
            prefix=op+'_block'+str(bi)+'_';indices=saved[prefix+'indices'];d=len(indices)
            if not np.array_equal(indices,source[prefix+'indices']):raise ValueError('carrier block identity differs')
            value=_factor_at(saved,prefix,r);first=corrected_source_factor(source,prefix,r)
            for family in range(3):
                rows=(2*family+branch_index)*64+indices
                w=W[:,rows].reshape(n*d,-1);wx=Wx[:,rows].reshape(n*d,-1)
                for ri,((H,Hr,_,_),(Hx,Hxr,Z,Zr)) in enumerate(zip(value,first)):
                    for key,a in (('value',H@w),('radial',Hr@w),
                        ('source',Hx@w+Z@wx),('radial_source',Hxr@w+Zr@wx)):
                        a=a.reshape(n,-1)
                        out[key][ri,:,rows,:]=(E@a).reshape(len(p),d,-1).transpose(1,0,2)
                        if key in ('value','source'):
                            keyt='time' if key=='value' else 'time_source'
                            out[keyt][ri,:,rows,:]=(Et@a).reshape(len(p),d,-1).transpose(1,0,2)
    return out
