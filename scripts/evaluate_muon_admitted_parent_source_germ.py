"""Execute the independently admitted parent-area source358/transpose component."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_per_arm_canonical_source import arm_variational_midpoint_map
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve admitted component')
    refs={}
    def read(folder,name,md=None):
        p=ROOT/folder/name;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if name.endswith('.json'):return json.loads(b)
        if md is None or refs[p.relative_to(ROOT).as_posix()]!=md['archives'][name]['sha256']:raise ValueError('same admitted actual source changed')
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    source=Path('artifacts/muon_per_arm_canonical_source_20261012/run_1');sm=read(source,'result.json');refs.update(sm['input_hashes'])
    admission=sm['applications']['area_source']
    if admission['parent_original146_max']>sm['tolerance']:raise ValueError('original standalone parent source must pass')
    d=read(source,'area_source_parent_original146.npz',sm)
    tf=Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1');tm=read(tf,'result.json');t=read(tf,'application.npz',tm)
    nf=Path('artifacts/muon_complex_paired_normal_action_20261012/run_1');nm=read(nf,'result.json');n=read(nf,'same_action_inputs.npz',nm)
    hf=Path('artifacts/muon_precise_complex_canonical_exterior_step_20261012/run_1');hm=read(hf,'result.json');h=complex(*hm['step_coordinate_time'])
    normal=n['parent_proper_and_attachment_trace'][-1];F=t['arm_0_named_frame_covectors']
    a=arm_variational_midpoint_map(t['parent_standalone_Hessian'],-h,d['delta_x'],d['canonical_momentum_target'],d['source_gradient'],F,
        phase_frame_value=F@d['direction'][106:],normal_covector=normal)
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
    for name,module in sorted(sys.modules.items()):
        q=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and q:
            try:rel=Path(q).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/q).read_bytes()).hexdigest()!=r for q,r in refs.items()):raise ValueError('same parent source action changed')
    pair=lambda z:[float(z.real),float(z.imag)]
    result=dict(classification='EVALUATED_ADMITTED_PARENT_AREA_SOURCE_ORIGINAL358_AND_LITERAL_TRANSPOSE_GERM',
        input_hashes=refs,archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        parent_original146_admission=admission['parent_original146_max'],unchanged_admission_tolerance=sm['tolerance'],
        oriented_computational_step=pair(-h),original358_rows_max=float(np.max(abs(a['original358_rows']))),
        framed_rows_max=float(np.max(abs(a['framed_rows']))),literal_transpose_rows_max=float(np.max(abs(a['literal_transpose_rows']))),
        transpose_pairing_difference=pair(a['transpose_pairing']-a['test_pairing']),
        final_proper_normal_source_pairing=pair(a['test_pairing']),
        initial_action_dual_error_max=float(np.max(abs(a['initial_action_dual']+d['canonical_momentum_target']))),
        final_action_dual_error_max=float(np.max(abs(a['final_action_dual']-a['Pi_final']))),
        child_source_component_not_admitted_or_filled_zero=True,
        actual_current_parent_Hessian_and_source_used=True,
        constant_face_coefficient_action_not_changing_background_evolution=True,
        reset_endpoint_rows_not_added_as_persistent_force=True,
        physical_normal_mode_or_outer_domain_or_first_hit_selected=False,
        error_scope='binary actual-face coefficient-germ source and analytic transpose component; evolving-body/domain/action errors not enclosed')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),original358_rows_max=result['original358_rows_max'],
        transpose_rows_max=result['literal_transpose_rows_max'],normal_pairing=result['final_proper_normal_source_pairing'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.output)
