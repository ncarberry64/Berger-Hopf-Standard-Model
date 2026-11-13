"""Uniform lapse/source-clock Euler identity of the retained child action.

The uniform log-lapse is NOT one of the represented twelve lapse modes.
This comparison derivative is evaluated before fixing that clock gauge;
it adds no equation to the original146 constitutive application. Inherited
connection time derivatives are independent prescribed source slots and
must be scaled in a simultaneous time-coordinate transformation.
"""
from __future__ import annotations
import numpy as np
from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_holomorphic_normal_geometry import (
    _geometry_variables, _fields, _response, _sqrt, _cos, _atanh,
    anchored_holomorphic_chart, holomorphic_geometry_rows,
)
from .muon_exact_material_response import _rule
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import HOPF_ORBIT_VOLUME
from .aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from .muon_holomorphic_child_action import _affine_geometry, _parameters
from .muon_nonlinear_n0_field_action import analytic_constant_maxwell_jet, analytic_intrinsic_n0_jet
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL


def uniform_clock_action_twojet(raw_child, time, initial_pair, reference_pair, rep,
                                *, nu_squared_action, surface_gamma=None,
                                log_uniform_lapse=0., inherited_time_increment=0.):
    """Two independent analytic comparison slots: logN0 and source rate.

    Return a two-jet without field-coordinate conjugation. At slot0=slot1=0
    its value is the original full action. The first source slot scales
    only the inherited TOTAL lambda_tau, not its value/radial slots.
    """
    raw=np.asarray(raw_child,complex)
    if raw.shape!=(268,):raise ValueError('same original raw268 required')
    q,v,m,delta,dr,wall,Cstar=_geometry_variables(raw[:100],differentiate=False)
    chart=anchored_holomorphic_chart(delta.value)
    constant=lambda a:Jet.constant(complex(a),2)
    alpha=Jet.affine(complex(log_uniform_lapse),np.array([1.,0.])).exp()
    kappa=Jet.affine(complex(inherited_time_increment),np.array([0.,1.]))
    bulk=constant(0.);inertia=constant(0.)
    nodes,weights=_rule(rep['cap_points'])
    for y,weight in zip(nodes,weights):
        chi=wall*y;f0=_fields(12,q,v,m,chi);r0=_response(chi,delta,dr,chart)
        f={k:constant(a.value)for k,a in f0.items()}
        r={k:constant(a.value)for k,a in r0.items()}
        C,A,B=f['C'],f['A'],f['B'];N=alpha*f['N']
        hc=(f['lc']-f['beta']*f['cp']-f['betap'])/N
        ha=(f['la']-f['beta']*f['ap'])/N;hb=(f['lb']-f['beta']*f['bp'])/N
        adm=hc*hc+3*ha*ha+3*hb*hb-(hc+3*ha+3*hb)**2
        fn=(r['fdot']-f['beta']*r['fprime'])/N
        X=r['fprime']**2/C**2+3*_cos(r['f'])**2/A**2+3*np.sin(r['f'].value)**2/B**2-fn*fn
        loc=r['localization_weight'];vol=C*A**3*B**3;spatial=A**3*B**3
        grav=3*spatial/C*N*(f['np']*(f['ap']+f['bp'])+f['ap']**2+f['bp']**2+3*f['ap']*f['bp'])
        alg=N*vol*(3/A**2+3/B**2-.5*(15*5**(1/3)/4)-loc*(.5*X+.125*X**4)+.5*adm)
        bulk+=weight*wall.value*(grav+alg);inertia+=weight*wall.value*vol*loc*(1+X**3)/N
    f0=_fields(12,q,v,m,wall);f={k:constant(a.value)for k,a in f0.items()}
    A,B=f['A'],f['B'];N=alpha*f['N'];R=A*B/_sqrt(A*A+B*B)
    U=f['C']*(dr.value+f['beta'])/N;rho=A**3*B**3
    rho_rate=3*rho*(f['la']+f['lb']+(f['ap']+f['bp'])*dr.value)
    induced=N*_sqrt(1-U*U)
    total=bulk-.25/(2*HOPF_ORBIT_VOLUME**2*inertia)-standard_model_casimir_coefficient()/R*N-_atanh(U)*rho_rate
    area=-rho*induced
    if surface_gamma is not None:total+=surface_gamma*area
    geo=holomorphic_geometry_rows(raw[:100],rep['rho'],differentiate=False)
    initial,reference=np.asarray(initial_pair,complex),np.asarray(reference_pair,complex)
    p=_affine_geometry(initial[0],time);rp,rc=(_affine_geometry(x,time)for x in reference)
    eff=_parameters(p,rep['rho'])-_parameters(rp,rep['rho'])+_parameters(rc,rep['rho'])
    gb=np.asarray(rep['gauge_basis'])[:,:,0].reshape(len(eff),80,20)
    gr=np.asarray(rep['gauge_radial_basis'])[:,:,0].reshape(len(eff),80,20)
    av=np.einsum('rjc,j->rc',gb,raw[100:180]).reshape(-1,5,4)
    at=np.einsum('rjc,j->rc',gb,raw[180:260]).reshape(-1,5,4)
    ar=np.einsum('rjc,j->rc',gr,raw[100:180]).reshape(-1,5,4)
    av[:,2:]+=M[None]*(eff[:,0]-1)[:,None,None]
    at[:,2:]+=M[None]*eff[:,1,None,None];ar[:,2:]+=M[None]*eff[:,2,None,None]
    for j,(row,weight)in enumerate(zip(geo['rows'],rep['radial_quadrature'])):
        e,r,d,k,b=(constant(row[n].value)for n in('electric','radial','angular','electric_radial','shift'))
        e/=alpha;k/=alpha;r*=alpha;d*=alpha
        cur=analytic_constant_maxwell_jet(av[j],at[j],ar[j],np.ones(5))['curvatures']
        X,T,RR,BB=(cur[n]for n in('Ftr','Ft','Fr','B'))
        source=M*eff[j,1]
        y2=constant(np.sum(T*T))-2*b*np.sum(T*RR)+b*b*np.sum(RR*RR)
        y2+=2*kappa*(np.sum(source*T)-b*np.sum(source*RR))+kappa*kappa*np.sum(source*source)
        full=.5*(k*(X@X)+e*y2-r*np.sum(RR*RR)-d*np.sum(BB*BB))
        lam,lt,lr=(constant(row[n].value)for n in('connection_lambda','lambda_tau','lambda_rho'))
        baseline=.5*np.sum(M*M)*(e*(lt-b*lr)**2-r*lr**2-d*(2*(lam-1)*lam)**2)
        total+=MAXWELL_TO_CAP*weight*(full-baseline)
    ew=(_parameters(p,[WALL])-_parameters(rp,[WALL])+_parameters(rc,[WALL]))[0]
    wall_A=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:180]);wall_A[2:]+=M*(ew[0]-1)
    for j,w in enumerate((R**3/induced,induced*R,induced*R**3)):
        a=analytic_intrinsic_n0_jet(wall_A,raw[260:264],raw[264:],np.eye(3)[j],
            lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu_squared_action)
        total+=w*a['value']
    return dict(action=total,surface_per_gamma=area,uniform_log_lapse_is_original_multiplier=False,
        inherited_source_time_slot_scaled_separately=True,original146_equations_modified=False,
        physical_energy_or_phase_space_constraint_selected=False)
