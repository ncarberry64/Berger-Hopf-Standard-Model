"""Bounded outward original pole-domain trial with full frame transitions.

Recharting changes coordinates of all regular amplitudes, never their
values. Every value/source transition is retained for sewing the domain
to a saved response; no minimum-norm physical state is selected.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import qr
from .muon_d5_temporal_bulk_refinement import _rectangular_collocation
from .muon_d5_complement_bulk_response import _collocation_rule


def rechart_regular_frame(value,source):
    """Use a nonsingular row chart, retaining the amplitude transition."""
    Y,Yx=map(np.asarray,(value,source));d,k=Y.shape
    if Yx.shape!=Y.shape or not 0<k<d:raise ValueError('full regular frame/source required')
    _,_,rows=qr(Y.T,pivoting=True,mode='economic');p=rows[:k]
    T,Tx=Y[p],Yx[p]
    Q=np.linalg.solve(T.T,Y.T).T
    Qx=np.linalg.solve(T.T,(Yx-Q@Tx).T).T
    return dict(value=Q,source=Qx,pivot_rows=p,amplitude_transition=T,
        amplitude_transition_source=Tx,pivot_condition=np.array(np.linalg.cond(T)),
        value_reconstruction_rows=Q@T-Y,
        source_reconstruction_rows=Qx@T+Q@Tx-Yx)


def propagate_recharted_regular_frame(boundaries,generators,generator_sources,
        seed,seed_source,*,order=3):
    b=np.asarray(boundaries,float);G,Gx=map(np.asarray,(generators,generator_sources))
    Y,Yx=map(lambda a:np.asarray(a,complex),(seed,seed_source));d,k=Y.shape
    if np.any(np.diff(b)<=0) or b[0]<=0 or G.shape!=Gx.shape or G.shape!=(len(b)-1,order,d,d):
        raise ValueError('positive original radial partition and full stage operators required')
    _,_,integral,A=_collocation_rule(order)
    out={name:[] for name in ('initials','source_initials','slopes','source_slopes',
        'transitions','transition_sources','pivot_rows','pivot_conditions','stage_rows',
        'value_reconstruction_rows','source_reconstruction_rows')}
    for cell,h in enumerate(np.diff(b)):
        out['initials'].append(Y.copy());out['source_initials'].append(Yx.copy())
        S,Sx,rv,rx,_=_rectangular_collocation(G[cell],Gx[cell],Y,Yx,h,A)
        end=Y+h*np.einsum('q,qdk->dk',integral(1.),S)
        endx=Yx+h*np.einsum('q,qdk->dk',integral(1.),Sx)
        chart=rechart_regular_frame(end,endx)
        out['slopes'].append(S);out['source_slopes'].append(Sx)
        for key,old in (('transitions','amplitude_transition'),('transition_sources','amplitude_transition_source'),
                ('pivot_rows','pivot_rows'),('pivot_conditions','pivot_condition'),
                ('value_reconstruction_rows','value_reconstruction_rows'),('source_reconstruction_rows','source_reconstruction_rows')):
            out[key].append(chart[old])
        out['stage_rows'].append([rv,rx]);Y,Yx=chart['value'],chart['source']
    return dict(radial_boundaries=b,**{key:np.array(v) for key,v in out.items()},
        final_frame=Y,final_frame_source=Yx)


def recharted_frame_at(application,rho,*,order=3):
    """Original field jets in the local cell's retained regular coordinates."""
    b=application['radial_boundaries'];r=float(rho)
    if not b[0]<=r<=b[-1]:raise ValueError('outside executed pole-domain trial')
    c=min(max(np.searchsorted(b,r,side='right')-1,0),len(b)-2);h=b[c+1]-b[c]
    z=(r-b[c])/h;_,p,integral,_=_collocation_rule(order)
    values=np.array([a(z) for a in p]);weights=integral(z);out={}
    for prefix in ('','source_'):
        S=application[prefix+'slopes'][c]
        Y=application[prefix+'initials'][c]+h*np.einsum('q,qdk->dk',weights,S)
        Yr=np.einsum('q,qdk->dk',values,S)
        out[prefix+'value']=r*Y;out[prefix+'radial']=Y+r*Yr
    out['local_amplitude_chart_cell']=np.array(c)
    return out


def sew_regular_pole_rows(boundary,boundary_source,value,value_source):
    """Apply the genuine regular-domain row to actual saved field columns."""
    B,Bx,V,Vx=map(np.asarray,(boundary,boundary_source,value,value_source))
    if Bx.shape!=B.shape or Vx.shape!=V.shape or B.shape[1]!=V.shape[0]:
        raise ValueError('same-domain actual regular-boundary and saved field/source columns required')
    return dict(value_rows=B@V,source_rows=Bx@V+B@Vx,
        independent_state_source_coefficient=B@V)
