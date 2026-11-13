"""Telescope the actual terminal constraint defect on the same action chart."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(terminal_folder,output):
    base=ROOT/terminal_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every same-terminal application')
    rb=(base/'result.json').read_bytes();md=json.loads(rb);refs=dict(md['input_hashes'])
    refs[(base/'result.json').relative_to(ROOT).as_posix()]=sha256(rb).hexdigest()
    path=base/'actual_complex_terminal_full_action.npz'
    refs[path.relative_to(ROOT).as_posix()]=sha256(path.read_bytes()).hexdigest()
    if refs[path.relative_to(ROOT).as_posix()]!=md['archives'][path.name]['sha256']:
        raise ValueError('actual terminal action changed')
    with np.load(path,allow_pickle=False)as z:a={k:z[k].copy()for k in z.files}
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];params=md['action_parameters']
    raw=a['raw_fields'];n=106;P=a['coordinate_lift'];ids=a['original_value_permutation']
    lifts=chronological_n0_field_lifts(rep,ids);gv=np.eye(84)[:80,ids];tg=gv.copy()
    for j,label in enumerate(rep['gauge_labels']):
        if label['field']=='A_tau':tg[j]=0.
    delta=np.zeros_like(raw)
    delta[100:180]=gv@a['original_terminal_field_value']
    delta[180:260]=tg@a['original_terminal_field_coordinate_rate']
    delta[260:264]=lifts['hv']@a['original_terminal_field_value']
    delta[264:]=lifts['hv']@a['original_terminal_field_coordinate_rate']
    original_chart=raw-delta
    # This is a control on exactly the same complex time/profile/geometry,
    # not a replacement real terminal or a new initial canonical state.
    print(json.dumps(dict(stage='same_complex_terminal_without_field_correction',
        coordinate_time=[a['coordinate_time'].item().real,a['coordinate_time'].item().imag])),flush=True)
    b=holomorphic_inherited_child_action(original_chart,a['coordinate_time'].item(),
        phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep,**params)
    control=base/'same_real_original_action_control.npz'
    refs[control.relative_to(ROOT).as_posix()]=sha256(control.read_bytes()).hexdigest()
    with np.load(control,allow_pickle=False)as z:realG=P.T@z['new_raw_gradient']
    actualG=a['action_gradient'];baseG=b['gradient']
    midpoint_to_chart=baseG-realG;field_effect=actualG-baseG
    telescope=actualG-realG-midpoint_to_chart-field_effect
    out.mkdir(parents=True);arrays=dict(actual_raw=raw,uncorrected_chart_raw=original_chart,
        exact_raw_field_correction=delta,coordinate_time=a['coordinate_time'],
        coordinate_lift=P,uncorrected_chart_gradient=baseG,
        uncorrected_chart_hessian=b['hessian'],actual_terminal_gradient=actualG,
        same_real_midpoint_gradient=realG,midpoint_to_terminal_chart_gradient=midpoint_to_chart,
        global_field_correction_gradient=field_effect,gradient_telescope_residual=telescope)
    p=out/'application.npz';_compressed_npz(p,arrays)
    if p.stat().st_size>10*1024**2:raise RuntimeError('split full action operands')
    def blocks(g):
        return dict(Lv_norm=float(np.linalg.norm(g[n:2*n])),
            lapse_rows_max=float(np.max(abs(g[2*n:2*n+12]))),
            shift_rows_max=float(np.max(abs(g[2*n+12:2*n+24]))),
            At_Gauss_rows_max=float(np.max(abs(g[2*n+24:]))))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):
        raise RuntimeError('same terminal action or control changed')
    result=dict(classification='EVALUATED_SAME_COMPLEX_TERMINAL_CONSTRAINT_DEFECT_ATTRIBUTION',
        input_hashes=refs,archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        same_real_midpoint=blocks(realG),same_complex_terminal_before_global_field_correction=blocks(baseG),
        actual_corrected_complex_terminal=blocks(actualG),
        finite_chart_change=blocks(midpoint_to_chart),global_field_correction_effect=blocks(field_effect),
        telescope_residual_max=float(np.max(abs(telescope))),
        complex_terminal_geometry_or_profiles_changed_max=float(np.max(abs(delta[:100]))),
        actual_fixed_x_Pi_target_changed=False,new_terminal_or_initial_load_selected=False,
        diagnostic_chart_not_canonical_exterior_history=True,
        error_scope='binary64 original analytic action telescope; no canonical convergence, physical continuation/stop or Pauli bound')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='same_terminal_defect_attribution_complete',
        finite_chart_change=result['finite_chart_change'],global_field_effect=result['global_field_correction_effect'],
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--terminal-folder',type=Path,default=Path('artifacts/muon_holomorphic_child_terminal_20261011/run_2'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.terminal_folder,a.output)
