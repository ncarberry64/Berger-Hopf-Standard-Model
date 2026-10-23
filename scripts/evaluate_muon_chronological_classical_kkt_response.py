"""Apply every original classical residual row to the whole KKT Hessian.

This is a classical Newton direction, not a quantum stationary solution.
The native source and the physical endpoint/exterior matching are not
replaced by zeros. No gauge row, multiplier or final cotangent is dropped.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys,warnings
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_chronological_kkt_equilibration import equilibrate_chronological_kkt,original_chronological_kkt_apply
from bhsm.interface.muon_chronological_spectral_blocks import chronological_spectral_factor,chronological_source_solve
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(folder,output):
    folder=ROOT/folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve original Newton applications')
    pins={}
    def read(p):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    report=read(folder/'result.json')
    pieces=[]
    for p in sorted(folder.glob('original_KKT_blocks_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1])):
        if sha256(p.read_bytes()).hexdigest()!=report['archives'][p.name]['sha256']:raise ValueError('original KKT archive changed')
        pieces.append(read(p))
    if not pieces:raise ValueError('all original directed field/KKT arrays required')
    D,U,L,g=[np.concatenate([p[k]for p in pieces])for k in('KKT_diagonal','KKT_upper','KKT_lower','classical_KKT_residual')]
    if D.shape!=(1150,88,88)or U.shape!=(1149,88,88)or L.shape!=U.shape or g.shape!=(1150,88):
        raise ValueError('same complete84+4 global action/domain required')
    eq=equilibrate_chronological_kkt(D,U,L);s=eq['coordinate_scales']
    caught=[]
    with warnings.catch_warnings(record=True)as caught:
        warnings.simplefilter('always')
        f=chronological_spectral_factor(eq['diagonal'],eq['upper'],eq['lower'])
        y=np.asarray(chronological_source_solve(f,list(-s*g)))
    delta=s*y
    residual=original_chronological_kkt_apply(D,U,L,delta)+g
    action_size=(np.einsum('nij,nj->ni',abs(D),abs(delta)))
    action_size[:-1]+=np.einsum('nij,nj->ni',abs(U),abs(delta[1:]));action_size[1:]+=np.einsum('nij,nj->ni',abs(L),abs(delta[:-1]))
    component_relative=abs(residual)/np.maximum(action_size+abs(g),np.finfo(float).tiny)
    if not np.isfinite(delta).all()or not np.isfinite(residual).all():raise ArithmeticError('unavailable finite KKT response; preserve owned quotient requirements')
    warnings_text=[str(w.message)for w in caught]
    pivots=[float(min(abs(np.diag(x[0]))))for x in f['LU']]
    out.mkdir(parents=True);p=out/'classical_kkt_direction.npz'
    _compressed_npz(p,dict(original_field_direction=delta[:,:84],original_frame_reaction_direction=delta[:,84:],
        original_linearized_KKT_residual=residual,original_KKT_residual=g,
        coordinate_scales=s,scaled_equation_direction=y,
        original_componentwise_backward_residual=component_relative,
        balanced_Schur_minimum_pivots=np.array(pivots)))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            pins[rel]=sha256(Path(path).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_chronological_kkt_equilibration.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/k).read_bytes()).hexdigest()!=h for k,h in pins.items()):raise RuntimeError('original KKT source changed')
    record=dict(classification='EVALUATED_WHOLE_CLASSICAL_CHRONOLOGICAL_KKT_NEWTON_DIRECTION',
        input_hashes=pins,archive=dict(path=p.name,bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()),
        original_free_field_rows=1150*84,original_At_Gauss_rows=1150*16,named_frame_multiplier_rows=1150*4,
        original_gradient_norm=float(np.linalg.norm(g)),original_gradient_final_face_norm=float(np.linalg.norm(g[-1,:84])),
        field_direction_norm=float(np.linalg.norm(delta[:,:84])),frame_reaction_direction_norm=float(np.linalg.norm(delta[:,84:])),
        original_linearized_row_residual_norm=float(np.linalg.norm(residual)),original_linearized_row_residual_max=float(np.max(abs(residual))),
        original_Gauss_linearized_residual_norm=float(np.linalg.norm(residual[:,:16])),
        original_frame_linearized_residual_norm=float(np.linalg.norm(residual[:,84:])),
        original_componentwise_backward_residual_max=float(np.max(component_relative)),
        minimum_balanced_Schur_pivot=float(min(pivots)),LU_warnings=warnings_text,
        equilibration_history=eq['equilibration_history'],
        final_natural_cotangent_discarded=False,Gauss_or_frame_rows_deleted=False,
        native_source_supplied=False,native_source_assigned_zero=False,
        nonlinear_residual_at_direction_evaluated=False,physical_quantum_stationarity_claimed=False,
        source_domain=report['source_domain'],coefficient_extension=report['coefficient_extension'],
        physical_exterior_relative_domain_or_Pauli_identified=False,physical_a_mu=None,
        error_scope='binary64 original classical KKT direction and every original row; no nonlinear stationarity, gauge/exterior-domain completion or quantum/native Pauli enclosure')
    rp=out/'result.json';rp.write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in record.items()if k not in('input_hashes','equilibration_history')},sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.input_folder,a.output)
