"""Evaluated pieces of native cutoff/domain binding and whole replacement.

No physical cutoff, formation mode, CAR state or C1/C2 transmission map is
selected. Completed native0 arrays are inputs, never recomputed here.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import schur,solve_sylvester,expm

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_moving_geometric_action import moving_cap_action_jet,_sqrt
from .muon_coupled_reference_replacement import GEOMETRY_IDS,_geometry_fields
from .muon_stationary_native_reference_load import factor_twojet


def surface_inertia_forms(raw):
    """Exact bare-area proper-normal kinetic coefficients and100 two-jets.

    L/gamma=-N rho sqrt(1-U²), p=C/(Cstar sqrt(1-U²)), dτ=l dt.
    l L_sdot,sdot/p²=rho identically. No mode norm or active-stratum
    multiplicity is supplied by this local identity.
    """
    raw=np.asarray(raw,float)
    if raw.shape!=(100,):raise ValueError('original geometry100 required')
    w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],
        source_value=raw[98],source_rate=raw[99])
    f=w['fields'];Q=_sqrt(1-w['U']**2)
    p=f['C']/(w['Cstar']*Q);l=w['induced_lapse']
    result={}
    for name,rho in [('M8',f['A']**3*f['B']**3),('M5_one_quotient',w['R4']**3/(2*np.pi**2))]:
        coordinate_inertia=rho*f['C']**2/(w['Cstar']**2*f['N']*Q**3)
        momentum=rho*p*w['U']
        source=Jet.affine(raw[98],np.eye(100)[98])
        recovered=l*coordinate_inertia/p**2
        delta=recovered-rho
        area=-l*rho
        result[name]=dict(proper_inertia_per_gamma=rho,
            coordinate_sdot_inertia_per_gamma=coordinate_inertia,
            coordinate_source_momentum_per_gamma=momentum,
            qdot_momentum_factor_per_gamma=-source*momentum,
            original_area_per_gamma=area,
            identity_twojet_defect=max(abs(delta.value),np.max(abs(delta.gradient)),np.max(abs(delta.hessian))),
            independent_area_kinetic_defect=abs(area.hessian[99,99]-coordinate_inertia.value),
            independent_momentum_kinetic_defect=abs(momentum.gradient[99]-coordinate_inertia.value))
    lam=w['mechanical_connection_lambda'];wr=w['wall_rate']
    rate_log_R=(1-lam)*(f['la']+f['ap']*wr)+lam*(f['lb']+f['bp']*wr)
    return dict(forms=result,proper_normal_projection=p,induced_lapse=l,
        wall_velocity=w['U'],ambient_lapse=f['N'],
        canonical_Cauchy_density_factor=_sqrt(w['R4']**3),
        proper_density_connection=1.5*rate_log_R/l,
        radius=w['R4'])


def cutoff_inertia_coefficient(jet100,*,dimension,cutoff_anchor,full_geometry=False):
    """Known -c^(-d/2) rho coefficient in the implicit cutoff row.

    Return its152 (static151,c) or101 (geometry100,c) two-jet, PER unassigned alpha and
    squared formed-mode trace/pairing. This is an actually evaluated
    inertia-form coefficient, not the complete contraction or cutoff row.
    """
    c=float(cutoff_anchor)
    if not np.isfinite(c) or c<=0 or dimension not in (4,7):
        raise ValueError('explicit positive numerical anchor and registered surface dimension required')
    size=101 if full_geometry else 152
    ids=np.arange(100) if full_geometry else GEOMETRY_IDS
    count=len(ids)
    g=np.zeros(size);h=np.zeros((size,size))
    g[:count]=jet100.gradient[ids]
    h[:count,:count]=jet100.hessian[np.ix_(ids,ids)]
    rho=Jet(jet100.value,g,h);gc=np.zeros(size);gc[-1]=1
    power=-dimension/2
    cp=Jet(c**power,power*c**(power-1)*gc,
           power*(power-1)*c**(power-2)*np.outer(gc,gc))
    return -rho*cp


def recorded_local_value(saved,radial_points,radial_weights):
    """Value of the newly removed full local term, using completed arrays.

    No Maxwell solve, weak response or native heat calculation is repeated.
    The same material Higgs action supplies its value. Background mechanical
    Maxwell energy is subtracted here because it already lives in the cap.
    """
    from .muon_adopted_incoming_reference import static_field_maps
    from .muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
    from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from .muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
    from .muon_parent_gauge_geometry_correction import retained_scalar_matching_coefficients,ORBIT_VOLUME_SQUARED
    from .muon_parent_retarded_hypercharge import WALL
    x=saved['provisional_iterate151'];raw=_geometry_fields(x);n=len(radial_points)
    p,pr=static_field_maps(radial_points,enrich_temporal=True)
    independent=(p@x[62:146]).reshape(n,5,4)
    independent_r=(pr@x[62:146]).reshape(n,5,4)
    total,total_r=saved['after_total_connection'],saved['after_total_connection_radial']
    density=saved['after_densities']
    full=analytic_constant_maxwell_batch(total,np.zeros_like(total),total_r,density)['value']
    bg=analytic_constant_maxwell_batch(total-independent,np.zeros_like(total),total_r-independent_r,density)['value']
    maxwell=MAXWELL_TO_CAP*np.dot(radial_weights,full-bg)
    w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    wm,_=static_field_maps(np.array([WALL]),enrich_temporal=True)
    matching=retained_scalar_matching_coefficients()
    scalar=material_intrinsic_higgs_gauge_action_jet(w,
        scalar_coefficients=x[146:150],scalar_value_map=np.eye(4)[None],
        scalar_derivative_map=np.zeros((1,4,4,4)),gauge_coefficients=x[62:146],
        gauge_trace_map=wm.reshape(1,5,4,84),angular_quadrature=np.ones(1),
        lambda_H=matching['lambda_H'],nu_squared_GeV_squared=matching['nu_squared_GeV_squared'],
        log_energy_unit_GeV=float(x[150]))['action']/ORBIT_VOLUME_SQUARED
    imaginary=max(abs(complex(maxwell).imag),abs(complex(scalar.value).imag))
    if imaginary>1e-12:raise ArithmeticError('real local action acquired an imaginary component')
    return dict(full_local_action_value=float((maxwell+scalar.value).real),
        independent_Maxwell_value=float(maxwell.real),material_Higgs_value=float(np.real(scalar.value)),
        real_action_imaginary_defect=float(imaginary))


def remove_recorded_local(saved):
    """Remove the ENTIRE recorded independent Maxwell/material Higgs term.

    Reuse saved full known two-jets at exactly the same background. Only
    the geometric bare-cap piece needed for this new extraction is applied.
    Its mechanical Maxwell term is retained. The already removed zeta is
    neither applied again nor precision-tested. This is not an allocation
    of continuum overlap to one heat block.
    """
    x=saved['provisional_iterate151'];raw=_geometry_fields(x)
    a=moving_cap_action_jet(12,raw[:37],raw[37:74],raw[74:98],points=32,
        source_value=raw[98],source_rate=raw[99])
    bare=a['bulk']+a['FR']+a['moving_GHY_Hayward']
    g=np.zeros(151);h=np.zeros((151,151))
    g[:62]=bare.gradient[GEOMETRY_IDS]
    h[:62,:62]=bare.hessian[np.ix_(GEOMETRY_IDS,GEOMETRY_IDS)]
    return dict(bare_gradient151=g,bare_Hessian151=h,bare_action_value=float(bare.value),
        local_gradient151=saved['after_known_gradient']-g,
        local_Hessian151=saved['after_known_hessian']-h,
        bare_geometry_gradient100=bare.gradient,bare_geometry_Hessian100=bare.hessian)


def past_future_weyl(theta,*,spectral_parameter,z=-1j):
    """Same-action stationary half-line return, including all two-jets.

    lambda<0 is a native resolvent coordinate, not energy or cutoff.
    Past L2 decay picks the positive-real exponent subspace. The future
    map is only the already-used stationary comparison's diagnostic mate,
    never a physical child/vacuum or a C1/C2 identity gluing.
    """
    lam=float(spectral_parameter)
    if not np.isfinite(lam) or lam>=0:raise ValueError('explicit negative native resolvent parameter required')
    f=factor_twojet(theta);w,wg,wh=f['W'];o,og,oh=f['Omega']
    C,B=w+z*o,w-z*o
    cg,bg=np.zeros((23,18,18),complex),np.zeros((23,18,18),complex)
    ch,bh=np.zeros((23,23,18,18),complex),np.zeros((23,23,18,18),complex)
    cg[:22],bg[:22]=wg+z*og,wg-z*og
    ch[:22,:22],bh[:22,:22]=wh+z*oh,wh-z*oh
    system=np.block([[-C,np.eye(18)],[-lam*np.eye(18),B]])
    eig=np.linalg.eigvals(system)
    if np.min(abs(eig.real))<1e-8:raise ArithmeticError('past/future dichotomy unresolved')
    result={}
    for name,sign in [('past',1),('future_comparison',-1)]:
        T,Q,count=schur(system,output='complex',sort=lambda x:sign*x.real>0)
        if count!=18:raise ArithmeticError('stationary half-line dimension changed')
        u,v=Q[:18,:18],Q[18:,:18]
        M=v@np.linalg.solve(u,np.eye(18))
        L,R=M-B,M-C
        solve=lambda b:solve_sylvester(L,R,b)
        mg=np.array([solve(M@cg[k]+bg[k]@M-(np.eye(18) if k==22 else 0.)) for k in range(23)])
        mh=np.empty((23,23,18,18),complex);second_defect=0.
        for i in range(23):
            for j in range(i+1):
                rhs=(M@ch[i,j]+bh[i,j]@M+mg[i]@cg[j]+mg[j]@cg[i]
                     +bg[i]@mg[j]+bg[j]@mg[i]-mg[i]@mg[j]-mg[j]@mg[i])
                mh[i,j]=solve(rhs);mh[j,i]=mh[i,j]
                second_defect=max(second_defect,float(np.max(abs(L@mh[i,j]+mh[i,j]@R-rhs))))
        rr=M@M-M@C-B@M+lam*np.eye(18)
        left=M.T;left_rr=left@left-left@B.T-C.T@left+lam*np.eye(18)
        first=np.array([L@mg[i]+mg[i]@R-M@cg[i]-bg[i]@M+(np.eye(18) if i==22 else 0.) for i in range(23)])
        result[name]=dict(value=M,gradient23=mg,hessian23=mh,
            decaying_frame36x18=Q[:,:18],
            Riccati_original_row_max=float(np.max(abs(rr))),
            first_original_row_max=float(np.max(abs(first))),
            second_original_row_max=second_defect,
            analytic_transpose_original_row_max=float(np.max(abs(left_rr))),
            value_graph_condition=float(np.linalg.cond(u)),
            analytic_left_value=M.T)
    return dict(maps=result,W=w,Omega=o,B=B,C=C,system=system,
        spectral_parameter=lam,z=z,dichotomy_real_gap=float(np.min(abs(eig.real))))


def consume_comparison_domain(application,theta_gradient,theta_hessian):
    """Insert the new return into original Green/conormal rows and vertices.

    The source delta*I18 enumerates the operator kernel. It is not a packet
    coefficient, chosen spinor or occupation. Ordered past/future response
    derivatives remain separate and need not individually be symmetric.
    Their sum belongs to the existing whole-line native0, not an extra force.
    """
    p=application['maps']['past'];f=application['maps']['future_comparison']
    Mp,Mf=p['value'],f['value'];J=Mp-Mf
    Q=np.linalg.solve(J,np.eye(18));jg=p['gradient23']-f['gradient23']
    qg=-Q@jg@Q
    jh=p['hessian23']-f['hessian23']
    qh=Q@jg[:,None]@Q@jg[None,:]@Q+Q@jg[None,:]@Q@jg[:,None]@Q-Q@jh@Q
    source_first=jg@Q+J@qg
    source_second=jh@Q+jg[:,None]@qg[None,:]+jg[None,:]@qg[:,None]+J@qh
    betap=np.einsum('ab,iba->i',Q,p['gradient23'])
    betaf=-np.einsum('ab,iba->i',Q,f['gradient23'])
    dp=np.einsum('jab,iba->ij',qg,p['gradient23'])+np.einsum('ab,ijba->ij',Q,p['hessian23'])
    df=-np.einsum('jab,iba->ij',qg,f['gradient23'])-np.einsum('ab,ijba->ij',Q,f['hessian23'])
    j=np.zeros((23,152));j[:22,:151]=theta_gradient;j[22,151]=1
    h=np.zeros((23,152,152));h[:22,:151,:151]=theta_hessian
    bgp=j.T@betap;bgf=j.T@betaf
    dhp=j.T@dp@j+np.einsum('a,aij->ij',betap,h)
    dhf=j.T@df@j+np.einsum('a,aij->ij',betaf,h)
    C,B=application['C'],application['B'];lam=application['spectral_parameter']
    # Independent source solve in original36-dimensional first-order graph
    # frames; neither conormal is assigned by multiplying M into Q here.
    fp=p['decaying_frame36x18'];ff=f['decaying_frame36x18']
    matching=np.block([[fp[:18],-ff[:18]],[fp[18:],-ff[18:]]])
    rhs=np.vstack((np.zeros((18,18)),np.eye(18)))
    coefficients=np.linalg.solve(matching,rhs)
    left=fp@coefficients[:18];right=ff@coefficients[18:]
    independent_rows=matching@coefficients-rhs
    left_system=np.block([[-B.T,np.eye(18)],[-lam*np.eye(18),C.T]])
    left_frames=[]
    for sign in (1,-1):
        _,frame,count=schur(left_system,output='complex',sort=lambda x:sign*x.real>0)
        if count!=18:raise ArithmeticError('analytic-left dichotomy dimension changed')
        left_frames.append(frame[:,:18])
    lp,lf=left_frames
    lm=np.block([[lp[:18],-lf[:18]],[lp[18:],-lf[18:]]])
    left_coefficients=np.linalg.solve(lm,rhs)
    left_source_defect=float(np.max(abs(lm@left_coefficients-rhs)))
    left_kernel_defect=0.
    traces=[];residual=0.
    for index,(t,M) in enumerate([(-.25,Mp),(.25,Mf)]):
        u=expm((M-C)*t)@Q;v=M@u
        du=(M-C)@u;dv=M@du
        residual=max(residual,float(np.max(abs(du+C@u-v))),
            float(np.max(abs(-dv+B@v-lam*u))))
        traces.append(np.stack((u,v)))
        ll=expm(left_system*t)@left_frames[index]@left_coefficients[index*18:(index+1)*18]
        opposite=Mf if t<0 else Mp
        reflected=(expm((opposite-C)*(-t))@Q).T
        left_kernel_defect=max(left_kernel_defect,float(np.max(abs(ll[:18]-reflected))))
    # A new resolvent/domain identity, not a repeat of E1 heat precision.
    nodes,weights=np.polynomial.legendre.leggauss(96)
    frequency=np.zeros((18,18),complex)
    for n,weight in zip(nodes,weights):
        om=np.tan(np.pi*n/2)
        P=(-1j*om*np.eye(18)+B)@(1j*om*np.eye(18)+C)
        frequency+=weight/(4*np.cos(np.pi*n/2)**2)*np.linalg.solve(P-lam*np.eye(18),np.eye(18))
    return dict(boundary_Green18=Q,past_cut_covector152=bgp,future_comparison_cut_covector152=bgf,
        boundary_Green_gradient23=qg,boundary_Green_Hessian23=qh,
        original36_source_matching_matrix=matching,original36_source_matching_rhs=rhs,
        original36_source_coefficients=coefficients,original36_source_rows=independent_rows,
        independently_solved_past_trace_and_conormal=left,
        independently_solved_future_trace_and_conormal=right,
        independently_solved_analytic_left_source_coefficients=left_coefficients,
        analytic_left_source_original_rows_max=left_source_defect,
        independently_solved_left_reflection_kernel_defect=left_kernel_defect,
        past_ordered_derivative152=dhp,future_comparison_ordered_derivative152=dhf,
        full_gluing_covector152=bgp+bgf,full_gluing_Hessian152=dhp+dhf,
        Poisson_values_and_conormals=np.array(traces),
        original_first_order_rows_max=residual,
        conormal_jump_rows=Mp@Q-Mf@Q-np.eye(18),
        past_core_seam_rows=-left[18:]+Mp@left[:18],
        independent_source_Green_value_defect=float(np.max(abs(left[:18]-Q))),
        differentiated_source_jump_first_max=float(np.max(abs(source_first))),
        differentiated_source_jump_second_max=float(np.max(abs(source_second))),
        frequency_Green_identity_defect=float(np.max(abs(frequency-Q))),
        full_gluing_Hessian_symmetry_defect=float(np.max(abs((dhp+dhf)-(dhp+dhf).T))))
