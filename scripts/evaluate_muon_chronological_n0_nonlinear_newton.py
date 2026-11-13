"""Evaluate and continue the literal complete-graph classical Newton step.

All field values and rates are varied before the original quartic action.
The quantum source ledger stays separate; classical stationarity on this
fixed numerical graph is not a physical or quantum stationary solution.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys,warnings
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_nonlinear_chronological_n0_action import chronological_n0_classical_binding,native_source_ledger
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_coupled_lorentz_radial_green import encode
from bhsm.interface.muon_nonlinear_chronological_n0_action import nonlinear_chronological_n0_action,chronological_field_KKT_blocks
from bhsm.interface.muon_chronological_kkt_equilibration import equilibrate_chronological_kkt,original_chronological_kkt_apply
from bhsm.interface.muon_chronological_spectral_blocks import chronological_spectral_factor,chronological_source_solve


def materialize(output,*,direction_folder,maximum_updates=3,residual_tolerance=1e-8):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every nonlinear action application')
    if type(maximum_updates)is not int or not 1<=maximum_updates<=5 or residual_tolerance<=0:
        raise ValueError('explicit finite classical iteration budget and positive tolerance required')
    a=chronological_n0_classical_binding();pins=a['input_hashes'];folder=ROOT/direction_folder
    def read(p):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(folder/'result.json');ap=folder/md['archive']['path'];direction=read(ap)
    if pins[ap.relative_to(ROOT).as_posix()]!=md['archive']['sha256']:
        raise ValueError('same original classical Newton direction changed')
    if md['classification']!='EVALUATED_WHOLE_CLASSICAL_CHRONOLOGICAL_KKT_NEWTON_DIRECTION':
        raise ValueError('all original field/Gauss/frame Newton rows required')
    pins.update(md['input_hashes'])
    x=direction['original_field_direction'].copy();rho=direction['original_frame_reaction_direction'].copy()
    if x.shape!=(1150,84)or rho.shape!=(1150,4):raise ValueError('same complete chronological unknowns required')
    # Freeze the executable coefficient/source bytes before the nonlinear
    # action application, then verify those same files at completion.
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            p=Path(path)
            try:rel=p.relative_to(ROOT).as_posix()
            except ValueError:continue
            pins[rel]=sha256(p.read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),
        'scripts/evaluate_muon_nonlinear_chronological_n0_action.py','scripts/evaluate_muon_reached_trace_action.py',
        'scripts/evaluate_muon_coupled_lorentz_radial_green.py','tests/test_muon_nonlinear_chronological_n0_action.py',
        'tests/test_muon_chronological_kkt_equilibration.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True);archives={};records=[];application=0
    def save(name,arrays):
        p=out/name;deterministic_archive(p,arrays)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split every complete nonlinear state and operator array')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def evaluate(q,r):
        nonlocal application
        application+=1
        def progress(done,total):
            print(json.dumps(dict(stage='literal_nonlinear_action',application=application,quadrature_nodes=done,total=total)),flush=True)
        action=nonlinear_chronological_n0_action(q,a['quadrature'],a['representation'],temporal_nodes=1151,
            value_permutation=a['value_permutation'],progress=progress)
        k=chronological_field_KKT_blocks(action,reaction=r)
        return action,k
    action,kkt=evaluate(x,rho)
    previous=float(np.linalg.norm(direction['original_KKT_residual']))
    for iteration in range(1,maximum_updates+1):
        residual=kkt['residual'];norm=float(np.linalg.norm(residual));maximum=float(np.max(abs(residual)))
        record=dict(iteration=iteration,original_KKT_residual_norm=norm,original_KKT_residual_max=maximum,
            actual_original_Gauss_residual_norm=float(np.linalg.norm(residual[:,:16])),
            actual_named_frame_residual_norm=float(np.linalg.norm(residual[:,84:])),
            interior_field_residual_norm=float(np.linalg.norm(residual[:-1,:84])),
            birth_real_field_residual_norm=float(np.linalg.norm(residual[574,:84])),
            final_natural_field_residual_norm=float(np.linalg.norm(residual[-1,:84])),
            original_field_displacement_norm=float(np.linalg.norm(x)),frame_reaction_norm=float(np.linalg.norm(rho)),
            relative_to_previous_residual=norm/previous)
        records.append(record);print(json.dumps(dict(stage='complete_nonlinear_residual',**record)),flush=True)
        # Every actual state/residual is complete and written once.
        for start in range(0,1150,128):
            save(f'iteration_{iteration}_state_{start}.npz',dict(node_start=np.array(start+1),
                field_coefficients=x[start:start+128],frame_reactions=rho[start:start+128],
                original_action_gradient=action['gradient'][start:start+128],original_KKT_residual=residual[start:start+128]))
        if maximum<=residual_tolerance or iteration==maximum_updates:break
        eq=equilibrate_chronological_kkt(kkt['diagonal'],kkt['upper'],kkt['lower']);s=eq['coordinate_scales']
        with warnings.catch_warnings(record=True)as caught:
            warnings.simplefilter('always');f=chronological_spectral_factor(eq['diagonal'],eq['upper'],eq['lower'])
            y=np.asarray(chronological_source_solve(f,list(-s*residual)))
        delta=s*y;linear=original_chronological_kkt_apply(kkt['diagonal'],kkt['upper'],kkt['lower'],delta)+residual
        record.update(next_original_linearized_residual_norm=float(np.linalg.norm(linear)),
            next_original_linearized_residual_max=float(np.max(abs(linear))),
            next_field_step_norm=float(np.linalg.norm(delta[:,:84])),LU_warnings=[str(w.message)for w in caught])
        if not np.isfinite(delta).all():raise ArithmeticError('literal classical Newton step unavailable')
        accepted=False
        for damping in(1.,.5,.25,.125):
            candidate_x=x+damping*delta[:,:84];candidate_rho=rho+damping*delta[:,84:]
            candidate_action,candidate_kkt=evaluate(candidate_x,candidate_rho)
            candidate_norm=float(np.linalg.norm(candidate_kkt['residual']))
            if candidate_norm<norm:
                x,rho,action,kkt=candidate_x,candidate_rho,candidate_action,candidate_kkt
                record['accepted_step_fraction']=damping;accepted=True;break
        if not accepted:
            record['next_step_status']='no actual residual decrease on the retained finite damping tests';break
        previous=norm
    for start in range(0,1150,16):
        stop=min(start+16,1150);ns=max(0,min(stop,1149)-start)
        save(f'final_original_KKT_blocks_{start}.npz',dict(node_start=np.array(start+1),
            KKT_diagonal=kkt['diagonal'][start:stop],KKT_upper=kkt['upper'][start:start+ns],KKT_lower=kkt['lower'][start:start+ns]))
    save('original_trace_reactions.npz',dict(initial_face_gradient=action['initial_face_gradient'],
        initial_face_Hessian=action['initial_face_Hessian'],initial_to_first_Hessian=action['initial_to_first_Hessian'],
        frame_rows_per_node=action['frame_rows_per_node'],frame_indices=action['frame_indices'],
        Gauss_indices_per_node=action['Gauss_indices_per_node'],value_permutation=a['value_permutation']))
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise RuntimeError('same literal nonlinear action source changed')
    final=kkt['residual'];converged=float(np.max(abs(final)))<=residual_tolerance
    result=dict(classification='EVALUATED_COMPLETE_CHRONOLOGICAL_LITERAL_CLASSICAL_NONLINEAR_NEWTON_APPLICATION',
        input_hashes=pins,archives=archives,records=records,source_domain=a['source_domain'],coefficient_extension=a['coefficient_extension'],
        original_free_field_rows=96600,original_At_Gauss_rows=18400,named_frame_rows=4600,
        initial_only_trace_removed=0,free_final_natural_trace=1150,birth_real_trace_node=575,
        all_original_endpoint_corner_and_frame_reactions_retained=True,
        final_classical_action_value=encode(action['value']),actual_classical_residual_max=float(np.max(abs(final))),
        actual_classical_residual_norm=float(np.linalg.norm(final)),classical_only_residual_tolerance=residual_tolerance,
        declared_classical_numerical_criterion_met=converged,maximum_actual_Newton_updates=maximum_updates,
        native_source_ledger=native_source_ledger(),native_source_assigned_zero=False,
        nonlinear_quantum_or_geometry_or_physical_domain_stationarity_claimed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 actual complete fixed-geometry classical action Newton residual; coefficient extension, quantum graded source/domain, geometry stationarity and physical matching not enclosed')
    rp=out/'result.json';rp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),**{k:v for k,v in result.items()if k not in('input_hashes','archives')}),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--direction-folder',type=Path,default=Path('artifacts/muon_chronological_classical_kkt_response_20261011/run_1'))
    p.add_argument('--maximum-updates',type=int,default=3);p.add_argument('--residual-tolerance',type=float,default=1e-8)
    q=p.parse_args();materialize(q.output,direction_folder=q.direction_folder,maximum_updates=q.maximum_updates,residual_tolerance=q.residual_tolerance)
