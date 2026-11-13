"""One actual causal B point, complete n3→n2/n4 named wall/H test actions."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_n1_magnetic_action import original_signed_stage,original_named_wall_lift
from bhsm.interface.muon_holomorphic_n3_magnetic_return import source_n3_return_angular_images,projected_magnetic_return_action
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source_folder,output):
    src=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve each actual n3 action execution')
    pins={};archives={}
    def read(p,expected=None):
        p=ROOT/p if not p.is_absolute()else p
        if not p.is_relative_to(ROOT):raise ValueError('same checkout input required')
        data=p.read_bytes();digest=sha256(data).hexdigest();pins[p.relative_to(ROOT).as_posix()]=digest
        if expected is not None and digest!=expected:raise ValueError('frozen actual source bytes changed')
        if p.suffix=='.json':return json.loads(data)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    md=read(src/'result.json');side=md['side'];case=md['case']
    if side!='outgoing' or case!='normal_basis':raise ValueError('this reached application is the outgoing normal causal point')
    points=read(src/'actual_zero_Cauchy_magnetic_source_points.npz',md['archives']['actual_zero_Cauchy_magnetic_source_points.npz']['sha256'])
    hit=np.flatnonzero(abs(points['sigma']-.75)<1e-14)
    if len(hit)!=1:raise ValueError('the actual canonical source point sigma=.75 is required')
    i=int(hit[0]);cell=int(points['cell'][i]);order=np.asarray(md['finite_causal_prefix_original_stage_order'],int)
    original_stage=int(order[cell]);name=md['stages'][original_stage]['source_archive']
    raw_folder=Path(md['source_folder']);background=read(ROOT/raw_folder/'result.json')
    a=read(ROOT/raw_folder/name,background['archives'][name]['sha256'])
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation']
    directions=lambda key:np.stack((a[key+'_high'],a[key+'_low']),axis=-1)
    binding=original_signed_stage(a['stage_raw'],directions('stage_raw_direction'),a['parent_source_stage_raw'],
        directions('parent_source_stage_raw_direction'),a['reference_stage_pair'],directions('reference_stage_direction'),rep,
        side='child',lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=background['action_parameters']['nu_squared_action'])
    T=np.c_[original_named_wall_lift(rep,binding['value_permutation']),np.eye(84)[:,80:84]]
    named_defect=float(np.max(abs(np.r_[binding['lifts']['W'],binding['lifts']['hv']]@T-np.eye(24))))
    angular=source_n3_return_angular_images();E=angular['derivatives'];f=points['total_field'][i];ft=points['total_coordinate_rate'][i]
    for n,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if n.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    for rel in (Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_holomorphic_n3_magnetic_return.py',
                'tests/test_muon_holomorphic_n1_magnetic_operands.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,obj):
        p=out/name;_compressed_npz(p,obj)
        if p.stat().st_size>=10*1024**2:raise ValueError('split each explicit operator action below10MiB')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('actual_causal_B_and_named_tests.npz',dict(total_field=f,total_coordinate_rate=ft,test_lift=T,
        source_raw=a['stage_raw'],parent_source_stage_raw=a['parent_source_stage_raw'],reference_stage_pair=a['reference_stage_pair'],
        sigma=points['sigma'][i],coordinate_time=a['coordinate_time'],value_permutation=binding['value_permutation'],
        source_H=binding['lifts']['hv']@f.reshape(84,12),source_Hdot=binding['lifts']['hv']@ft.reshape(84,12)))
    records=[];summary={}
    for degree in (2,4):
        G=angular['gaunts'][degree]
        z=projected_magnetic_return_action(binding,f,ft,T,E[degree],E[3],E[1],G)
        reverse=projected_magnetic_return_action(binding,f,ft,T,E[3],E[degree],E[1],G.transpose(1,0,2))
        rec=dict(return_degree=degree,starting_degree=3,source_degree=1,named_action_shape=list(z['delta_K'].shape),
            placement_norms={},literal_reverse_max_defects={},literal_reverse_relative_defects={})
        for key,other in (('K','K'),('B_forward','B_reverse'),('B_reverse','B_forward'),('M','M')):
            delta=z['delta_'+key];defect=reverse['delta_'+other]-delta.transpose(0,2,1)
            maximum=float(np.max(abs(defect)));scale=float(np.max(abs(delta)))
            rec['placement_norms'][key]=float(np.linalg.norm(delta));rec['literal_reverse_max_defects'][key]=maximum
            rec['literal_reverse_relative_defects'][key]=maximum/max(scale,np.finfo(float).tiny)
            if maximum>3e-12*max(scale,1.):raise ArithmeticError('independent source-side transpose relation failed')
            for axis in range(3):
                fields={k:v[axis]for k,v in z.items()if k in('delta_'+key,'Maxwell_left_'+key,'Maxwell_right_'+key,'intrinsic_'+key)}
                if key=='K':fields['Maxwell_curvature_contact']=z['Maxwell_curvature_contact'][axis]
                save(f'n3_to_n{degree}_axis_{axis}_{key}_action.npz',fields)
            summary[f'n{degree}_{key}_axis_norms']=np.linalg.norm(delta,axis=(1,2))
        save(f'n3_to_n{degree}_angular_maps.npz',dict(gaunt=G,target_derivatives=E[degree],trial_derivatives=E[3],
            source_derivatives=E[1],target_labels=angular['labels'][degree],trial_labels=angular['labels'][3]))
        records.append(rec);print(json.dumps(rec,sort_keys=True),flush=True)
    save('complete_return_actions_summary.npz',summary)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=v for p,v in pins.items()):raise ValueError('producer or input bytes changed')
    result=dict(classification='EVALUATED_ACTUAL_CAUSAL_B_N3_TO_N2_N4_NAMED_WALL_H_TEST_OPERATOR_ACTION',
        input_hashes=pins,archives=archives,source_folder=source_folder.as_posix(),side=side,case=case,
        causal_point_index=i,source_sigma=float(points['sigma'][i]),source_cell=cell,original_stage=original_stage,
        source_value_norm=float(np.linalg.norm(f)),source_coordinate_rate_norm=float(np.linalg.norm(ft)),
        source_unbordered_Euler_rows_max=float(np.max(abs(points['original_unbordered_Euler_rows'][i]))),
        source_reconstructed_rows_max=float(np.max(abs(points['original_reconstructed_rows'][i]))),
        source_uncancelled_row_scale_max=float(np.max(points['original_row_uncancelled_scale'][i])),
        source_residuals_are_not_a_physical_or_operator_error_bound=True,return_actions=records,
        named_original_wall_and_H_test_image_defect=named_defect,
        test_lift_provenance='twenty original labelled wall_lift radial3 gauge coordinates plus four original natural Higgs coordinates',
        complete_n3_times_n1_image_residual=angular['complete_n3_times_n1_image_residual'],
        complete_n3_source_return_degrees=[2,4],source_only_derivative_orientation_adapter=True,
        total_original84_times_n1_source_with_induced_H_Hdot_At_radial_germs_retained=True,
        source_contains_eR4_squared_half_once=True,coefficient_source_or_dual_conjugated=False,
        independent_literal_reverse_angular_placements_evaluated=True,
        full84_n3_n4_inverse_or_native_starting_loop_complement_evaluated=False,
        same_stage_physical_current_or_adjoint_directions_selected=False,
        named_test_coordinate_actions_are_not_a_selected_Green_or_Pauli_covector=True,
        old_positive_reference_or_old_magnetic_background_consumed=False,
        whole_stage_geometry_coframe_first_derivative_scope='this D3 field direction holds supplied stage geometry; Validation quadratic companion separately executes full stage coefficient derivative and both causal response slots',
        next_physical_matching_relation='action-selected Gamma2=Bi+Bf U; Gamma2(Epole)R=0, L Gamma2(Epole)=0, Z=L Gamma2_E R, H_B=-Z^-1 L Gamma2_B R; named operator actions do not select these exterior/state maps',
        physical_Bi_Bf_pole_spin_LSZ_native_loop_or_Pauli_selected=False,physical_a_mu=None,physical_g_mu=None)
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),archives=len(archives))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.source_folder,a.output)
