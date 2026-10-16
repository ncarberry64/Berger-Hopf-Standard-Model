"""Complete action-derived D4 Cauchy germs on the proven original ea02 cut.

Composes saved native217 momentum/clock rows on the same carried seven
field/source directions. No new action/history solve, retraction, assumed
response clock, physical correction or outgoing condition is introduced.
The three-port birth0 section is deliberately NOT used or spliced here.
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
PUB='artifacts/muon_actual_source_corner_radial_jets_20261016'
SEVEN=PUB+'/bhsm_original_ea02_same_field_seven_clock_20261016/final_run_1'
JAC=PUB+'/bhsm_original_ea02_same_field_position_jacobi_20261016/run_1'
GAUSS=PUB+'/bhsm_original_ea02_same_field_gauss_jacobi_20261016/run_1'
PRIMAL='artifacts/muon_actual_radial_cauchy_common_forms_20261016/bhsm_original_ea02_same_field_position_euler_20261016/native_epoch_D4_run_1'
CURRENT='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
TARGET=CURRENT+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
CLOCK=CURRENT+'/actual_same_cut_native_MP_matrixfree_continuous_clock_run_1/actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz'
RUNTIME=CURRENT+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'


def run(output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
    def pin(path,expected=None):
        p=Path(path);p=p if p.is_absolute()else ROOT/p;key=p.relative_to(ROOT).as_posix();h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('Frozen epoch/source changed: '+key)
        pins[key]=h;return p
    def read(path,expected=None):
        p=pin(path,expected)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def imported(name,path):
        p=pin(path);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec)
        sys.modules[name]=m;spec.loader.exec_module(m);return m
    sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    ctx.prec=288
    imported('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    exact=imported('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    def val(z,k):
        return exact.parse_acb_exact_dyadic(z,k+'_exact')if k+'_exact_real_mid_mantissa'in z else _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    rows=lambda a,ix:acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ix])
    def receipt(folder,source):
        j=read(folder+'/result.json')
        if j['source_sha256']!=source:raise ValueError('Reviewed source identity required')
        pin(folder+'/executed_producer.py',source);return j
    cm=receipt(SEVEN,'95a64f63e2a541abf698ce7e65afc75a3f4eddb5932f239b74458a171e5be1be')
    jm=receipt(JAC,'a761a939cffb6b426ac254f59a8263feeb644ebdfc3843f69b061ee607b4ba3f')
    pm=receipt(PRIMAL,'d6b0dbb2e34185011f243f7f571da2f536ebc58c6138fab380f856a2f5db96b9')
    gm=receipt(GAUSS,'519371278ad0884047147d7b97364d2af7f5f7ae145d15cda1549b56cce35902')
    if not cm['admitted_original210_and_frame7_clock']:raise ValueError('Actual original210+7 response clock must pass first')
    def archive(folder,name,meta=None):
        expected=None
        if meta is not None:
            x=meta.get('archives',{}).get(name)
            if x is not None:expected=x['sha256']
            elif meta.get('archive',{}).get('name')==name:expected=meta['archive']['sha256']
        return read(folder+'/'+name,expected)
    target=read(TARGET,'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b')
    clock=read(CLOCK,'18fcc0d4fa588c4fcd7aaa8822be76c132b660e0a2f223f7be55fcb9d8d41290')
    old=archive(SEVEN,'actual_same_cut_phase_h_R_seven.npz',cm)
    response=archive(SEVEN,'actual_same_cut_seven_continuous_response_clock.npz',cm)
    olddot=archive(SEVEN,'iteration_01_fresh_original210_seven_clock.npz',cm)
    new=archive(JAC,'actual_D4_position_velocity_h_R_seven.npz')
    newdot=archive(JAC,'actual_D4_velocity_Rdot_seven.npz')
    jac=archive(JAC,'actual_D4_same_field_position_Jacobi_and_affine_residual.npz',jm)
    primal=archive(PRIMAL,'same_field_primal_position_Euler_and_Gauss.npz',pm)
    # Name resolved from the reviewed all60 Gauss receipt, not a new formation.
    gname=gm['archive']['name'];gauss=archive(GAUSS,gname,gm)
    for z in(clock,response,jac,primal):
        if not np.array_equal(z['master368'],target['master368'])or z['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('A field/clock/principal-branch splice is forbidden')
    R0,Rd0=val(response,'actual_complete_seven_response'),val(response,'actual_complete_seven_response_clock')
    R,Rd=val(jac,'actual_enlarged_seven_field'),val(jac,'actual_enlarged_seven_field_clock')
    n=217;embedding=np.asarray(primal['old368_to_enlarged_child'],int);newq=np.asarray(primal['new_position_indices'],int)
    if len(embedding)!=368 or len(newq)!=59 or not np.array_equal(embedding[158:316],n+embedding[:158]):raise ValueError('Complete paired old368/new59 incidence required')
    if not np.array_equal(newq,jac['new_position_indices']):raise ValueError('Same new velocity ordering required')
    for a,b in((val(old,'actual_right'),R0),(val(new,'actual_right'),R),(val(newdot,'actual_right'),Rd),(val(olddot,'actual_right'),Rd0)):
        if _upper(a-b)>1e-25:raise ValueError('Actual source/response/response-clock operand changed')
    for i,d in enumerate(embedding):
        if _upper(rows(R,[252+int(d)])-rows(R0,[252+i]))>1e-25 or _upper(rows(Rd,[252+int(d)])-rows(Rd0,[252+i]))>1e-25:raise ValueError('Complete carried field/time directions must embed exactly')
    if max(_upper(rows(R,np.arange(252))),_upper(rows(Rd,np.arange(252))))>0:
        if _upper(rows(R,np.arange(252))-rows(R0,np.arange(252)))>1e-25 or _upper(rows(Rd,np.arange(252))-val(response,'actual_parent_seven_source_clock'))>1e-25:raise ValueError('Parent source/sourceDot changed')
    if not np.array_equal(old['test_full_action_indices'],252+np.arange(158,368))or not np.array_equal(new['test_full_action_indices'],252+np.r_[newq,n+newq]):raise ValueError('Exact old/new momentum test rows required')
    dp,dpt,pi,pit=acb_mat(n,7),acb_mat(n,7),acb_mat(n,1),acb_mat(n,1)
    oldHR,oldhHR,oldHRd=(val(z,k)for z,k in((old,'phase_Hessian_on_actual_right'),(old,'phase_Hessian_first_on_actual_right'),(olddot,'phase_Hessian_on_actual_right')))
    oldg,oldgt=val(old,'phase_gradient'),val(old,'phase_gradient_first')
    for i,d in enumerate(embedding[:158]):
        pi[int(d),0],pit[int(d),0]=oldg[i,0],oldgt[i,0]
        for j in range(7):dp[int(d),j],dpt[int(d),j]=oldHR[i,j],oldhHR[i,j]+oldHRd[i,j]
    newHR,newhHR,newHRd=(val(z,k)for z,k in((new,'phase_Hessian_on_actual_right'),(new,'phase_Hessian_first_on_actual_right'),(newdot,'phase_Hessian_on_actual_right')))
    newg,newgt=val(primal,'new_position_Lv'),val(primal,'new_position_total_clock_Lv')
    for i,d in enumerate(newq):
        pi[int(d),0],pit[int(d),0]=newg[i,0],newgt[i,0]
        for j in range(7):dp[int(d),j],dpt[int(d),j]=newHR[59+i,j],newhHR[59+i,j]+newHRd[i,j]
    Q,Qd=acb_mat(2*n,7),acb_mat(2*n,7)
    for i in range(n):
        for j in range(7):Q[i,j],Q[n+i,j]=R[252+i,j],dp[i,j];Qd[i,j],Qd[n+i,j]=Rd[252+i,j],dpt[i,j]
    # The exact native canonical derivative reproduces the independently
    # exported Jacobi row: KqR = HqR - (deltaPi)_dot.
    jacobi=val(jac,'actual_new_position_Kz_trial')
    kcheck=rows(newHR,np.arange(59))-rows(dpt,newq)-jacobi
    gcheck=rows(pi,newq)-val(primal,'new_position_Lv')
    # Full reference-time first on the carried old functions is not a newly
    # solved higher-radial response. Its new field coefficients remain0 only
    # in the same-function representation, not as a physical solution claim.
    if max(_upper(kcheck),_upper(gcheck))>1e-25:raise ValueError('Canonical/Jacobi incidence changed')
    # All supplied point/density/wall base+primal-clock germs must coincide.
    germ_checks={}
    for key in('child_point_coefficients','child_metric_density','child_wall_connection'):
        for suffix in('','_directional_first'):
            k=key+suffix;germ_checks[k]=_upper(val(old,k)-val(new,k))
    if max(germ_checks.values())>2e-10:raise ValueError('The full physical coefficient/clock germ changed')
    oldcutPi=val(clock,'phase_gradient')
    primalcheck=_upper(rows(oldg,np.arange(158))-rows(oldcutPi,np.arange(158)))
    if primalcheck>2e-10:raise ValueError('Primal canonical momentum belongs to a different epoch')
    arrays=dict(coordinate_time=target['coordinate_time'],master368=target['master368'],
        raw_pair=target['raw_pair'],reference_pair=target['reference_pair'],enlarged_dynamic_count=np.asarray(n),
        old368_to_complete_D4_child=embedding,new59_position_indices=newq)
    values=dict(complete_D4_source_complete_canonical_seven=Q,complete_D4_source_complete_canonical_seven_clock=Qd,
        complete_D4_primal_momentum=pi,complete_D4_primal_momentum_clock=pit,
        complete_D4_momentum_seven=dp,complete_D4_momentum_seven_clock=dpt,
        exact_carried_full_D4_field_seven=R,exact_carried_full_D4_field_seven_clock=Rd,
        actual_parent_sourceDot=val(response,'actual_parent_seven_source_clock'),
        complete_D4_primal_algebraic_r=val(primal,'enlarged_primal_Gauss_r'),
        native_new_position_Jacobi_identity_rows=kcheck)
    # Preserve every all60 Gauss/Jacobi operand under its reviewed name.
    for k in gauss:
        if k.endswith('_high')and('Gauss'in k or'gauss'in k):values['all60_saved_'+k[:-5]]=val(gauss,k[:-5])
    for k,a in values.items():
        arrays[k+'_high'],arrays[k+'_low']=_split(a);arrays.update(exact.export_acb_exact_dyadic(a,k+'_exact'))
    archive=out/'actual_ea02_complete_D4_cauchy_momentum_clock_and_source_germs.npz';_compressed_npz(archive,arrays)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):pin(Path(p).resolve())
    for path in('src/bhsm/interface/muon_retarded_profile_cell_action.py','src/bhsm/interface/muon_fixed_source_forced_canonical.py','src/bhsm/interface/muon_causal_cauchy_history_return.py'):pin(path)
    pin(Path(__file__))
    report=dict(classification='ACTUAL_ORIGINAL_EA02_COMPLETE_D4_SOURCE_COMPLETE_CANONICAL_GERMS',
        source_sha256=sha256(producer).hexdigest(),input_and_source_sha256=dict(sorted(pins.items())),
        archive=dict(name=archive.name,bytes=archive.stat().st_size,sha256=sha256(archive.read_bytes()).hexdigest()),
        coefficient_clock_germ_checks=germ_checks,primal_old158_momentum_epoch_check_upper=primalcheck,
        exact_new59_canonical_Jacobi_identity_upper=_upper(kcheck),
        complete217_primal_momentum_upper=_upper(pi),new59_primal_momentum_upper=_upper(rows(pi,newq)),
        complete217_seven_momentum_upper=_upper(dp),new59_seven_momentum_upper=_upper(rows(dp,newq)),
        complete217_seven_momentum_clock_upper=_upper(dpt),
        exact_original_ea02_primal_source_response_clock_preserved=True,sourceDot_or_Rdot_zero_assigned=False,
        birth0_section_spliced=False,source_complete_momentum_and_Gauss_loads_kept=True,
        action_or_D5_or_history_replayed=False,new_action_Hxx_or_field_solve=False,
        local_retarded_impulse_sign='For E=Lq-dtPi+Jdelta=0, Pi_plus-Pi_minus=J; q_continuous for a momentum impulse.',
        regular_source_velocity_contact='Pi=deltaLv+g_v is source_complete; switching g_v alone jumps deltaLv by-minusg_v, not fullPi.',
        physical_new_radial_response_or_mean_solved=False,physical_outgoing_or_full_derivative_or_spin_moment=False,
        original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items()if k not in('input_and_source_sha256','archive')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    try:run(a.output)
    except Exception as e:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise
