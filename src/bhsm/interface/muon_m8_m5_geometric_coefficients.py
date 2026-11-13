"""Source-owned M8 coframe / M5 quotient scalar coefficient jets.

The original coframe is (N dt,C(dchi+beta dt),A theta_u^a,B theta_v^a).
Both three-sphere factors and the normal direction are retained.  The
LEFT Maurer--Cartan convention is dtheta^i=-epsilon_ijk theta^j wedge
theta^k, [U_i,U_j]=2 epsilon_ijk U_k.  Curvature components use base
order (0,chi,a=1,2,3), F=domega+[omega,omega]/2, and full ordered mu,nu
summation in the KK contact -i LF F^i_mu,nu Gamma^mu Gamma^nu Gamma^i/8.

Every scalar input carries explicit independent analytic value/x/y/xy
jets. The square-root and logarithm VALUE anchors must be supplied in
the inherited nonzero source chart; no branch, absolute-value metric,
Clifford representation, internal carrier, background or state is chosen.
"""
from __future__ import annotations

from collections.abc import Mapping

import numpy as np


KEYS = ("value", "x", "y", "xy")
FIELD_NAMES = ("N","C","A","B","beta","np","cp","ap","bp",
               "betap","la","lb","lc")


def _scalar_jet(a,name):
    if not isinstance(a,Mapping) or set(a)!=set(KEYS):
        raise ValueError(name+" requires explicit value/x/y/xy")
    out={}
    for key in KEYS:
        v=np.asarray(a[key],complex)
        if v.shape!=() or not np.isfinite(v):
            raise ValueError(name+": finite scalar "+key+" required")
        out[key]=v.copy()
    return out


def _constant(value):
    return {key:np.asarray(value if key=="value" else 0,complex) for key in KEYS}


def _sum(*terms):
    return {key:sum(t[key] for t in terms) for key in KEYS}


def _scale(a,c):
    return {key:a[key]*c for key in KEYS}


def _mul(a,b):
    return dict(value=a["value"]*b["value"],
        x=a["x"]*b["value"]+a["value"]*b["x"],
        y=a["y"]*b["value"]+a["value"]*b["y"],
        xy=a["xy"]*b["value"]+a["x"]*b["y"]
           +a["y"]*b["x"]+a["value"]*b["xy"])


def _inverse(a):
    v=a["value"]
    if v==0:raise ValueError("nonzero source-chart denominator required")
    return dict(value=1/v,x=-a["x"]/v**2,y=-a["y"]/v**2,
        xy=2*a["x"]*a["y"]/v**3-a["xy"]/v**2)


def _div(a,b):return _mul(a,_inverse(b))


def _power(a,n):
    out=_constant(1)
    for _ in range(n):out=_mul(out,a)
    return out


def _anchored_sqrt(a,value):
    v=complex(value)
    if not np.isfinite(v) or v==0:
        raise ValueError("finite nonzero inherited LF square-root value required")
    # Absolute magnitudes enter only this consistency test, never a branch
    # selection or a replacement of an analytic geometric coefficient.
    if abs(v*v-a["value"])>5e-12*max(abs(v*v),abs(a["value"]),1e-300):
        raise ValueError("LF value is not the supplied source-chart square root")
    x,y=a["x"]/(2*v),a["y"]/(2*v)
    return dict(value=np.asarray(v),x=x,y=y,xy=(a["xy"]-2*x*y)/(2*v))


def _anchored_log(a,value):
    v=complex(value)
    if not np.isfinite(v) or abs(np.exp(v)-a["value"])>5e-12*max(abs(a["value"]),1e-300):
        raise ValueError("explicit logLF value does not match the inherited LF chart")
    w=a["value"]
    return dict(value=np.asarray(v),x=a["x"]/w,y=a["y"]/w,
        xy=a["xy"]/w-a["x"]*a["y"]/w**2)


def _exp(a):
    v=np.exp(a["value"])
    return dict(value=v,x=v*a["x"],y=v*a["y"],
                xy=v*(a["xy"]+a["x"]*a["y"]))


def m8_m5_geometric_coefficient_jets(fields, *, fiber_radius_value, fiber_log_value):
    """Return exact same-coframe coefficient/contact jets on a supplied germ.

    la/lb/lc are coordinate-time derivatives of log(A/B/C); ap/bp/cp and
    np are chi derivatives of log(A/B/C/N), and betap=partial_chi beta.
    These inputs include their actual total source contacts.  This function
    evaluates identities, not an Einstein/background or spectral solve.
    """
    if not isinstance(fields,Mapping) or set(fields)!=set(FIELD_NAMES):
        raise ValueError("exact original N,C,A,B,beta,np,cp,ap,bp,betap,la,lb,lc fields required")
    f={name:_scalar_jet(fields[name],name) for name in FIELD_NAMES}
    N,C,A,B,beta=(f[name] for name in ("N","C","A","B","beta"))
    for name in ("N","C","A","B"):
        if f[name]["value"]==0:raise ValueError("nonzero regular coframe "+name+" required")
    A2,B2=_power(A,2),_power(B,2)
    L2=_sum(A2,B2)
    LF=_anchored_sqrt(L2,fiber_radius_value)
    logLF=_anchored_log(LF,fiber_log_value)
    r=_div(_mul(A,B),LF)
    lam=_div(A2,L2)
    one_minus_lam=_sum(_constant(1),_scale(lam,-1))
    lambda_factor=_scale(_mul(lam,one_minus_lam),2)
    Lt=_div(_sum(_mul(A2,f["la"]),_mul(B2,f["lb"])),L2)
    Lchi=_div(_sum(_mul(A2,f["ap"]),_mul(B2,f["bp"])),L2)
    rt=_sum(f["la"],f["lb"],_scale(Lt,-1))
    rchi=_sum(f["ap"],f["bp"],_scale(Lchi,-1))
    E0logLF=_div(_sum(Lt,_scale(_mul(beta,Lchi),-1)),N)
    EchilogLF=_div(Lchi,C)
    E0lambda=_div(_mul(lambda_factor,_sum(f["la"],_scale(f["lb"],-1),
        _scale(_mul(beta,_sum(f["ap"],_scale(f["bp"],-1))),-1))),N)
    Echilambda=_div(_mul(lambda_factor,_sum(f["ap"],_scale(f["bp"],-1))),C)
    h08=_scale(_div(_sum(f["lc"],_scale(f["la"],3),_scale(f["lb"],3),
        _scale(_mul(beta,_sum(f["cp"],_scale(f["ap"],3),_scale(f["bp"],3))),-1),
        _scale(f["betap"],-1)),N),.5)
    hc8=_scale(_div(_sum(f["np"],_scale(f["ap"],3),_scale(f["bp"],3)),C),.5)
    h05=_scale(_div(_sum(f["lc"],_scale(rt,3),
        _scale(_mul(beta,_sum(f["cp"],_scale(rchi,3))),-1),_scale(f["betap"],-1)),N),.5)
    hc5=_scale(_div(_sum(f["np"],_scale(rchi,3)),C),.5)
    fiber_norm=_exp(_scale(logLF,-1.5))
    norm0,normchi=_scale(E0logLF,-1.5),_scale(EchilogLF,-1.5)
    delta0,deltachi=_sum(h08,_scale(h05,-1)),_sum(hc8,_scale(hc5,-1))
    F0a=_scale(_div(E0lambda,r),np.eye(3))
    Fchia=_scale(_div(Echilambda,r),np.eye(3))
    epsilon=np.zeros((3,3,3))
    epsilon[0,1,2]=epsilon[1,2,0]=epsilon[2,0,1]=1
    epsilon[0,2,1]=epsilon[2,1,0]=epsilon[1,0,2]=-1
    Fab=_scale(_div(_scale(_mul(lam,one_minus_lam),-2),_power(r,2)),epsilon)
    Ffull={}
    for key in KEYS:
        tensor=np.zeros((3,5,5),complex)
        tensor[:,0,2:]=F0a[key];tensor[:,2:,0]=-F0a[key]
        tensor[:,1,2:]=Fchia[key];tensor[:,2:,1]=-Fchia[key]
        tensor[:,2:,2:]=Fab[key]
        Ffull[key]=tensor
    kk=_scale(_mul(LF,Ffull),-1j/8)
    mu8=_mul(_mul(N,C),_mul(_power(A,3),_power(B,3)))
    mu5=_mul(_mul(N,C),_power(r,3))
    L3=_power(LF,3)
    vf=_scale(L3,2*np.pi**2)
    normalized_mode=_scale(fiber_norm,1/np.sqrt(2*np.pi**2))
    full_principal={key:np.r_[_inverse(C)[key],np.repeat(_inverse(A)[key],3),
                                  np.repeat(_inverse(B)[key],3)] for key in KEYS}
    return dict(LF=LF,r=r,**{"lambda":lam},log_LF=logLF,
        h0_M8=h08,hchi_M8=hc8,h0_M5=h05,hchi_M5=hc5,
        log_LF_coordinate_time=Lt,log_LF_radial=Lchi,
        log_r_coordinate_time=rt,log_r_radial=rchi,
        E0_log_LF=E0logLF,Echi_log_LF=EchilogLF,
        fiber_norm_Lm32=fiber_norm,normalized_fiber_constant_mode=normalized_mode,
        fiber_norm_E0_over_norm=norm0,fiber_norm_Echi_over_norm=normchi,
        mean_contact_difference_0=delta0,mean_contact_difference_chi=deltachi,
        mean_contact_cancellation_0=_sum(delta0,norm0),
        mean_contact_cancellation_chi=_sum(deltachi,normchi),
        E0_lambda=E0lambda,Echi_lambda=Echilambda,F_0a=F0a,F_chia=Fchia,F_ab=Fab,
        F_full=Ffull,KK_full_ordered=kk,
        mu8=mu8,mu5=mu5,fiber_volume=vf,
        coarea_density_rows=_sum(mu8,_scale(_mul(mu5,L3),-1)),
        analytic_fiber_normalization_rows=_sum(_mul(_power(normalized_mode,2),vf),_constant(-1)),
        original_seven_spatial_principal_coefficients=full_principal,
        original_seven_spatial_coframe_inverse_scales=full_principal,
        original_time_principal_coefficient=_inverse(N),
        original_chi_Gamma0_principal_coefficient=_scale(_div(beta,N),-1),
        vertical_DF_coefficient=_inverse(LF),
        original_u_spin_triple_coefficient=_scale(_inverse(A),1.5j),
        original_v_spin_triple_coefficient=_scale(_inverse(B),1.5j),
        input_field_order=FIELD_NAMES,jet_order=KEYS,
        base_frame_order=("0","chi","1","2","3"),
        curvature_fibre_order=("i","mu","nu"),
        curvature_angular_order=("i","a","b"),
        curvature_contact_summation="full ordered mu,nu; no extra antisymmetric factor2",
        original_S3_Haar_volume=2*np.pi**2,
        original_six_angular_and_one_normal_principals_retained=True,
        inverse_spatial_scales_alone_are_full_coordinate_principal_symbol=False,
        vertical_DF_set_to_zero=False,Clifford_or_SM_carrier_selected=False,
        positive_measure_or_physical_background_selected=False,
        source_coefficients_conjugated=False,new_action_coefficient_selected=False,
        full_native_operator_or_physical_outgoing_solution_claimed=False)
