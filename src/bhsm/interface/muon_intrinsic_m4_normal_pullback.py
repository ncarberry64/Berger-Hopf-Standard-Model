"""Intrinsic M4 metric applications in the retained moving normal chart.

The quotient radius is A B / sqrt(A**2+B**2), not the M8 orbit measure.
The homogeneous application uses exactly (q, qdot, lapse/shift, s, sdot)
from ``muon_moving_geometric_action``.  Its dense normal two-jet also retains
angular graph contacts.  No Higgs field, representation attachment, gauge
fluctuation, formation eigenmode, or stationary base is selected here.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .aether_n3_exact_full_local_action_jet_v17_60 import _linear, _variables
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from .muon_birth_candidate_geometry_action import wall_geometry_snapshot
from .muon_moving_geometric_action import _fields, _sqrt, retained_state


def intrinsic_m4_weight_jet(order, coordinates, velocities, multipliers, *,
                            source_value=0., source_rate=0., trial_normal=1.):
    """Return the full local two-jets of R4^3/l, l R4 and l R4^3.

    ``l=N sqrt(1-U^2)``, ``U=C*(wall_rate+beta)/N`` and
    ``wall=pi/4+s*trial_normal/C_star(q)``.  The time derivative of C_star
    is included in wall_rate; qdot is a jet coordinate, not an extra lapse.
    The weights multiply |D_t H|^2, -|D_unitS3 H|^2 and -V(H), respectively,
    in coordinate time and the unit round S3 measure.  No ambient derivative
    of the intrinsic H field is introduced.

    Mechanical coefficient jets are the geometric connection only.  A
    caller must supply its associated-bundle representation and any other
    gauge fields before using them in a Higgs covariant derivative.
    """
    if not isinstance(order, (int, np.integer)) or isinstance(order, (bool, np.bool_)) or order < 1:
        raise ValueError('positive retained Galerkin order required')
    if not all(math.isfinite(x) for x in (source_value, source_rate, trial_normal)):
        raise ValueError('finite source, rate and trial normal required')
    qdim=1+3*order; mdim=2*order; total=2*qdim+mdim+2
    qq=np.asarray(coordinates, dtype=float); vv=np.asarray(velocities, dtype=float)
    mm=np.asarray(multipliers, dtype=float)
    if qq.shape!=(qdim,) or vv.shape!=(qdim,) or mm.shape!=(mdim,):
        raise ValueError('retained state dimensions required')
    if not np.all(np.isfinite(np.concatenate((qq,vv,mm)))):
        raise ValueError('finite retained state required')
    q=_variables(qq,0,total); v=_variables(vv,qdim,total)
    m=_variables(mm,2*qdim,total)
    src,rate=_variables(np.array([source_value,source_rate]),total-2,total)
    signs_k=(-1.)**np.arange(1,order+1)
    signs_j=(-1.)**np.arange(order)
    Cstar=RADIUS0*(q[0]+_linear(q[1:1+order],signs_k)
                   +_linear(q[1+order:1+2*order],signs_j)).exp()
    if not math.isfinite(Cstar.value) or Cstar.value<=0:
        raise ValueError('positive finite wall radial coefficient required')
    amplitude=float(trial_normal)/Cstar
    if abs(float(source_value)*float(trial_normal)/Cstar.value)>=2/9:
        raise ValueError('source outside retained local normal chart')
    logCdot=v[0]+_linear(v[1:1+order],signs_k)+_linear(v[1+order:1+2*order],signs_j)
    wall=math.pi/4+amplitude*src
    wall_rate=amplitude*(rate-logCdot*src)
    fields=_fields(order,q,v,m,wall)
    C,A,B,N=(fields[name] for name in ('C','A','B','N'))
    if any(not math.isfinite(x.value) or x.value<=0 for x in (C,A,B,N)):
        raise ValueError('positive finite induced metric coefficients required')
    R4=A*B/_sqrt(A*A+B*B)
    lam=A*A/(A*A+B*B)
    U=C*(wall_rate+fields['beta'])/N
    if not math.isfinite(U.value) or abs(U.value)>=1:
        raise ValueError('timelike intrinsic material wall required')
    lapse=N*_sqrt(1-U*U)
    wT=R4**3/lapse; wS=lapse*R4; wV=lapse*R4**3
    for coefficient in (wT,wS,wV,lam,lam/R4,(lam-1)/R4):
        if not (math.isfinite(coefficient.value) and np.isfinite(coefficient.gradient).all()
                and np.isfinite(coefficient.hessian).all()):
            raise ValueError('finite metric and connection two-jets required')
    return dict(time_weight=wT,spatial_weight=wS,potential_weight=wV,
                wT=wT,wS=wS,wV=wV,R4=R4,induced_lapse=lapse,U=U,
                Cstar=Cstar,wall=wall,wall_rate=wall_rate,fields=fields,
                mechanical_connection_lambda=lam,
                mechanical_connection_one_minus_lambda=1-lam,
                section0_orthonormal_connection_coefficient=lam/R4,
                section1_orthonormal_connection_coefficient=(lam-1)/R4,
                qdim=qdim,mdim=mdim,source_indices=(total-2,total-1),
                coordinate_order=('q','qdot','lapse_shift','s','sdot'),
                angular_measure='unit round S3 measure, volume 2*pi^2',
                signature='+---',associated_bundle_representation=None,
                intrinsic_H_selected=False,full_gauge_connection_selected=False,
                physical_formation_mode_selected=False,stationarity_claim=False)


def homogeneous_kinetic_density(data):
    """Return the 4x4 density tensor jets diag(wT,-wS,-wS,-wS)."""
    size=len(data['time_weight'].gradient)
    result=np.empty((4,4), dtype=object)
    for i in range(4):
        for j in range(4):
            result[i,j]=Jet.constant(0.,size)
    result[0,0]=data['time_weight']
    for i in range(1,4):
        result[i,i]=-data['spatial_weight']
    return result


def metric_normal_two_jet(geometry, *, normal_value=1.,
                          normal_coordinate_time_derivative=0.,
                          normal_unit_s3_gradient=(0.,0.,0.),
                          embedding_coordinate_second=0., unit_s3_metric=None):
    """Apply a radial normal graph to the intrinsic metric, including contacts.

    At the retained wall beta=0.  In the inherited coordinates
    h=N^2 dt^2-R4^2 ghat-C^2[(z_dot+beta)dt+d_S3 z]^2.
    z_s=v/C_star and z_s,t=(v_dot-log(C_star)_dot*v)/C_star.
    ``embedding_coordinate_second`` is z_ss in this chart; its default zero
    is the affine chart used by the homogeneous application, not a solved
    embedding equation.  The gradient is a covector in the supplied unit
    S3 metric (the default is its orthonormal coframe at one point).

    Returned kinetic_density is sqrt(|h|) h^{-1}.  It contracts intrinsic
    covariant field/test derivatives; no H normal extension is assumed.
    Boundary test transport and gauge representation remain caller operands.
    """
    vals=(normal_value,normal_coordinate_time_derivative,embedding_coordinate_second)
    grad=np.asarray(normal_unit_s3_gradient,dtype=float)
    if not all(math.isfinite(x) for x in vals) or grad.shape!=(3,) or not np.isfinite(grad).all():
        raise ValueError('finite normal value, rate, gradient and embedding contact required')
    G=np.eye(3) if unit_s3_metric is None else np.asarray(unit_s3_metric,dtype=float)
    if G.shape!=(3,3) or not np.isfinite(G).all() or not np.allclose(G,G.T,atol=0.,rtol=0.):
        raise ValueError('symmetric positive unit S3 metric required')
    try:
        np.linalg.cholesky(G)
    except np.linalg.LinAlgError as exc:
        raise ValueError('symmetric positive unit S3 metric required') from exc
    C=float(geometry['C']); N=float(geometry['N']); r=float(geometry['R4'])
    if not all(math.isfinite(x) and x>0 for x in (C,N,r)):
        raise ValueError('positive finite retained wall geometry required')
    if float(geometry['shift']['beta'])!=0.:
        raise ValueError('retained zero-shift wall base required')
    first=geometry['chi_first_log']; second=geometry['chi_second_log']
    r_chi=float(first['R4'])
    r_chichi=float(second['R4'])
    n_chi=float(first['N']); n_chichi=float(second['N'])
    lc=float(geometry['coordinate_time_log_rates']['C'])
    bp=float(geometry['shift']['beta_chi'])
    if not all(math.isfinite(x) for x in (r_chi,r_chichi,n_chi,n_chichi,lc,bp)):
        raise ValueError('finite retained metric profile derivatives required')
    z1=float(normal_value)/C; z2=float(embedding_coordinate_second)
    r1=r_chi*z1; r2=r_chichi*z1*z1+r_chi*z2
    n1=n_chi*z1; n2=n_chichi*z1*z1+n_chi*z2
    u1=(float(normal_coordinate_time_derivative)+(bp-lc)*float(normal_value))/C
    p1=grad/C
    h=np.zeros((4,4)); h1=np.zeros((4,4)); h2=np.zeros((4,4))
    h[0,0]=N*N; h[1:,1:]=-r*r*G
    h1[0,0]=2*N*N*n1; h1[1:,1:]=-2*r*r*r1*G
    h2[0,0]=2*N*N*(n2+2*n1*n1)-2*C*C*u1*u1
    h2[0,1:]=h2[1:,0]=-2*C*C*u1*p1
    h2[1:,1:]=-2*r*r*(r2+2*r1*r1)*G-2*C*C*np.outer(p1,p1)
    inverse=np.linalg.inv(h)
    inverse1=-inverse@h1@inverse
    inverse2=2*inverse@h1@inverse@h1@inverse-inverse@h2@inverse
    volume=N*r**3*math.sqrt(float(np.linalg.det(G)))
    log_volume1=.5*float(np.trace(inverse@h1))
    log_volume2=.5*float(np.trace(inverse@h2-inverse@h1@inverse@h1))
    volume1=volume*log_volume1
    volume2=volume*(log_volume2+log_volume1**2)
    density=volume*inverse
    density1=volume1*inverse+volume*inverse1
    density2=volume2*inverse+2*volume1*inverse1+volume*inverse2
    return dict(metric=h,metric_first=h1,metric_second=h2,
                inverse_metric=inverse,inverse_metric_first=inverse1,inverse_metric_second=inverse2,
                volume_density=volume,volume_density_first=volume1,volume_density_second=volume2,
                kinetic_density=density,kinetic_density_first=density1,kinetic_density_second=density2,
                wall_coordinate_first=z1,wall_coordinate_second=z2,
                graph_speed_first=u1,graph_gradient_first=p1,
                log_R4_first=r1,log_R4_second=r2,
                induced_measure='intrinsic M4 coordinate time and unit S3 measure',signature='+---',
                intrinsic_H_normal_derivative=None,associated_bundle_representation=None,
                physical_formation_mode_selected=False,stationarity_claim=False)


def retained_intrinsic_m4_application(repository, side='outgoing_C2', *, trial_normal=1.):
    """Apply both metric backends to the receipt-pinned retained state only."""
    q,v,m=retained_state(Path(repository),side)
    geometry=wall_geometry_snapshot(q,v,m,order=12)
    return dict(geometry=geometry,
                weights=intrinsic_m4_weight_jet(12,q,v,m,trial_normal=trial_normal),
                normal_metric=metric_normal_two_jet(geometry,normal_value=trial_normal),
                side=side,full_stationary_base=False,intrinsic_H_selected=False)
