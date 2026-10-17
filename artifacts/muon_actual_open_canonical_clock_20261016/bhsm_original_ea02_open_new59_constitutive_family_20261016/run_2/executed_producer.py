"""Open new59 momentum family and fresh local constitutive coefficients.

All31 kernel coordinates and eight source/domain compatibility equations stay
open.  The seven evaluated particular rays are a coordinate origin for this
affine family, not a physical choice of the free coordinates or outgoing data.
The cached border is used only to precondition fresh original277 equations.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BACKEND='audits/bhsm_original_ea02_d4_phase_operator_20261016.py'
BACKEND_SHA='c2f11bd4890631c03afee8b0db1fe8a93e505a12071da9cd2b9923744e8a5c6d'
RANK_SHA='7682206f2b824ed500e4091799feea246641163dacb6b3f849a2f2829d8e06c7'
RANK_ARCHIVE_SHA='202df02e2978df08c5b4e682ca8ae2471434fe6a477e2fadece35c19f1ebfcf0'
CAUCHY_SHA='63d04359f42673671169f61bcfa395b04fe5008c05912b65c95090c0a4458942'
CAUCHY_ARCHIVE_SHA='7e11ceedc78de309d8944797982ed35aded42056f5b3fd9bccd871455591d5b3'


def execute(rank_folder,cauchy_folder,output,*,maximum_checks=3):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    p=ROOT/BACKEND
    if sha256(p.read_bytes()).hexdigest()!=BACKEND_SHA:raise ValueError('Reviewed fresh phase backend changed')
    spec=importlib.util.spec_from_file_location('actual_open_family_phase_backend',p)
    backend=importlib.util.module_from_spec(spec);sys.modules[spec.name]=backend;spec.loader.exec_module(backend)
    op=backend.ActualEa02D4PhaseOperator();acb_mat=op.acb_mat;op.pin(p,BACKEND_SHA)
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    rank_folder,cauchy_folder=Path(rank_folder).resolve(),Path(cauchy_folder).resolve()
    def packet(folder,expected_source,expected_archive):
        m=op.read(folder/'result.json')
        if m['source_sha256']!=expected_source:raise ValueError('Reviewed operand producer changed')
        op.pin(folder/'executed_producer.py',expected_source)
        if m['archive']['sha256']!=expected_archive:raise ValueError('Operand archive metadata changed')
        return op.read(folder/m['archive']['name'],expected_archive),m
    r,rm=packet(rank_folder,RANK_SHA,RANK_ARCHIVE_SHA)
    c,cm=packet(cauchy_folder,CAUCHY_SHA,CAUCHY_ARCHIVE_SHA)
    for z in(r,c):
        if not np.array_equal(z['master368'],op.target['master368']) or z['coordinate_time'].item()!=op.target['coordinate_time'].item():raise ValueError('No different-cut or retracted source/state')
    B=op.value(r,'fresh_new59_momentum_to_temporal_Gauss_map')
    L=op.value(r,'exact_left_cokernel_selector')
    V=op.value(r,'fresh_full_velocity_gauge_map')
    active=np.asarray(r['full_pivot_temporal_rows'],int);pivots=np.asarray(r['full_pivot_new59_columns'],int)
    free=np.asarray(r['unresolved_new59_free_coordinate_labels'],int);zero_rows=np.asarray(r['exact_zero_temporal_rows'],int)
    newq=np.asarray(r['new59_position_indices'],int);oldq=np.asarray(r['old158_position_indices'],int)
    if (B.nrows(),B.ncols(),L.nrows(),L.ncols(),len(active),len(pivots),len(free))!=(36,59,8,36,28,28,31):raise ValueError('Exact certified28+31+8 map required')
    if not np.array_equal(np.sort(np.r_[newq,oldq]),np.arange(217)) or not np.array_equal(newq,c['new59_position_indices']):raise ValueError('Original disjoint217 momentum labels required')
    P=acb_mat(59,36);N=acb_mat(59,31)
    for i,j in zip(active,pivots):
        if float(abs(B[int(i),int(j)]).lower())<=0:raise ValueError('Certified nonzero pivot required')
        P[int(j),int(i)]=1/B[int(i),int(j)]
    for j,label in enumerate(free):N[int(label),j]=1
    I=op.matrix(np.eye(36));projector=I-L.transpose()*L
    algebra=dict(particular_pivot_range_rows=B*P-projector,kernel_rows=B*N,left_cokernel_rows=L*B)
    # The saved certified pivots carry interval radii.  A reciprocal product
    # must enclose the exact identity; its radius need not vanish numerically.
    if max(op.upper(v)for v in algebra.values())>1e-50 or any(not v[i,j].contains(0)for v in algebra.values()for i in range(v.nrows())for j in range(v.ncols())):raise ArithmeticError('Certified affine coordinate maps failed')
    g=op.value(c,'all60_saved_actual_affine_seven_Gauss_trial_residual')
    primal_g=op.value(c,'complete_D4_primal_algebraic_r')
    Kg=op.value(c,'all60_saved_actual_native_Gauss_Kz_trial')
    b=op.rows(g,np.arange(24,60));rank_b=op.value(r,'actual_seven_affine_Gauss_load_for_new_momentum_change')
    gauss_affine_check=g-Kg
    for i in range(60):gauss_affine_check[i,0]-=primal_g[i,0]
    if max(op.upper(b-rank_b),op.upper(gauss_affine_check))>1e-50:raise ValueError('Native affine Gauss load must include primalr only once in column0')
    particular=P*b;cokernel=L*b
    rhs=acb_mat(277,7);free_rhs=acb_mat(277,31)
    for i,d in enumerate(newq):
        for j in range(7):rhs[int(d),j]=particular[i,j]
        for j in range(31):free_rhs[int(d),j]=N[i,j]
    for i in range(60):
        for j in range(7):rhs[217+i,j]=-g[i,j]
    # Exact literal coefficient map, independent of approximate Hessian gauge
    # identities.  No conjugation is used in this complex analytic action.
    Z=acb_mat(277,36)
    for i in range(217):
        for j in range(36):Z[i,j]=V[i,j]
    for i in range(36):Z[217+24+i,i]=1
    source_compatibility=Z.transpose()*rhs+L.transpose()*cokernel
    free_compatibility=Z.transpose()*free_rhs
    if max(op.upper(source_compatibility),op.upper(free_compatibility))>1e-50:raise ArithmeticError('Momentum/Gauss sign or open-family coefficient map failed')
    # A frame fixes only the computational particular. It is not selected as
    # the physical allowed outgoing subspace; reactions remain explicit.
    candidate,reaction,cached_residual=op.precondition(rhs)
    history=[];germchecks=[]
    for step in range(maximum_checks):
        print(json.dumps(dict(stage='fresh_open_affine_particular_constitutive_check',iteration=step,rights=7,original_rows=277)),flush=True)
        Hcandidate,app=op.apply_phase(candidate);germchecks.append(dict(op.last_primal_germ_checks))
        _compressed_npz(out/f'fresh_particular_phase_application_{step:02d}.npz',app)
        original=Hcandidate-rhs;framed=original+op.F.transpose()*reaction;frame=op.F*candidate
        row=dict(iteration=step,original277_upper=op.upper(original),bordered_top_upper=op.upper(framed),fixed_frame_upper=op.upper(frame),reaction_upper=op.upper(reaction))
        history.append(row);print(json.dumps(row),flush=True)
        if max(row['original277_upper'],row['bordered_top_upper'],row['fixed_frame_upper'])<=2e-10:break
        if step+1<maximum_checks:
            correction,dr,unused=op.precondition(-framed,-frame);candidate+=correction;reaction+=dr
    trialPi=op.value(c,'complete_D4_momentum_seven');deltaPi=op.rows(Hcandidate,np.arange(217))
    actual_updated_Pi=trialPi+deltaPi;target_updated_Pi=trialPi+op.rows(rhs,np.arange(217))
    actual_remaining_G=g+op.rows(Hcandidate,np.arange(217,277))
    old_preservation=op.rows(deltaPi,oldq);new_Pi_rows=op.rows(deltaPi,newq)-particular
    original_rows=Hcandidate-rhs
    closed=bool(max(op.upper(original_rows),op.upper(frame),op.upper(framed),op.upper(actual_remaining_G),op.upper(old_preservation),op.upper(new_Pi_rows))<=2e-10)
    values=dict(algebra,particular_momentum_map_P=P,open31_momentum_kernel_map_N=N,
        active_temporal_range_projector=projector,full60_actual_affine_Gauss_before=g,
        full60_actual_primal_Gauss_separate=primal_g,full60_actual_trial_KGz_separate=Kg,
        affine_primal_counting_check=gauss_affine_check,known_new59_particular_coefficients=particular,
        eight_open_source_domain_compatibility_coefficients=cokernel,
        phase_rhs_known_seven=rhs,phase_rhs_open31_coefficients=free_rhs,
        exact_source_compatibility_identity=source_compatibility,exact_open31_compatibility_identity=free_compatibility,
        computational_particular_phase_coefficients=candidate,computational_frame_reactions=reaction,
        cached_bordered_initial_solve_rows=cached_residual,fresh_Hphase_particular=Hcandidate,
        fresh_original277_rows=original_rows,fresh_plus_frame_reaction_rows=framed,
        fixed_computational_frame_rows=frame,actual_new59_particular_momentum_rows=new_Pi_rows,
        actual_old158_momentum_change_rows=old_preservation,actual_full60_affine_Gauss_after=actual_remaining_G,
        actual_temporal_cokernel_Gauss_after=L*op.rows(actual_remaining_G,np.arange(24,60)),
        native_response_momentum_before=trialPi,native_response_momentum_after_particular=actual_updated_Pi,
        target_native_response_momentum_particular=target_updated_Pi,
        bare_primal217_momentum_separate=op.value(c,'complete_D4_primal_momentum'),
        native_primal_old158_momentum_separate=op.value(r,'native_action_old158_momentum'),
        original_stored_old158_momentum_separate=op.value(r,'fixed_original_old158_canonical_momentum'),
        literal_gauge_phase_coefficients=Z,fresh_Noether_compression_on_particular=Z.transpose()*Hcandidate)
    arrays=dict(master368=op.target['master368'],coordinate_time=op.target['coordinate_time'],
        new59_position_indices=newq,old158_position_indices=oldq,full_pivot_temporal_rows=active,
        full_pivot_new59_columns=pivots,open31_free_new_momentum_coordinate_labels=free,
        eight_cokernel_temporal_labels=zero_rows)
    for key,a in values.items():
        arrays[key+'_high'],arrays[key+'_low']=op.split(a);arrays.update(op.exact.export_acb_exact_dyadic(a,key+'_exact'))
    archive=out/'actual_open_new59_affine_constitutive_family_and_fresh_seven.npz';_compressed_npz(archive,arrays)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):op.pin(Path(p).resolve())
    op.pin(Path(__file__))
    report=dict(classification='ACTUAL_EA02_OPEN_NEW59_AFFINE_CONSTITUTIVE_FAMILY',source_sha256=sha256(source).hexdigest(),
        input_and_source_sha256=dict(sorted(op.pins.items())),archive=dict(name=archive.name,bytes=archive.stat().st_size,sha256=sha256(archive.read_bytes()).hexdigest()),
        certified_new_momentum_rank=28,open_new_momentum_coordinates=31,retained_source_domain_cokernel_rows=8,
        momentum_family_formula='deltaPi_new=P*b_native_affine+N*c31; eight equations L*b_native_affine remain open',
        phase_family_relation='Hphase*deltaeta=rhs_known+rhs_free*c31; no physical c31 values selected',
        particular_momentum_upper=op.upper(particular),cokernel_load_upper=op.upper(cokernel),
        affine_primal_counting_check_upper=op.upper(gauss_affine_check),
        affine_coordinate_algebra_upper=max(op.upper(v)for v in algebra.values()),
        exact_source_compatibility_identity_upper=op.upper(source_compatibility),
        fresh_original277_upper=op.upper(original_rows),fresh_plus_frame_reaction_upper=op.upper(framed),
        fixed_computational_frame_upper=op.upper(frame),frame_reaction_upper=op.upper(reaction),
        old158_native_response_momentum_change_upper=op.upper(old_preservation),
        actual_new59_momentum_rows_upper=op.upper(new_Pi_rows),actual_full60_affine_Gauss_after_upper=op.upper(actual_remaining_G),
        actual_old24_mechanical_Gauss_after_upper=op.upper(op.rows(actual_remaining_G,np.arange(24))),
        actual_temporal36_Gauss_after_upper=op.upper(op.rows(actual_remaining_G,np.arange(24,60))),
        retained_cokernel_Gauss_after_upper=op.upper(L*op.rows(actual_remaining_G,np.arange(24,60))),
        fresh_Noether_compression_on_particular_upper=op.upper(Z.transpose()*Hcandidate),
        fresh_matvec_calls=op.calls,fresh_check_history=history,fresh_same_primal_germ_guards=germchecks,
        coefficient_check_tolerance=2e-10,known_particular_coefficients_original_rows_within_tolerance=closed,
        computational_kernel_origin_is_not_a_physical_zero_free_choice=True,
        all31_free_momentum_coordinates_remain_open=True,all8_exact_source_domain_compatibility_rows_retained=True,
        nonzero_cokernel_or_frame_reaction_discarded=False,bare_primal_momentum_kept_separate=True,
        primal_r_added_once_only_to_affine_column0=True,old158_fixed_as_diagnostic_not_physical_domain=True,
        new_primal_or_history_or_Cauchy_retraction_performed=False,new_retarded_evolution_or_outgoing_domain_solved=False,
        physical_radial_convergence_or_Maxwell226_validated=False,full_physical_derivative_passed=False,
        normalized_physical_two_spin_state=False,physical_muon_magnetic_moment=None,original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items()if k not in('input_and_source_sha256','archive','fresh_same_primal_germ_guards')}),flush=True)
    if not closed:raise ArithmeticError('Fresh original277/oldPi/fullGauss particular coefficient check failed; preserved readout is not admitted')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in('rank-folder','cauchy-folder','output'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--maximum-checks',type=int,default=3);a=p.parse_args()
    try:execute(a.rank_folder,a.cauchy_folder,a.output,maximum_checks=a.maximum_checks)
    except Exception as error:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise
