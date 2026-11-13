"""Analytic full18 current body on the corrected chronological field chart.

The future-coordinate first germ differentiates the saved affine geometry,
the inherited parent/reference clock, and the actual nodal field value.
At enters the body and its coefficient germ but no At kinetic rate is
introduced into the underlying field action. No pole/state is selected.
"""
from __future__ import annotations
import numpy as np
from .muon_continued_action_reality import _geometry,_affine_raw,action_reality_coefficient,_higgs_mass_realified
from .muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from .muon_parent_maxwell_full_weak import M
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation


def analytic_geometry_coordinate_first(raw,rate):
    """Exact first directional derivative of the owned analytic coframe."""
    x,v=(np.asarray(a,complex)for a in(raw,rate))
    if x.shape!=v.shape or x.ndim!=1 or len(x)<100 or not np.isfinite(x).all()or not np.isfinite(v).all():
        raise ValueError('the full analytic raw field and its coordinate germ are required')
    g=_geometry(x);q,dq=x[:37],v[:37];vel,dvel=x[37:74],v[37:74];m,dm=x[74:98],v[74:98]
    k,j=np.arange(1,13),np.arange(12);sk,sj=(-1.)**k,(-1.)**j
    cs=g['Cstar'];dlcs=dq[0]+dq[1:13]@sk+dq[13:25]@sj
    ld=vel[0]+vel[1:13]@sk+vel[13:25]@sj;dld=dvel[0]+dvel[1:13]@sk+dvel[13:25]@sj
    dc=(v[98]-x[98]*dlcs)/cs
    dcr=(v[99]-dld*x[98]-ld*v[98])/cs-g['wall_rate']*dlcs
    chi=g['wall'];ck=np.cos(4*k*chi);cj=np.cos(4*j*chi)
    dck=-4*k*np.sin(4*k*chi)*dc;dcj=-4*j*np.sin(4*j*chi)*dc
    win=np.sin(2*chi)**2;dwin=2*np.sin(4*chi)*dc
    u=q[1:13]@ck;du=dq[1:13]@ck+q[1:13]@dck
    b=win*(q[25:37]@cj);db=dwin*(q[25:37]@cj)+win*(dq[25:37]@cj+q[25:37]@dcj)
    w=win*(q[13:25]@cj);dw=dwin*(q[13:25]@cj)+win*(dq[13:25]@cj+q[13:25]@dcj)
    A,B,C=g['A'],g['B'],g['C'];radA=A/np.cos(chi);radB=B/np.sin(chi)
    dA=A*(dq[0]+du+db)-radA*np.sin(chi)*dc
    dB=B*(dq[0]+du-db)+radB*np.cos(chi)*dc
    dC=C*(dq[0]+du+dw)
    Nb=g['lapse_base'];dNb=Nb*(dm[:12]@ck+m[:12]@dck)
    beta=np.sin(4*chi)*(m[12:]@cj)
    dbeta=4*np.cos(4*chi)*dc*(m[12:]@cj)+np.sin(4*chi)*(dm[12:]@cj+m[12:]@dcj)
    U=g['U'];dU=(dC*(g['wall_rate']+beta)+C*(dcr+dbeta))/Nb-U*dNb/Nb
    den=A*A+B*B;dden=2*(A*dA+B*dB)
    dR=(dA*B+A*dB)/np.sqrt(den)-.5*g['R4']*dden/den
    dN=dNb*np.sqrt(1-U*U)-Nb*U*dU/np.sqrt(1-U*U)
    dlambda=2*A*dA/den-g['mechanical_lambda']*dden/den
    return dict(values=g,coordinate_first=dict(R4=dR,N=dN,mechanical_lambda=dlambda,
        Cstar=cs*dlcs,delta=dc,wall=dc,wall_rate=dcr,U=dU,C=dC,A=dA,B=dB,lapse_base=dNb))


def _affine_rate(raw):
    a=np.asarray(raw,complex);r=np.zeros_like(a);r[:37]=a[37:74];r[98]=a[99];return r


def chronological_current_body_point(phase,anchor,offset,field_value,field_coordinate_rate,lifts):
    """Full18 value and inside-edge germ, including all inherited contacts."""
    v,t=(np.asarray(a,complex)for a in(field_value,field_coordinate_rate))
    if v.shape!=(84,)or t.shape!=(84,)or not np.isfinite(v).all()or not np.isfinite(t).all():
        raise ValueError('all original84 field values and coefficient rates are required')
    app=action_reality_coefficient(phase,float(anchor),complex(offset))
    sample=profile_preserving_raw_sample(phase,float(anchor));rate=sample['raw_coordinate_time_derivative'].astype(complex)
    germ=analytic_geometry_coordinate_first(app['raw'],rate);g,dg=germ['values'],germ['coordinate_first']
    ng=phase['representation']['gauge_count'];trace_rate=np.einsum('fcj,j->fc',phase['representation']['wall_trace_map'],rate[100:100+ng])
    inherited_rate=0j
    if phase['receipt']['side']=='outgoing':
        time=complex(anchor)+complex(offset);pr=phase['arrays']['initial_pair'][0];rp,rc=phase['arrays']['reference_pair']
        lr=[]
        for a in(pr,rp,rc):
            b=_affine_raw(a,time);lr.append(analytic_geometry_coordinate_first(b,_affine_rate(a))['coordinate_first']['mechanical_lambda'])
        inherited_rate=lr[0]-dg['mechanical_lambda']-(lr[1]-lr[2]);trace_rate[2:]+=M*inherited_rate
    wall=app['wall_independent_plus_inherited'].copy();wall[2:]+=M*(g['mechanical_lambda']-1)
    wall_rate=trace_rate.copy();wall_rate[2:]+=M*dg['mechanical_lambda']
    wall+=(lifts['W']@v).reshape(5,4);wall_rate+=(lifts['W']@t).reshape(5,4)
    H=app['raw'][-8:-4]+lifts['hv']@v;Hd=rate[-8:-4]+lifts['hv']@t
    rep=lepton_current_hilbert_representation();G=lepton_unit_trace_gauge_representation()['generators']
    Os=np.einsum('ac,cij->aij',wall[2:],G);Osd=np.einsum('ac,cij->aij',wall_rate[2:],G)
    numerator=-1j*np.einsum('aij,ajk->ik',rep['alpha'],Os)+1.5*rep['gamma5']
    nd=-1j*np.einsum('aij,ajk->ik',rep['alpha'],Osd)
    Omega=np.einsum('c,cij->ij',wall[0],G)/g['N']
    Omegad=np.einsum('c,cij->ij',wall_rate[0],G)/g['N']-Omega*dg['N']/g['N']
    W=numerator/g['R4']+_higgs_mass_realified(H)
    Wd=nd/g['R4']-numerator*dg['R4']/g['R4']**2+_higgs_mass_realified(Hd)
    body=W-1j*Omega;bodyd=Wd-1j*Omegad
    return dict(Hcan=body,Hcan_coordinate_first=bodyd,Hcan_proper_first=bodyd/g['N'],
        W=W,W_coordinate_first=Wd,Omega_tau=Omega,Omega_tau_coordinate_first=Omegad,
        R=g['R4'],N=g['N'],R_coordinate_first=dg['R4'],N_coordinate_first=dg['N'],
        H_realified=H,H_coordinate_first=Hd,wall_connection=wall,wall_coordinate_first=wall_rate,
        field_value=v,field_coordinate_rate=t,original_base_Hcan=app['Hcan'],
        inherited_profile_coordinate_first=inherited_rate,mechanical_connection_counted_once=True,
        all18_and_fixed_Y_retained=True,At_action_kinetic_rate_inserted=False,
        future_coordinate_first_is_physical_pole_or_continuous_Euler=False)
