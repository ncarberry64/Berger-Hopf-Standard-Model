"""Actual uncontracted M5 geometric Spin transport on the supplied child wall.

All coefficients follow the retained real child cell. The ambient/adapted
Spin connections, intrinsic-wall LC, U2 factor and f_eta body are distinct.
No initial physical Spin/reset lift, native carrier or E/B source is chosen.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm_real_full_d5_combined_eta_open_form_20261016 import PHASES,radial_representation,sample_coefficients
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase,profile_preserving_raw_sample
from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt
from bhsm.interface.muon_m5_geometric_spin_connection import (
    PRIMITIVES,m5_geometric_spin_connection,independent_coordinate_tetrad_connection)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace,moving_d5_material_trace_frame
from bhsm.interface.muon_combined_f_eta_contact import combined_f_eta_contact
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

def real(a,name):
    a=np.asarray(a)
    if not np.isfinite(a).all()or(np.iscomplexobj(a)and np.any(a.imag!=0)):
        raise ValueError('Actual real source chart required: '+name)
    return np.asarray(a.real,float)

def error(a,b):
    absolute=float(np.max(abs(a-b)));den=max(float(np.max(abs(a))),float(np.max(abs(b))))
    return dict(absolute=absolute,relative_to_nonzero=absolute/den if den else None)

def actual_germ(phase,t):
    sample=profile_preserving_raw_sample(phase,t);raw,rate=sample['raw_fields'],sample['raw_coordinate_time_derivative']
    coherence=max(np.max(abs(rate[:37]-raw[37:74])),abs(rate[98]-raw[99]))
    if coherence>1e-12:raise ValueError('Actual saved position/velocity and source-rate coherence required')
    q,v,m,delta,dr,wall,_=_geometry_variables(raw[:100]);jac=wall/WALL
    f=_fields(12,q,v,m,wall)
    N=f['N'];C=f['C']*jac;z=(f['beta']+dr)/jac
    R=f['A']*f['B']/_sqrt(f['A']**2+f['B']**2)
    Nr=N*f['np']*jac;Cr=C*f['cp']*jac;zr=f['betap']+dr/wall
    Rchi=f['ap']+f['bp']-(f['A']**2*f['ap']+f['B']**2*f['bp'])/(f['A']**2+f['B']**2)
    Rr=R*Rchi*jac
    J=(N,C,z,R,Nr,None,Cr,zr,None,Rr);p=np.zeros((2,10))
    for j,a in enumerate(J):
        if a is not None:p[:,j]=real([a.value,a.gradient@rate[:100]],PRIMITIVES[j])
    for j,a in((5,C),(8,R)):
        p[:,j]=real([a.gradient@rate[:100],rate[:100]@a.hessian@rate[:100]],PRIMITIVES[j])
    U=C*z/N
    if abs(U.value)>=1:raise ValueError('Actual timelike material wall required')
    Ut=U.gradient@rate[:100];Utt=rate[:100]@U.hessian@rate[:100]
    eta=np.arctanh(U.value);et=Ut/(1-U.value**2)
    ett=Utt/(1-U.value**2)+2*U.value*Ut**2/(1-U.value**2)**2
    # Independent source-form coefficients before Dirac contraction.
    a=f['np']/f['C'];k=(f['lc']-f['beta']*f['cp']-f['betap'])/N
    lR=f['la']+f['lb']-(f['A']**2*f['la']+f['B']**2*f['lb'])/(f['A']**2+f['B']**2)
    H0=(lR-f['beta']*Rchi)/N;H4=Rchi/f['C']
    original=np.array([[w.value,w.gradient@rate[:100]]for w in(a,k,H0,H4,1/R)]).T
    return dict(raw=raw,rawtime=rate,primitives=p,
        N_time=float(real(N.gradient@rate[:100],'Nt')),z_time=float(real(z.gradient@rate[:100],'zt')),
        rapidity_value_first_second=real([eta,et,ett],'actual wall rapidity'),
        wall_velocity_value_first=real([U.value,Ut],'wall velocity'),
        original_scalar_contacts=real(original,'original scalar contacts'),coherence=float(coherence))

def torsion_rows(connection):
    w=connection['lower_connection_frame_value_first'][0];a,k,H0,H4,invR=connection['scalar_contacts'][0]
    eps=connection['orientation'];de=np.zeros((5,5,5));levi=np.zeros((3,3,3))
    for i in range(3):levi[i,(i+1)%3,(i+2)%3]=1;levi[i,(i+2)%3,(i+1)%3]=-1
    de[0,0,1]=-eps*a;de[0,1,0]=eps*a;de[1,0,1]=k;de[1,1,0]=-k
    for i in range(3):
        de[i+2,0,i+2]=H0;de[i+2,i+2,0]=-H0
        de[i+2,1,i+2]=eps*H4;de[i+2,i+2,1]=-eps*H4
        de[i+2,2:,2:]=2*invR*levi[i]
    upper=w*np.array([1.,-1.,-1.,-1.,-1.])[:,None,None]
    return de+upper.swapaxes(1,2)-upper

def boost_increment(alpha,alpha_source):
    return np.array([2*np.sinh(alpha/2)**2,-np.sinh(alpha)]),np.array([
        np.sinh(alpha)*alpha_source,-np.cosh(alpha)*alpha_source])

def literal_MP_affine_coframe_control(phase,rate,h,binary_reference):
    """Independent literal coframe/metric partials on exact binary input history.

    No Jet, contracted Dirac contact, Cartan helper or rounded endpoint
    coframe is used here. The same source float constants are converted
    exactly, without substituting a different pi/radius normalization.
    """
    references=[]
    for precision in(80,100):
        with mp.workdps(precision):
            mid=[mp.mpf(float(x))for x in phase['arrays'][phase['stage_key']][0,:100]]
            velocity=[mp.mpf(float(x))for x in rate[:100]]
            hh=mp.mpf(h);tm=mp.mpf(h/2);rho0=mp.mpf(WALL)
            r0=mp.mpf(RADIUS0);pi4=mp.mpf(float(np.pi/4))
            def coframe(t,rho):
                x=[a+(t-tm)*b for a,b in zip(mid,velocity)]
                q,v,m=x[:37],x[37:74],x[74:98]
                cs=r0*mp.exp(q[0]+sum((-1)**k*q[k]for k in range(1,13))
                    +sum((-1)**j*q[13+j]for j in range(12)))
                lc=v[0]+sum((-1)**k*v[k]for k in range(1,13))+sum((-1)**j*v[13+j]for j in range(12))
                wall=pi4+x[98]/cs;dr=(x[99]-lc*x[98])/cs;chi=rho*wall/rho0
                u=sum(q[k]*mp.cos(4*k*chi)for k in range(1,13))
                w=mp.sin(2*chi)**2*sum(q[13+j]*mp.cos(4*j*chi)for j in range(12))
                N=mp.exp(sum(m[k-1]*mp.cos(4*k*chi)for k in range(1,13)))
                C=r0*mp.exp(q[0]+u+w)*wall/rho0
                beta=mp.sin(4*chi)*sum(m[12+j]*mp.cos(4*j*chi)for j in range(12))
                z=(beta+(rho/rho0)*dr)/(wall/rho0)
                return N,C,z
            def omega(t):
                N,C,z=coframe(t,rho0)
                Nr=mp.diff(lambda r:coframe(t,r)[0],rho0)
                Ct=mp.diff(lambda s:coframe(s,rho0)[1],t)
                Cr=mp.diff(lambda r:coframe(t,r)[1],rho0)
                zr=mp.diff(lambda r:coframe(t,r)[2],rho0)
                return Nr/C+C*z*(Ct-z*Cr-C*zr)/(N*C)
            def eta(t):
                N,C,z=coframe(t,rho0)
                return mp.atanh(C*z/N)
            nodes,weights=mp.gauss_quadrature(16,'legendre')
            integral=hh/2*sum(w*omega((x+1)*hh/2)for x,w in zip(nodes,weights))
            first=omega(hh)-omega(mp.mpf(0))
            deta=eta(hh)-eta(mp.mpf(0))
            detafirst=mp.diff(eta,hh)-mp.diff(eta,mp.mpf(0))
            references.append(dict(ambient=(+integral,+first),adapted=(+(integral+deta),+(first+detafirst))))
    controls=[]
    with mp.workdps(100):
        for name in('ambient','adapted'):
            for source in(0,1):
                ref=references[-1][name][source];binary=mp.mpf(float(binary_reference[name][source]))
                controls.append(dict(frame=name,source_order=source,reference=mp.nstr(ref,70),
                    binary_absolute_error=float(abs(binary-ref)),
                    binary_relative_to_nonzero=float(abs((binary-ref)/ref))if ref else None,
                    MP80_MP100_absolute=float(abs(references[0][name][source]-ref))))
    return dict(precision_digits=[80,100],Gauss_order=16,controls=controls,
        input_scope='Exact binary64 raw midpoint/rate/h and original float constants; literal affine100 history and original N/C/z Fourier coframe, no exterior evaluation')

def execute(output):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent actual applications')
    phase=load_profile_preserving_phase(PHASES['outgoing'],repository=ROOT)
    if phase['receipt']['steps']!=1:raise ValueError('Original complete child cell required')
    h=float(phase['receipt']['span'])
    if h<=0:raise ValueError('Supported future child interval required')
    full=full_d5_localized_lepton_trace();gamma4=full['gamma5D_particle'][[0,4,1,2,3]]
    gamma128=full['gamma5D_self_dual128'][[0,4,1,2,3]];K128=gamma128[0]@gamma128[1]
    G0128=gamma128[0];K384=np.kron(np.eye(3),K128);G0384=np.kron(np.eye(3),G0128)
    cache={};checks=[];arrays=dict(existing_Gamma5D_selfdual128=gamma128,boost_generator128=K128,boost_generator384=K384)
    def get(t):
        t=float(t)
        if t<0 or t>h:raise ValueError('No external history or normal chart permitted')
        if t not in cache:
            s=actual_germ(phase,t);p=s['primitives']
            a=m5_geometric_spin_connection(p,gamma=gamma4,orientation=1)
            coordinate=independent_coordinate_tetrad_connection(p[0],N_time=s['N_time'],z_time=s['z_time'],orientation=1)
            checks.append(dict(time=t,metric_Christoffel_vs_Cartan=error(coordinate['lower_connection_coordinate'],a['lower_connection_coordinate_value_first'][0]),
                scalar_owner_vs_material_derivatives=error(s['original_scalar_contacts'],a['scalar_contacts']),
                tetrad_postulate_max=float(np.max(abs(coordinate['tetrad_postulate_rows']))),
                torsion_max=float(np.max(abs(torsion_rows(a))))))
            omega=a['wall_boost_connection_scalar_value_first']
            s.update(omega=omega,adapted_omega=omega+s['rapidity_value_first_second'][1:],connection=a)
            cache[t]=s
        return cache[t]
    quadrature=[]
    for n in(8,16,32):
        x,w=np.polynomial.legendre.leggauss(n);ts=(x+1)*h/2
        ambient=h/2*np.einsum('q,qs->s',w,np.array([get(t)['omega']for t in ts]))
        adapted=h/2*np.einsum('q,qs->s',w,np.array([get(t)['adapted_omega']for t in ts]))
        quadrature.append(dict(order=n,ambient_integral_value_first=ambient.tolist(),adapted_integral_value_first=adapted.tolist()))
        arrays[f'Gauss{n}_times']=ts;arrays[f'Gauss{n}_weights']=w*h/2
        arrays[f'Gauss{n}_ambient_integral_value_first']=ambient;arrays[f'Gauss{n}_adapted_integral_value_first']=adapted
    initial,final=get(0.),get(h);reference={name:np.array(quadrature[-1][name+'_integral_value_first'])for name in('ambient','adapted')}
    refinement=[]
    for name,key in(('ambient','omega'),('adapted','adapted_omega')):
        for n in(8,16,32):
            dt=h/n;y=np.zeros(2);yx=y.copy()
            def rhs(t,y,yx):
                a,ax=get(t)[key]/2
                return np.array([-a*y[1],-a*(1+y[0])]),np.array([-ax*y[1]-a*yx[1],-ax*(1+y[0])-a*yx[0]])
            for k in range(n):
                t=k*dt;r1=rhs(t,y,yx);r2=rhs(t+dt/2,y+dt*r1[0]/2,yx+dt*r1[1]/2)
                r3=rhs(t+dt/2,y+dt*r2[0]/2,yx+dt*r2[1]/2);r4=rhs((k+1)*dt,y+dt*r3[0],yx+dt*r3[1])
                y+=dt*(r1[0]+2*r2[0]+2*r3[0]+r4[0])/6;yx+=dt*(r1[1]+2*r2[1]+2*r3[1]+r4[1])/6
            exact,exactx=boost_increment(*(reference[name]/2))
            arrays[f'{name}_RK4_{n}_boost_increment_coefficients']=y;arrays[f'{name}_RK4_{n}_boost_increment_source_first']=yx
            refinement.append(dict(frame=name,steps=n,increment_value=error(y,exact),source_first=error(yx,exactx)))
    rep=radial_representation(phase['representation'],np.array([WALL]));endpoint_controls=[]
    for j,t in enumerate((0.,h/2,h)):
        s=get(t);c,sample=sample_coefficients(phase,t,rep)
        arrays[f'selected{j}_time']=np.array(t)
        for key in('raw','rawtime','primitives','rapidity_value_first_second','wall_velocity_value_first','omega','adapted_omega'):
            arrays[f'selected{j}_'+key]=s[key]
        for eps in(-1,1):
            a=m5_geometric_spin_connection(s['primitives'],gamma=gamma128,orientation=eps)
            for key in('lower_connection_frame_value_first','lower_connection_coordinate_value_first',
                'Spin_connection_frame_value_first','Spin_connection_coordinate_value_first','wall_boost_connection_primitive_covector'):
                arrays[f'selected{j}_eta{eps}_'+key]=a[key]
            B=moving_d5_material_trace_frame(-eps*s['wall_velocity_value_first'][0],-eps*s['wall_velocity_value_first'][1],full_representation=full)
            Omega=a['Spin_connection_coordinate_value_first'][0,0]
            adapted=B['spin_boost_inverse128']@Omega@B['spin_boost128']+B['spin_boost_inverse128']@B['spin_boost_first128']
            Bt=B['spin_boost_first128'];Bit=B['spin_boost_inverse_first128']
            eta_t,eta_tt=s['rapidity_value_first_second'][1:]
            Btt=eps*eta_tt*K128@B['spin_boost128']/2+eta_t**2*B['spin_boost128']/4
            adapted_first=(Bit@Omega@B['spin_boost128']
                +B['spin_boost_inverse128']@a['Spin_connection_coordinate_value_first'][1,0]@B['spin_boost128']
                +B['spin_boost_inverse128']@Omega@Bt+Bit@Bt+B['spin_boost_inverse128']@Btt)
            endpoint_controls.append(dict(time=t,orientation=eps,adapted_connection=error(adapted,eps*s['adapted_omega'][0]*K128/2),
                adapted_connection_source_first=error(adapted_first,eps*s['adapted_omega'][1]*K128/2),
                owned_h0=error((a['scalar_contacts'][0,1]+3*a['scalar_contacts'][0,2])/2,c['geometric_time_contact'][0]),
                owned_h4=error((a['scalar_contacts'][0,0]+3*a['scalar_contacts'][0,3])/2,c['geometric_radial_contact'][0])))
            arrays[f'selected{j}_eta{eps}_adapted_Spin_connection']=adapted
            arrays[f'selected{j}_eta{eps}_adapted_Spin_connection_source_first']=adapted_first
            eta=[]
            for branch in('particle','conjugate'):
                e=combined_f_eta_contact(c,gamma=full['gamma5D_'+branch],carrier_count=16,angular_count=1,sheet_orientation=eps)
                eta.append(e['combined_f_eta_contact'][0])
            arrays[f'selected{j}_eta{eps}_separate_original_f_eta_contact128']=np.block([[eta[0],np.zeros_like(eta[0])],[np.zeros_like(eta[1]),eta[1]]])
    lift_controls=[]
    for name in('ambient','adapted'):
        alpha,alphax=reference[name]/2
        for eps in(-1,1):
            coeff,first=boost_increment(eps*alpha,eps*alphax)
            U=np.eye(128)+coeff[0]*np.eye(128)+coeff[1]*K128
            Ux=first[0]*np.eye(128)+first[1]*K128
            arrays[f'{name}_eta{eps}_parallel_increment128']=coeff[0]*np.eye(128)+coeff[1]*K128
            arrays[f'{name}_eta{eps}_parallel_source_first128']=Ux
            arrays[f'{name}_eta{eps}_parallel384']=np.kron(np.eye(3),U)
            arrays[f'{name}_eta{eps}_parallel_source_first384']=np.kron(np.eye(3),Ux)
            lift_controls.append(dict(frame=name,orientation=eps,pseudoisometry128=float(np.max(abs(U.conj().T@G0128@U-G0128))),
                source_pseudoisometry128=float(np.max(abs(Ux.conj().T@G0128@U+U.conj().T@G0128@Ux))),
                full384_pseudoisometry=float(np.max(abs(arrays[f'{name}_eta{eps}_parallel384'].conj().T@G0384@arrays[f'{name}_eta{eps}_parallel384']-G0384)))))
    # Ordered moving-frame endpoint conversion, not an ambient=intrinsic claim.
    frame_controls=[]
    for eps in(-1,1):
        B0=moving_d5_material_trace_frame(-eps*initial['wall_velocity_value_first'][0],-eps*initial['wall_velocity_value_first'][1],full_representation=full)
        B1=moving_d5_material_trace_frame(-eps*final['wall_velocity_value_first'][0],-eps*final['wall_velocity_value_first'][1],full_representation=full)
        U=arrays[f'ambient_eta{eps}_parallel384'][:128,:128]
        Ux=arrays[f'ambient_eta{eps}_parallel_source_first128']
        expected=arrays[f'adapted_eta{eps}_parallel384'][:128,:128]
        expectedx=arrays[f'adapted_eta{eps}_parallel_source_first128']
        actualx=(B1['spin_boost_inverse_first128']@U@B0['spin_boost128']
            +B1['spin_boost_inverse128']@Ux@B0['spin_boost128']
            +B1['spin_boost_inverse128']@U@B0['spin_boost_first128'])
        frame_controls.append(dict(orientation=eps,
            ordered_frame_conversion=error(B1['spin_boost_inverse128']@U@B0['spin_boost128'],expected),
            ordered_frame_conversion_source_first=error(actualx,expectedx)))
    with mp.workdps(80):
        mp_controls=[]
        for name in('ambient','adapted'):
            alpha,alphax=reference[name]/2;co,dx=boost_increment(alpha,alphax)
            aa,ax=mp.mpf(alpha),mp.mpf(alphax)
            controls=[mp.cosh(aa)-1,-mp.sinh(aa),mp.sinh(aa)*ax,-mp.cosh(aa)*ax]
            for k,(value,ref)in enumerate(zip(np.r_[co,dx],controls)):
                mp_controls.append(dict(frame=name,component=k,absolute=float(abs(mp.mpf(value)-ref)),relative_to_nonzero=float(abs((mp.mpf(value)-ref)/ref))if ref else None))
    pins=dict(phase['input_hashes'])
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT)and Path(p).suffix=='.py':
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(classification='ACTUAL_REAL_CHILD_WALL_UNCONTRACTED_M5_GEOMETRIC_SPIN_PARALLEL_TRANSPORT',
        supported_child_interval=[0.,h],primitive_order=PRIMITIVES,quadrature=quadrature,RK4_refinements=refinement,
        metric_Cartan_tetrad_checks=checks,full_existing_carrier_endpoint_controls=endpoint_controls,
        Spin_lift_controls=lift_controls,ordered_ambient_adapted_frame_controls=frame_controls,
        independent_MP80_boost_component_controls=mp_controls,
        independent_literal_MP_coframe_precision=literal_MP_affine_coframe_control(phase,initial['rawtime'],h,reference),
        ambient_source_FTC=error(reference['ambient'][1],final['omega'][0]-initial['omega'][0]),
        adapted_connection_integral_vs_endpoint_rapidity=error(reference['adapted'][0],reference['ambient'][0]+final['rapidity_value_first_second'][0]-initial['rapidity_value_first_second'][0]),
        adapted_source_integral_vs_endpoint_rapidity=error(reference['adapted'][1],reference['ambient'][1]+final['rapidity_value_first_second'][1]-initial['rapidity_value_first_second'][1]),
        connection_definition='LOWER omega, RIGHT Maurer dtheta=+epsilon theta wedge theta; Omega=1/4 FULL ordered omegaAB GammaA GammaB',
        moving_frame_connection='B^-1 Omega B+B^-1 Bdot, B=S(-eps Uwall); adapted coefficient eps*(omega04_t+eta_dot)/2',
        angular_connection_kernels_and_full10_primitive_wall_covector_retained=True,
        physical_initial_Spin_lift=None,physical_initial_F0=None,physical_initial_U2_lift=None,
        intrinsic_4D_LC_identified_with_ambient_M5=False,original_eta_contact_included_in_Spin_parallel_generator=False,
        original_eta_contact_retained_separately=True,U2_gauge_connection_included_in_geometric_Spin_generator=False,
        full_128_and_384_existing_D5_Clifford_carriers_used=True,geometric_M8_Spin16_identified_with_SMtrace=False,
        source_axis='supplied inside-cell rawtime germ, fixed interval; full physical energy/B/reset/endpoint source not supplied',
        energy_field_variation_kernels_scope='Every N,C,z,R and first-derivative primitive varies; unknown physical source contracts saved covectors plus moving-trajectory and initial/end contacts',
        parallel_lift_not_a_normalized_state_or_chosen_reset=True,no_external_normal_chart_or_history_extrapolation=True,
        field_history_or_source_profile_reintegrated=False,coupled_corrections=0,
        full_physical_outgoing_derivative_at_2e_minus10=False,physical_two_spin_normalization=None,physical_muon_magnetic_moment=None,
        input_and_source_sha256=dict(sorted(pins.items())))
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    result['numerical_sha256']=sha256((out/'application.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=result['classification'],numerical_sha256=result['numerical_sha256']),sort_keys=True))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();execute(a.output)
