"""One targeted radial trial on ACTUAL consumed child lepton data.

Time, branch, preparation and all supplied data are unchanged. Old birth
degree2 data embed in a Chebyshev boundary-refined radial chart. Additional
birth coordinates and all unconsumed carriers remain independent ports;
no full response family or physical boundary state is selected here.
"""
from __future__ import annotations
import numpy as np
from numpy.polynomial.chebyshev import chebvander,chebder,chebval
from scipy.linalg import lu_factor,lu_solve

from .muon_d5_child_characteristic_field import (
    _pde_matrix,_characteristic_system,characteristic_bases,
)
from .muon_d5_complement_bulk_response import nodal_derivative
from .muon_d5_temporal_bulk_refinement import time_evaluation_matrix


def radial_trial_chart(old_times,old_radii,count=17):
    """Fixed cell, actual represented nodes, old shared nodes preserved."""
    t,r=map(lambda a:np.asarray(a,float),(old_times,old_radii))
    if len(t)!=6 or len(r)!=3 or count!=17:raise ValueError('one explicit t6/rho17 trial from completed rho3 required')
    new=r[0]+(r[-1]-r[0])*(1-np.cos(np.pi*np.arange(count)/(count-1)))/2
    shared=np.array([0,8,16]);new[shared]=r
    if np.any(np.diff(new)<=0):raise ValueError('radial coordinates collapsed at float representation')
    extension=time_evaluation_matrix(r,new);higher=np.setdiff1d(np.arange(count),shared)
    return dict(times=t,radii=new,old_radii=r,shared_radial_indices=shared,
        new_radial_indices=higher,birth_degree2_extension=extension,
        higher_birth_free_lift=np.eye(count)[:,higher],time_derivative=nodal_derivative(t),
        radial_derivative=nodal_derivative(new))


def extend_actual_data(old_data,old_source,indices,branch,eps,chart):
    """Coordinate partial only: higher birth data remain symbolic/free."""
    z,zx=np.asarray(old_data),np.asarray(old_source);idx=np.asarray(indices,int)
    if z.shape!=zx.shape or z.ndim!=3 or z.shape[:2]!=(8,384):raise ValueError('actual full384 eight-slot coefficients required')
    # Exactly MUON family index1; both charge copies have independent rows.
    b=0 if branch=='particle' else 1;rows=(2+b)*64+idx
    initial=z[:3,rows];initialx=zx[:3,rows]
    birth=np.einsum('ij,jak->iak',chart['birth_degree2_extension'],initial)
    birthx=np.einsum('ij,jak->iak',chart['birth_degree2_extension'],initialx)
    (_,ii),(_,oi)=characteristic_bases(branch,eps,idx)
    local=np.r_[ii,32+oi];block=slice((2+b)*64,(3+b)*64)
    incoming=z[3:,block][:,local];incomingx=zx[3:,block][:,local]
    return np.concatenate((birth,incoming),axis=0).reshape(-1,z.shape[-1]),np.concatenate((birthx,incomingx),axis=0).reshape(-1,z.shape[-1]),rows


def old_field_initializer(value,time_derivative,probe_times,probe_radii,chart):
    """Recover completed degree5 time/degree2 radial field, no old solve.

    Three saved value/time-derivative samples identify its six time
    coefficients. This uses the completed ACTUAL consumed response, not
    its inaccurate earlier unit-family initializer.
    """
    tp=np.asarray(probe_times,float);rp=np.asarray(probe_radii,float);t=chart['times']
    z=2*(tp-t[0])/(t[-1]-t[0])-1;V=chebvander(z,5)
    coeff=np.eye(6);derivative=chebder(coeff,axis=0)*2
    W=chebval(z,derivative).T
    # Derivative rows are scaled by the physical cell width for conditioning.
    A=np.r_[V,W];targets=2*(t-t[0])/(t[-1]-t[0])-1
    Et=chebvander(targets,5)@np.linalg.inv(A)
    # Recover the already owned degree2 polynomial on its FULL old cell.
    # These three independent samples identify it; their smaller convex
    # hull is not the domain boundary of that completed polynomial.
    oldr=chart['old_radii'];zs=2*(rp-oldr[0])/(oldr[-1]-oldr[0])-1
    zn=2*(chart['radii']-oldr[0])/(oldr[-1]-oldr[0])-1
    Er=chebvander(zn,2)@np.linalg.inv(chebvander(zs,2))
    supplied=np.concatenate((np.asarray(value),(t[-1]-t[0])*np.asarray(time_derivative)),axis=0)
    return np.einsum('ti,rj,ijak->trak',Et,Er,supplied,optimize=True)


def compile_consumed_trial(values,sources,chart,indices,branch,eps):
    """One factorization; no inverse or full field-family solve."""
    nt,nr,d=values['time'].shape[:3];TI=np.linalg.inv(values['time'])
    (inner,_),(outer,_)=characteristic_bases(branch,eps,indices)
    P=_pde_matrix(values,chart['time_derivative'],chart['radial_derivative'])
    scale=float(chart['times'][-1]-chart['times'][0])
    M,B=_characteristic_system(P,nt,nr,d,inner,outer,scale,TI)
    return dict(values=values,sources=sources,chart=chart,TI=TI,inner=inner,outer=outer,
        M=M,B=B,lu=lu_factor(M),nt=nt,nr=nr,d=d,scale=scale)


def solve_consumed_trial(system,data,initializer):
    """Actual value rows, initialized from the completed rho3 polynomial."""
    s=system;guess=np.asarray(initializer).reshape(s['nt']*s['nr']*s['d'],-1)
    rhs=s['B']@np.asarray(data);before=rhs-s['M']@guess
    result=guess+lu_solve(s['lu'],before)
    return result.reshape(s['nt'],s['nr'],s['d'],-1),dict(
        value_stage_before_max=float(np.max(abs(before))),value_stage_after_max=float(np.max(abs(rhs-s['M']@result))),
        actual_input_columns=result.shape[-1],old_actual_field_initializer_reused=True,
        full_family_solved=False,physical_data_selected=False)


def _node_derivatives(system,value):
    Dt,Dr=system['chart']['time_derivative'],system['chart']['radial_derivative']
    return np.einsum('ij,jrak->irak',Dt,value),np.einsum('rs,isak->irak',Dr,value)


def solve_consumed_trial_source(system,value,data_source,source_slot,initializer):
    """Both original coefficient and corrected state-source terms retained."""
    s=system;T,R,K=(s['values'][k] for k in ('time','radial','body'))
    Tx,Rx,Kx=(s['sources'][k][source_slot] for k in ('time','radial','body'))
    Vt,Vr=_node_derivatives(s,value);L=T@Vt+R@Vr+K@value
    vertex=Tx@Vt+Rx@Vr+Kx@value;TIx=-s['TI']@Tx@s['TI']
    acted=s['scale']*vertex.copy()
    acted[0]=0;half=s['d']//2
    for i in range(1,s['nt']):
      for r,Qout in ((0,s['outer']),(s['nr']-1,s['inner'])):
        acted[i,r,:half]=0
        acted[i,r,half:]=s['scale']*Qout.conj().T@(s['TI'][i,r]@vertex[i,r]+TIx[i,r]@L[i,r])
    rhs=s['B']@np.asarray(data_source)-acted.reshape(s['nt']*s['nr']*s['d'],-1)
    guess=np.asarray(initializer).reshape(rhs.shape);before=rhs-s['M']@guess
    result=guess+lu_solve(s['lu'],before)
    return result.reshape(s['nt'],s['nr'],s['d'],-1),dict(source_slot=source_slot,
        source_stage_before_max=float(np.max(abs(before))),source_stage_after_max=float(np.max(abs(rhs-s['M']@result))),
        actual_input_columns=result.shape[-1],inverse_time_vertex_included=True,
        higher_birth_data_source_unassigned=True,physical_data_selected=False)


def evaluate_consumed_trial(system,value,source,times,radii):
    c=system['chart'];Et=time_evaluation_matrix(c['times'],times);Er=time_evaluation_matrix(c['radii'],radii)
    Et1=time_evaluation_matrix(c['times'],times,1);Er1=time_evaluation_matrix(c['radii'],radii,1)
    f=lambda A,B,V:np.einsum('ti,rj,ijak->trak',A,B,V,optimize=True)
    return dict(value=f(Et,Er,value),time=f(Et1,Er,value),radial=f(Et,Er1,value),
        source=f(Et,Er,source),time_source=f(Et1,Er,source),radial_source=f(Et,Er1,source))
