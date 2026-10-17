"""Supported child-wall fundamental clock/U2 transport, not a selected reset.

The source is the original real one-cell child history on [0,h]. Initial
physical F0/DF0/U0 remain coupled unknowns. The fundamental angular flow is
derived from gamma_ti=0; no field-independent E/B variation is inferred.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
import mpmath as mp
from scipy.linalg import expm

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm_real_full_d5_combined_eta_open_form_20261016 import (
    PHASES,radial_representation,sample_coefficients)
from bhsm.interface.muon_profile_preserving_phase_sample import (
    load_profile_preserving_phase,profile_preserving_raw_sample)
from bhsm.interface.muon_holomorphic_normal_geometry import (
    _geometry_variables,_fields,_sqrt,holomorphic_geometry_rows)
from bhsm.interface.muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_intrinsic_worldvolume_scalar_transport import induced_worldvolume_flow
from bhsm.interface.muon_full_d5_localized_lepton_trace import (
    full_d5_localized_lepton_trace,moving_d5_material_trace_frame)
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

def real(a,name):
    a=np.asarray(a)
    if not np.isfinite(a).all()or(np.iscomplexobj(a)and np.any(a.imag!=0)):
        raise ValueError('Actual real chart required: '+name)
    return np.asarray(a.real,float)

def err(a,b):
    absolute=float(np.max(abs(a-b)));den=max(float(np.max(abs(a))),float(np.max(abs(b))))
    return dict(absolute=absolute,relative_to_nonzero=(absolute/den if den else None))

def ell_germ(raw,rate):
    q,v,m,delta,dr,wall,_=_geometry_variables(raw[:100])
    f=_fields(12,q,v,m,wall)
    U=f['C']*(dr+f['beta'])/f['N']
    ell=f['N']*_sqrt(1-U*U)
    R=f['A']*f['B']/_sqrt(f['A']**2+f['B']**2)
    if abs(U.value)>=1:raise ValueError('Actual timelike wall required')
    return {k:real(np.array([a.value,a.gradient@rate[:100]]),k)
        for k,a in dict(ell=ell,wall_velocity=U,radius=R).items()}

def profile_lambda(raw):
    a=holomorphic_geometry_rows(raw[:100],np.array([WALL]),differentiate=False,connection_only=True)
    return real(a['rows'][0]['connection_lambda'].value,'mechanical lambda').item()

def source(phase,time):
    s=profile_preserving_raw_sample(phase,time);raw,rate=s['raw_fields'],s['raw_coordinate_time_derivative']
    g=ell_germ(raw,rate)
    W=phase['representation']['wall_trace_map']
    A=np.einsum('fcj,j->fc',W,raw[100:180]);Ax=np.einsum('fcj,j->fc',W,rate[100:180])
    if phase['receipt']['side']=='outgoing':
        pair,ref=phase['arrays']['initial_pair'],phase['arrays']['reference_pair']
        parent=affine_geometry_germ(pair[0],time)
        refs=np.array([affine_geometry_germ(a,time)for a in ref])
        lam=profile_lambda(parent)-profile_lambda(refs[0])+profile_lambda(refs[1])
    else:lam=profile_lambda(raw)
    A[2:]+=M*(lam-1)
    generators=higgs_u2_real_representation()['complex_generators']
    a=np.einsum('fc,cij->fij',A,generators)
    ax=np.einsum('c,cij->ij',Ax[0],generators)
    if np.max(abs(a+a.conj().swapaxes(-1,-2)))>1e-13:raise ValueError('Owned U2 anti-Hermitian gauge basis required')
    h=np.diag([g['ell'][0]**2,*([-g['radius'][0]**2]*3)])[None]
    flow=induced_worldvolume_flow(h,np.zeros((1,3,4,4)))
    return dict(g,raw=raw,rawtime=rate,connection=A,connection_U2=a,At_first_U2=ax,
        b=flow['b'][0],divergence=flow['haar_divergence'][0],flow_clock=flow['lapse'][0])

def series_increment(a):
    """exp(a)-I without subtracting a nearly unit matrix."""
    term=a.copy();value=a.copy()
    for k in range(2,12):term=term@a/k;value+=term
    return value

def mp_increment_control(At,h,binary_increment):
    references=[]
    for precision in(80,100):
        with mp.workdps(precision):
            a=mp.matrix([[mp.mpc(float(z.real),float(z.imag))for z in row]for row in At])
            references.append(mp.expm(-mp.mpf(h)*a)-mp.eye(2))
    components=[]
    with mp.workdps(100):
        for i in range(2):
            for j in range(2):
                for label,part in(('real',mp.re),('imag',mp.im)):
                    reference=part(references[-1][i,j]);value=mp.mpf(float(getattr(binary_increment[i,j],label)))
                    absolute=abs(value-reference)
                    components.append(dict(row=i,column=j,component=label,
                        reference=mp.nstr(reference,60),absolute_error=float(absolute),
                        relative_to_nonzero=(float(absolute/abs(reference))if reference else None)))
        absolute=max(abs(references[0][i,j]-references[1][i,j])for i in range(2)for j in range(2))
        return dict(precision_digits=[80,100],component_controls=components,
            max_nonzero_component_relative=max(c['relative_to_nonzero']for c in components if c['relative_to_nonzero']is not None),
            MP80_MP100_absolute=float(absolute),binary_to_MP='exact binary64 float components, not decimal transcription')

def execute(output):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent applications')
    child=load_profile_preserving_phase(PHASES['outgoing'],repository=ROOT)
    parent=load_profile_preserving_phase(PHASES['incoming'],repository=ROOT)
    if child['receipt']['steps']!=1 or parent['receipt']['steps']!=1:raise ValueError('Original complete one-cell sources required')
    h=float(child['receipt']['span'])
    if h<=0 or float(parent['receipt']['span'])>=0:raise ValueError('Actual opposite one-sided supports required')
    cache={}
    def get(t):
        t=float(t)
        if t<0 or t>h:raise ValueError('No evaluation beyond supported child interval')
        if t not in cache:cache[t]=source(child,t)
        return cache[t]
    arrays={};records=[];gauss=[]
    # These are maps from an arbitrary initial label, not chosen physical points.
    arrays['derived_angular_fundamental_differential']=np.eye(3)
    arrays['derived_angular_fundamental_Haar_jacobian']=np.array(1.)
    for n in(8,16,32):
        x,w=np.polynomial.legendre.leggauss(n);times=(x+1)*h/2
        samples=[get(t)for t in times]
        clock=h/2*np.dot(w,[a['ell'][0]for a in samples])
        clockx=h/2*np.dot(w,[a['ell'][1]for a in samples])
        gauss.append((clock,clockx))
        arrays[f'gauss{n}_times']=times;arrays[f'gauss{n}_weights']=w*h/2
        arrays[f'gauss{n}_clock_value_first']=np.array([clock,clockx])
    initial=get(0.);final=get(h);A0=initial['connection_U2'][0]
    exact_inc=series_increment(-h*A0)
    central=np.trace(A0)/2;traceless=A0-central*np.eye(2)
    central_inc=np.expm1(-h*central)
    su2_inc=series_increment(-h*traceless)
    split_inc=central_inc*np.eye(2)+(1+central_inc)*su2_inc
    arrays.update(U2_At_initial=A0,U2_At_initial_source_first=initial['At_first_U2'],
        exact_constant_At_Wilson_increment=exact_inc,
        exact_central_U1_increment=np.array(central_inc),exact_traceless_SU2_increment=su2_inc,
        central_traceless_split_Wilson_increment=split_inc,
        local_Wilson_first=-A0,local_Wilson_second=A0@A0-initial['At_first_U2'],
        local_clock_value_first_second=np.array([0.,initial['ell'][0],initial['ell'][1]]))
    # An independent explicit RK4 evolves the INCREMENT, retaining tiny phases.
    for n in(8,16,32):
        dt=h/n;Y=np.zeros((2,2),complex);Yx=Y.copy();tau=0.;taux=0.
        def rhs(t,Y,Yx):
            a=get(t);At=a['connection_U2'][0];Atx=a['At_first_U2']
            return (-At-At@Y,-Atx-Atx@Y-At@Yx,a['ell'][0],a['ell'][1])
        for k in range(n):
            t=k*dt
            r1=rhs(t,Y,Yx)
            r2=rhs(t+dt/2,Y+dt*r1[0]/2,Yx+dt*r1[1]/2)
            r3=rhs(t+dt/2,Y+dt*r2[0]/2,Yx+dt*r2[1]/2)
            r4=rhs((k+1)*dt,Y+dt*r3[0],Yx+dt*r3[1])
            Y+=dt*(r1[0]+2*r2[0]+2*r3[0]+r4[0])/6
            Yx+=dt*(r1[1]+2*r2[1]+2*r3[1]+r4[1])/6
            tau+=dt*(r1[2]+2*r2[2]+2*r3[2]+r4[2])/6
            taux+=dt*(r1[3]+2*r2[3]+2*r3[3]+r4[3])/6
        arrays[f'RK4_{n}_Wilson_increment']=Y;arrays[f'RK4_{n}_Wilson_increment_source_first']=Yx
        arrays[f'RK4_{n}_clock_value_first']=np.array([tau,taux])
        records.append(dict(steps=n,clock_value=float(tau),clock_fixed_endpoint_source_first=float(taux),
            clock_vs_Gauss32=err(np.array([tau,taux]),np.array(gauss[-1])),
            clock_value_vs_Gauss32=err(np.array(tau),np.array(gauss[-1][0])),
            clock_first_vs_Gauss32=err(np.array(taux),np.array(gauss[-1][1])),
            Wilson_increment_vs_constant_exact=err(Y,exact_inc),
            Wilson_first_variation_norm=float(np.linalg.norm(Yx)),
            Wilson_unitarity_increment_rows=float(np.max(abs(Y+Y.conj().T+Y.conj().T@Y)))))
    # Rebind selected samples through the full inherited source constructor.
    f=full_d5_localized_lepton_trace();rep=radial_representation(child['representation'],np.array([WALL]))
    source_controls=[]
    for j,t in enumerate((0.,h/2,h)):
        a=get(t);c,s=sample_coefficients(child,t,rep)
        known=real(c['gauge_connection_material'][0],'full inherited connection')
        fullfirst=real(c['gauge_connection_material_first'][0,0,0],'full At first')
        source_controls.append(dict(time=t,connection_value=err(a['connection'],known),
            At_source_first=err(a['At_first_U2'],np.einsum('c,cij->ij',fullfirst,higgs_u2_real_representation()['complex_generators'])),
            proper_clock=err(a['ell'],real(np.array([c['surface_proper_clock_rate'][0],c['surface_proper_clock_rate_first'][0,0]]),'full clock germ'))))
        arrays[f'selected{j}_time']=np.array(t)
        for name in('raw','rawtime','ell','wall_velocity','radius','connection','connection_U2','At_first_U2','b'):
            arrays[f'selected{j}_'+name]=a[name]
        # This kernel is NONZERO even though the present background b=0.
        arrays[f'selected{j}_delta_h_ti_to_effective_connection_kernel']=a['connection_U2'][2:]/a['radius'][0]**2
        for eps in(-1,1):
            boost=moving_d5_material_trace_frame(-eps*a['wall_velocity'][0],-eps*a['wall_velocity'][1],full_representation=f)
            for name in('spin_boost128','spin_boost_first128','spin_boost_inverse128'):
                arrays[f'selected{j}_eta{eps}_'+name]=boost[name]
    p=source(parent,0.);lp,lc=p['ell'],initial['ell'];slope=lp[0]/lc[0]
    clock_second=lp[1]/lc[0]-lp[0]**2*lc[1]/lc[0]**3
    arrays['conditional_two_side_clock_slope_second']=np.array([slope,clock_second])
    arrays['conditional_two_side_clock_radius_first_residual']=np.array(p['radius'][1]-initial['radius'][1]*slope)
    arrays['parent_birth_ell_value_first']=lp
    arrays['child_birth_ell_value_first']=lc
    sampled=list(cache.values())
    Atvariation=max(float(np.max(abs(a['connection_U2'][0]-A0)))for a in sampled)
    Atxnorm=max(float(np.max(abs(a['At_first_U2'])))for a in sampled)
    if Atvariation!=0 or Atxnorm!=0:raise ValueError('This exact-exponential control is owned only by the verified constant-At source cell')
    pins=dict(parent['input_hashes']);pins.update(child['input_hashes'])
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(ROOT)and Path(path).suffix=='.py':
            path=Path(path);pins[path.relative_to(ROOT).as_posix()]=sha256(path.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(classification='SUPPORTED_REAL_CHILD_WALL_FUNDAMENTAL_WORLDVOLUME_CLOCK_U2_TRANSPORT',
        supported_child_coordinate_interval=[0.,h],records=records,
        Gauss_orders=[8,16,32],Gauss_clock_value_first=[list(map(float,a))for a in gauss],
        Gauss8_to16=err(np.array(gauss[0]),np.array(gauss[1])),Gauss16_to32=err(np.array(gauss[1]),np.array(gauss[2])),
        independent_clock_source_FTC=err(np.array(gauss[-1][1]),np.array(final['ell'][0]-initial['ell'][0])),
        constant_At_verified_on_all_samples=Atvariation,constant_At_source_first_verified=Atxnorm,
        actual_U2_At_nonzero_norm=float(np.linalg.norm(A0)),
        actual_central_U1_At_nonzero_norm=float(abs(central)),actual_traceless_SU2_At_norm=float(np.linalg.norm(traceless)),
        Wilson_increment_nonzero_norm=float(np.linalg.norm(exact_inc)),
        Wilson_central_traceless_increment_control=err(exact_inc,split_inc),
        independent_MP_exponential_increment=mp_increment_control(A0,h,exact_inc),
        scipy_exponential_value_control=err(np.eye(2)+exact_inc,expm(-h*A0)),
        local_conditional_two_side_clock_slope=float(slope),local_conditional_two_side_clock_second=float(clock_second),
        local_conditional_metric_radius_first_residual=float(arrays['conditional_two_side_clock_radius_first_residual']),
        supported_orientation_preserving_two_side_clock_interval_has_positive_length=False,
        two_side_scope='Point-germ comparison only: incoming t<=0,child T>=0 share0; no unowned time reversal or two-side metric isometry imposed',
        full_source_constructor_controls=source_controls,
        actual_background_angular_flow_and_Haar_divergence_maximum=max(float(np.max(abs(a['b'])))+abs(float(a['divergence']))for a in sampled),
        angular_fundamental_flow='Q(t)=Q0, D_Q0 Q=I, HaarJac=1 from actual gamma_ti=0; physical initial correspondence not chosen',
        physical_initial_F0=None,physical_initial_DF0=None,physical_initial_U0=None,
        physical_F_B_or_full_spin_bundle_lift_evaluated=False,
        full_spin_parallel_transport_evaluated=False,
        nonzero_wall_spin_boost_and_source_frames_retained=True,
        spin_boost_scope='Actual kinematic eta-sheet coframe boosts, not a substitute for full Spin parallel transport',
        linearized_axis='Supplied inside-cell rawtime coefficient germ, fixed integration endpoints; physical endpoint/initial-map contacts remain explicit unknowns',
        physical_E_B_or_outgoing_domain_derivative_evaluated=False,
        nonhomogeneous_variation_law='delta Qdot=delta b; delta effective A=delta At+delta b^i Ai; delta HaarJacdot=div(delta b); spatial kernels saved, not set0',
        initial_data_and_endpoint_contacts='F(t)=flow_t0(F0), U(t)=G(t,0)U0; delta U=delta G*U0+G*delta U0; delta tau_total=delta tau_coeff+ell(h)delta h-ell(0)delta0; moving-start/end Wilson contacts retained symbolically',
        physical_H_parallel_or_later_child_state_selected=False,physical_incoming_or_outgoing_loads=None,
        child_cell_reused_without_history_or_profile_reintegration=True,external_unit_normal_chart_used=False,
        spin_deletion_or_coupled_corrections=0,physical_radial_or_time_convergence=False,
        complete_physical_derivative_at_2e_minus10=False,normalized_physical_spins=None,physical_muon_magnetic_moment=None,
        input_and_source_sha256=dict(sorted(pins.items())))
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    result['numerical_sha256']=sha256((out/'application.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=result['classification'],numerical_sha256=result['numerical_sha256']),sort_keys=True))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();execute(a.output)
