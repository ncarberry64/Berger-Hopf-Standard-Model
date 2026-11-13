"""Actual full217 position-force matvec supplement at the original ea02 cut.

Composes the frozen native phase backend; it does not edit it.  The
classical inherited action is differentiated on its fixed source/chart.
No dense Hxx, retarded history or physical outgoing operator is selected.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PHASE='audits/bhsm_original_ea02_d4_phase_operator_20261016.py'
PHASE_SHA='c2f11bd4890631c03afee8b0db1fe8a93e505a12071da9cd2b9923744e8a5c6d'
CORNERS='artifacts/muon_actual_source_corner_radial_jets_20261016'
OLD_Q=CORNERS+'/bhsm_original_ea02_same_field_seven_clock_20261016/final_run_1/actual_same_cut_position_H_R_seven.npz'
NEW_Q=CORNERS+'/bhsm_original_ea02_same_field_position_jacobi_20261016/run_1/actual_D4_same_field_position_Jacobi_and_affine_residual.npz'
CAUCHY='artifacts/muon_actual_cauchy_constraint_clock_20261016/bhsm_original_ea02_complete_d4_cauchy_20261016/run_1'
LITERAL='artifacts/muon_actual_native_coefficients_source_completion_20261016/bhsm_original_ea02_literal_seven_Jacobi_control_20261016/run_1/independent_literal_full59x7_Jacobi_and_source_operands.npz'


class ActualEa02D4PositionOperator:
    """Locked same-cut full217 force block H_q on arbitrary full746 rights."""
    def __init__(self,*,precision=256):
        p=ROOT/PHASE
        if sha256(p.read_bytes()).hexdigest()!=PHASE_SHA:raise ValueError('The reviewed frozen phase backend changed')
        spec=importlib.util.spec_from_file_location('ea02_frozen_phase_for_position_force',p)
        m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
        self.phase=m.ActualEa02D4PhaseOperator(precision=precision)
        self.phase.pin(PHASE,PHASE_SHA)
        self.acb_mat=self.phase.acb_mat;self.calls=0
        self.positionids=252+np.arange(self.phase.n)
        self.oldmap=np.asarray(self.phase.primal['old368_to_enlarged_child'],int)
        self.newq=np.asarray(self.phase.primal['new_position_indices'],int)
        if not np.array_equal(np.sort(np.r_[self.oldmap[:158],self.newq]),np.arange(217)):
            raise ValueError('All old158 and new59 position labels required')

    def apply_full_position(self,right):
        """Return H_q right and full literal application, with source contacts."""
        op=self.phase
        if right.nrows()!=746:raise ValueError('Full746 parent/child source rights required')
        rh,rl=op.split(right);zero=np.zeros(746,complex);self.calls+=1
        app=op.packed.phase_action_contractions(op.target['raw_pair'],op.target['reference_pair'],
            op.rep,op.P,op.maps,self.positionids,zero,zero,rh,rl,
            extra_base=op.base[op.extra-252],include_directional_first=False,include_parent_action=False,
            precision_bits=op.precision,material_chart_precision='independent_mp_same_material_equations',
            material_chart_owner=op.chart.anchored_material_chart4,allow_geometry_position_tests=True,
            nu_squared_action=op.params['nu_squared_action'],surface_gamma=op.params['surface_gamma'],
            export_exact_action_balls=True,right_exact=right)
        checks={k:op.upper(op.value(app,k)-op.value(op.primal,k))for k in
            ('child_point_coefficients','child_metric_density','child_wall_connection')}
        if max(checks.values())>2e-10:raise ValueError('Position matvec changed the original native primal/source germ')
        if not bool(app['fourth_implicit_profile_derivative_not_required']):
            raise ValueError('This base-Hessian supplement must not request a fourth clock contact')
        self.last_primal_germ_checks=checks
        return op.value(app,'phase_Hessian_on_actual_right'),app

    def apply_position(self,position):
        if position.nrows()!=217:raise ValueError('All217 position test-source coordinates required')
        right=self.acb_mat(746,position.ncols())
        for i,d in enumerate(self.positionids):
            for j in range(position.ncols()):right[int(d),j]=position[i,j]
        return self.apply_full_position(right)


def execute(cauchy_folder,output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    op=ActualEa02D4PositionOperator();ph=op.phase;M=op.acb_mat
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    cdir=Path(cauchy_folder);cm=ph.read(cdir/'result.json','f10d2140d0b5a24fe684c28d520a838ed04ca583828182b13d3043c7a25d2f94')
    c=ph.read(cdir/cm['archive']['name'],'7e11ceedc78de309d8944797982ed35aded42056f5b3fd9bccd871455591d5b3')
    old=ph.read(OLD_Q,'bb8450dc0bd00e805988eae1093f187b01c62269b0af8f1e142bda1fdcc982e0')
    new=ph.read(NEW_Q,'8c1cc039945303a0d4aabc956da3daf353b36085cc3403a5f20fdc7dbb466883')
    literal=ph.read(LITERAL,'8a9a46fd7c51a536aed136cb7449c8f6b4a39c342666728cbf98476fb9319a95')
    if not np.array_equal(c['master368'],ph.target['master368'])or c['coordinate_time'].item()!=ph.target['coordinate_time'].item():
        raise ValueError('Actual original full217 Cauchy data must share the exact primal/epoch')
    if not np.array_equal(new['master368'],ph.target['master368'])or new['coordinate_time'].item()!=ph.target['coordinate_time'].item():
        raise ValueError('New59 cached force belongs to another field/epoch')
    R=ph.value(c,'exact_carried_full_D4_field_seven')
    right_guard=ph.upper(R-ph.value(new,'actual_enlarged_seven_field'))
    oldR=ph.value(old,'actual_right')
    extracted=M(620,7)
    for i in range(252):
        for j in range(7):extracted[i,j]=R[i,j]
    for i,d in enumerate(op.oldmap):
        for j in range(7):extracted[252+i,j]=R[252+int(d),j]
    old_right_guard=ph.upper(extracted-oldR)
    if max(right_guard,old_right_guard)>1e-25:raise ValueError('Retained seven source/field rights must match both force references')
    # Two bounded external phase tests are controls only, not states or loads.
    phaseR=ph.rows(R,ph.phaseids);phase_tests=M(277,2);scales=[]
    for k,col in enumerate((1,4)):
        norm=ph.upper(ph.rows(phaseR.transpose(),[col]));scales.append(norm)
        if norm<=0:raise ValueError('Declared phase control must retain a nonzero actual column')
        for i in range(277):phase_tests[i,k]=phaseR[i,col]/norm
    bundle=M(746,9)
    for i in range(746):
        for j in range(7):bundle[i,j]=R[i,j]
    for i,d in enumerate(ph.phaseids):
        for j in range(2):bundle[int(d),7+j]=phase_tests[i,j]
    print(json.dumps(dict(stage='fresh_full217_position_force',position_rows=217,actual_rights=7,external_phase_tests=2)),flush=True)
    Hq,app=op.apply_full_position(bundle)
    _compressed_npz(out/'fresh_native_full217_position_force_on_actual_seven_and_two_phase.npz',app)
    fullHqR=ph.rows(Hq.transpose(),np.arange(7)).transpose()
    HqPhase=ph.rows(Hq.transpose(),np.arange(7,9)).transpose()
    old_check=ph.rows(fullHqR,op.oldmap[:158])-ph.value(old,'phase_Hessian_on_actual_right')
    new_check=ph.rows(fullHqR,op.newq)-ph.value(new,'actual_new_position_H_R')
    new_literal_check=ph.rows(fullHqR,op.newq)-ph.value(literal,'independent_literal_position_H_R')
    Gq=ph.value(app,'phase_gradient')
    old_Gq_check=ph.rows(Gq,op.oldmap[:158])-ph.value(old,'phase_gradient')
    new_Gq_check=ph.rows(Gq,op.newq)-ph.value(ph.primal,'new_position_Lq')
    PiDot=ph.value(c,'complete_D4_primal_momentum_clock')
    primal=Gq-PiDot
    # Independently reverse the q/phase test order through the frozen PHASE
    # block.  The two unit q directions exercise old geometry and new gauge.
    qtests=M(217,2);qtests[int(op.oldmap[0]),0]=1;qtests[int(op.newq[0]),1]=1
    qfull=M(746,2)
    for i,d in enumerate(op.positionids):
        for j in range(2):qfull[int(d),j]=qtests[i,j]
    print(json.dumps(dict(stage='fresh_reversed_phase_position_cross_transpose',phase_rows=277,position_tests=2)),flush=True)
    HphaseQ,papp=ph.apply_full(qfull)
    _compressed_npz(out/'fresh_native_phase_force_on_two_position_controls.npz',papp)
    cross=qtests.transpose()*HqPhase-HphaseQ.transpose()*phase_tests
    checks=dict(actual_seven_right_same_new59_reference=right_guard,actual_seven_right_same_old158_reference=old_right_guard,
        all_old158_force_vs_separate_cached_native=ph.upper(old_check),
        all_new59_force_vs_separate_cached_native=ph.upper(new_check),
        all_new59_force_vs_independent_literal_polynomial=ph.upper(new_literal_check),
        old158_primal_force_reproduction=ph.upper(old_Gq_check),
        new59_primal_force_reproduction=ph.upper(new_Gq_check),
        q_phase_analytic_cross_transpose=ph.upper(cross))
    if max(checks.values())>2e-10:raise ArithmeticError('Full217 force or independent q/phase incidence controls failed')
    affine_clock_target=M(fullHqR)
    for i in range(217):affine_clock_target[i,0]+=primal[i,0]
    values=dict(actual_full746_seven_field=R,actual_full217_position_force_on_seven=fullHqR,
        actual_full217_primal_Lq=Gq,actual_full217_primal_momentum_clock=PiDot,
        actual_full217_primal_Euler_residual=primal,required_affine_seven_canonical_momentum_clock=affine_clock_target,
        old158_force_vs_separate_cached_control=old_check,new59_force_vs_separate_cached_control=new_check,
        new59_force_vs_independent_literal_control=new_literal_check,
        external_two_phase_tests=phase_tests,external_two_position_tests=qtests,
        full217_force_on_external_phase_tests=HqPhase,full277_phase_on_external_position_tests=HphaseQ,
        analytic_q_phase_cross_transpose_rows=cross)
    arrays=dict(master368=ph.target['master368'],coordinate_time=ph.target['coordinate_time'],
        position_test_full_indices=op.positionids,old158_position_indices=op.oldmap[:158],
        new59_position_indices=op.newq,external_phase_test_scales=np.asarray(scales))
    for k,a in values.items():
        arrays[k+'_high'],arrays[k+'_low']=ph.split(a);arrays.update(ph.exact.export_acb_exact_dyadic(a,k+'_exact'))
    path=out/'actual_full217_position_force_backend_and_same_cut_controls.npz';_compressed_npz(path,arrays)
    for name,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):ph.pin(Path(p).resolve())
    ph.pin(Path(__file__))
    report=dict(classification='ACTUAL_ORIGINAL_EA02_FULL217_POSITION_FORCE_MATRIXFREE_SUPPLEMENT',
        source_sha256=sha256(source).hexdigest(),input_and_source_sha256=dict(sorted(ph.pins.items())),
        archive=dict(name=path.name,bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()),
        frozen_phase_backend_sha256=PHASE_SHA,position_rows=217,actual_right_columns=7,
        external_phase_test_columns=2,external_position_test_columns=2,
        fresh_position_force_calls=op.calls,fresh_reversed_phase_calls=ph.calls,
        fresh_same_primal_germ_guards=op.last_primal_germ_checks,
        fresh_reversed_same_primal_germ_guards=ph.last_primal_germ_checks,
        independent_same_cut_reference_and_cross_controls=checks,
        actual_full217_force_on_seven_upper=ph.upper(fullHqR),
        actual_full217_primal_Euler_residual_upper=ph.upper(primal),
        primal_Euler_is_retained_not_assumed_stationary=True,
        required_affine_clock_relation='deltaPi_dot=H_q*R+r_q*affine_column0',
        classical_inherited_action_parent_source_contacts_retained_once=True,
        full217_force_backend_on_general_full746_rights_available=True,
        fourth_clock_derivative_or_dense_Hxx_built=False,
        frozen_phase_backend_or_original_runtime_modified=False,
        canonical_momentum_family_free_coordinates_or_frames_selected=False,
        fresh_full_D4_continuous_clock_solved=False,
        native_unsquared_or_heat_exterior_operator_identification=False,
        physical_four_histories_or_outgoing_domain_completed=False,
        physical_total_derivative_radial_convergence_Maxwell226=False,
        physical_two_spin_normalization_or_muon_moment=False,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('independent_same_cut_reference_and_cross_controls','actual_full217_force_on_seven_upper','actual_full217_primal_Euler_residual_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cauchy-folder',type=Path,default=ROOT/CAUCHY);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(ROOT/'src'))
    try:execute(a.cauchy_folder,a.output)
    except Exception as e:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        raise

