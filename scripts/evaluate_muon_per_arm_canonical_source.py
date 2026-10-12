"""Execute actual own-parent and inherited-child source canonical admission."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_per_arm_canonical_source import per_arm_source_reconstitution,arm_variational_midpoint_map
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def clean(x):
    if isinstance(x,dict):return{k:clean(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return[clean(v)for v in x]
    if isinstance(x,(complex,np.complexfloating)):return[float(x.real),float(x.imag)]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,np.generic):return x.item()
    return x


def materialize(trace_folder,source_folder,normal_folder,step_folder,output,tolerance):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve source-aware per-arm admission results')
    refs={}
    def receipt(folder):
        p=ROOT/folder/'result.json';b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest();return json.loads(b)
    def archive(folder,md,name):
        p=ROOT/folder/name;b=p.read_bytes();h=sha256(b).hexdigest()
        if h!=md['archives'][name]['sha256']:raise ValueError('same actual canonical source changed')
        refs[p.relative_to(ROOT).as_posix()]=h
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    tm,sm,nm,hm=[receipt(p)for p in(trace_folder,source_folder,normal_folder,step_folder)]
    for md in(tm,sm,nm):refs.update(md['input_hashes'])
    trace=archive(trace_folder,tm,'application.npz');normal=archive(normal_folder,nm,'same_action_inputs.npz')
    if not np.array_equal(trace['raw_pair'],normal['raw_pair'])or not np.array_equal(trace['reference_pair'],normal['reference_pair']):raise ValueError('same final candidate parent/reference required')
    H=trace['full_joint_Hessian'];Hp=trace['parent_standalone_Hessian'];Fp=trace['arm_0_named_frame_covectors'];Fc=trace['arm_1_named_frame_covectors']
    h=complex(*hm['step_coordinate_time']);records={};archives={};out.mkdir(parents=True)
    def save(name,obj):
        p=out/name;_compressed_npz(p,{k:v for k,v in obj.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>10*1024**2:raise ValueError('split every original phase/source application')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for case in('normal_basis','area_source'):
        original=archive(source_folder,sm,case+'_original_trial_and_force.npz');d=original['original_master_direction'];g=original['source_gradient504']
        own=np.zeros(252,complex)if case=='normal_basis'else normal['area_gradient504'][:252]
        a=per_arm_source_reconstitution(Hp,H,d,g,Fp,Fc,standalone_parent_source=own)
        delta=a['reconstituted_joint_direction'];effect=delta-d
        natural=original['natural_force_indices'];J_source=normal['master_lift'];face_first=trace['joint_temporal_face_dual_first']
        rec=dict(parent_original146_max=float(np.max(abs(a['parent']['original_phase_rows']))),
            parent_standalone_Ly_max=float(np.max(abs(a['parent']['Gauss_rows']))),
            child_original146_max=float(np.max(abs(a['child']['original_phase_rows']))),
            child_Ly_max=float(np.max(abs(a['child']['Gauss_rows']))),
            parent_framed_rows_max=float(np.max(abs(a['parent']['framed_rows']))),child_framed_rows_max=float(np.max(abs(a['child']['framed_rows']))),
            full_joint_Gauss_max=float(np.max(abs(a['original_joint_Gauss_rows']))),
            own_minus_joint_parent_Pi_target_norm=float(np.linalg.norm(a['parent_own_momentum_target']-a['parent_joint_momentum_same_trial'])),
            parent_direction_change_norm=float(np.linalg.norm(a['parent']['direction']-d[:252])),
            child_direction_change_norm=float(np.linalg.norm(a['child']['direction']-d[252:])),
            inherited_child_source_change_norm=float(np.linalg.norm(a['child_inherited_source_change'])),
            temporal_face_dual_change_norm=float(np.linalg.norm(face_first@effect)),
            supplied_parent_normal_pairing=normal['parent_proper_and_attachment_trace'][-1]@delta[:106],
            supplied_child_normal_pairing=normal['child_proper_and_attachment_trace'][-1]@delta[252:358],
            parent_frame_reactions=a['parent']['frame_reactions'],child_frame_reactions=a['child']['frame_reactions'],
            parent_own_target_preserved=True,child_original_total_target_preserved=True,
            standalone_parent_source_scope='zero computational normal source'if case=='normal_basis'else'own parent area coefficient, independent of graph inherited/ref-clock source',
            body_source_feedback_count=1,coefficient_germ_propagation={})
        save(case+'_parent_original146.npz',a['parent']);save(case+'_child_original146.npz',a['child'])
        save(case+'_coupled_source_effects.npz',dict(input_direction=d,reconstituted_direction=delta,source=g,standalone_parent_source=own,
            original_joint_Gauss=a['original_joint_Gauss_rows'],parent_own_Pi=a['parent_own_momentum_target'],parent_joint_Pi_control=a['parent_joint_momentum_same_trial'],
            child_total_Pi=a['child_original_total_momentum_target'],child_inherited_source=a['child_inherited_source'],
            child_inherited_source_change=a['child_inherited_source_change'],temporal_face_dual_change=face_first@effect,
            original_source_kinematic_traces=original['kinematic_trace_indices'],natural_force_indices=natural))
        admitted=rec['parent_original146_max']<=tolerance and rec['child_original146_max']<=tolerance
        rec['all_original_initial_rows_admitted']=admitted
        if admitted:
            parent=arm_variational_midpoint_map(Hp,-h,a['parent']['delta_x'],a['parent']['canonical_momentum_target'],own,Fp,
                phase_frame_value=Fp@a['parent']['direction'][106:],normal_covector=normal['parent_proper_and_attachment_trace'][-1])
            # The parent midpoint here is a backward outer-face control.
            # Child source uses the reconstituted parent birth direction,
            # rather than grafting that different-time control as its source.
            child=arm_variational_midpoint_map(H[252:,252:],h,a['child']['delta_x'],a['child']['canonical_momentum_target'],a['child']['source_gradient'],Fc,
                phase_frame_value=Fc@a['child']['direction'][106:],normal_covector=normal['child_proper_and_attachment_trace'][-1])
            for side,b in(('parent',parent),('child',child)):
                save(case+'_'+side+'_original358_coefficient_germ.npz',b)
                rec['coefficient_germ_propagation'][side]=dict(original358_rows_max=float(np.max(abs(b['original358_rows']))),
                    literal_transpose_rows_max=float(np.max(abs(b['literal_transpose_rows']))),pairing_difference=b['transpose_pairing']-b['test_pairing'],
                    initial_action_dual_error_max=float(np.max(abs(b['initial_action_dual']+a[side]['canonical_momentum_target']))),
                    final_action_dual_error_max=float(np.max(abs(b['final_action_dual']-b['Pi_final']))),
                    final_normal_pairing=b['test_pairing'],actual_changing_background_step_not_executed=True)
        else:rec['coefficient_germ_not_launched_reason']='one or more absolute original phase admission rows exceed unchanged tolerance; no physical missing-datum inference'
        records[case]=rec;print(json.dumps(clean(dict(stage='per_arm_canonical_source_admission',case=case,**rec))),flush=True)
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            try:rel=Path(p).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_per_arm_canonical_source.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=q for p,q in refs.items()):raise ValueError('same source-aware admission inputs changed')
    result=dict(classification='EVALUATED_SAME_FINAL_CANDIDATE_PER_ARM_CANONICAL_SOURCE_ADMISSION_AND_GUARDED_GERM_MAP',
        archives=archives,input_hashes=refs,applications=records,action_parameters=tm['action_parameters'],tolerance=tolerance,
        incoming_parent_own_Pi_not_joint_Pi=True,full_inherited_child_source_applied_once=True,
        original146_rows_and_Gauss_absolute_guard_retained=True,
        original_reset73_are_temporal_endpoint_rows_not_bulk_constraints=True,
        no_persistent_reset_trace_reaction_or_secondary_selector=True,
        numerical_step_control=[h.real,h.imag],old_step_used_only_as_computational_germ_map_control_not_background_graft=True,
        prescribed_normal_is_computational_source_not_physical_psi=True,
        changing_background_endpoint_clock_or_first_hit_not_selected=True,
        error_scope='binary signed same-final-candidate per-arm source/transpose solves, admission absolute rows and natural face pairing effects retained; no matrix/evaluation/physical domain enclosure')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='per_arm_canonical_source_complete',result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--trace-folder',type=Path,default=Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1'))
    p.add_argument('--source-folder',type=Path,default=Path('artifacts/muon_reset_constrained_canonical_variation_20261012/run_2'))
    p.add_argument('--normal-folder',type=Path,default=Path('artifacts/muon_complex_paired_normal_action_20261012/run_1'))
    p.add_argument('--step-folder',type=Path,default=Path('artifacts/muon_precise_complex_canonical_exterior_step_20261012/run_1'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--tolerance',type=float,default=2e-10)
    a=p.parse_args();materialize(a.trace_folder,a.source_folder,a.normal_folder,a.step_folder,a.output,a.tolerance)
