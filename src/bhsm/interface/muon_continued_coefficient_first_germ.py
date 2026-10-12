"""Exact first derivative of the retained inside-cell coefficient map.

The independent reflected branch is differentiated with its own supplied
coordinate slope.  This differentiates the saved representation; it does
not replace it by a continuous Euler solution or select an exterior state.
"""
from __future__ import annotations
import numpy as np

from .muon_continued_action_reality import (
    action_reality_coefficient, _higgs_mass_realified)
from .muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_parent_maxwell_full_weak import M


def geometry_first_germ(raw,raw_first):
    """Differentiate the actual regular square-root coframe analytically."""
    x,dx=(np.asarray(a,complex)for a in(raw,raw_first))
    if x.ndim!=1 or dx.shape!=x.shape or len(x)<100 or not np.isfinite([x,dx]).all():
        raise ValueError('complete realified affine geometry and first germ required')
    q,v,m=x[:37],x[37:74],x[74:98]
    dq,dv,dm=dx[:37],dx[37:74],dx[74:98]
    k=np.arange(1,13);j=np.arange(12);sk=(-1.)**k;sj=(-1.)**j
    cs=RADIUS0*np.exp(q[0]+q[1:13]@sk+q[13:25]@sj)
    dcs=cs*(dq[0]+dq[1:13]@sk+dq[13:25]@sj)
    ld=v[0]+v[1:13]@sk+v[13:25]@sj
    dld=dv[0]+dv[1:13]@sk+dv[13:25]@sj
    delta=x[98]/cs;ddelta=dx[98]/cs-delta*dcs/cs
    dr=(x[99]-ld*x[98])/cs
    ddr=(dx[99]-dld*x[98]-ld*dx[98])/cs-dr*dcs/cs
    chi=np.pi/4+delta;dchi=ddelta
    ck=np.cos(4*k*chi);cj=np.cos(4*j*chi)
    dck=-4*k*np.sin(4*k*chi)*dchi;dcj=-4*j*np.sin(4*j*chi)*dchi
    win=np.sin(2*chi)**2;dwin=4*np.sin(2*chi)*np.cos(2*chi)*dchi
    u=q[1:13]@ck;du=dq[1:13]@ck+q[1:13]@dck
    b=win*(q[25:37]@cj);db=dwin*(q[25:37]@cj)+win*(dq[25:37]@cj+q[25:37]@dcj)
    wall=win*(q[13:25]@cj)
    dwall=dwin*(q[13:25]@cj)+win*(dq[13:25]@cj+q[13:25]@dcj)
    radius=RADIUS0*np.exp(q[0]);dradius=radius*dq[0]
    C=radius*np.exp(u+wall);dC=C*(dq[0]+du+dwall)
    A=radius*np.exp(u+b)*np.cos(chi)
    dA=radius*np.exp(u+b)*((dq[0]+du+db)*np.cos(chi)-np.sin(chi)*dchi)
    B=radius*np.exp(u-b)*np.sin(chi)
    dB=radius*np.exp(u-b)*((dq[0]+du-db)*np.sin(chi)+np.cos(chi)*dchi)
    N=np.exp(m[:12]@ck);dN=N*(dm[:12]@ck+m[:12]@dck)
    beta=np.sin(4*chi)*(m[12:]@cj)
    dbeta=4*np.cos(4*chi)*dchi*(m[12:]@cj)+np.sin(4*chi)*(dm[12:]@cj+m[12:]@dcj)
    den=A*A+B*B;dden=2*(A*dA+B*dB)
    U=C*(dr+beta)/N
    dU=(dC*(dr+beta)+C*(ddr+dbeta))/N-U*dN/N
    if den.real<=0 or (1-U*U).real<=0:raise ValueError('coframe left the owned regular square-root chart')
    R=A*B/np.sqrt(den);dR=(dA*B+A*dB)/np.sqrt(den)-R*dden/(2*den)
    lapse=N*np.sqrt(1-U*U);dlapse=dN*np.sqrt(1-U*U)-N*U*dU/np.sqrt(1-U*U)
    lam=A*A/den;dlam=2*A*dA/den-lam*dden/den
    values=dict(R4=R,N=lapse,mechanical_lambda=lam,Cstar=cs,delta=delta,
        wall=chi,wall_rate=dr,U=U,C=C,A=A,B=B,lapse_base=N)
    first=dict(R4=dR,N=dlapse,mechanical_lambda=dlam,Cstar=dcs,delta=ddelta,
        wall=dchi,wall_rate=ddr,U=dU,C=dC,A=dA,B=dB,lapse_base=dN)
    return dict(value=values,first=first)


def action_coefficient_first_germ(phase,anchor,offset,coordinate_slope):
    """The same Hcan, coframe and inherited image plus their s derivative."""
    anchor=float(anchor);z=complex(offset);slope=complex(coordinate_slope)
    base=action_reality_coefficient(phase,anchor,z)
    sample=profile_preserving_raw_sample(phase,anchor)
    dx=sample['raw_coordinate_time_derivative'].astype(complex)*slope
    raw=base['raw'];geo=geometry_first_germ(raw,dx)
    ng=phase['representation']['gauge_count'];T=phase['representation']['wall_trace_map']
    dtrace=np.einsum('fcj,j->fc',T,dx[100:100+ng])
    image_first=0j
    if phase['receipt']['side']=='outgoing':
        t=anchor+z;initial=phase['arrays']['initial_pair'][0]
        branches=[initial,*phase['arrays']['reference_pair']]
        dg=[]
        for x0 in branches:
            rate=np.zeros_like(x0,dtype=complex);rate[:37]=x0[37:74];rate[98]=x0[99]
            app=geometry_first_germ(np.asarray(x0,complex)+t*rate,slope*rate)
            dg.append(app['first']['mechanical_lambda'])
        image_first=dg[0]-geo['first']['mechanical_lambda']-(dg[1]-dg[2])
        dtrace[2:]+=M*image_first
    G=lepton_unit_trace_gauge_representation()['generators']
    trace=base['wall_independent_plus_inherited'];N=geo['value']['N'];dN=geo['first']['N']
    R=geo['value']['R4'];dR=geo['first']['R4']
    dOmega=np.einsum('c,cij->ij',dtrace[0],G)/N-base['Omega']*dN/N
    dspace=dtrace[2:]+M*geo['first']['mechanical_lambda']
    dOs=np.einsum('ac,cij->aij',dspace,G)
    rep=lepton_current_hilbert_representation()
    mass=_higgs_mass_realified(raw[-8:-4]);dmass=_higgs_mass_realified(dx[-8:-4])
    dW=-1j*np.einsum('aij,ajk->ik',rep['alpha'],dOs)/R-(base['W']-mass)*dR/R+dmass
    mismatch=max(abs(geo['value'][k]-base['geometry'][k]) for k in geo['value'])
    if mismatch>3e-13*max(1.,*(abs(x)for x in base['geometry'].values())):
        raise ArithmeticError('the derivative map changed the retained value coframe')
    return dict(value=base,Hcan_first=dW-1j*dOmega,geometry_first=geo['first'],
        raw_first=dx,wall_trace_first=dtrace,inherited_image_first=image_first,
        coordinate_slope=slope,first_order_zero_from_affine_raw_provenance=True,
        derivative_is_exact_of_saved_inside_cell_representation=True,
        continuous_Euler_or_physical_state_selected=False)
