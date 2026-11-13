"""Actual open D4 canonical-clock RHS on the original off-shell ea02 cut.

The parent response clock is supplied, qdot is the response velocity, and all
277 phase clocks remain unknown. Corrected native Tt/Wt and reference contacts
are used once. No31 free clock values, retarded domain or outer correction is
selected. This is the classical inherited action, not the AE4 heat operator.
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
POSITION='audits/bhsm_original_ea02_d4_position_operator_20261016.py'
POSITION_SHA='70670f411a2a11d301677359500be28fb9769f1557000b3262eb5939816ae389'
CLOCK='artifacts/muon_baton_zoo_maximal_current_realization_20261013/actual_same_cut_native_MP_matrixfree_continuous_clock_run_1/actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz'
CLOCK_SHA='18fcc0d4fa588c4fcd7aaa8822be76c132b660e0a2f223f7be55fcb9d8d41290'
FAMILY_SHA='972d919260a53d24bfebf77d3a6890f0cc2621f996cdc60fb62522c97464b83b'
FAMILY_ARCHIVE_SHA='7cb64de2130a2d3967f3a470132f0ae426ca3283da88d3ddc9b354fc040f15d4'
CAUCHY_SHA='63d04359f42673671169f61bcfa395b04fe5008c05912b65c95090c0a4458942'
CAUCHY_ARCHIVE_SHA='7e11ceedc78de309d8944797982ed35aded42056f5b3fd9bccd871455591d5b3'


class ActualEa02D4ContinuousClockRelation:
    """Open Hphase*phaseDot=f(R,sourceDot,b) with all original277 rows."""
    def __init__(self,*,precision=256):
        p=ROOT/POSITION
        if sha256(p.read_bytes()).hexdigest()!=POSITION_SHA:raise ValueError('Reviewed full217 force backend changed')
        spec=importlib.util.spec_from_file_location('ea02_position_for_open_clock',p)
        m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
        self.position=m.ActualEa02D4PositionOperator(precision=precision);self.phase=self.position.phase
        op=self.phase;op.pin(POSITION,POSITION_SHA)
        self.clock=op.read(CLOCK,CLOCK_SHA)
        if not np.array_equal(self.clock['master368'],op.target['master368'])or self.clock['coordinate_time'].item()!=op.target['coordinate_time'].item():raise ValueError('Actual native primal clock must share exact full368/time')
        self.h=op.value(op.primal,'complete_augmented_direction')
        if self.h.nrows()!=746 or self.h.ncols()!=1:raise ValueError('Complete746 primal material clock required')
        oldmap=np.asarray(op.primal['old368_to_enlarged_child'],int)
        h0=op.value(self.clock,'actual_total_master_clock_direction');embedded=op.acb_mat(746,1)
        for i in range(252):embedded[i,0]=h0[i,0]
        for i,d in enumerate(oldmap):embedded[252+int(d),0]=h0[252+i,0]
        if op.upper(self.h-embedded)>1e-50:raise ValueError('No different primal-clock or newly chosen higher radial velocity')
        self.Th=op.packed._coefficient_array(None,op.native_maps['extra_point_lift_total_clock_high'],op.native_maps['extra_point_lift_total_clock_low'])
        self.Wh=op.packed._coefficient_array(None,op.native_maps['extra_wall_lift_total_clock_high'],op.native_maps['extra_wall_lift_total_clock_low'])
        # Verify rather than assume that the published computational all-At
        # frame is this fixed coefficient selector. It is not physical BC.
        selector=op.acb_mat(36,277)
        for i in range(36):selector[i,241+i]=1
        self.frame_selector_defect=op.upper(op.F-selector)
        if self.frame_selector_defect!=0:raise ValueError('Moving computational frame would require its actual derivative')
        self.calls=0

    def phase_material_clock_contraction(self,right):
        """Return J_phase(h,right); rightDot is NOT assigned a value here."""
        op=self.phase
        if right.nrows()!=746:raise ValueError('Full parent/child response right required')
        rh,rl=op.split(right);hh,hl=op.split(self.h);self.calls+=1
        app=op.packed.phase_action_contractions(op.target['raw_pair'],op.target['reference_pair'],
            op.rep,op.P,op.maps,op.phaseids,hh[:,0],hl[:,0],rh,rl,
            extra_base=op.base[op.extra-252],reference_direction=self.clock['reference_affine_clock_once'],
            include_directional_first=True,include_parent_action=False,precision_bits=op.precision,
            material_chart_precision='independent_mp_same_material_equations',material_chart_owner=op.chart.anchored_material_chart4,
            extra_point_lift_first=self.Th,extra_wall_lift_first=self.Wh,
            nu_squared_action=op.params['nu_squared_action'],surface_gamma=op.params['surface_gamma'],
            export_exact_action_balls=True,right_exact=right,direction_exact=self.h)
        checks={}
        for key in('child_point_coefficients','child_metric_density','child_wall_connection'):
            checks[key]=op.upper(op.value(app,key)-op.value(op.primal,key))
            derivative=key+'_directional_first'
            checks[derivative]=op.upper(op.value(app,derivative)-op.value(op.primal,derivative))
        if max(checks.values())>2e-10:raise ValueError('Mixed clock application changed the reviewed base or directional-first germ')
        self.last_clock_germ_checks=checks
        return op.value(app,'phase_Hessian_first_on_actual_right'),app

    def apply_clock_rhs(self,right,parent_source_clock,affine_coefficients,primal_momentum_clock):
        """Return full277 RHS and exact factored operands, without solving it.

        parent_source_clock is the actual response-source derivative, distinct
        from the primal h. affine_coefficients is an explicit1 by nr b row.
        The unknown child phaseDot occupies a separate277-coordinate block.
        """
        op=self.phase;ncols=right.ncols()
        if right.nrows()!=746 or parent_source_clock.nrows()!=252 or parent_source_clock.ncols()!=ncols or affine_coefficients.nrows()!=1 or affine_coefficients.ncols()!=ncols:raise ValueError('Complete response/source and explicit affine incidence required')
        if primal_momentum_clock.nrows()!=217 or primal_momentum_clock.ncols()!=1:raise ValueError('Actual bare-primal217 momentum clock required')
        known=op.acb_mat(746,ncols)
        for i in range(252):
            for j in range(ncols):known[i,j]=parent_source_clock[i,j]
        for i in range(217):
            for j in range(ncols):known[252+i,j]=right[252+217+i,j]
        Hq,qapp=self.position.apply_full_position(right)
        J,happ=self.phase_material_clock_contraction(right)
        Hknown,kapp=op.apply_full(known)
        Gq=op.value(qapp,'phase_gradient');Gphase=op.value(happ,'phase_gradient')
        Gtphase=op.value(happ,'phase_gradient_first');Euler=Gq-primal_momentum_clock
        canonical_target=op.acb_mat(277,ncols)
        for i in range(217):
            for j in range(ncols):canonical_target[i,j]=Hq[i,j]+Euler[i,0]*affine_coefficients[0,j]
        for i in range(60):
            for j in range(ncols):canonical_target[217+i,j]=-Gtphase[217+i,0]*affine_coefficients[0,j]
        rhs=canonical_target-J-Hknown
        values=dict(known_parent_and_qdot_clock=known,actual_full217_Hq_R=Hq,
            actual_phase_material_clock_H_R=J,actual_phase_H_known_parent_and_qdot=Hknown,
            actual_bare_primal217_Lq=Gq,actual_bare_primal217_Pi_dot=primal_momentum_clock,
            actual_bare_primal217_Euler=Euler,actual_bare_primal277_gradient=Gphase,
            actual_bare_primal277_gradient_total_clock=Gtphase,canonical_target_with_primal_affine_once=canonical_target,
            open_phase277_clock_rhs=rhs,actual_complete746_primal_clock=self.h,
            actual_parent_response_source_clock=parent_source_clock,affine_column_incidence=affine_coefficients)
        return rhs,values,dict(position=qapp,material_clock=happ,known_clock=kapp)


def execute(family_folder,cauchy_folder,output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    operator=ActualEa02D4ContinuousClockRelation();op=operator.phase
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    def packet(folder,source_sha,archive_sha):
        folder=Path(folder).resolve();m=op.read(folder/'result.json');op.pin(folder/'executed_producer.py',source_sha)
        if m['source_sha256']!=source_sha or m['archive']['sha256']!=archive_sha:raise ValueError('Reviewed source/operand archive required')
        return op.read(folder/m['archive']['name'],archive_sha)
    f=packet(family_folder,FAMILY_SHA,FAMILY_ARCHIVE_SHA);c=packet(cauchy_folder,CAUCHY_SHA,CAUCHY_ARCHIVE_SHA)
    for z in(f,c):
        if not np.array_equal(z['master368'],op.target['master368'])or z['coordinate_time'].item()!=op.target['coordinate_time'].item():raise ValueError('No original-cut/field/source splice')
    right=op.value(c,'exact_carried_full_D4_field_seven');part=op.value(f,'computational_particular_phase_coefficients')
    for i,d in enumerate(op.phaseids):
        for j in range(7):right[int(d),j]+=part[i,j]
    parent_clock=op.value(c,'actual_parent_sourceDot');b=op.acb_mat(1,7);b[0,0]=1
    print(json.dumps(dict(stage='fresh_open_family_continuous_clock_rhs',known_rays=7,position_rows=217,phase_rows=277)),flush=True)
    rhs,values,apps=operator.apply_clock_rhs(right,parent_clock,b,op.value(c,'complete_D4_primal_momentum_clock'))
    for key,app in apps.items():_compressed_npz(out/f'fresh_{key}_application.npz',app)
    Z=op.value(f,'literal_gauge_phase_coefficients');L=op.acb_mat(8,36)
    for i,j in enumerate(f['eight_cokernel_temporal_labels']):L[i,int(j)]=1
    compression=Z.transpose()*rhs;cokernel=L*compression
    values.update(actual_open_family_particular_full746_right=right,
        all36_clock_compatibility_compression=compression,eight_clock_source_domain_cokernel_compression=cokernel,
        actual_initial_full60_affine_Gauss_residual_retained=op.value(f,'actual_full60_affine_Gauss_after'),
        actual_response217_momentum_particular=op.value(f,'native_response_momentum_after_particular'),
        actual_bare_primal217_momentum_separate=op.value(f,'bare_primal217_momentum_separate'),
        symbolic_open31_phase_rhs_coefficient_map=op.value(f,'phase_rhs_open31_coefficients'))
    # The Pi-dot portion of this fresh mixed gradient must be the same actual
    # bare-primal clock, not a response clock or zero higher-coordinate seed.
    PiDot_check=op.rows(values['actual_bare_primal277_gradient_total_clock'],np.arange(217))-values['actual_bare_primal217_Pi_dot']
    values['same_bare_primal217_Pi_dot_guard']=PiDot_check
    if op.upper(PiDot_check)>2e-10:raise ValueError('Fresh mixed germ changed the full217 bare-primal momentum clock')
    arrays=dict(master368=op.target['master368'],coordinate_time=op.target['coordinate_time'],
        open31_momentum_coordinate_labels=f['open31_free_new_momentum_coordinate_labels'],
        eight_cokernel_temporal_labels=f['eight_cokernel_temporal_labels'])
    for key,a in values.items():
        arrays[key+'_high'],arrays[key+'_low']=op.split(a);arrays.update(op.exact.export_acb_exact_dyadic(a,key+'_exact'))
    archive=out/'actual_open_D4_continuous_clock_relation_and_known_seven_rhs.npz';_compressed_npz(archive,arrays)
    for name,module in list(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if path and(name=='bhsm'or name.startswith('bhsm.'))and Path(path).resolve().is_relative_to(ROOT):op.pin(Path(path).resolve())
    op.pin(Path(__file__))
    report=dict(classification='ACTUAL_ORIGINAL_EA02_OPEN_D4_CONTINUOUS_CANONICAL_CLOCK_RELATION',source_sha256=sha256(source).hexdigest(),
        input_and_source_sha256=dict(sorted(op.pins.items())),archive=dict(name=archive.name,bytes=archive.stat().st_size,sha256=sha256(archive.read_bytes()).hexdigest()),
        relation='Hphase*unknown_phaseDot=[HqR+rE*b; -Gt_G*b]-J_phase(h,R)-Hphase_full*known(parentDot,qDot=R_v)',
        response_Pi_dot_target='HqR+(Lq0-dtLv0)*b; total_Pi_dot adds bare dtLv0 separately',
        actual_full217_Euler_upper=op.upper(values['actual_bare_primal217_Euler']),
        full277_known_clock_rhs_upper=op.upper(rhs),all36_clock_compatibility_upper=op.upper(compression),
        eight_source_domain_clock_cokernel_upper=op.upper(cokernel),
        primal217_Pi_dot_reproduction_upper=op.upper(PiDot_check),
        same_base_and_material_directional_first_germ_guards=operator.last_clock_germ_checks,
        fixed_computational_frame_selector_defect=operator.frame_selector_defect,
        corrected_native_point_and_wall_clock_incidence_used=True,reference_clock_included_once=True,
        known_qDot_uses_UPDATED_particular_velocity=True,parent_response_sourceDot_kept_actual=True,
        unknown277_phase_clock_assigned=False,open31_free_coordinate_or_clock_values_selected=False,
        eight_compatibility_rows_or_offshell_Noether_contacts_dropped=False,
        physical_generator_variation_not_replaced_by_derivative_of_cached_Z=True,
        source_domain_Noether_terms_not_assumed_zero=True,primal_stationarity_assumed=False,
        unknown_source_q_or_outgoing_complements_not_declared_new_parameters=True,
        complete_continuous_clock_or_chronological_retarded_solution_claimed=False,
        classical_Hessian_identified_with_native_Dstrat_or_heat=False,physical_total_derivative_passed=False,
        Maxwell226_radial_or_spin_moment_validated=False,original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items()if k not in('input_and_source_sha256','archive')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in('family-folder','cauchy-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    try:execute(a.family_folder,a.cauchy_folder,a.output)
    except Exception as error:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise
