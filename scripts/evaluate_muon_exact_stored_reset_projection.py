"""Attribute one reached reset-port residual to exact stored302 arithmetic."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from flint import acb,acb_mat,ctx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_complex_coupled_reset_continuation import coupled_reset_application
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.aether_full_reset_action_jacobian import _attachment_jacobian_at_order,_symmetric_power


def materialize(source_folder,output,precision):
    source=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('one stored302 attribution is immutable')
    refs={};rb=(source/'result.json').read_bytes();md=json.loads(rb);refs.update(md['input_hashes'])
    refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(rb).hexdigest()
    p=source/'application.npz';b=p.read_bytes()
    if sha256(b).hexdigest()!=md['archives'][p.name]['sha256']:raise ValueError('actual final reset state changed')
    refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
    with np.load(p,allow_pickle=False)as z:saved={k:z[k].copy()for k in z.files}
    input_path=next(Path(p)for p in refs if p.endswith('true_phase_projection_inputs.npz'))
    if sha256((ROOT/input_path).read_bytes()).hexdigest()!=refs[input_path.as_posix()]:raise ValueError('same source weights changed')
    with np.load(ROOT/input_path,allow_pickle=False)as z:weights=z['state_weights'].copy();normal=z['normalization_coordinates'].copy()
    phase,_=retained_input('outgoing',refs)
    a=coupled_reset_application(saved['raw_pair'],saved['reference_pair'],phase['representation'],weights,normal,
        action_parameters=md['action_parameters'],compute_jacobian=False)
    app=a['projection'];K=app['saddle'];rhs=app['saddle_rhs'];theta=app['analytic_temporal_dual']
    old=ctx.prec;ctx.prec=precision
    try:
        convert=lambda x:acb_mat([[acb(float(v.real),float(v.imag))for v in row]for row in np.asarray(x)])
        KK=convert(K);rr=convert(rhs);TT=convert(np.r_[theta,np.zeros(10)][:,None])
        exact=KK.solve(rr);adjoint=KK.transpose().solve(TT)
        npart=292;C=convert(app['common_trace_map']);thetab=convert(theta[:,None])
        L=acb_mat([[exact[i,j]for j in range(6)]for i in range(npart)])
        ports=C.transpose()*L.transpose()*thetab
        er=KK*exact-rr;ar=KK.transpose()*adjoint-TT
        exact_residual=max(float(abs(er[i,j]).upper())for i in range(302)for j in range(6))
        exact_adjoint=max(float(abs(ar[i,0]).upper())for i in range(302))
        high=np.array([complex(float(ports[i,0].real.mid()),float(ports[i,0].imag.mid()))for i in range(3)])
        rows=a['residual'].copy();B=_attachment_jacobian_at_order(12,normal);bn=_symmetric_power(B@B.T,.5)
        ai=a['groups']['common_attachment_temporal_dual'];ni=a['groups']['common_normal_temporal_dual']
        rows[ai]=bn@high[:2];rows[ni]=high[2]
        strings=np.array([[str(ports[i,0].real),str(ports[i,0].imag)]for i in range(3)])
        lifted=np.array([[complex(float(exact[i,j].real.mid()),float(exact[i,j].imag.mid()))for j in range(6)]for i in range(302)])
        paired=np.array([complex(float(adjoint[i,0].real.mid()),float(adjoint[i,0].imag.mid()))for i in range(302)])
    finally:ctx.prec=old
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,dict(raw_pair=saved['raw_pair'],reference_pair=saved['reference_pair'],
        stored_saddle302=K,stored_rhs=rhs,stored_analytic_dual=theta,binary_common_port=app['common_trace_cotangent'],
        exact_stored_common_port=high,exact_stored_port_ball_strings=strings,exact_stored_rounded_lift=lifted,
        exact_stored_rounded_adjoint=paired,binary_original226_rows=a['residual'],exact_stored_port_original226_rows=rows,
        original_reexecution_minus_saved=a['residual']-saved['original226_rows']))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same attribution action source changed')
    result=dict(classification='ONE_EXACT_STORED302_FULL_PHASE_RESET_PORT_AND_TRANSPOSE_ADJOINT_ATTRIBUTION',input_hashes=refs,
        archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},precision_bits=precision,
        exact_stored_primal_residual_upper=exact_residual,exact_stored_transpose_adjoint_residual_upper=exact_adjoint,
        exact_stored_minus_binary_port_norm=float(np.linalg.norm(high-app['common_trace_cotangent'])),
        binary_original226_rows_max=float(np.max(abs(a['residual']))),exact_stored_port_original226_rows_max=float(np.max(abs(rows))),
        reexecuted_original_minus_saved_max=float(np.max(abs(a['residual']-saved['original226_rows']))),
        original_state_or_action_Hessian_changed=False,physical_parameter_or_first_hit_selected=False,
        error_scope='outward Acb arithmetic of exact stored binary302 saddle/rhs/dual only; binary source/action/Hessian production and physical formation/domain errors excluded')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='exact_stored302_projection_attribution_complete',binary_rows_max=result['binary_original226_rows_max'],
        exact_stored_port_rows_max=result['exact_stored_port_original226_rows_max'],port_difference_norm=result['exact_stored_minus_binary_port_norm'],
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,
        default=Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--precision-bits',type=int,default=192)
    a=p.parse_args();materialize(a.source_folder,a.output,a.precision_bits)
