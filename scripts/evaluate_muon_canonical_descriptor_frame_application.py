"""Apply the same-action frame/Schur source image to a reference CONTROL."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_canonical_descriptor_frame_application import canonical_reference_schur_application
from bhsm.interface.muon_material_rate_canonical_reduction import fixed_position_material_rate_chart
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(endpoint,reference_archive,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every reference-image control')
    refs={}
    def read(p):
        p=ROOT/p;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(endpoint/'result.json');refs.update(md['input_hashes']);data=read(endpoint/'application.npz')
    if refs[(endpoint/'application.npz').as_posix()]!=md['archives']['application.npz']['sha256']:
        raise ValueError('same canonical endpoint changed')
    if not md['compatible_endpoint']:raise ValueError('actual compatible endpoint required')
    old=read(reference_archive);reference=old['branch_reference']
    if reference.shape!=(61,):raise ValueError('literal old geometry(v37,m24) reference only')
    chart=fixed_position_material_rate_chart(data['raw_fields'][:100])
    T,Ti=chart['velocity_algebraic_lift'],chart['velocity_algebraic_inverse']
    D=data['action_Hessian'][106:,106:];C=data['named_frame_covectors'];Z=data['literal_gauge_generators']
    geometry=np.r_[np.arange(37),np.arange(106,130)]
    a=canonical_reference_schur_application(T.T@D@T,C@T,Ti@Z,geometry,reference)
    raw_direction=T@a['reference_control_full_direction']
    raw_source=Ti.T@a['reference_control_full_source'];rho=a['named_source_frame_reaction']
    raw_rows=D@raw_direction-raw_source-C.T@rho
    source_compatibility=Z.T@raw_source
    primitive_direction=T@a['section'][:,:61]@a['supplied_reference']
    primitive_image=D@primitive_direction
    arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
    arrays.update(original_Dirac_Hessian=D,material_lift=T,material_inverse=Ti,
        original_named_frame_covectors=C,original_literal_gauge_generators=Z,
        original_reference_control_direction=raw_direction,original_source=raw_source,
        original_full_source_rows=raw_rows,original_source_gauge_compatibility=source_compatibility,
        original_historical_reference_direction=primitive_direction,original_historical_reference_action_image=primitive_image,
        original_endpoint_raw_fields=data['raw_fields'],original_endpoint_master=data['coefficients'],
        original_endpoint_canonical_Pi=data['canonical_momentum_target'],coordinate_time=data['coordinate_time'],
        reference_control_eigenvalue=np.array(a['reference_control_eigenvalue']))
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_canonical_descriptor_frame_application.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same action/reference source changed')
    c=lambda z:[complex(z).real,complex(z).imag]
    result=dict(classification='CONTROL_ONLY_ACTUAL_COUPLED_CANONICAL_FRAME_AND_REFERENCE_SOURCE_APPLICATION',
        input_hashes=refs,archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        geometry_reference_labels='old v37,m24 labels embedded at fixed material normal rate; original delta normalrate=s*ell.deltaqdot',
        field_and_normal_internal_dimension=83,named_frame_section_dimension=144,
        named_frame_kernel_defect_max=float(np.max(abs(a['named_frame_kernel_defect']))),
        literal_generator_image_max=float(np.max(abs(a['original_generator_image']))),
        primitive_reference_full_image_norm=float(np.linalg.norm(a['primitive_reference_full_image'])),
        primitive_reference_internal_source_norm=float(np.linalg.norm(a['primitive_reference_internal_source'])),
        internal_reference_response_norm=float(np.linalg.norm(a['internal_response_to_reference'])),
        reduced_reference_image_norm=float(np.linalg.norm(a['reduced_reference_image'])),
        internal_linear_rows_max=float(np.max(abs(a['internal_linear_rows']))),
        internal_balanced_condition_number=a['internal_balanced_condition_number'],
        internal_raw_condition_number=a['internal_raw_condition_number'],
        internal_smallest_singular_value=float(a['internal_singular_values'][-1]),
        internal_zero_eigenvalue_distance=a['internal_zero_eigenvalue_distance'],
        internal_invertibility_is_numerical_not_verified=True,
        full_kernel_equivalence_excludes_a_zero_of_internal83=True,
        original_historical_reference_action_image_norm=float(np.linalg.norm(primitive_image)),
        reference_control_eigenvalue=c(a['reference_control_eigenvalue']),reference_control_overlap=float(a['reference_control_overlap']),
        reference_control_gap=a['reference_gap'],original_source_rows_max=float(np.max(abs(raw_rows))),
        named_source_reaction_max=float(np.max(abs(rho))),gauge_source_compatibility_max=float(np.max(abs(source_compatibility))),
        input_MP_compatible_rows_max=md['original_rows_max'],input_binary_rows_max=md['binary_original_rows_max'],
        original_action_measure_and_connection_contacts_retained=True,
        historical_eigenvalue_or_duration_transplanted=False,arbitrary_cross_block_homotopy_used=False,
        source_dual_is_analytic_transpose=True,Hilbert_or_physical_normal_Gram_assigned=False,
        physical_stop_formation_or_pole_selected=False,
        actual_zero_equation='D_original psi - C_original.T reaction =0, C_original psi=0; equivalent Schur zero only if internal83 invertible',
        remaining_binding='continue an action-owned selected line on the actual constrained full background/domain and verify simple oriented first hit; the old reference overlap alone does not identify it',
        error_scope='binary64 actual action frame/Schur/reference-source calculation with all induced fields and reactions, not a physical reference selector or outward continuum/Pauli enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:result[k]for k in('classification','primitive_reference_internal_source_norm','internal_reference_response_norm','reference_control_eigenvalue','reference_control_overlap','original_source_rows_max','gauge_source_compatibility_max')},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--endpoint',type=Path,default=Path('artifacts/muon_complex_canonical_endpoint_20261012/continued_run_1'))
    p.add_argument('--reference-archive',type=Path,default=Path('artifacts/flagship_integration/BHSM_N12_C2_LOHNER_STEP_1222.npz'))
    p.add_argument('--output',type=Path,required=True);args=p.parse_args();materialize(args.endpoint,args.reference_archive,args.output)
