"""Execute primary/secondary reset-compatible canonical computational sources."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_reset_secondary_canonical_source import secondary_compatible_action_source
from bhsm.interface.muon_reset_constrained_canonical_variation import canonical_variation_evolution
from bhsm.interface.muon_complex_paired_normal_action import _balanced_solver
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def clean(a):
    if isinstance(a,dict):return{k:clean(v)for k,v in a.items()}
    if isinstance(a,(list,tuple)):return[clean(v)for v in a]
    if isinstance(a,(complex,np.complexfloating)):return[float(a.real),float(a.imag)]
    if isinstance(a,np.ndarray):return clean(a.tolist())
    if isinstance(a,np.generic):return a.item()
    return a


def materialize(source_folder,normal_folder,reset_folder,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve secondary source applications')
    refs={}
    def read(folder,name,md=None):
        p=ROOT/folder/name;b=p.read_bytes();h=sha256(b).hexdigest();refs[p.relative_to(ROOT).as_posix()]=h
        if name.endswith('.json'):return json.loads(b)
        if md is None or h!=md['archives'][name]['sha256']:raise ValueError('completed secondary source input changed')
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    sm=read(source_folder,'result.json');nm=read(normal_folder,'result.json');rm=read(reset_folder,'result.json')
    for md in(sm,nm,rm):refs.update(md['input_hashes'])
    inputs=read(normal_folder,'same_action_inputs.npz',nm);clock=read(normal_folder,'clock_and_joint_tangent.npz',nm);reset=read(reset_folder,'application.npz',rm)
    if not np.array_equal(inputs['raw_pair'],reset['raw_pair']):raise ValueError('same full pair source required')
    H=inputs['Hessian504'];Ht=clock['Hessian_coordinate_time_first'];J=reset['original226_Jacobian'];x=np.r_[np.arange(106),252+np.arange(106)];v=x+106;y=np.r_[np.arange(212,252),np.arange(464,504)]
    static=np.zeros((8,504),complex);static[:,x]=inputs['named_static_radial_frames'][:,:212];static[:,y]=inputs['named_static_radial_frames'][:,212:]
    groups={k:(v if isinstance(v,dict)else dict(indices=v))for k,v in rm['groups'].items()}
    out.mkdir(parents=True);archives={};summaries={}
    def save(name,obj):
        p=out/name;_compressed_npz(p,obj)
        if p.stat().st_size>10*1024**2:raise ValueError('split all original source rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for name,amp in(('normal_basis',1),('area_source',0)):
        old=read(source_folder,name+'_original_trial_and_force.npz',sm);prior=read(source_folder,name+'_canonical_variational_evolution.npz',sm)
        a=read(source_folder,name+'_canonical_embedding.npz',sm);a.update(read(source_folder,name+'_phase_elimination.npz',sm))
        a.update(x_indices=x,v_indices=v,y_indices=y,phase_indices=np.r_[v,y],frames=inputs['named_temporal_frames'],hessian_time_first=Ht,
            source_gradient=old['source_gradient504'],source_gradient_time_first=old['source_gradient_time_first504'])
        B=J[old['kinematic_trace_indices']];Bt=prior['original_trace_Jacobian_time_first'];N=prior['proper_normal_row'];Nt=prior['proper_normal_row_time_first']
        t=secondary_compatible_action_source(H,a,B,Bt,N,Nt,static[:4],normal_amplitude=amp,normal_rate=0,
            trace_source=prior['direct_kinematic_trace_source'],trace_source_rate=prior['direct_kinematic_trace_source_time_first'],
            normal_source=0,normal_source_rate=0)
        e=canonical_variation_evolution(H,a,t);delta=t['original_master_direction'];q=t['canonical_coordinates'];response=J@delta+old['source_original226']
        solve,_=_balanced_solver(a['original_phase_saddle']);actual_rhs=a['canonical_rhs_map']@q+a['source_rhs'];direct=solve(actual_rhs)
        direct_delta=np.zeros(504,complex);direct_delta[x]=q[:212];direct_delta[np.r_[v,y]]=direct[:292]
        ly=H[y]@delta+a['source_gradient'][y];direct_ly=H[y]@direct_delta+a['source_gradient'][y]
        secondary=B[:,x]@delta[v]+Bt@delta+prior['direct_kinematic_trace_source_time_first'];direct_secondary=B[:,x]@direct_delta[v]+Bt@direct_delta+prior['direct_kinematic_trace_source_time_first']
        natural=old['natural_force_indices']
        summaries[name]=dict(primary_original_trace_max=float(np.max(abs(B@delta+prior['direct_kinematic_trace_source']))),
            secondary_original_trace_max=float(np.max(abs(secondary))),
            normal_amplitude=t['normal_amplitude'],normal_rate=t['normal_rate'],
            original_Ly_rows_max=float(np.max(abs(ly))),source_aware_direct_phase_Ly_rows_max=float(np.max(abs(direct_ly))),
            source_aware_direct_secondary_rows_max=float(np.max(abs(direct_secondary))),
            source_aware_phase_minus_basis_norm=float(np.linalg.norm(direct_delta-delta)),
            source_aware_natural_force_change_norm=float(np.linalg.norm((J@(direct_delta-delta))[natural])),
            stored_KKT_rows_max=float(np.max(abs(t['original_rows']))),
            literal_quadratic_stationarity_max=float(np.max(abs(t['true_quadratic_stationarity_rows']))),
            stored_minus_quadratic_stationarity_max=float(np.max(abs(t['stored_operator_minus_quadratic_stationarity']))),
            original_static8_frame_max=float(np.max(abs(static@delta))),
            primary_normal_force=t['normal_primary_force'],normal_secondary_reaction=t['normal_secondary_reaction'],
            original_natural_force_max=float(np.max(abs(response[natural]))),
            canonical_initial_trial_norm=float(np.linalg.norm(q)),original_master_direction_norm=float(np.linalg.norm(delta)),
            canonical_compatibility_time_first_max=float(np.max(abs(e['original_compatibility_time_first']))),
            unforced_momentum_rate_error_max=float(np.max(abs(e['original_momentum_rate_identity']))),
            unforced_Ly_time_first_max=float(np.max(abs(e['original_algebraic_time_first']))),
            unforced_trace_time_first_max=float(np.max(abs(Bt@delta+B@e['original_master_direction_time_first']))),
            balanced_KKT_condition=t['balanced_condition'],original_Gauss_admissibility_guard_passed=False,
            physical_initial_momentum_selected=False)
        save(name+'_secondary_signed_KKT.npz',{k:t[k]for k in('original_KKT','original_rhs','solution','original_rows',
            'primary_constraint_rows','secondary_constraint_rows','primary_constraint_rhs','secondary_constraint_rhs',
            'primary_constraint_residual','secondary_constraint_residual','true_quadratic_stationarity_rows','stored_operator_minus_quadratic_stationarity')})
        save(name+'_original_response.npz',dict(original_master_direction=delta,canonical_initial_coordinates=q,
            original226_response=response,natural_force_indices=natural,source_gradient=a['source_gradient'],source_gradient_time_first=a['source_gradient_time_first'],
            kinematic_trace_indices=old['kinematic_trace_indices'],original_Ly_response=ly,named_Ward_response=reset['Ward_rows']@response,
            full224_Ward_quotient_indices=old['full224_Ward_quotient_indices'],proper_normal_row=N,proper_normal_time_first=Nt,
            primary_trace_rows=B,trace_time_first=Bt,direct_trace_source=prior['direct_kinematic_trace_source'],
            direct_trace_source_time_first=prior['direct_kinematic_trace_source_time_first'],
            direct_source_aware_direction=direct_delta,source_aware_phase_solution=direct,source_aware_phase_rhs=actual_rhs,
            source_aware_original_Ly_response=direct_ly,source_aware_trace_secondary=direct_secondary))
        save(name+'_unforced_canonical_evolution.npz',{k:val for k,val in e.items()if isinstance(val,np.ndarray)})
        print(json.dumps(clean(dict(stage='secondary_compatible_source',case=name,**summaries[name]))),flush=True)
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            try:rel=Path(p).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_reset_secondary_canonical_source.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise ValueError('same secondary source changed')
    result=dict(classification='EVALUATED_PRIMARY_SECONDARY_CANONICAL_COMPUTATIONAL_SOURCE_AND_ABSOLUTE_ADMISSIBILITY_CHECK',
        archives=archives,input_hashes=refs,applications=summaries,action_parameters=rm['action_parameters'],
        computational_normal_function='normal_basis a(t)=1, area_source a(t)=0; a_dot=a_ddot=0 as declared computational test, not physical psi',
        direct_trace_gamma_source_and_time_zero_from_held_trace_equation=True,
        normal_force_readout_not_forced_zero=True,full_original80_Ly_guard_not_replaced_by_small_framed_rows=True,
        physical_gamma_or_first_hit_or_inherited_momentum_selected=False,
        required_next_action='differentiate actual secondary conditions, solve internal trace/normal force reactions and primary compatibility simultaneously using actual Cddot/Nddot/source jets; all original rows must be checked',
        error_scope='binary signed stored-action KKT and actual source-aware phase reconstruction; producer asymmetry, elimination cancellation, prior finite Hdot and physical domain error excluded from any enclosure')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='secondary_canonical_source_complete',result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,default=Path('artifacts/muon_reset_constrained_canonical_variation_20261012/run_2'))
    p.add_argument('--normal-folder',type=Path,default=Path('artifacts/muon_complex_paired_normal_action_20261012/run_1'))
    p.add_argument('--reset-folder',type=Path,default=Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.source_folder,a.normal_folder,a.reset_folder,a.output)
