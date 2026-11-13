"""Consume a finite returned sigma-normal prefix in the original two-sheet D5.

The represented collar trial has a supplied held transverse coefficient
derivative. Located interpolation interfaces are integrated once and their
Green returns retained. This is an action application on that finite trial
domain, not physical normal-mode normalization or a retarded exterior.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import CubicHermiteSpline
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_sigma_normal_collar_transport import CanonicalC1History,sigma_geometry_point,_fixed_radial_maps
from bhsm.interface.muon_sigma_collar_d5_weak_action import collar_spin_gauge_transport,original_collar_coordinate_action,partial_two_sheet_collar_trace
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_sigma_foliation_eta,d5_sigma_normal_flow_germ
from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt
from bhsm.interface.muon_holomorphic_child_action import _affine_geometry
from bhsm.interface.muon_holomorphic_current_source import _wall_coframe
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace,moving_d5_material_trace_frame
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_continued_action_reality import _higgs_mass_realified
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from evaluate_muon_d5_finite_trace_pole_match import clean


def complex_point_coefficients(raw,rho,parent,refs,rep):
    """Original analytic point coefficients; no float projection of rho."""
    q,v,m,d,dr,wall,_=_geometry_variables(raw[:100]);f=_fields(12,q,v,m,(rho/WALL)*wall)
    R=f['A']*f['B']/_sqrt(f['A']**2+f['B']**2)
    lr=f['la']+f['lb']-(f['A']**2*f['la']+f['B']**2*f['lb'])/(f['A']**2+f['B']**2)
    rr=f['ap']+f['bp']-(f['A']**2*f['ap']+f['B']**2*f['bp'])/(f['A']**2+f['B']**2)
    def lam(x):
        qq,vv,mm,dd,rate,ww,_=_geometry_variables(x[:100]);ff=_fields(12,qq,vv,mm,(rho/WALL)*ww)
        return (ff['A']**2/(ff['A']**2+ff['B']**2)).value
    B,_=_fixed_radial_maps(rep,rho);A=np.einsum('r,rfc->fc',B,raw[100:180].reshape(4,5,4))
    total=lam(parent)-lam(refs[0])+lam(refs[1]);A[2:]+=M*(total-1)
    _,clock,_=_wall_coframe(raw)
    return dict(lapse=f['N'].value,radial_coframe=(f['C']*wall/WALL).value,radius=R.value,
        coordinate_shift=((f['beta']+(rho/WALL)*dr)/(wall/WALL)).value,
        geometric_time_contact=((f['lc']+3*lr-f['beta']*(f['cp']+3*rr)-f['betap'])/(2*f['N'])).value,
        geometric_radial_contact=((f['np']+3*rr)/(2*f['C'])).value,
        gauge_connection_material=A,surface_proper_clock=clock.value,total_mechanical_profile=total)


def materialize(trial,normal_flow,output,energy,order):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve each partial action application')
    if order<3 or order>8:raise ValueError('bounded quadrature order required')
    pins={};archives={}
    def read(p):
        p=ROOT/p if not p.is_absolute()else p;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    data=read(ROOT/trial/'candidate.npz');result=read(ROOT/normal_flow/'result.json');hist=read(ROOT/normal_flow/'actual_C1_history.npz')
    prefix=sorted(n for n in result['archives']if n.startswith('normal_prefix_'))[-1];flow=read(ROOT/normal_flow/prefix)
    record=result['normal_prefixes'][-1]
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation'];full=full_d5_localized_lepton_trace()
    history=CanonicalC1History(hist['coordinate_times'],hist['raw_fields'],hist['canonical_raw_time'],phase['coordinates'])
    s=flow['s'];maps=np.array([flow[k]for k in('particle_gauge_transport','particle_analytic_dual_transport','conjugate_gauge_transport','conjugate_analytic_dual_transport')]).transpose(1,0,2,3)
    y=np.c_[flow['coordinate_time'],flow['material_rho'],flow['normal_leaf_transverse'],flow['normal_log_density'],flow['normal_action_integral'],flow['spin_normal_connection_integral'],maps.reshape(len(s),-1)]
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split compact represented action output')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def point(yy,cell):
        raw,rate=history.value(yy[0],cell);c=sigma_geometry_point(raw,rate,yy[1])
        n=d5_sigma_foliation_eta(c,gamma=full['gamma5D_particle'],carrier_count=1,angular_count=1,sheet_orientation=1)
        a=d5_sigma_normal_flow_germ(c,n,coordinate_time_first_slot=0)
        parent=_affine_geometry(data['raw_pair'][0],yy[0]);refs=np.array([_affine_geometry(r,yy[0])for r in data['reference_pair']])
        cc=complex_point_coefficients(raw,yy[1],parent,refs,rep)
        return raw,rate,c,n,a,cc
    def derivative(yy,cell):
        raw,rate,c,n,a,cc=point(yy,cell);F=-a['sigma_flow_coordinate_velocity'][0]
        D=-np.c_[a['sigma_flow_coordinate_velocity_time'][0],a['sigma_flow_coordinate_velocity_radial'][0]]
        n0,n4=(n[k][0]for k in('sigma_normal_timelike_component','sigma_normal_radial_component'))
        N,C,z=(c[k][0]for k in('lapse','radial_coframe','coordinate_shift'))
        nr=c['lapse_log_radial'][0]*N;cr=c['radial_coframe_log_radial'][0]*C;zr=c['coordinate_shift_radial'][0];ct=c['radial_coframe_first'][0,0]
        omega=-(nr/(N*C)*n0+(ct-z*cr-C*zr)/(N*C)*n4)
        A=cc['gauge_connection_material'];connection=A[0]*F[0]+A[1]*F[1]
        G=full['unitTr16_gauge_particle'];Om=np.einsum('a,aij->ij',connection,G);Ob=np.einsum('a,aij->ij',connection,G.conj())
        T,L,Tb,Lb=yy[7:].reshape(4,16,16)
        return np.r_[F,D@yy[2:4],-a['sigma_flow_log_density_normal_first'][0],np.sin(c['eta_profile'][0])**2,omega,
            (-Om@T).ravel(),(L@Om).ravel(),(-Ob@Tb).ravel(),(Lb@Ob).ravel()]
    c0,n0,a0=point(y[0],0)[2:5];U0=(n0['sigma_normal_timelike_component']/n0['sigma_normal_radial_component'])[0]
    f0=c0['eta_profile'][0];Rw=c0['radius'][0];AR=flow['trial_wall_amplitude'].item()/np.sin(f0);AL=flow['literal_left_trial_wall_amplitude'].item()/np.sin(f0)
    frames={eps:moving_d5_material_trace_frame(-eps*U0,0,full_representation=full)for eps in(1,-1)}
    K=np.zeros((2,2,64,64),complex);KE=np.zeros_like(K);points=[];point_diagnostics=[];endpoint_green={};face_returns=[]
    nodes,weights=leggauss(order);raw_parts=[];spin_parts=[];independent_half_density=[]
    def trial_at(yy,dy,cell,eps):
        raw,rate,c,n,a,cc=point(yy,cell);T,L,Tb,Lb=yy[7:].reshape(4,16,16);dT,dL,dTb,dLb=dy[7:].reshape(4,16,16)
        transport=collar_spin_gauge_transport(yy[6],dy[6],T,L,Tb,Lb,dT,dL,dTb,dLb,full=full,sheet_orientation=eps)
        S0=frames[eps]['spin_boost128'];SI0=frames[eps]['spin_boost_inverse128']
        right=transport['spin_gauge_transport128']@S0;left=SI0@transport['spin_gauge_analytic_dual128']
        dright=transport['spin_gauge_transport_first128']@S0
        f=c['eta_profile'][0];fs=c['eta_profile_coordinate_time'][0]*dy[0]+c['eta_profile_radial'][0]*dy[1]
        ur=AR*np.sin(f)*np.exp(-yy[4]/2);ul=AL*np.sin(f)*np.exp(-yy[4]/2);urs=ur*(fs/np.tan(f)-dy[4]/2)
        # Held transverse coefficient test is explicitly chosen for this
        # one-line finite trial. It is not a physical mode/source jet.
        V=ur*right;Vs=urs*right+ur*dright;Vq=np.zeros_like(V)
        G0=full['gamma5D_self_dual128'][0];literal=ul*G0@left
        F=-a['sigma_flow_coordinate_velocity'][0];noutf=-F[0]*c['eta_profile_coordinate_time'][0]-F[1]*c['eta_profile_radial'][0]
        mass=-noutf/np.tan(f);U=(n['sigma_normal_timelike_component']/n['sigma_normal_radial_component'])[0]
        dU=a['sigma_flow_normal_velocity_time'][0]*dy[0]+a['sigma_flow_normal_velocity_radial'][0]*dy[1]
        adapted=moving_d5_material_trace_frame(-eps*U,-eps*dU,full_representation=full)
        right_adapted=adapted['spin_boost_inverse128']@right
        right_adapted_s=adapted['spin_boost_inverse_first128']@right+adapted['spin_boost_inverse128']@dright
        # Before/after face jumps remain external interface returns.
        diag=dict(analytic_inverse_rows_max=float(np.max(abs(transport['analytic_inverse_rows']))),
            analytic_inverse_first_rows_max=float(np.max(abs(transport['analytic_inverse_first_rows']))),
            adapted_frame_first_norm=float(np.linalg.norm(right_adapted_s)),
            mode_normal_ODE_rows=urs+dy[4]*ur/2-mass*ur,
            returned_coordinate_ODE_defect_norm=float(np.linalg.norm(dy[:2]-F)))
        operators=[]
        for b,branch in enumerate(('particle','conjugate')):
            sl=slice(64*b,64*(b+1));g=full['gamma5D_'+branch];gg=full['unitTr16_gauge_particle'];gg=gg if b==0 else gg.conj()
            operators.append(original_collar_coordinate_action(cc,gamma=g,generators=gg,right_value=V[sl,sl],right_normal_first=Vs[sl,sl],
                right_transverse_first=Vq[sl,sl],literal_left_value=literal[sl,sl],normal_coordinate_velocity=dy[:2],leaf_transverse=yy[2:4],
                eta_mass_outward=mass,normal_timelike_outward=n['sigma_normal_timelike_component'][0],
                normal_radial_outward=n['sigma_normal_radial_component'][0],sheet_orientation=eps,
                surface_proper_clock=cc['surface_proper_clock'],energy=energy))
        return operators,transport,right_adapted,right_adapted_s,diag,raw,c
    # Every positive-length interval occurs once. The zero-length
    # before/after (and repeated after) samples never receive a weight.
    for j in range(len(s)-1):
        lo,hi=s[j],s[j+1]
        if hi<=lo:continue
        cell=history.cell((y[j,0]+y[j+1,0])/2);d0=derivative(y[j],cell);d1=derivative(y[j+1],cell)
        spline=CubicHermiteSpline([lo,hi],np.array([y[j],y[j+1]]),np.array([d0,d1]))
        for x,w in zip(nodes,weights):
            ss=(lo+hi)/2+(hi-lo)*x/2;yy=spline(ss);dy=spline(ss,1);wt=(hi-lo)*w/2
            for ei,eps in enumerate((1,-1)):
                op,t,adapt,adapt_s,diag,raw,c=trial_at(yy,dy,cell,eps)
                density=-c['volume_density'][0]*(yy[2]*dy[1]-yy[3]*dy[0])
                diag['returned_volume_density_defect']=density-Rw**3*np.exp(yy[4])
                for b in range(2):K[ei,b]+=wt*density*op[b]['literal_weak_integrand'];KE[ei,b]+=wt*density*op[b]['literal_energy_integrand']
                if eps==1:
                    points.append((ss,yy[0],yy[1],wt,density));raw_parts.append(raw)
                    spin_parts.append((adapt,adapt_s));point_diagnostics.append(diag)
                    # Independent finite difference of the returned
                    # half-density, distinct from the algebraic us row.
                    delta=(hi-lo)*1e-3
                    def half(z):
                        yz=spline(z);cz=point(yz[0:][...],cell)[2]
                        uz=AR*np.sin(cz['eta_profile'][0])*np.exp(-yz[4]/2)
                        return np.exp(yz[4]/2)*uz
                    for factor in(1.,.5):
                        hh=delta*factor;fd=(half(ss+hh)-half(ss-hh))/(2*hh)
                        actual_half=AR*np.sin(c['eta_profile'][0]);fn=c['eta_profile_coordinate_time'][0]*dy[0]+c['eta_profile_radial'][0]*dy[1]
                        independent_half_density.append((ss,hh,fd-fn/np.tan(c['eta_profile'][0])*actual_half,fd))
        for index,position in((j,'left'),(j+1,'right')):
            yy=y[index];dy=derivative(yy,cell)
            matrices=[]
            for eps in(1,-1):
                op,*_=trial_at(yy,dy,cell,eps);density=Rw**3*np.exp(yy[4]);matrices.append(np.array([density*a['literal_normal_Green_integrand']for a in op]))
            endpoint_green[(index,cell)]=np.array(matrices)
    # Actual face traces have separate left/right charts. No repeated
    # after sample creates a second return or integral contribution.
    for face_s in np.unique(s):
        same=np.where(s==face_s)[0]
        if len(same)<2:continue
        left_candidates=[v for(i,c),v in endpoint_green.items()if i==same[0]]
        right_candidates=[v for(i,c),v in endpoint_green.items()if i==same[-1]]
        if left_candidates and right_candidates:face_returns.append(right_candidates[0]-left_candidates[0])
    block=lambda a:np.block([[a[0],np.zeros((64,64),complex)],[np.zeros((64,64),complex),a[1]]])
    K384=np.array([np.kron(np.eye(3),block(a))for a in K]);KE384=np.array([np.kron(np.eye(3),block(a))for a in KE])
    raw0=history.value(y[0,0],0)[0];_,ell0,_=_wall_coframe(raw0);surface_density=ell0.value*Rw**3
    a=partial_two_sheet_collar_trace(K384,KE384,full=full,fixedY_mass=_higgs_mass_realified(raw0[260:264]),surface_density=surface_density)
    save('partial_two_sheet_action_and_Gamma.npz',{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
    save('partial_collar_integrands_and_returns.npz',dict(original_branch_action=K,original_branch_action_energy=KE,
        quadrature_points=np.array(points),quadrature_raw_fields=np.array(raw_parts),
        independent_returned_half_density_difference_rows=np.array(independent_half_density),
        before_after_interface_Green_returns=np.array(face_returns),
        initial_normal_Green=next(iter(endpoint_green.values())),final_normal_Green=next(reversed(endpoint_green.values())),
        adapted_spin_gauge_maps=np.array([z[0]for z in spin_parts]),adapted_spin_gauge_normal_first=np.array([z[1]for z in spin_parts])))
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=v for p,v in pins.items()):raise ValueError('same executed source and action required')
    result=dict(classification='EVALUATED_PARTIAL_SIGMA_COLLAR_ORIGINAL_TWO_SHEET_D5_ACTION',input_hashes=pins,archives=archives,
        energy=energy,quadrature_order=order,positive_length_intervals=int(np.sum(np.diff(s)>0)),quadrature_points=len(points),
        before_after_interface_returns=len(face_returns),actual_partial_action_norm=float(np.linalg.norm(K384)),
        actual_partial_action_energy_norm=float(np.linalg.norm(KE384)),partial_Gamma_norm=float(np.linalg.norm(a['partial_field_Gamma'])),
        partial_Gamma_energy_norm=float(np.linalg.norm(a['partial_field_Gamma_energy'])),
        complete_field_trace_rows_max=float(np.max(abs(a['complete_field_and_chiral_trace_rows']))),
        complete_field_trace_energy_rows_max=float(np.max(abs(a['complete_field_and_chiral_trace_energy_rows']))),
        independent_returned_half_density_FD_rows_max=float(np.max(abs(np.array(independent_half_density)[:,2]))),
        analytic_spin_gauge_inverse_rows_max=max(d['analytic_inverse_rows_max']for d in point_diagnostics),
        analytic_spin_gauge_inverse_first_rows_max=max(d['analytic_inverse_first_rows_max']for d in point_diagnostics),
        adapted_frame_first_norm_max=max(d['adapted_frame_first_norm']for d in point_diagnostics),
        returned_coordinate_ODE_defect_norm_max=max(d['returned_coordinate_ODE_defect_norm']for d in point_diagnostics),
        returned_volume_density_defect_max=max(abs(d['returned_volume_density_defect'])for d in point_diagnostics),
        interface_Green_return_norm=float(np.linalg.norm(face_returns)),actual_partial_mode_pairing=flow['partial_mode_norm'].item(),
        independent_left_right_trial_amplitudes=dict(right=flow['trial_wall_amplitude'].item(),left=flow['literal_left_trial_wall_amplitude'].item()),
        once_only_fixedY_Higgs_seam=True,full_two_sheet_field_fibers=768,full_complementary_field_rows=750,
        angular_scope='n0 trial only; reached n1/n3 magnetic and n2/n4 complement not consumed by this scalar collar action',
        transverse_trial_scope='explicit held coefficient derivative on the one supplied normal line; not the physical source/normal-motion derivative',
        interpolation_scope='returned normal state reconstructed by per-interval Hermite polynomials; located complex face returns kept; not analytic physical sewing',
        finite_first_order_border_not_retarded_boundary_selector=True,partial_integral_not_full_normalization=True,
        quadrature_interpolation_FD_action_and_complement_errors_not_enclosed=True,
        physical_Gamma2_pole_charge_LSZ_or_Pauli_admitted=False,physical_a_mu=None,physical_g_mu=None)
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),Gamma_norm=result['partial_Gamma_norm'],original_rows=result['complete_field_trace_rows_max'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--trial',type=Path,required=True);p.add_argument('--normal-flow',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--energy',type=float,required=True);p.add_argument('--quadrature-order',type=int,default=4)
    a=p.parse_args();materialize(a.trial,a.normal_flow,a.output,a.energy,a.quadrature_order)
