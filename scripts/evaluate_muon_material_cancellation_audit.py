"""Separate stored123 solve arithmetic from original action/map cancellation."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from flint import acb,acb_mat,ctx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_material_rate_canonical_reduction import fixed_position_material_rate_chart
from bhsm.interface.muon_quadratic_canonical_field_elimination import _balanced_solve
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(checkpoint,output,precision):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve independent cancellation evidence')
    refs={}
    def read(p):
        p=ROOT/p;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    saved=read(checkpoint)
    rootpath=Path('artifacts/muon_reduced_complex_canonical_geometry_20261011/run_1')
    md=read(rootpath/'result.json');refs.update(md['input_hashes']);anchor=read(rootpath/'application.npz')
    terminal=read('artifacts/muon_holomorphic_child_terminal_20261011/run_2/actual_complex_terminal_full_action.npz')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];P=phase['coordinates']['lift'];n=106
    chart=fixed_position_material_rate_chart((P@anchor['coefficients'])[:100]);T=chart['velocity_algebraic_lift'];Ti=chart['velocity_algebraic_inverse'];S=chart['fixed_position_phase_lift']
    f,g=chart['field_indices'],chart['nonlinear_geometry_indices'];eta=anchor['coefficients'];p0=anchor['canonical_momentum_target']
    e=np.r_[eta[:n],Ti@eta[n:]];e[n+g]=saved['nonlinear_material_coordinates'];time=anchor['coordinate_time'].item()
    evaluate=lambda u:holomorphic_inherited_child_action(P@(S@u),time,phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep,**md['action_parameters'])
    a=evaluate(e);Gp=S.T@a['gradient'];D=S.T@a['hessian']@S
    target=T.T@np.r_[p0,np.zeros(40,complex)];r=Gp[n:]-target
    frame=canonical_central_frame(terminal['raw_fields'],rep);C=frame['named_frame_covectors']@T;Cf=C[:,f]
    reference=Ti@terminal['master_coefficients'][n:]
    K=np.block([[D[n+f[:,None],n+f],Cf.T],[Cf,np.zeros((2,2),complex)]])
    rhs=-np.r_[r[f],C@(e[n:]-reference)]
    double,_,_=_balanced_solve(K,rhs)
    old=ctx.prec;ctx.prec=precision
    try:
        def matrix(x):return acb_mat([[acb(float(z.real),float(z.imag))for z in row]for row in np.asarray(x)])
        KK,rr=matrix(K),matrix(rhs[:,None]);sol=KK.solve(rr)
        exact_residual=KK*sol-rr
        arb_residual_upper=max(float(abs(exact_residual[j,0]).upper())for j in range(len(rhs)))
        high=np.array([complex(float(sol[j,0].real.mid()),float(sol[j,0].imag.mid()))for j in range(len(rhs))])
        records=[];arrays=dict(stored_field_frame123=K,stored_rhs=rhs,quadratic_anchor_material=e,
            material_lift=T,original_momentum_target=p0,checkpoint_original_rows=saved['original_constitutive_rows'])
        for label,delta in(('binary64_balanced',double),('arb_rounded_to_binary64',high)):
            uu=e.copy();uu[n+f]+=delta[:-2];aa=evaluate(uu);GG=S.T@aa['gradient'];HH=S.T@aa['hessian']@S
            original=np.r_[aa['gradient'][n:2*n]-p0,aa['gradient'][2*n:]]
            rrnew=GG[n:]-target;affine=rrnew[f]-r[f]-K[:-2,:-2]@delta[:-2]
            framed=np.r_[rrnew[f]+Cf.T@delta[-2:],C@(uu[n:]-reference)]
            kres=KK*matrix(delta[:,None])-rr
            stored_upper=max(float(abs(kres[j,0]).upper())for j in range(len(rhs)))
            qdef=HH[n+f[:,None],n+f]-K[:-2,:-2]
            records.append(dict(method=label,stored_linear_equation_residual_upper=stored_upper,
                fresh_action_field_affine_defect_max=float(np.max(abs(affine))),
                fresh_action_quadratic_Hessian_relative_defect=float(np.max(abs(qdef))/max(1.,np.max(abs(K[:-2,:-2])))),
                fresh_action_framed121_residual_max=float(np.max(abs(framed))),
                original146_residual_max=float(np.max(abs(original))),
                original_momentum_residual_max=float(np.max(abs(original[:n]))),original_algebraic_residual_max=float(np.max(abs(original[n:])))))
            arrays.update({label+'_delta':delta,label+'_original_coefficients':S@uu,
                label+'_fresh_action_rows':original,label+'_affine_action_defect':affine,label+'_framed121_rows':framed})
    finally:ctx.prec=old
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same actual action source changed')
    md=dict(classification='EXACT_STORED123_SOLVE_VERSUS_MATERIAL_MAP_ORIGINAL_ACTION_CANCELLATION',input_hashes=refs,
        archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},precision_bits=precision,
        exact_ball_solution_residual_upper=arb_residual_upper,comparisons=records,
        binary_solution_difference_norm=float(np.linalg.norm(high-double)),original_x_and_Pi_fixed=True,
        rows_removed=0,high_precision_scope='exact stored binary64 K/rhs only; action production and coordinate pullbacks remain binary64',
        compatible_canonical_point_selected=False,physical_error_enclosure=False)
    p=out/'result.json';p.write_text(json.dumps(md,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=md['classification'],comparisons=records,exact_ball_solution_residual_upper=arb_residual_upper,binary_solution_difference_norm=md['binary_solution_difference_norm']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--precision-bits',type=int,default=192)
    a=p.parse_args();materialize(a.checkpoint,a.output,a.precision_bits)
