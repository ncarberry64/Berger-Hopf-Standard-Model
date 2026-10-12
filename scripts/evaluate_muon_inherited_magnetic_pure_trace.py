"""Actual source-on pure U_B operand before physical exterior maps are selected."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_n1_magnetic_action import original_signed_stage
from bhsm.interface.muon_inherited_magnetic_pure_trace import bind_inherited_magnetic_trace_points,pure_unsquared_magnetic_trace_jets
from bhsm.interface.muon_holomorphic_current_source import two_term_complex_sum
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source_folder,output):
    src=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve actual pure transfer application')
    pins={};archives={}
    def read(p,expected=None):
        p=ROOT/p if not p.is_absolute()else p
        if not p.is_relative_to(ROOT):raise ValueError('same checkout source required')
        raw=p.read_bytes();digest=sha256(raw).hexdigest();pins[p.relative_to(ROOT).as_posix()]=digest
        if expected is not None and digest!=expected:raise ValueError('actual source archive bytes changed')
        if p.suffix=='.json':return json.loads(raw)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    md=read(src/'result.json')
    if not md['actual_parent_birth_action_reconstituted_at_preserved_free_q_Pi']:raise ValueError('same born source-on state required')
    endpoint_folder=ROOT/'artifacts/muon_corrected_birth_source_endpoint_20261012/run_1'
    endpoint_md=read(endpoint_folder/'result.json');endpoint_name='same_birth_full302_and_original226.npz'
    endpoint_rows=read(endpoint_folder/endpoint_name,endpoint_md['archives'][endpoint_name]['sha256'])['fresh_original226_rows']
    remaining_row=endpoint_rows[223]
    stagefolder=ROOT/'artifacts/muon_changing_canonical_source_20261012/run_3';sm=read(stagefolder/'result.json')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation'];prepared=[]
    for case in('normal_basis','area_source'):
        pn=case+'_inherited_on_source_points.npz';points=read(src/pn,md['archives'][pn]['sha256'])
        cn=case+'_inherited_on_source_unsquared_current.npz';current=read(src/cn,md['archives'][cn]['sha256'])
        bindings=[];steps=[];provenance=[]
        for j in range(2):
            name=f'outgoing_{j:04d}_{case}_source_response.npz';a=read(stagefolder/name,sm['archives'][name]['sha256'])
            first=lambda key:np.stack((a[key+'_high'],a[key+'_low']),axis=-1)
            bindings.append(original_signed_stage(a['stage_raw'],first('stage_raw_direction'),a['parent_source_stage_raw'],
                first('parent_source_stage_raw_direction'),a['reference_stage_pair'],first('reference_stage_direction'),rep,
                side='child',lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=sm['action_parameters']['nu_squared_action']))
            steps.append(a['coordinate_time_step'].item());provenance.append(name)
        prepared.append((case,points,current,bindings,np.array(steps),provenance))
    for n,m in sorted(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if n.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_inherited_magnetic_pure_trace.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True);records={}
    def save(name,data):
        p=out/name;_compressed_npz(p,{n:v for n,v in data.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split compact actual operands below10MiB')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def summary(x):return dict(norm=float(np.linalg.norm(x)),maximum=float(np.max(abs(x))))
    for case,points,current,bindings,steps,provenance in prepared:
        bound=bind_inherited_magnetic_trace_points(bindings,points)
        xi_defect=float(np.max(abs(bound['actual_Xi']-current['actual_Xi_n0_n1'])))
        xi_scale=float(np.max(abs(current['actual_Xi_n0_n1'])))
        if xi_defect>3e-13*max(xi_scale,1.):raise ValueError('pure trace source is not the same actual magnetic Xi')
        value=pure_unsquared_magnetic_trace_jets(bound['generators'],bound['generator_first'],steps,bound)
        for name in('full_unsquared_transfer','magnetic_transfer'):
            hi,lo=two_term_complex_sum(value[name+'_first'][0],value[name+'_first'][1])
            value[name+'_first_combined_high']=hi;value[name+'_first_combined_low']=lo
        save(case+'_actual_trace_source_and_stage_generators.npz',bound)
        save(case+'_pure_U_B_and_all_source_first_slots.npz',value)
        records[case]=dict(actual_stage_provenance=provenance,coordinate_steps=[[float(v.real),float(v.imag)]for v in steps],
            source_points=len(points['cell']),rebuilt_Xi_minus_actual_current_Xi_max=xi_defect,
            rebuilt_Xi_scale=xi_scale,pure_magnetic_transfer=summary(value['magnetic_transfer']),
            source_first_high_low=[summary(v)for v in value['magnetic_transfer_first']],
            source_first_slots={n:summary(value['magnetic_transfer_first_'+n])for n in('left_propagator','insertion','right_propagator')},
            literal_transpose_identity=summary(value['literal_transpose_identity_defect']),
            current_bilinear_norm_for_distinction=md['applications'][case]['current_terms']['total'],
            upstream_free_domain_row_max=md['applications'][case]['free_domain_and_constraint_dual_range_max'],
            upstream_canonical_propagation_rows_max=md['applications'][case]['original_propagated_rows_max'])
        print(json.dumps(dict(case=case,**records[case]),sort_keys=True),flush=True)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual source/stage bytes changed')
    result=dict(classification='EVALUATED_INHERITED_SOURCE_ON_UNSQUARED_PURE_MAGNETIC_TRANSFER_OPERAND',
        input_hashes=pins,archives=archives,source_folder=source_folder.as_posix(),applications=records,
        pure_trace_definition='U_B=integral U(f,t)(-i N Xi_B)U(t,i) dt on A=(iN)^-1 d_t+H',
        source_first_definition='left propagator response + d(-i N Xi_B) insertion + right propagator response; high/low acted separately',
        current_J_transpose_inverse_J_not_used_as_transfer=True,
        all18_three_family_neutral_fibers_retained=True,source_spinor_test_degrees=[0,1],
        n1_input_n2_output_angular_source_image_not_evaluated=True,
        original_time_orientation='positive outgoing inherited child finite prefix with actual source ON at birth',
        coordinate_step_point_quadrature_and_energy_anchor_held=True,continued_external_energy_anchor=0.,
        no_source_qdot_restart_old_child_zero_or_positive_reference_operator_graft=True,
        body_source_fields_vertices_and_N_motion_rebuilt_from_same_actual_changing_stage=True,
        physical_Gamma_B_relation='Gamma2_B=Bi_B+Bf_B U+Bf U_B; this application supplies U and U_B, not action-selected Bi/Bf or their jets',
        physical_pole_relation='Gamma2(Epole)R=0, L Gamma2(Epole)=0; Z=L Gamma2_E R; H_B=-Z^-1 L Gamma2_B R',
        remaining_coupled_action_relation='original full226 formation/energy/tension/exterior source matching; finite free field-sector closure does not solve this separately evaluated birth candidate',
        remaining_full226_attachment_row_index=223,remaining_full226_attachment_row_complex=[float(remaining_row.real),float(remaining_row.imag)],
        remaining_full226_attachment_row_absolute=float(abs(remaining_row)),remaining_original226_reset_guard=endpoint_md['reset_tolerance'],
        physical_pole_residue_charge_native_loop_or_Pauli_selected=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary unsquared n0+n1 test transfer on fixed two-stage action and supplied20-point quadrature; no physical domain, external pole, higher angular image or anomaly error enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),archives=len(archives))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.source_folder,a.output)
