"""Actual bounded sigma-normal flow on a current canonical shooting history.

At a reached time face, an explicitly bounded original child canonical
callback extension is attempted. No history outside those admitted finite
cells or incomplete normal integral is silently filled in.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_sigma_normal_collar_transport import CanonicalC1History,transport_sigma_normal,_fixed_radial_maps
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_child_clock_application import holomorphic_child_explicit_clock_application
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_coupled_phase_trace_projection import _solve
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_complex_canonical_midpoint import solve_complex_canonical_midpoint
from bhsm.interface.muon_warm_complex_canonical_compatibility import warm_complex_constitutive_compatibility
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from evaluate_muon_d5_finite_trace_pole_match import clean


def materialize(trial,d5_component,output,normal_length,max_extensions,nu_squared,surface_gamma):
    src=ROOT/trial;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every normal-domain application')
    pins={};archives={};records=[]
    def read(p):
        p=ROOT/p if not p.is_absolute()else p
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    data=read(src/'candidate.npz');phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation'];coords=phase['coordinates'];P=coords['lift'];full=full_d5_localized_lepton_trace()
    component=read(ROOT/d5_component/'stage_0000_current_geometry_normal_and_material_trace.npz')
    amplitude=component['actual_normalized_Gamma0_multiplier'].item()
    pars=dict(nu_squared_action=nu_squared,surface_gamma=surface_gamma);out.mkdir(parents=True)
    def save(name,a):
        path=out/name;_compressed_npz(path,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if path.stat().st_size>=10*1024**2:raise ValueError('split compact source-flow result')
        archives[name]=dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest())
    tangent_records=[]
    def tangent(raw,t):
        a=holomorphic_child_explicit_clock_application(raw,t,data['raw_pair'],data['reference_pair'],rep,**pars)
        H=a['canonical_tangent_operator'];rhs=a['canonical_tangent_rhs'];F=canonical_central_frame(raw,rep)['named_frame_covectors']
        K=np.block([[H,F.T],[F,np.zeros((2,2),complex)]]);r=np.r_[rhs,np.zeros(2)]
        z,rs,cs=_solve(K,r);master=P.T@raw;dt=P@np.r_[master[106:212],z[:146]]
        tangent_records.append(dict(time=t,original_rows_max=float(np.max(abs(K@z-r))),
            RHS_max=float(np.max(abs(r))),uncancelled_row_scale_max=float(np.max(abs(K)@abs(z)+abs(r))),
            scaled_original_rows_max=float(np.max(abs(rs*(K@z-r))))))
        return dt
    B,D=zip(*[_fixed_radial_maps(rep,r)for r in rep['rho']]);basis_error=max(float(np.max(abs(np.array(B)-rep['radial_value_map']))),float(np.max(abs(np.array(D)-rep['radial_derivative_map']))))
    if basis_error>1e-10:raise ValueError('same original four complex radial source functions required')
    nodes=[(0.,data['raw_pair'][1],data['master_child'],data['own_child_Pi'])]
    for j in range(2):
        s=read(src/f'stage_{j:04d}.npz');e=read(src/f'endpoint_{j:04d}.npz')
        nodes.extend(((float(s['coordinate_time'].real),s['stage_raw'],s['stage_master'],None),
            (float(e['coordinate_time'].real),e['endpoint_raw'],e['endpoint_master'],e['endpoint_Pi'])))
    times=[n[0]for n in nodes];raws=[n[1]for n in nodes];rates=[tangent(n[1],n[0])for n in nodes]
    print(json.dumps(clean(dict(stage='normal_history_bound',nodes=len(nodes),basis_reproduction_max=basis_error,tangent_rows=tangent_records)),sort_keys=True),flush=True)
    h=times[-1]-times[-3];frame=canonical_central_frame(data['raw_pair'][1],rep);reference=data['master_child'][106:].copy()
    e=nodes[-1][2].copy();pi=nodes[-1][3].copy();extensions=[]
    callback=lambda eta,t:holomorphic_inherited_child_action(P@eta,t,data['raw_pair'],data['reference_pair'],rep,**pars)
    for attempt in range(max_extensions+1):
        history=CanonicalC1History(np.array(times),np.array(raws),np.array(rates),coords)
        arrays,record=transport_sigma_normal(history,rep,full,start_time=0.,wall_amplitude=amplitude,
            literal_left_wall_amplitude=amplitude,normal_length=normal_length)
        records.append(record);save(f'normal_prefix_{attempt:04d}.npz',arrays)
        print(json.dumps(clean(dict(stage='actual_normal_transport',attempt=attempt,**record)),sort_keys=True),flush=True)
        if record['status']!='SUPPLIED_CANONICAL_TIME_FACE'or attempt==max_extensions:break
        # Extend precisely the reached positive child time face using the
        # SAME original full action, Pi, source/reset seeds and named frames.
        tm=times[-1]+h/2;te=times[-1]+h
        def progress(i,z,rho,a,f,K,scale,hh):
            print(json.dumps(clean(dict(stage='reached_original_canonical_callback',iteration=i,detail=hh[-1])),sort_keys=True),flush=True)
        step=solve_complex_canonical_midpoint(e[:106],pi,e.copy(),h,lambda x:callback(x,tm),frame,
            frame_reference=reference,tolerance=2e-10,max_iterations=6,checkpoint=progress)
        a=step['application'];save(f'extension_{attempt:04d}_stage.npz',dict(stage_raw=P@a['midpoint_coefficients'],
            stage_master=a['midpoint_coefficients'],stage_Hessian=a['action']['hessian'],stage_gradient=a['action']['gradient'],
            original358_rows=a['residual'],frame_rows=step['framed_rows'][-2:],coordinate_time=np.array(tm),coordinate_step=np.array(h)))
        ex=dict(status=step['status'],original358_rows_max=float(np.max(abs(a['residual']))),
            largest_original358_row=int(np.argmax(abs(a['residual']))),coordinate_time=tm,history=step['history'])
        if step['status']!='ALL_ORIGINAL_COMPLEX_CANONICAL_ROWS_TOLERANCE':extensions.append(ex);break
        guess=np.r_[a['x_new'],a['v_mid'],a['y_mid']]
        end=warm_complex_constitutive_compatibility(guess,a['p_new'],lambda x:callback(x,te),frame,
            frame_reference=reference,tolerance=2e-10,max_iterations=6)
        ex.update(endpoint_status=end['status'],original146_rows_max=float(np.max(abs(end['original_constitutive_rows']))),
            largest_original146_row=int(np.argmax(abs(end['original_constitutive_rows']))),endpoint_coordinate_time=te)
        extensions.append(ex);save(f'extension_{attempt:04d}_endpoint.npz',dict(endpoint_raw=P@end['coefficients'],
            endpoint_master=end['coefficients'],endpoint_Pi=a['p_new'],original146_rows=end['original_constitutive_rows'],
            frame_rows=end['framed_rows'][-2:],coordinate_time=np.array(te)))
        if end['status']!='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE':break
        midraw=P@a['midpoint_coefficients'];endraw=P@end['coefficients'];times.extend((tm,te));raws.extend((midraw,endraw));rates.extend((tangent(midraw,tm),tangent(endraw,te)))
        e=end['coefficients'];pi=a['p_new']
    save('actual_C1_history.npz',dict(coordinate_times=np.array(times),raw_fields=np.array(raws),canonical_raw_time=np.array(rates)))
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in(Path(__file__),ROOT/'tests/test_muon_sigma_normal_collar_transport.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=v for p,v in pins.items()):raise ValueError('same actual canonical/source/normal history required')
    result=dict(classification='EVALUATED_ACTUAL_SIGMA_NORMAL_FLOW_DENSITY_AND_ANALYTIC_SOURCE_DUAL',
        input_hashes=pins,archives=archives,trial=trial.as_posix(),normal_prefixes=records,canonical_extensions=extensions,
        action_parameters=pars,canonical_time_tangent_rows=tangent_records,original_radial_source_basis_reproduction_max=basis_error,
        actual_C1_birth_midpoint_true_endpoint_history=True,actual_reached_original_child_callback_attempted=bool(extensions),
        parent_reference_source_clock_composed_once=True,normal_trial_wall_amplitude_not_a_fitted_coefficient=True,
        incomplete_action_integral_not_filled_by_radial_cap_norm=True,
        full_normalization_retarded_domain_or_physical_pole_admitted=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='actual finite canonical C1 polynomial history and normal ODE with recorded complex-cell jumps; interpolation/ODE/contour/complement and action errors are not enclosures')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--trial',type=Path,required=True);p.add_argument('--d5-component',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--normal-length',type=float,default=1e-7);p.add_argument('--canonical-extensions',type=int,default=1);p.add_argument('--nu-squared',type=float,required=True);p.add_argument('--surface-gamma',type=float)
    a=p.parse_args();materialize(a.trial,a.d5_component,a.output,a.normal_length,a.canonical_extensions,a.nu_squared,a.surface_gamma)
