"""Export literal moving-reference field source before coefficient tests."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_moving_reference_trace_source import moving_reference_profile_source,fixed_radial_coefficient_test_restriction
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve full profile/wall/source images')
    folder=ROOT/'artifacts/muon_complex_paired_normal_action_20261012/run_1'
    b=(folder/'result.json').read_bytes();md=json.loads(b);refs=dict(md['input_hashes'])
    refs[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
    def load(name):
        p=folder/name;b=p.read_bytes();h=sha256(b).hexdigest()
        if h!=md['archives'][name]['sha256']:raise ValueError('same moving-reference source changed '+name)
        refs[p.relative_to(ROOT).as_posix()]=h
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    base=load('same_action_inputs.npz');clock=load('clock_and_joint_tangent.npz')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];rho=np.asarray(rep['rho']);quad=np.asarray(rep['radial_quadrature'])
    raw,ref=base['raw_pair'],base['reference_pair'];a=moving_reference_profile_source(ref,rho)
    coordinates=generic_coordinate_lift(rep['gauge_labels']);dy=np.asarray(coordinates['dynamic_gauge_indices'])
    gb=np.asarray(rep['gauge_basis'])[:,:,0].reshape(len(rho),80,20)
    gr=np.asarray(rep['gauge_radial_basis'])[:,:,0].reshape(len(rho),80,20)
    B=gb[:,dy].transpose(0,2,1).reshape(-1,64)
    restriction=fixed_radial_coefficient_test_restriction(B,quad,a['full_material_field_source'])
    wallmap=rep['wall_trace_map'].reshape(20,80)[:,dy]
    source_coefficients=restriction['represented_source_test_coefficients']
    wall_test_source=wallmap@source_coefficients
    exactwall=a['full_material_wall_source'].reshape(3,20).T
    # Actual same-chart baseline source relation is tested directly before
    # invoking any finite coefficient restriction. Future/radial slots are
    # retained outputs and are not temporal matching/conormal constraints.
    independent=np.empty((3,len(rho),20),complex)
    jump=raw[1,100:180]-raw[0,100:180];ratejump=raw[1,180:260]-raw[0,180:260]
    independent[0]=np.einsum('rjc,j->rc',gb[:,dy],jump[dy])
    independent[1]=np.einsum('rjc,j->rc',gb[:,dy],ratejump[dy])
    independent[2]=np.einsum('rjc,j->rc',gr[:,dy],jump[dy])
    reference_image=np.zeros((3,len(rho),5,4),complex)
    reference_image[:,:,2:]=a['reference_difference'].T[:,:,None,None]*M[None,None]
    baseline=independent-reference_image.reshape(3,len(rho),20)
    baseline_wall=wallmap@jump[dy]
    reference_wall=np.r_[np.zeros(8),M.reshape(-1)*a['wall_reference_difference'][0]]
    wp=next(Path(p)for p in refs if p.endswith('true_phase_projection_inputs.npz'))
    if sha256((ROOT/wp).read_bytes()).hexdigest()!=refs[wp.as_posix()]:raise ValueError('source finite-difference weights changed')
    with np.load(ROOT/wp,allow_pickle=False)as z:weights=z['state_weights']
    magnitude=float(np.max(abs(np.tile(np.r_[weights,np.ones(170)],2)*a['reference_affine_raw_rate'].reshape(-1))))
    controls={};fd_arrays={}
    for label,h in(('primary',2e-5),('half_step',1e-5)):
        direction=a['reference_affine_raw_rate']/magnitude
        plus=moving_reference_profile_source(ref+h*direction,rho);minus=moving_reference_profile_source(ref-h*direction,rho)
        fd=magnitude*(-plus['reference_difference']+minus['reference_difference'])/(2*h)
        fw=magnitude*(-plus['wall_reference_difference']+minus['wall_reference_difference'])/(2*h)
        fd_arrays[label+'_profile_source_FD']=fd;fd_arrays[label+'_wall_source_FD']=fw
        controls[label]=dict(normalized_step=h,coordinate_clock_step=h/magnitude,
            profile_max_error=float(np.max(abs(fd-a['child_source_first']))),
            profile_relative_error=float(np.linalg.norm(fd-a['child_source_first'])/np.linalg.norm(a['child_source_first'])),
            wall_max_error=float(np.max(abs(fw-a['wall_child_source_first']))))
    rp=ROOT/'artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1/result.json'
    rb=rp.read_bytes();refs[rp.relative_to(ROOT).as_posix()]=sha256(rb).hexdigest();rm=json.loads(rb)
    gaugeids=np.asarray(rm['groups']['gauge_trace']);Hids=np.asarray(rm['groups']['Higgs_trace'])
    theta_clock=np.r_[-clock['gradient_clock_first'][106:212],-clock['gradient_clock_first'][358:464]]
    arrays=dict(raw_pair=raw,reference_pair=ref,radial_points=rho,radial_quadrature=quad,
        dynamic_gauge_indices=dy,dynamic_gauge_value_map=B,actual_dynamic_wall_trace_map=wallmap,
        original_gauge_trace_indices=gaugeids,original_Higgs_trace_indices=Hids,
        original_fixed_offset_gauge_R_s=np.zeros(64,complex),held_independent_Higgs_trace_R_s=np.zeros(4,complex),
        represented_gauge_test_R_s=source_coefficients[:,0],
        exact_wall_source=exactwall,represented_wall_test_source=wall_test_source,
        wall_source_not_recovered_by_test_restriction=exactwall-wall_test_source,
        baseline_independent_dynamic_profile_jump=independent,baseline_reference_profile_image=reference_image,
        baseline_fullpoint_dynamic_trace=baseline,baseline_wall_dynamic_trace=baseline_wall-reference_wall,
        exact_action_gradient_reference_clock=clock['gradient_clock_first'],
        exact_temporal_face_dual_reference_clock=theta_clock,
        **{k:v for k,v in a.items()if isinstance(v,np.ndarray)},
        **{k:v for k,v in restriction.items()if isinstance(v,np.ndarray)},**fd_arrays)
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            try:rel=Path(p).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_moving_reference_trace_source.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise ValueError('actual profile source input changed')
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,arrays)
    if p.stat().st_size>10*1024**2:raise ValueError('split complete moving source image')
    maximum=lambda x:float(np.max(abs(x)))
    data=dict(classification='EVALUATED_FULL_MOVING_REFERENCE_PROFILE_AND_ORIGINAL_FIELD_TRACE_SOURCE_TESTS',
        archives={'application.npz':dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},input_hashes=refs,
        action_parameters=md['action_parameters'],slot_order=['value','Eulerian time','radial'],
        radial_source_reproduction_max=maximum(a['child_source_first']-clock['effective_connection_clock_first']),
        wall_source_reproduction_max=maximum(a['wall_child_source_first']-clock['effective_wall_connection_clock_first']),
        profile_source_norm=float(np.linalg.norm(a['child_source_first'])),
        full_field_source_norms_by_slot=np.linalg.norm(a['full_material_field_source'].reshape(3,-1),axis=1).tolist(),
        exact_wall_source_norms_by_slot=np.linalg.norm(exactwall,axis=0).tolist(),
        represented_gauge_test_source_norms=np.linalg.norm(source_coefficients,axis=0).tolist(),
        weighted_full_source_norms=restriction['weighted_source_norms'].tolist(),
        weighted_complement_norms=restriction['weighted_complement_norms'].tolist(),
        unweighted_complement_norms=np.linalg.norm(restriction['full_source_image_complement'],axis=0).tolist(),
        exact_wall_minus_test_wall_norms=np.linalg.norm(exactwall-wall_test_source,axis=0).tolist(),
        coefficient_test_identity_defect_max=maximum(restriction['test_map_identity_defect']),
        weighted_test_complement_max=maximum(restriction['weighted_test_complement']),
        finite_coefficient_test_condition=restriction['coefficient_test_condition'],
        baseline_fullpoint_dynamic_value_trace_norm=float(np.linalg.norm(baseline[0])),
        baseline_wall_dynamic_value_trace_norm=float(np.linalg.norm(baseline_wall-reference_wall)),
        existing_original_gauge_coefficient_rows_max=maximum(base['original226_reset_rows'][gaugeids]),
        reference_clock_normalization=magnitude,literal_source_FD_controls=controls,
        source_law='at fixed actual pp and independent fields: d(pp-rp+rc)=-d(rp)+d(rc); actual parent motion excluded',
        existing_coefficient_reset_scope='literal frozen affine coefficient offset has partial_clock0; it is not the complete moving fullpoint trace source',
        represented_R_s_scope='old64 coefficient tests applied via their explicit real fixed-basis quadrature dual; full image/complement and exact wall source retained, no exact fullpoint closure claimed',
        direct_Higgs_value_source_scope='H held independently; no bundle/event-map variation selected. Higgs action/current response remains in saved full clock gradient and subsequent coupled inverse.',
        temporal_dual_reference_clock_scope='theta=2Pi_own_parent-Pi_graph; ownparent explicit_reference_clock0; both graph Pi clock derivatives retained',
        future_rate_and_radial_images_are_outputs_not_temporal_matching_constraints=True,
        comparison_quad_not_physical_action_or_resistance=True,source_coefficients_conjugated=False,
        exact_wall_not_replaced_by_projected_wall=True,physical_event_clock_or_mode_or_Bi_Bf_or_Pauli_selected=False,
        error_scope='binary analytic profile first jets and finite real-basis tests plus literal two-step FD controls; complement is retained, no physical matching or outward enclosure inferred')
    p=out/'result.json';p.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),source_norms=data['full_field_source_norms_by_slot'],
        complement_norms=data['weighted_complement_norms'],wall_test_difference=data['exact_wall_minus_test_wall_norms'],
        source_reproduction=[data['radial_source_reproduction_max'],data['wall_source_reproduction_max']],controls=controls),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);materialize(p.parse_args().output)
