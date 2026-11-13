"""Full original-to-Hopf geometric Spin16 lift, without a mode projection.

The original coframe uses (u,v); the adapted one uses (horizontal,fibre).
The same fixed Clifford arrays represent these two frames ONLY through
the explicit spin lift below. No SM/statistics carrier or physical state
is identified. Source x/y are independent analytic axes, never conjugated.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from .muon_m8_m5_geometric_coefficients import m8_m5_geometric_coefficient_jets
from .muon_m8_geometric_kk_clifford import m8_geometric_kk_clifford_jets


KEYS=('value','x','y','xy')


def _jet(a,shape,name):
    if set(a)!=set(KEYS):raise ValueError(name+': all explicit value/x/y/xy contacts required')
    out={k:np.asarray(a[k],complex)for k in KEYS}
    if any(v.shape!=shape or not np.isfinite(v).all()for v in out.values()):raise ValueError(name+': finite same-shape contacts required')
    return out


def _constant(a):return dict(value=np.asarray(a,complex),x=np.zeros_like(a,dtype=complex),y=np.zeros_like(a,dtype=complex),xy=np.zeros_like(a,dtype=complex))


def _sum(*a):return {k:sum(v[k]for v in a)for k in KEYS}


def _scale(a,b):return {k:a[k]*b for k in KEYS}


def _product(a,b,operation=lambda x,y:x*y):
    return dict(value=operation(a['value'],b['value']),
        x=operation(a['x'],b['value'])+operation(a['value'],b['x']),
        y=operation(a['y'],b['value'])+operation(a['value'],b['y']),
        xy=operation(a['xy'],b['value'])+operation(a['x'],b['y'])+operation(a['y'],b['x'])+operation(a['value'],b['xy']))


def _inverse(a):
    v=a['value']
    if v==0:raise ValueError('Regular nonzero scalar required')
    return dict(value=1/v,x=-a['x']/v**2,y=-a['y']/v**2,xy=2*a['x']*a['y']/v**3-a['xy']/v**2)


def _divide(a,b):return _product(a,_inverse(b))


def _matrix(a,M):return {k:a[k]*M for k in KEYS}


def _matmul(a,b):return _product(a,b,lambda x,y:x@y)


def _angle(A,B):
    av,bv=A['value'],B['value']
    if av.imag!=0 or bv.imag!=0 or min(av.real,bv.real)<=0:raise ValueError('Regular positive REAL original orbit radii required at base')
    den=av*av+bv*bv
    first=lambda aa,bb:(bv*aa-av*bb)/den
    xy=(bv*A['xy']-av*B['xy'])/den
    xy+=(-2*av*bv*A['x']*A['y']+2*av*bv*B['x']*B['y']
          +(av*av-bv*bv)*(A['x']*B['y']+B['x']*A['y']))/den**2
    return dict(value=np.asarray(np.arctan2(av.real,bv.real),complex),
        x=first(A['x'],B['x']),y=first(A['y'],B['y']),xy=xy)


def _exponential(theta,K,sign):
    V=expm(sign*theta['value']*K/2)
    generator=sign*K/2
    return dict(value=V,x=theta['x']*generator@V,y=theta['y']*generator@V,
        xy=(theta['xy']*generator+theta['x']*theta['y']*(generator@generator))@V)


def m8_original_hopf_spin_lift_jets(fields,*,gamma5_base):
    """Bind full adapted Cartan/KK body to the owned original coframe.

    fields is the SAME13-field explicit four-jet schema as the existing
    M8/M5 scalar coefficient owner. la/lb are coordinate-time log rates,
    ap/bp coordinate-chi log rates; all supplied source contacts are used.
    The regular base A,B,N,C is real positive. Source contacts may complex.

    psi_ad=S psi_orig, D_ad=S D_orig S^-1,
    S=exp[theta sum_a Gamma_u,a Gamma_v,a/2], theta=atan2(A,B).
    Thus S partial_mu S^-1=-theta_mu K/2. The full differential symbols
    retain U_a and V_a without a finite associated-mode projection.
    """
    names=('N','C','A','B','beta','np','cp','ap','bp','betap','la','lb','lc')
    if set(fields)!=set(names):raise ValueError('Same complete13-field geometry/source schema required')
    f={n:_jet(fields[n],(),n)for n in names}
    for n in('N','C','A','B'):
        v=f[n]['value']
        if v.imag!=0 or v.real<=0:raise ValueError('Real positive coframe base required: '+n)
    A,B,N,C,beta=(f[n]for n in('A','B','N','C','beta'))
    lv=np.sqrt(A['value']**2+B['value']**2)
    geo=m8_m5_geometric_coefficient_jets(f,fiber_radius_value=lv,fiber_log_value=np.log(lv))
    cliff=m8_geometric_kk_clifford_jets(gamma5_base=gamma5_base,geometric_coefficients=geo)
    G=cliff['gamma8_all'];I=np.eye(16,dtype=complex)
    bivectors=np.array([G[a+2]@G[a+5]for a in range(3)]);K=bivectors.sum(axis=0)
    theta=_angle(A,B);S,T=_exponential(theta,K,1),_exponential(theta,K,-1)
    # Direct supplied rates, including ALL their mixed source contacts.
    theta_t=_product(_divide(_product(A,B),_product(geo['LF'],geo['LF'])),_sum(f['la'],_scale(f['lb'],-1)))
    theta_r=_product(_divide(_product(A,B),_product(geo['LF'],geo['LF'])),_sum(f['ap'],_scale(f['bp'],-1)))
    spin_t,spin_r=_matrix(theta_t,-K/2),_matrix(theta_r,-K/2)
    ct=_matrix(_inverse(N),1j*G[0]);cr=_sum(_matrix(_divide(beta,N),-1j*G[0]),_matrix(_inverse(C),1j*G[1]))
    density=_sum(_matrix(geo['h0_M8'],1j*G[0]),_matrix(geo['hchi_M8'],1j*G[1]))
    original_body=_sum(density,_matrix(_inverse(A),1.5j*G[2]@G[3]@G[4]),_matrix(_inverse(B),1.5j*G[5]@G[6]@G[7]))
    transformed_body=_sum(_matmul(_matmul(S,original_body),T),_matmul(ct,spin_t),_matmul(cr,spin_r))
    # Full fixed-Clifford adapted Cartan decomposition. The vertical
    # connection acts on horizontal spin as well as fibre functions.
    eps=np.zeros((3,3,3))
    for a in range(3):eps[a,(a+1)%3,(a+2)%3]=1;eps[a,(a+2)%3,(a+1)%3]=-1
    Jh=np.array([sum(eps[a,b,c]*G[b+2]@G[c+2]/2 for b in range(3)for c in range(3))for a in range(3)])
    vertical_horizontal_spin=sum(1j*G[a+5]@Jh[a]for a in range(3))
    horizontal_spin=_matrix(_divide(_sum(_constant(1.),_scale(geo['lambda'],-2)),geo['r']),1.5j*G[2]@G[3]@G[4])
    vertical_spin=_matrix(_inverse(geo['LF']),1.5j*G[5]@G[6]@G[7])
    vertical_frame_connection=_matrix(_inverse(geo['LF']),vertical_horizontal_spin)
    adapted_body=_sum(density,horizontal_spin,vertical_spin,vertical_frame_connection,cliff['KK'])
    # Source jets of all unit U/V vector-field coefficients. These are
    # operator-valued differential coefficients, not a chosen mode cutoff.
    coefficient_U=[];coefficient_V=[]
    for a in range(3):
        coefficient_U.append(_sum(_matrix(_divide(_sum(_constant(1.),_scale(geo['lambda'],-1)),geo['r']),1j*G[a+2]),_matrix(_inverse(geo['LF']),1j*G[a+5])))
        coefficient_V.append(_sum(_matrix(_divide(geo['lambda'],geo['r']),-1j*G[a+2]),_matrix(_inverse(geo['LF']),1j*G[a+5])))
    # Independent coefficient identity from spin conjugating the original.
    original_U=[_matmul(_matmul(S,_matrix(_inverse(A),1j*G[a+2])),T)for a in range(3)]
    original_V=[_matmul(_matmul(S,_matrix(_inverse(B),1j*G[a+5])),T)for a in range(3)]
    rotation={}
    ca,sa=_divide(B,geo['LF']),_divide(A,geo['LF'])
    for key in KEYS:
        R=np.zeros((8,8),complex)
        if key=='value':R[:2,:2]=np.eye(2)
        for a in range(3):R[a+2,a+2]=R[a+5,a+5]=ca[key];R[a+2,a+5]=-sa[key];R[a+5,a+2]=sa[key]
        rotation[key]=R
    inv_rows=_matmul(S,T)
    inv_rows['value']-=I
    principal_rows={key:np.array([original_U[a][key]-coefficient_U[a][key]for a in range(3)]+[original_V[a][key]-coefficient_V[a][key]for a in range(3)])for key in KEYS}
    normalized_body=_sum(adapted_body,cliff['normalized_M8_time_normal_spin_density'],_scale(density,-1))
    product=np.eye(16,dtype=complex)
    for biv in bivectors:product=product@expm(theta['value']*biv/2)
    return dict(angle=theta,angle_coordinate_time=theta_t,angle_coordinate_chi=theta_r,
        S=S,analytic_inverse=T,coframe_rotation=rotation,spin_connection_time=spin_t,spin_connection_chi=spin_r,
        gamma_original_and_fixed_adapted_slots=G,boost_free_spatial_generators=bivectors,
        vertical_horizontal_spin_generators=Jh,
        time_coordinate_principal=ct,chi_coordinate_principal=cr,
        original_body=original_body,transformed_original_body=transformed_body,adapted_Cartan_KK_body=adapted_body,
        horizontal_spin_body=horizontal_spin,vertical_spin_body=vertical_spin,
        vertical_horizontal_spin_connection_body=vertical_frame_connection,
        KK=cliff['KK'],normalized_full_body=normalized_body,
        unit_U_principal={key:np.array([a[key]for a in coefficient_U])for key in KEYS},
        unit_V_principal={key:np.array([a[key]for a in coefficient_V])for key in KEYS},
        transformed_body_minus_adapted_body={key:transformed_body[key]-adapted_body[key]for key in KEYS},
        transformed_principal_minus_adapted=principal_rows,spin_inverse_rows=inv_rows,
        finite_gamma_ordered_product_difference=product-S['value'],
        generator_commutator_rows=np.array([a@b-b@a for a in bivectors for b in bivectors]),
        value_unitarity_rows=S['value'].conj().T@S['value']-I,
        geometric_coefficients=geo,
        component_convention='psi_ad=S psi_original; D_ad=S D_original S^-1',
        horizontal_vectors='H_a=(1-lambda)U_a-lambda V_a',vertical_vectors='T_a=U_a+V_a',
        all_original_u_v_directions_retained=True,associated_mode_projection_selected=False,
        complement_set_zero=False,native_statistics_or_SM_carrier_selected=False,
        physical_state_or_outgoing_domain_selected=False,physical_derivative_gate_passed=False)
