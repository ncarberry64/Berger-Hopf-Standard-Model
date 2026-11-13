"""Actual all10-generator Spin Duhamel kernels on the frozen real child wall."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from hashlib import sha256
import numpy as np
import mpmath as mp
from scipy import sparse
from scipy.linalg import block_diag

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'audits')]
import bhsm_real_child_wall_geometric_spin_transport_20261016 as frozen
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_m5_geometric_spin_connection import m5_geometric_spin_connection
from bhsm.interface.muon_spin_duhamel_insertion import spin_duhamel_insertion_kernels,spin_endpoint_and_frame_kernels,LORENTZ_PAIRS
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

BACKGROUND='artifacts/muon_real_radial_spin_bolt_20261016/geometric_spin_run_1'
BACKGROUND_SHA='287888657ad739da19982a6dbe71958b300e20c655e9fa66a38fcd4f05b514de'
FROZEN_SOURCE_SHA='0c3b8a7e2d2009276f460d316259a92efb8450e65a8362badc6edcb987cce7d3'

def maximum(a):return float(np.max(abs(a)))
def error(a,b):
    v=maximum(a-b);d=max(maximum(a),maximum(b));return dict(absolute=v,relative_to_nonzero=v/d if d else None)
def save_sparse(arrays,name,A):
    A=sparse.csr_matrix(A);arrays[name+'_data']=A.data;arrays[name+'_indices']=A.indices;arrays[name+'_indptr']=A.indptr;arrays[name+'_shape']=np.array(A.shape,np.int64)
def lift128(M):return sparse.block_diag((sparse.kron(sparse.csr_matrix(M[:4,:4]),sparse.eye(16)),sparse.kron(sparse.csr_matrix(M[4:,4:]),sparse.eye(16))),format='csr')
def lift384(M):return sparse.kron(sparse.eye(3),lift128(M),format='csr')
def save_full(arrays,name,M):
    if M.ndim==2:
        save_sparse(arrays,name+'128',lift128(M));save_sparse(arrays,name+'384',lift384(M))
    else:
        save_sparse(arrays,name+'128',sparse.vstack([lift128(a)for a in M]));save_sparse(arrays,name+'384',sparse.vstack([lift384(a)for a in M]))
def increment(A):
    v=A.copy();t=A.copy()
    for n in range(2,18):t=t@A/n;v+=t
    return v
def profile(j,u):return 1+.031*(j+1)*u-.17*u*u+.11*u**3
def profile_time(j,u,h):return(.031*(j+1)-.34*u+.33*u*u)/h
def mm(a):return mp.matrix([[mp.mpc(float(z.real),float(z.imag))for z in row]for row in a])
def binary(a):return np.array([[complex(z)for z in row]for row in a.tolist()])

def execute(output):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent actual applications')
    if sha256(Path(frozen.__file__).read_bytes()).hexdigest()!=FROZEN_SOURCE_SHA:raise ValueError('Published Spin source changed')
    folder=ROOT/BACKGROUND;receipt=json.loads((folder/'result.json').read_text())
    if receipt['numerical_sha256']!=BACKGROUND_SHA or sha256((folder/'application.npz').read_bytes()).hexdigest()!=BACKGROUND_SHA:raise ValueError('Published Spin background changed')
    with np.load(folder/'application.npz',allow_pickle=False)as z:old={k:z[k].copy()for k in z.files}
    phase=load_profile_preserving_phase(frozen.PHASES['outgoing'],repository=ROOT);h=float(phase['receipt']['span'])
    if h!=1e-5 or phase['receipt']['steps']!=1:raise ValueError('Same complete supported one-cell background required')
    full=full_d5_localized_lepton_trace();Gp=full['gamma5D_particle'][[0,4,1,2,3]];Gc=full['gamma5D_conjugate'][[0,4,1,2,3]]
    G8=np.array([block_diag(a,b)for a,b in zip(Gp,Gc)]);G128=full['gamma5D_self_dual128'][[0,4,1,2,3]]
    factor=max(maximum(lift128(a).toarray()-b)for a,b in zip(G8,G128))
    if factor!=0:raise ValueError('Exact EXISTING Spin4 x(SM16+conjugate16) row factorization required')
    K=G8[0]@G8[1];J=np.array([G8[a]@G8[b]/2 for a,b in LORENTZ_PAIRS])
    arrays=dict(existing_gamma_particle_conjugate_spin8=G8,existing_gamma_selfdual128=G128,
        existing_generator_pairs=np.array(LORENTZ_PAIRS),source_profile_coefficients=np.array([[1,.031*(j+1),-.17,.11]for j in range(10)]))
    save_full(arrays,'Duhamel_base_minus_generator',-J)
    cache={}
    def get(t):
        t=float(t)
        if t<0 or t>h:raise ValueError('Outside published child history support')
        if t not in cache:
            s=frozen.actual_germ(phase,t);a=m5_geometric_spin_connection(s['primitives'],gamma=Gp,orientation=1)
            o=a['wall_boost_connection_scalar_value_first']
            cache[t]=np.array([o,o+s['rapidity_value_first_second'][1:]])
        return cache[t]
    total=np.array([old['Gauss32_ambient_integral_value_first'][0],old['Gauss32_adapted_integral_value_first'][0]])/2
    def split(s,n):
        if s==0:return total.copy()
        if s==h:return -total.copy()
        # Exact derivative-weighted identity avoids cancellation at s=h/2.
        q,w=np.polynomial.legendre.leggauss(n);v=(h-2*s)*get(s)[:,0]
        for lo,hi,weight in((0.,s,lambda t:t),(s,h,lambda t:h-t)):
            ts=lo+(q+1)*(hi-lo)/2
            v+=(hi-lo)/2*np.einsum('q,q,qf->f',w,np.array([weight(t)for t in ts]),np.array([get(t)[:,1]for t in ts]))
        return v/2
    responses={};time_records=[];split_controls=[];ward_records=[];tail=0.;literal_defect=0.
    for n in(8,16,32):
        q,w=np.polynomial.legendre.leggauss(n);times=(q+1)*h/2;weights=w*h/2;deltas=np.array([split(t,8 if n<32 else 16)for t in times])
        arrays[f'Gauss{n}_times']=times;arrays[f'Gauss{n}_weights']=weights;arrays[f'Gauss{n}_split_parameters']=deltas
        for frame in range(2):
            for eps in(-1,1):
                base=np.zeros((10,8,8),complex);correction=base.copy();ward=base.copy()
                for it,(t,ww,dd)in enumerate(zip(times,weights,deltas)):
                    a=spin_duhamel_insertion_kernels(G8,total_parameter=total[frame],split_parameter=dd[frame],orientation=eps)
                    ff=np.array([profile(j,t/h)for j in range(10)])
                    base+=ww*ff[:,None,None]*a['stable_kernel_base'];correction+=ww*ff[:,None,None]*a['stable_kernel_correction']
                    L=np.eye(8)+increment(-eps*(total[frame]+dd[frame])*K/2)
                    R=np.eye(8)+increment(-eps*(total[frame]-dd[frame])*K/2)
                    Omega=eps*get(t)[frame,0]*K/2
                    for j,jj in enumerate(J):
                        frame_source=profile_time(j,t/h,h)*jj+ff[j]*(Omega@jj-jj@Omega)
                        ward[j]-=ww*(L@frame_source@R)
                    tail=max(tail,*a['literal_increment_remainder_bounds']);literal_defect=max(literal_defect,maximum(a['literal_minus_Clifford_identity_correction']))
                    if n==32:
                        name=f'frame{frame}_eps{eps}_Gauss32_node{it}_'
                        save_full(arrays,name+'kernel_correction',a['stable_kernel_correction'])
                        arrays[name+'literal_finite_gamma_correction_spin8']=a['literal_finite_gamma_kernel_correction']
                        arrays[name+'correction_coefficients_J_KJ']=np.array([a['correction_coefficient_J'],a['correction_coefficient_KJ']])
                key=(frame,eps,n);responses[key]=base+correction
                P=np.eye(8)+increment(-eps*total[frame]*K)
                target=np.array([-profile(j,1)*jj@P+profile(j,0)*P@jj for j,jj in enumerate(J)])
                for j in range(10):ward_records.append(dict(time_order=n,frame=frame,orientation=eps,generator=j,
                    direct_pure_frame_Ward=error(ward[j],target[j])))
                name=f'frame{frame}_eps{eps}_Gauss{n}_';arrays[name+'response_base_spin8']=base;arrays[name+'response_correction_spin8']=correction
                arrays[name+'pure_frame_Ward_response_spin8']=ward
                save_full(arrays,name+'response',base+correction)
                if n>8:
                    time_records.append(dict(frame=frame,orientation=eps,orders=[n//2,n],all10_response=error(responses[frame,eps,n//2],responses[key])))
        print(json.dumps(dict(completed_time_order=n,cached_actual_coefficients=len(cache))),flush=True)
    # Include actual endpoints and the cancellation-sensitive midpoint.
    special={}
    for t in(0.,h/2,h):
        values=[split(t,n)for n in(8,16,32)]
        split_controls.append(dict(time=t,order8_to16=error(values[0],values[1]),order16_to32=error(values[1],values[2]),split_values=[v.tolist()for v in values]))
        for frame in range(2):
            for eps in(-1,1):
                a=spin_duhamel_insertion_kernels(G8,total_parameter=total[frame],split_parameter=values[-1][frame],orientation=eps)
                special[t,frame,eps]=a;tag=f'special_t{t:.8g}_frame{frame}_eps{eps}_'
                save_full(arrays,tag+'kernel_correction',a['stable_kernel_correction'])
                save_full(arrays,tag+'literal_finite_gamma_correction',a['literal_finite_gamma_kernel_correction'])
                arrays[tag+'correction_coefficients_J_KJ']=np.array([a['correction_coefficient_J'],a['correction_coefficient_KJ']])
    # MP exponentials retain the actual fixed gamma entries, not idealized zeros.
    mp_records=[]
    with mp.workdps(80):
        Km=mm(K)
        for(t,frame,eps),a in special.items():
            dd=float(split_controls[(0.,h/2,h).index(t)]['split_values'][-1][frame]);aa=mp.mpf(total[frame]);d=mp.mpf(dd)
            L=mp.expm(-eps*(aa+d)*Km/2);R=mp.expm(-eps*(aa-d)*Km/2)
            for j,jj in enumerate(J):
                ref=-L*mm(jj)*R;corr=ref+mm(jj)
                mp_records.append(dict(time=t,frame=frame,orientation=eps,generator=j,
                    stable_full_kernel=error(a['stable_kernel'][j],binary(ref)),
                    stable_correction=error(a['stable_kernel_correction'][j],binary(corr)),
                    literal_finite_gamma_correction=error(a['literal_finite_gamma_kernel_correction'][j],binary(corr))))
    # Literal perturbed ORDERED ODE, every generator/step/refinement retained.
    fd_records=[]
    for n in(8,16,32):
        dt=h/n;grid=np.linspace(0,h,2*n+1);background=np.array([get(t)[:,0]/2 for t in grid])
        for frame in range(2):
            for eps in(-1,1):
                for j,jj in enumerate(J):
                    def ode(xi):
                        Y=np.zeros((8,8),complex)
                        for k in range(n):
                            def rhs(index,Z):
                                u=index/(2*n);A=eps*background[index,frame]*K+xi*profile(j,u)*jj
                                return -A-A@Z
                            r1=rhs(2*k,Y);r2=rhs(2*k+1,Y+dt*r1/2);r3=rhs(2*k+1,Y+dt*r2/2);r4=rhs(2*k+2,Y+dt*r3)
                            Y+=dt*(r1+2*r2+2*r3+r4)/6
                        return Y
                    for step in(.08,.04,.02):
                        derivative=((ode(-2*step)-ode(2*step))+8*(ode(step)-ode(-step)))/(12*step)
                        fd_records.append(dict(time_steps=n,frame=frame,orientation=eps,generator=j,parameter_step=step,
                            nonzero_target_norm=float(np.linalg.norm(responses[frame,eps,32][j])),
                            derivative=error(derivative,responses[frame,eps,32][j])))
        print(json.dumps(dict(completed_ordered_ODE_steps=n)),flush=True)
    # All moving time and independent initial/final frame contact coefficients.
    endpoint_records=[]
    for frame,name in enumerate(('ambient','adapted')):
        for eps in(-1,1):
            P=np.eye(8)+increment(-eps*total[frame]*K)
            a=spin_endpoint_and_frame_kernels(G8,parallel=P,
                initial_connection=eps*get(0.)[frame,0]*K/2,final_connection=eps*get(h)[frame,0]*K/2)
            for label in('moving_initial_time','moving_final_time','independent_initial_frame','independent_final_frame','initial_physical_lift_variation_left_multiplier'):
                save_full(arrays,f'{name}_eps{eps}_'+label,a[label])
            if frame==1:
                for j,t in enumerate((0.,h)):
                    U=old[f'selected{2*j}_wall_velocity_value_first'][0]
                    coeff=eps*K/(2*(1-U*U))
                    save_full(arrays,f'{name}_eps{eps}_wall_velocity_endpoint{j}_contact',P@coeff if j==0 else -coeff@P)
            endpoint_records.append(dict(frame=frame,orientation=eps,
                independent_initial_frame_nonzero_norm=float(np.linalg.norm(a['independent_initial_frame'])),
                independent_final_frame_nonzero_norm=float(np.linalg.norm(a['independent_final_frame']))))
    pins=dict(phase['input_hashes']);pins[BACKGROUND+'/application.npz']=BACKGROUND_SHA;pins[BACKGROUND+'/result.json']=sha256((folder/'result.json').read_bytes()).hexdigest()
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT)and Path(p).suffix=='.py':p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(classification='ACTUAL_SUPPORTED_REAL_ALL10_LORENTZ_SPIN_DUHAMEL_KERNELS',
        supported_interval=[0.,h],frame_order=('ambient','adapted'),generator_pairs=LORENTZ_PAIRS,
        existing_full128_factorization_error=factor,full128_and384_rows_preserved=True,
        row_factorization='EXACT existing Spin4 x(SM16+conjugate16) and existing3 families; no extra species or statistics',
        sparse_storage='Exact nonzero entries; no small-entry threshold; all10 base and corrections separate, full128/384 Gauss32 plus endpoints/midpoint',
        time_quadrature_refinements=time_records,stable_split_controls=split_controls,
        independent_MP80_exponential_controls=mp_records,all_ordered_ODE_derivative_steps=fd_records,
        direct_all10_pure_frame_Ward_controls=ward_records,
        independent_endpoint_and_frame_kernels=endpoint_records,
        literal_finite_gamma_Taylor_diagnostic_order=17,max_literal_increment_tail_bound=tail,
        max_literal_finite_gamma_minus_Clifford_correction=literal_defect,
        all10_noncommuting_and_commuting_channels_kept=True,
        kernel_definition='-P(t1,s) J_AB P(s,t0); J_AB=GammaA GammaB/2; full ordered Lorentz convention',
        split_identity='split=(h-2s)*omega(s)/2 + integral_0^s t*omega_prime(t)/2 + integral_s^h (h-t)*omega_prime(t)/2',
        moving_endpoint_and_frame_sources_evaluated_as_kernels=True,
        physical_energy_or_B_connection_source=None,physical_initial_Spin_lift=None,physical_initial_F0=None,
        physical_endpoint_or_frame_variations_selected=False,physical_outgoing_domain_selected=False,
        full_common_native_operator_or_state_completed=False,U2_or_eta_contact_inserted_in_Spin_connection=False,
        physical_derivative_at_2e_minus10_passed=False,physical_normalized_spins=None,physical_muon_magnetic_moment=None,
        field_history_or_profile_reintegrated=False,coupled_corrections=0,input_and_source_sha256=dict(sorted(pins.items())))
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    result['numerical_sha256']=sha256((out/'application.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(numerical_sha256=result['numerical_sha256'],archive_bytes=(out/'application.npz').stat().st_size)),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();execute(a.output)
