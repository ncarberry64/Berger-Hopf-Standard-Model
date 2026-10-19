"""Original-coordinate source solve at the actually represented radial nodes.

At a narrow strip, rho=left+h*c rounds and (rho-left)/h differs from c.
The source stage equations and dense polynomial below use the same latter
nodes. This is a finite representation repair, not a changed physical norm.
The completed value10 field remains in its original representation.
"""
from __future__ import annotations
import numpy as np
from numpy.polynomial.legendre import leggauss

from .muon_d5_complement_bulk_response import _collocation_rule,_generator
from .muon_d5_temporal_bulk_refinement import coefficient_rows,time_evaluation_matrix,component_offblock_max
from .muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory
from .muon_d5_event_consumed_source_refinement import (
    source_forcing_gauss_update,original_source_forcing,_saved_value_block,_saved_source_block,LABELS,
)


def represented_radial_rule(nodes):
    """Literal cardinal polynomials and their integrals for the stored nodes."""
    x=np.asarray(nodes,float)
    if x.ndim!=1 or len(x)<2 or not np.isfinite(x).all() or np.any(np.diff(x)<=0) or x[0]<=0 or x[-1]>=1:
        raise ValueError('ordered distinct represented interior nodes required')
    polys=[]
    for j in range(len(x)):
        def cardinal(theta,j=j):
            return np.prod([(theta-x[k])/(x[j]-x[k]) for k in range(len(x)) if k!=j],axis=0)
        polys.append(cardinal)
    # A q-point cardinal has degree q-1. This exact finite polynomial
    # quadrature avoids expanded monomial cancellation in its primitive.
    z,w=leggauss((len(x)+1)//2)
    def integral(theta):
        points=theta*(z+1)/2
        return theta/2*np.array([np.dot(w,p(points)) for p in polys])
    A=np.array([integral(theta) for theta in x])
    return polys,integral,A


def solve_represented_radial_source(saved_value,completed_source,history,psi_e1):
    """Use completed consistent2 source as an initializer, with no value solve."""
    t=saved_value['times'];n=len(t);D=saved_value['time_derivative'];bounds=saved_value['radial_boundaries']
    if n!=10 or len(bounds)!=3 or not np.array_equal(t,completed_source['times']):
        raise ValueError('explicit held-value10, completed-source10, two-interval application required')
    if complex(completed_source['provisional_constant_psi_E1'])!=complex(psi_e1):raise ValueError('source direction changed')
    newhistory=ProvisionalNormalSourceHistory(history,psi_e1)
    xi=np.array([newhistory.source(ti)[0] for ti in t])
    if not np.array_equal(xi,completed_source['source_Xi268_nodes']):raise ValueError('saved source inputs changed')
    order=int(saved_value['radial_order']);ideal,_,_,_=_collocation_rule(order)
    rho=np.array([left+(right-left)*ideal for left,right in zip(bounds[:-1],bounds[1:])])
    theta=np.array([(r-left)/(right-left) for r,left,right in zip(rho,bounds[:-1],bounds[1:])])
    rules=[represented_radial_rule(row) for row in theta]
    coeff,_,_=coefficient_rows(newhistory,t,rho.ravel())
    out=dict(times=t.copy(),value_times=t.copy(),source_times=t.copy(),radial_boundaries=bounds.copy(),
        radial_order=np.array(order),represented_radial_theta=theta,represented_radial_rho=rho,
        source_label_codes=np.arange(4,dtype=np.int64),source_Xi268_nodes=xi,
        provisional_constant_psi_E1=np.array(psi_e1))
    for key,a in completed_source.items():
        if key.startswith('wall_') or any(key==label+'_wall'+suffix for label in LABELS for suffix in ('','_source')):
            out[key]=a.copy(order='K')
    reports={};offblock=transfer=0.
    for side in ('plus','minus'):
      labels=[label for label in LABELS if label.startswith(side+'_')]
      for branch_index,branch in enumerate(('particle','conjugate')):
        op=side+'_'+branch;c=coeff[op]
        components=[saved_value[op+'_block'+str(bi)+'_indices'] for bi in range(int(saved_value[op+'_block_count']))]
        offblock=max(offblock,component_offblock_max(c,components))
        if offblock!=0:raise ValueError('new source couples previously separate retained carrier blocks')
        for bi,indices in enumerate(components):
            base=op+'_block'+str(bi)+'_';d=len(indices)
            initial=np.concatenate([out[label+'_wall_source'][:,(2*family+branch_index)*64+indices].reshape(n*d,108)
                for label in labels for family in range(3)],axis=-1)
            initials=[];slopes_all=[];checks=[]
            for si,(left,right) in enumerate(zip(bounds[:-1],bounds[1:])):
                gs=[];forces=[];guesses=[]
                for j,r in enumerate(rho[si]):
                    ci=si*order+j
                    T,R,K,Tx,Rx,Kx=[c[key][ci][:,indices][:,:,indices] for key in ('time','radial','body','time_source','radial_source','body_source')]
                    G,_=_generator(T,R,K,Tx,Rx,Kx,D)
                    pieces=[_saved_value_block(saved_value,label,branch_index,op,bi,t,r) for label in labels]
                    V,Vr,Vt=[np.concatenate([piece[ki] for piece in pieces],axis=-1) for ki in range(3)]
                    F,diff=original_source_forcing(R,T,K,Rx,Tx,Kx,V,Vr,Vt)
                    transfer=max(transfer,float(np.max(abs(R@diff))))
                    gs.append(G);forces.append(F.reshape(n*d,-1))
                    guesses.append(np.concatenate([_saved_source_block(completed_source,label,op,bi,t,r) for label in labels],axis=-1))
                initials.append(initial)
                slope,check=source_forcing_gauss_update(np.array(gs),np.array(forces),initial,right-left,rules[si][2],np.array(guesses))
                slopes_all.append(slope);checks.append(check)
                initial=initial+(right-left)*np.einsum('q,qdk->dk',rules[si][1](1.),slope)
            for li,label in enumerate(labels):
                sl=slice(li*324,(li+1)*324);prefix=label+'_'+base
                out[prefix+'indices']=indices.copy();out[prefix+'source_initial']=np.array(initials)[...,sl]
                out[prefix+'source_slopes']=np.array(slopes_all)[...,sl]
            reports[base]=checks
        out[op+'_block_count']=np.array(int(saved_value[op+'_block_count']))
    moments=np.array([[np.dot(rule[1](1.),nodes**k)-1/(k+1) for k in range(2*order)] for rule,nodes in zip(rules,theta)])
    out['represented_rule_moment_defects_degree0_to9']=moments
    report=dict(classification='PROVISIONAL_ORIGINAL_RHO_CONSISTENT_SOURCE_NODE_APPLICATION',
        value_time_count=10,source_time_count=10,value_radial_steps=2,source_radial_steps=2,
        source_equation='R S_r+T S_t+K S=-(R_Xi V10_r+T_Xi V10_t+K_Xi V10)',
        same_represented_source_nodes_in_stages_and_dense_output=True,
        represented_theta_minus_ideal_Gauss_max=float(np.max(abs(theta-ideal))),
        represented_rule_moment_degree0_to4_defect_max=float(np.max(abs(moments[:,:order]))),
        represented_rule_moment_degree5_to9_defect_max=float(np.max(abs(moments[:,order:]))),
        source_original_coefficient_offblock_max=offblock,
        original_R_Xi_times_saved_value_defect_transfer_max=transfer,stage_checks=reports,
        cached_wall_source_reused=True,completed_consistent2_source_is_initializer=True,
        value_equations_resolved=False,old_value_nonpasses_retained=True,
        homogeneous_value_coordinates_per_time_node=366,homogeneous_bulk_source_response=None,
        physical_g_and_normal_profile_sources_assigned=False,physical_psi_time_coordinate_determined=False,
        full_physical_derivative=False,physical_admission=False,continuum_error_bound=False,
        numerical_scope='perturbed finite collocation nodes track stored physical-rho arithmetic; physical norms and 2e-10 guard unchanged')
    return out,report,newhistory


def evaluate_represented_radial_source(arrays,label,times,radii):
    if label not in LABELS:raise ValueError('executed consumed label required')
    t=arrays['times'];p=np.atleast_1d(np.asarray(times,float));r=np.atleast_1d(np.asarray(radii,float));bounds=arrays['radial_boundaries'];n=len(t)
    if np.any(r>bounds[0]+1e-15) or np.any(r<bounds[-1]-1e-15):raise ValueError('outside represented finite source strip')
    V=time_evaluation_matrix(t,p);Vt=time_evaluation_matrix(t,p,1)
    rules=[represented_radial_rule(row) for row in arrays['represented_radial_theta']]
    out={key:np.zeros((len(r),len(p),384,108),complex) for key in ('source','time_source','radial_source')}
    for branch_index,branch in enumerate(('particle','conjugate')):
      op=label.split('_')[0]+'_'+branch
      for bi in range(int(arrays[op+'_block_count'])):
        prefix=label+'_'+op+'_block'+str(bi)+'_';indices=arrays[prefix+'indices'];d=len(indices)
        for ri,rho in enumerate(r):
            si=min(np.searchsorted(-bounds,-rho,side='right')-1,len(bounds)-2);si=max(si,0)
            h=bounds[si+1]-bounds[si];x=(rho-bounds[si])/h;polys,integral,_=rules[si]
            slope=arrays[prefix+'source_slopes'][si]
            value=arrays[prefix+'source_initial'][si]+h*np.einsum('q,qdk->dk',integral(x),slope)
            radial=np.einsum('q,qdk->dk',np.array([poly(x) for poly in polys]),slope)
            for family in range(3):
                sl=slice(family*108,(family+1)*108);rows=(2*family+branch_index)*64+indices
                for key,w,a in (('source',V,value),('time_source',Vt,value),('radial_source',V,radial)):
                    b=a[:,sl].reshape(n,d,108)
                    out[key][ri,:,rows,:]=(w@b.reshape(n,-1)).reshape(len(p),d,108).transpose(1,0,2)
    return out
