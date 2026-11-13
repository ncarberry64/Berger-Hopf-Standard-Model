"""Fresh all-natural birth rows and complete signed 3-port action application."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_complex_coupled_reset_continuation import coupled_reset_application,central_reset_Ward_rows
from bhsm.interface.muon_coupled_birth_full_application import complete_birth_geometry_ports
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def clean(x):
    if isinstance(x,dict):return{k:clean(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return[clean(v)for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(complex,np.complexfloating)):return[float(x.real),float(x.imag)]
    if isinstance(x,np.generic):return x.item()
    return x


def materialize(source,output):
    source=ROOT/source;out=ROOT/output
    if out.exists():raise FileExistsError('preserve all-row birth action application')
    pins={};archives={}
    def read(path,expected=None):
        p=ROOT/path;b=p.read_bytes();h=sha256(b).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same completed input archive required')
        pins[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    md=read(source.relative_to(ROOT)/'result.json')
    saved=read(source.relative_to(ROOT)/'application.npz',md['archives']['application.npz']['sha256'])
    weights_path=next(Path(p)for p in md['input_hashes']if p.endswith('true_phase_projection_inputs.npz'))
    wt=read(weights_path,md['input_hashes'][weights_path.as_posix()])
    phase,_=retained_input('outgoing',pins);rep=phase['representation']
    raw,reference=saved['raw_pair'],saved['reference_pair'];params=md['action_parameters']
    print(json.dumps(dict(stage='fresh_all226_full536_birth_action_started',parameters=params)),flush=True)
    app=coupled_reset_application(raw,reference,rep,wt['state_weights'],wt['normalization_coordinates'],
                                action_parameters=params,compute_jacobian=False)
    ward=central_reset_Ward_rows(app,raw,rep)
    print(json.dumps(dict(stage='all_original_birth_rows',maximum=float(np.max(abs(app['residual']))),
                         worst_row=int(np.argmax(abs(app['residual']))))),flush=True)
    ports=complete_birth_geometry_ports(app,raw,rep);a=app['action']
    groups={}
    for name,ids in app['groups'].items():
        r=app['residual'][ids];j=int(np.argmax(abs(r)))
        groups[name]=dict(indices=ids,maximum=float(np.max(abs(r))),worst_original_row=ids[j],worst_complex=r[j])
    out.mkdir(parents=True)
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>=10*1024**2:raise ValueError('split complete action arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('actual_full_birth_action.npz',dict(raw_pair=raw,reference_pair=reference,master_lift=a['master_lift'],
        original226_rows=app['residual'],same_point_saved_original226_rows=saved['original226_candidate_rows'],
        full_gradient504=a['gradient'],full_Hessian504=a['hessian'],
        standalone_parent_gradient252=a['parent']['gradient'],standalone_parent_Hessian252=a['parent']['hessian'],
        area_gradient504=a['area_gradient_per_gamma'],area_Hessian504=a['area_Hessian_per_gamma'],
        joint_temporal_dual=a['temporal_cotangent'],area_temporal_dual=a['area_temporal_cotangent_per_gamma'],
        area_parameter_source=app['area_parameter_source'],Ward_rows=ward['rows'],Ward_identity=ward['original_nonlinear_identity'],
        original_full302_saddle=app['projection']['saddle'],original_full302_phase_rows=app['projection']['original_phase_rows'],
        original_full302_transpose_rows=app['projection']['analytic_adjoint_rows'],
        weights=wt['state_weights'],normalization=wt['normalization_coordinates']))
    for name in('kinetic','restoring'):
        p=ports[name];data={k:v for k,v in p.items()if isinstance(v,np.ndarray)}
        data.update({'sector_'+k:v for k,v in p['sector_forms'].items()})
        save(f'full_three_port_{name}.npz',data)
    save('proper_signed_port_matrices.npz',{k:np.asarray(v)for k,v in ports.items()
        if isinstance(v,np.ndarray)or k=='child_readout_lapse'})
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path and Path(path).is_relative_to(ROOT):
            p=Path(path);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in(Path(__file__),ROOT/'tests/test_muon_coupled_birth_full_application.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('same action input changed')
    report=dict(classification='EVALUATED_ALL_ORIGINAL_BIRTH_ROWS_AND_FULL_SIGNED_PROPER_GEOMETRY_PORTS',
        archives=archives,input_hashes=pins,action_parameters=params,groups=groups,
        all_original226_max=float(np.max(abs(app['residual']))),
        fresh_minus_saved_rows_max=float(np.max(abs(app['residual']-saved['original226_candidate_rows']))),
        exact_named_Ward_max=float(np.max(abs(ward['original_nonlinear_identity']))),
        full302_phase_rows_max=float(np.max(abs(app['projection']['original_phase_rows']))),
        full302_transpose_rows_max=float(np.max(abs(app['projection']['analytic_adjoint_rows']))),
        proper_inertia_matrix=ports['proper_inertia_matrix'],proper_restoring_matrix=ports['proper_restoring_matrix'],
        proper_parent_drive=ports['proper_parent_drive'],proper_child_resistance=ports['proper_child_resistance'],
        conditional_attachment_inertia=ports['conditional_attachment_inertia'],
        conditional_attachment_restoring=ports['conditional_attachment_restoring'],
        original_ports={k:dict(right_max=float(np.max(abs(ports[k]['original_right_rows']))),
            left_max=float(np.max(abs(ports[k]['original_left_rows']))),
            sector_sum_max=float(np.max(abs(ports[k]['sector_sum_difference']))))for k in('kinetic','restoring')},
        source_or_background_replay_performed=False,physical_matching_claimed=False,
        alpha_FSC_not_substituted_or_assigned=True,area_law='gamma=alpha_FSC*c^(-7/2)',
        unknown_layout='joint master504; original birth226 has two named Ward dependencies. Incoming canonical IVP/domain and chronological formation/exterior equations must constrain the remaining snapshot directions before an admissible coupled solve.',
        complete_attachments2_and_normal1_preserved=True,
        formation_operator='Full chronological Lx-d_t Lv and its changing coefficients, actual inherited sources, event and outer domains; the frozen port matrices here do not replace H_form.',
        scope='Fresh same completed endpoint full536 action/all natural rows, full302 temporal face and full complex3port proper-normal action/area application. No frozen normal mode, c/gamma, physical state or exterior pole selected.')
    p=out/'result.json';p.write_text(json.dumps(clean(report),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='full_birth_action_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),
                         all_original226_max=report['all_original226_max'],groups=clean(groups))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.source,a.output)
