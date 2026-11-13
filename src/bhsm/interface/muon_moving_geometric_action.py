"""Moving normal applications of the retained geometric/eta cap action.

This is a sector weak-action backend, not a stationary full-field KKT solve.
It extends the actual v17.60 integrand with the v15.40 anchored response and
its material boundary trace.  The scalar source is a trial normal, never a
selected muon mode.  The two-jet suffices for its partial action application;
it does not claim a finite nonlinear continuation or a continuum enclosure.
"""
from __future__ import annotations

import json
import math
from hashlib import sha256
from pathlib import Path
import numpy as np

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .aether_n3_exact_full_local_action_jet_v17_60 import _linear, _variables
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0, HOPF_ORBIT_VOLUME
from .aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient

STATE_RECEIPT = 'artifacts/muon_birth_transfer_value_20261008/retained_reset/run_1/result.json'
STATE_SOURCE = 'artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz'


def _compose(x, value, first, second):
    return Jet(value, first*x.gradient,
               first*x.hessian+second*np.outer(x.gradient,x.gradient))


def _sin(x):
    if not isinstance(x, Jet):
        return math.sin(x)
    return _compose(x, math.sin(x.value), math.cos(x.value), -math.sin(x.value))


def _cos(x):
    if not isinstance(x, Jet):
        return math.cos(x)
    return _compose(x, math.cos(x.value), -math.sin(x.value), -math.cos(x.value))


def _atanh(x):
    u=x.value
    if abs(u)>=1:
        raise ValueError("timelike material wall required")
    return _compose(x,math.atanh(u),1/(1-u*u),2*u/(1-u*u)**2)


def _sqrt(x):
    r=math.sqrt(x.value)
    return _compose(x,r,1/(2*r),-1/(4*r**3))


def retained_state(repository, side='outgoing_C2'):
    repository=Path(repository)
    if side not in ('outgoing_C2','incoming_C1_E1'):
        raise ValueError('retained incoming/outgoing state side required')
    data=json.loads((repository/STATE_RECEIPT).read_text(encoding='utf8'))
    b=data['geometry_field_blocks'][side]
    parts=tuple(np.array([float.fromhex(x) for x in b[name]['binary64_hex']])
                for name in ('q','velocity','lapse_shift_multipliers'))
    path=repository/STATE_SOURCE
    expected=next(row['sha256'] for row in data['input_identities'] if row['path']==STATE_SOURCE)
    if sha256(path.read_bytes()).hexdigest()!=expected:
        raise ValueError('retained state hash disagrees with action receipt')
    with np.load(path,allow_pickle=False) as original:
        start=0 if side=='outgoing_C2' else 98
        state=np.asarray(original['state'][start:start+98],dtype=float)
    received=np.concatenate(parts)
    if received.shape!=(98,) or not np.array_equal(received.view(np.uint64),state.view(np.uint64)):
        raise ValueError('receipt action blocks disagree with the original retained state')
    return parts


def response_two_jet(chi, source, k):
    """Exact anchored response derivatives for f=chi+s*k*(21sin2chi+5sin6chi).

    Z0=pi/16, Z_s=0, Z_ss=-231*pi*k**2/4 on [0,pi/2].
    Both f and sigma material-wall traces are constant through order two
    when chi_wall=pi/4-16*k*s.  Higher jets are deliberately not supplied.
    """
    a=21*_sin(2*chi)+5*_sin(6*chi)
    sigma0=-.5+2*chi/math.pi-_sin(4*chi)/(2*math.pi)
    sigma1=k*(52*_sin(2*chi)-14*_sin(6*chi)-2*_sin(10*chi))/math.pi
    sigma2=k*k*(982*_sin(4*chi)-256*_sin(8*chi)
                     -140*_sin(12*chi)-12.5*_sin(16*chi))/math.pi
    return chi+source*k*a, sigma0+source*sigma1+source*source*sigma2/2


def _fields(order,q,v,m,chi):
    n=len(q[0].gradient)
    radius=RADIUS0*q[0].exp()
    ks=np.arange(1,order+1); js=np.arange(order)
    ck=[_cos(4*int(j)*chi) for j in ks]
    cj=[_cos(4*int(j)*chi) for j in js]
    sk=[_sin(4*int(j)*chi) for j in ks]
    sj=[_sin(4*int(j)*chi) for j in js]
    def lin(vv,cc):
        return sum((x*y for x,y in zip(vv,cc)),Jet.constant(0.,n))
    window=_sin(2*chi)**2; wp=2*_sin(4*chi)
    u=lin(q[1:1+order],ck)
    w=window*lin(q[1+order:1+2*order],cj)
    b=window*lin(q[1+2*order:1+3*order],cj)
    up=lin(q[1:1+order],[-4*int(j)*x for j,x in zip(ks,sk)])
    wpc=[wp*x-4*int(j)*window*y for j,x,y in zip(js,cj,sj)]
    bp=lin(q[1+2*order:1+3*order],wpc)
    cprime=up+lin(q[1+order:1+2*order],wpc)
    aprime=up+bp-_sin(chi)/_cos(chi)
    bprime=up-bp+_cos(chi)/_sin(chi)
    C=radius*(u+w).exp(); A=radius*(u+b).exp()*_cos(chi)
    B=radius*(u-b).exp()*_sin(chi)
    N=lin(m[:order],ck).exp()
    nprime=lin(m[:order],[-4*int(j)*x for j,x in zip(ks,sk)])
    beta=_sin(4*chi)*lin(m[order:],cj)
    betaprime=4*_cos(4*chi)*lin(m[order:],cj)+_sin(4*chi)*lin(
        m[order:],[-4*int(j)*x for j,x in zip(js,sj)])
    udot=lin(v[1:1+order],ck)
    wdot=window*lin(v[1+order:1+2*order],cj)
    bdot=window*lin(v[1+2*order:1+3*order],cj)
    lc=v[0]+udot+wdot; la=v[0]+udot+bdot; lb=v[0]+udot-bdot
    return dict(C=C,A=A,B=B,N=N,cp=cprime,ap=aprime,bp=bprime,
                np=nprime,beta=beta,betap=betaprime,lc=lc,la=la,lb=lb)


def moving_cap_action_jet(order,coordinates,velocities,multipliers,*,points=96,
                          source_value=0.,source_rate=0.,trial_normal=1.):
    """Apply the retained cap action in an independent material normal chart.

    Coordinates are (q,qdot,lapse/shift,s,sdot).  At s=sdot=0 this is the
    unchanged v17.60 action.  Eulerian geometry is held fixed in s; only the
    join/response field and integration wall move.  Pullback integration
    evaluates all metric/ADM/trace terms at chi=y*chi_wall with its Jacobian.
    The chart's physical wall speed is trial_normal/C_star(q).  The sdot
    Hessian is an eta/FR kinetic contribution, not the full wall inertia.
    The coefficient-locked moving GHY/Hayward completion is included.
    The surface sector is returned per gamma, with all internal/mixed
    derivatives; active matter and event-drive applications remain separate.
    """
    if not all(math.isfinite(x) for x in (source_value,source_rate,trial_normal)):
        raise ValueError('finite trial source, rate and normal required')
    qdim=1+3*order; mdim=2*order; total=2*qdim+mdim+2
    qq=np.asarray(coordinates,dtype=float); vv=np.asarray(velocities,dtype=float)
    mm=np.asarray(multipliers,dtype=float)
    if qq.shape!=(qdim,) or vv.shape!=(qdim,) or mm.shape!=(mdim,):
        raise ValueError('retained state dimensions required')
    if not np.all(np.isfinite(np.concatenate((qq,vv,mm)))):
        raise ValueError('finite state required')
    q=_variables(qq,0,total); v=_variables(vv,qdim,total)
    m=_variables(mm,2*qdim,total)
    s=_variables(np.array([source_value,source_rate]),total-2,total)
    src,rate=s
    signs_k=(-1.)**np.arange(1,order+1)
    signs_j=(-1.)**np.arange(order)
    Cstar=RADIUS0*(q[0]+_linear(q[1:1+order],signs_k)
                   +_linear(q[1+order:1+2*order],signs_j)).exp()
    k=-float(trial_normal)/(16*Cstar)
    # Eulerian time derivative of the q-dependent unit-normal chart amplitude.
    logCdot=v[0]+_linear(v[1:1+order],signs_k)+_linear(v[1+order:1+2*order],signs_j)
    kdot=-k*logCdot
    wall=math.pi/4-16*k*src
    if abs(source_value*trial_normal/float(Cstar.value))>=2/9:
        raise ValueError('trial chart is outside its proved local monotonicity neighborhood')
    nodes,weights=np.polynomial.legendre.leggauss(points)
    bulk=Jet.constant(0.,total); inertia=Jet.constant(0.,total)
    for y,weight in zip((nodes+1)/2,weights/2):
        chi=wall*y; F=_fields(order,q,v,m,chi)
        f,sigma=response_two_jet(chi,src,k)
        a=21*_sin(2*chi)+5*_sin(6*chi)
        fp=1+src*k*(42*_cos(2*chi)+30*_cos(6*chi))
        fdot=(rate*k+src*kdot)*a
        C,A,B,N=(F[z] for z in ('C','A','B','N'))
        Hc=(F['lc']-F['beta']*F['cp']-F['betap'])/N
        Ha=(F['la']-F['beta']*F['ap'])/N
        Hb=(F['lb']-F['beta']*F['bp'])/N
        adm=Hc**2+3*Ha**2+3*Hb**2-(Hc+3*Ha+3*Hb)**2
        fn=(fdot-F['beta']*fp)/N
        X=fp**2/C**2+3*_cos(f)**2/A**2+3*_sin(f)**2/B**2-fn**2
        if not math.isfinite((1+X**3).value) or (1+X**3).value<=0:
            raise ValueError('retained eta Legendre form must stay positive')
        loc=1-4*sigma**2; volume=C*A**3*B**3; spatial=A**3*B**3
        grav=3*spatial/C*N*(F['np']*(F['ap']+F['bp'])
                           +F['ap']**2+F['bp']**2+3*F['ap']*F['bp'])
        alg=N*volume*(3/A**2+3/B**2-.5*(15*5**(1/3)/4)
                      -loc*(.5*X+.125*X**4)+.5*adm)
        bulk=bulk+weight*wall*(grav+alg)
        inertia=inertia+weight*wall*volume*loc*(1+X**3)/N
    if not math.isfinite(inertia.value) or inertia.value<=0:
        raise ValueError('positive finite FR inertia denominator required')
    FR=-.25/(2*HOPF_ORBIT_VOLUME**2*inertia)
    Fwall=_fields(order,q,v,m,wall)
    A,B,N=(Fwall[z] for z in ('A','B','N'))
    R4=A*B/_sqrt(A*A+B*B)
    casimir=-standard_model_casimir_coefficient()/R4*N
    # The original ADM/EH spatial integration already contains fixed-wall
    # GHY.  For U=C*(z_dot+beta)/N and theta=atanh(U), covariant GHY is
    # rho*Dt(theta)+N*rho*U*K+(N*rho)'/C.  The moving-domain EH divergences
    # cancel U*K and N'/C; spatial IBP cancels rho'/C.  The owned Hayward
    # endpoint cancels [rho*theta], leaving exactly -theta*Dt(rho).
    # It is one gravitational completion, not an additional membrane term.
    wall_rate=-16*(k*rate+kdot*src)
    U=Fwall['C']*(wall_rate+Fwall['beta'])/N
    theta=_atanh(U)
    rho=A**3*B**3
    rho_rate=3*rho*(Fwall['la']+Fwall['lb']
                    +(Fwall['ap']+Fwall['bp'])*wall_rate)
    moving_gravitational_boundary=-theta*rho_rate
    # Symbolic gamma is deliberately not assigned a measured value.  These
    # are complete derivatives of the same signed area sector, including
    # its internal and mixed blocks, in the same angular action measure.
    surface_per_gamma=-N*rho*_sqrt(1-U*U)
    return dict(total=bulk+FR+casimir+moving_gravitational_boundary,
                fixed_wall_extension=bulk+FR+casimir,bulk=bulk,FR=FR,
                moving_GHY_Hayward=moving_gravitational_boundary,
                surface_per_gamma=surface_per_gamma,
                retained_local_Casimir=casimir,FR_denominator=inertia,
                Cstar=Cstar,wall=wall,source_indices=(total-2,total-1),
                qdim=qdim,mdim=mdim)


def weak_action_blocks(data):
    """Expose the actual weak Euler/constraint and normal-source coefficients.

    B_q = S_qs-D_t S_qdot,s and B_m=S_ms.  The field Hessian is the temporal
    differential operator assembled from qq,qv,vq,vv,qm,vm,mm blocks, not an
    algebraic inverse of the local (q,qdot,m) matrix.  Endpoint S_qdot,s is
    retained as a boundary momentum contact.  No stationary-base assumption.
    """
    S=data['total']; nq=data['qdim']; nm=data['mdim']; ns,nr=data['source_indices']
    h=S.hessian; q=slice(0,nq); v=slice(nq,2*nq); m=slice(2*nq,2*nq+nm)
    return dict(S=float(S.value),S_q=S.gradient[q],canonical_momentum=S.gradient[v],
                multiplier_constraint_residual=S.gradient[m],
                normal_first_variation=float(S.gradient[ns]),
                B_q_direct=h[q,ns],B_q_momentum_contact=h[v,ns],B_m=h[m,ns],
                B_q_rate_direct=h[q,nr],B_q_rate_momentum_contact=h[v,nr],
                B_m_rate=h[m,nr],D_ss=float(h[ns,ns]),
                D_s_rate=float(h[ns,nr]),eta_FR_kinetic_component=float(h[nr,nr]),
                H_qq=h[q,q],H_qv=h[q,v],H_vq=h[v,q],H_vv=h[v,v],
                H_qm=h[q,m],H_vm=h[v,m],H_mm=h[m,m],
                stationarity_claim=False,physical_formation_mode_selected=False)
