"""Fresh matrix-free native D4 phase operator at the exact original ea02 cut.

The cached original-binary277 block and literal At36 frame are diagnostic
preconditioners only. Every fresh matvec uses the reviewed native material
chart and corrected point/wall incidences on the unchanged full368 primal.
No dense277-right campaign, Hxx, history solve or physical projection occurs.
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
CURRENT='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
TARGET=CURRENT+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
RUNTIME=CURRENT+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'
PRECOND=RADIAL+'/actual_common_cut_degree4_complete_phase_blocks_run_1/actual_same_current_complete_phase_and_literal_temporal_generator_operands.npz'
PRIMAL='artifacts/muon_actual_radial_cauchy_common_forms_20261016/bhsm_original_ea02_same_field_position_euler_20261016/native_epoch_D4_run_1'


class ActualEa02D4PhaseOperator:
    """The locked actual cut; supplied zeros are matvec tests, not exterior data."""
    def __init__(self,*,precision=256):
        sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
        from flint import ctx,acb_mat
        from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
        from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
        from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
        self.precision=int(precision);ctx.prec=self.precision;self.acb_mat=acb_mat
        self.matrix,self.upper,self.split=_matrix,_upper,_split;self.pins={};self.calls=0
        self.imported('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
        self.exact=self.imported('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
        self.pin(RUNTIME+'/new620_fresh_actual_native_MP_scalar_imported_runtime.py','8fcc5e3a5c0e2724cf24789c8326fb9725601f5a991e4f5e0b3189a27c0ca5fe')
        self.pin(RUNTIME+'/new620_fresh_same_material_equations_chart4_imported_runtime.py','0aca698c5906bccaf0ac022a31f3d5f78aa4ec6e245132e893bb50295c2be212')
        self.packed=self.imported('ea02_D4_phase_matvec_native_scalar',RUNTIME+'/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
        self.chart=self.imported('ea02_D4_phase_matvec_material_chart',RUNTIME+'/new620_fresh_same_material_equations_chart4_imported_runtime.py')
        self.target=self.read(TARGET,'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b')
        self.primal=self.read(PRIMAL+'/same_field_primal_position_Euler_and_Gauss.npz')
        self.native_maps=self.read(PRIMAL+'/native_clock_reconstructed_epoch_point_wall_maps.npz')
        self.maps=self.read(RADIAL+'/actual_linear_cut_degree4_complete_clock_epoch_maps_run_1/actual_degree_04_complete_clock_covariant_product_epoch_maps.npz')
        self.cache=self.read(PRECOND,'a54ca8625af892a58ad73f9dd3c993096db417f43f6bc030334f226d72f6201a')
        self.params=self.read('artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
        for z in(self.primal,self.cache,self.maps,self.native_maps):
            if z['coordinate_time'].item()!=self.target['coordinate_time'].item():raise ValueError('Different actual constitutive epoch')
        if not np.array_equal(self.primal['master368'],self.target['master368'])or not np.array_equal(self.maps['actual_nonzero_current_master368'],self.target['master368']):raise ValueError('No retraction/principal-branch splice')
        self.full,self.n=746,217;self.child=494;self.phaseids=252+np.arange(self.n,self.child)
        if int(self.maps['full_dimension'])!=self.full or int(self.maps['dynamic_count'])!=self.n or not np.array_equal(self.cache['phase_to_full_action_indices'],self.phaseids):raise ValueError('Actual full child277 phase chart required')
        self.phase_map_clock_change={}
        extra=np.asarray(self.maps['extra_coordinates_to_full'],int);phase=extra>=252+self.n
        for k in('extra_point_lift','extra_wall_lift'):
            for part in('high','low'):
                old,new=self.maps[k+'_'+part],self.native_maps[k+'_'+part]
                self.phase_map_clock_change[k+'_'+part]=float(np.max(abs(old[...,phase]-new[...,phase]),initial=0))
                self.maps[k+'_'+part]=new
        phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
        self.pins.update(phase['input_hashes']);self.rep=dict(phase['representation']);self.P=phase['coordinates']['lift']
        for k,rk in(('original_gauge_basis','gauge_basis'),('original_gauge_radial_basis','gauge_radial_basis'),('original_wall_trace_map','wall_trace_map')):
            v=self.maps[k+'_high']+self.maps[k+'_low']
            if np.any(v.imag!=0):raise ValueError('Do not project an actual complex basis')
            self.rep[rk]=v.real if rk=='wall_trace_map'else v.real.reshape(48,80,1,5,4)
        self.extra=extra;self.base=self.primal['same_field_child_coefficients']
        self.H0,self.F,self.Z=(self.value(self.cache,k)for k in('actual_complete_child_phase_Hessian','literal_all_At_frames','actual_literal_temporal_generators'))
        if (self.H0.nrows(),self.H0.ncols(),self.F.nrows(),self.F.ncols(),self.Z.nrows(),self.Z.ncols())!=(277,277,36,277,277,36):raise ValueError('Explicit cached277+At36 preconditioner only')
        self.border=acb_mat(313,313)
        for i in range(277):
            for j in range(277):self.border[i,j]=self.H0[i,j]
            for j in range(36):self.border[i,277+j]=self.F[j,i];self.border[277+j,i]=self.F[j,i]

    def pin(self,p,expected=None):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('Exact input/source bytes changed: '+str(p))
        self.pins[p.relative_to(ROOT).as_posix()if p.is_relative_to(ROOT)else str(p)]=h;return p

    def read(self,p,expected=None):
        p=self.pin(p,expected)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}

    def imported(self,name,path):
        spec=importlib.util.spec_from_file_location(name,self.pin(path));m=importlib.util.module_from_spec(spec)
        sys.modules[name]=m;spec.loader.exec_module(m);return m

    def value(self,z,k):
        return self.exact.parse_acb_exact_dyadic(z,k+'_exact')if k+'_exact_real_mid_mantissa'in z else self.matrix(z[k+'_high'])+self.matrix(z[k+'_low'])

    def rows(self,a,ids):return self.acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ids])

    def apply_phase(self,phase):
        if phase.nrows()!=277:raise ValueError('Every original217v+60y phase row required')
        right=self.acb_mat(self.full,phase.ncols())
        for i,d in enumerate(self.phaseids):
            for j in range(phase.ncols()):right[int(d),j]=phase[i,j]
        return self.apply_full(right)

    def apply_full(self,right):
        if right.nrows()!=self.full:raise ValueError('Full746 parent/child source incidence required')
        rh,rl=self.split(right);zero=np.zeros(self.full,complex);self.calls+=1
        app=self.packed.phase_action_contractions(self.target['raw_pair'],self.target['reference_pair'],
            self.rep,self.P,self.maps,self.phaseids,zero,zero,rh,rl,
            extra_base=self.base[self.extra-252],include_directional_first=False,include_parent_action=False,
            precision_bits=self.precision,material_chart_precision='independent_mp_same_material_equations',
            material_chart_owner=self.chart.anchored_material_chart4,
            nu_squared_action=self.params['nu_squared_action'],surface_gamma=self.params['surface_gamma'],
            export_exact_action_balls=True,right_exact=right)
        checks={k:self.upper(self.value(app,k)-self.value(self.primal,k))for k in
            ('child_point_coefficients','child_metric_density','child_wall_connection')}
        if max(checks.values())>2e-10:raise ValueError('Fresh phase application changed the reviewed primal/source coefficient germ')
        self.last_primal_germ_checks=checks
        return self.value(app,'phase_Hessian_on_actual_right'),app

    def precondition(self,rhs,frame_rhs=None):
        """Return candidate phase/reactions only; original equations are NOT passed."""
        if rhs.nrows()!=277:raise ValueError('All original phase RHS rows required')
        if frame_rhs is None:frame_rhs=self.acb_mat(36,rhs.ncols())
        if frame_rhs.nrows()!=36 or frame_rhs.ncols()!=rhs.ncols():raise ValueError('Explicit36 frame RHS rows required')
        full=self.acb_mat(313,rhs.ncols())
        for i in range(277):
            for j in range(rhs.ncols()):full[i,j]=rhs[i,j]
        for i in range(36):
            for j in range(rhs.ncols()):full[277+i,j]=frame_rhs[i,j]
        result=self.border.solve(full)
        return self.rows(result,np.arange(277)),self.rows(result,np.arange(277,313)),self.border*result-full


def execute(cauchy_folder,output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    op=ActualEa02D4PhaseOperator();acb_mat=op.acb_mat
    cm=op.read(Path(cauchy_folder)/'result.json','f10d2140d0b5a24fe684c28d520a838ed04ca583828182b13d3043c7a25d2f94')
    c=op.read(Path(cauchy_folder)/cm['archive']['name'],'7e11ceedc78de309d8944797982ed35aded42056f5b3fd9bccd871455591d5b3')
    R=op.value(c,'exact_carried_full_D4_field_seven');phase=op.rows(R,op.phaseids)
    # Scale only these external operator tests; no action norm, state or
    # minimum-norm completion is inferred from the coefficient maximum.
    v=acb_mat(277,2);normalizations=[]
    for k,col in enumerate((1,4)):
        norm=max(op.upper(op.rows(phase,[i]))for i in range(277));normalizations.append(norm)
        for i in range(277):v[i,k]=phase[i,col]/norm
    print(json.dumps(dict(stage='actual_native_D4_phase_actual_direction_matvec',rights=2,phase_rows=277)),flush=True)
    Hv,app=op.apply_phase(v);germchecks={'actual_two_phase':op.last_primal_germ_checks.copy()};_compressed_npz(out/'fresh_native_actual_two_phase_matvecs.npz',app)
    symmetry=v.transpose()*Hv-Hv.transpose()*v
    print(json.dumps(dict(stage='actual_native_D4_phase_literal_gauge_matvec',rights=6,phase_rows=277)),flush=True)
    gaugeids=np.array([0,3,8,15,24,35]);Z=acb_mat(277,len(gaugeids))
    for i in range(277):
        for j,d in enumerate(gaugeids):Z[i,j]=op.Z[i,int(d)]
    HZ,zapp=op.apply_phase(Z);germchecks['six_gauge']=op.last_primal_germ_checks.copy();_compressed_npz(out/'fresh_native_six_literal_temporal_gauge_matvecs.npz',zapp)
    # Literal all-At frames are diagnostic/preconditioning operands, not a
    # declaration that their reactions satisfy the unframed action equations.
    frame=op.F*v;pre,reaction,pre_rows=op.precondition(Hv,frame)
    print(json.dumps(dict(stage='actual_native_D4_phase_preconditioned_candidate_check',rights=2)),flush=True)
    checked,papp=op.apply_phase(pre);germchecks['preconditioned_candidate']=op.last_primal_germ_checks.copy();_compressed_npz(out/'fresh_native_preconditioned_candidate_two_matvecs.npz',papp)
    original=checked-Hv;framed=original+op.F.transpose()*reaction
    arrays=dict(selected_gauge_columns=gaugeids,external_test_coefficient_max_scales=np.asarray(normalizations))
    values=dict(actual_two_phase_test=v,fresh_native_two_phase_Hv=Hv,
        analytic_transpose_symmetry_rows=symmetry,cached_phase_vs_native_on_tests=op.H0*v-Hv,
        selected_literal_temporal_gauge_phase=Z,fresh_native_gauge_rows=HZ,
        explicit_cached_preconditioner_candidate=pre,explicit_cached_preconditioner_reaction=reaction,
        cached_bordered_solve_rows=pre_rows,fresh_original_preconditioned_rows=original,
        fresh_plus_frame_reaction_rows=framed,preconditioned_fixed_frame_rows=op.F*pre-frame,
        cached_H0_full_gauge_rows=op.H0*op.Z,
        literal_frame_generator_identity=op.F*op.Z-op.matrix(np.eye(36)))
    for k,a in values.items():
        arrays[k+'_high'],arrays[k+'_low']=op.split(a);arrays.update(op.exact.export_acb_exact_dyadic(a,k+'_exact'))
    archive=out/'actual_native_D4_matrixfree_phase_backend_controls.npz';_compressed_npz(archive,arrays)
    if max(op.upper(symmetry),op.upper(values['literal_frame_generator_identity']),
            op.upper(HZ),op.upper(values['cached_phase_vs_native_on_tests']),op.upper(original),
            op.upper(framed),op.upper(values['preconditioned_fixed_frame_rows']))>2e-10:
        raise ArithmeticError('Actual phase direction/gauge/preconditioned original-row closure failed')
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):op.pin(Path(p).resolve())
    op.pin(Path(__file__))
    report=dict(classification='ACTUAL_ORIGINAL_EA02_D4_FRESH_NATIVE_MATRIXFREE_PHASE_BACKEND',
        source_sha256=sha256(source).hexdigest(),input_and_source_sha256=dict(sorted(op.pins.items())),
        archive=dict(name=archive.name,bytes=archive.stat().st_size,sha256=sha256(archive.read_bytes()).hexdigest()),
        phase_rows=277,dynamic_velocity_rows=217,original_algebraic_rows=60,fresh_matvec_calls=op.calls,
        fresh_native_actual_direction_symmetry_upper=op.upper(symmetry),fresh_native_six_temporal_gauge_upper=op.upper(HZ),
        cached_original_binary_vs_fresh_native_on_tests_upper=op.upper(values['cached_phase_vs_native_on_tests']),
        cached_bordered_solve_upper=op.upper(pre_rows),fresh_original_preconditioned_rows_upper=op.upper(original),
        fresh_plus_frame_reaction_rows_upper=op.upper(framed),reaction_upper=op.upper(reaction),
        corrected_clock_value_map_change_on_phase_columns=op.phase_map_clock_change,
        cached277_and_F36_are_preconditioner_or_diagnostic_only=True,frame_reaction_counted_as_original_Gauss_pass=False,
        fresh_same_primal_point_density_wall_guards=germchecks,
        actual_selected_direction_and_original_candidate_rows_checked_at_2e10=True,
        packed_and_independent_material_chart_source_pins_enforced=True,
        fixed_primal_field_source_and_material_chart_preserved=True,dense277_rights_campaign_or_Hxx_built=False,
        new_primal_or_Cauchy_retraction_or_history_solve=False,source_compatible_initial_jump_selected=False,
        physical_new_retarded_field_or_outgoing_domain_solved=False,physical_total_derivative_spin_moment=False,
        original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items()if k not in('input_and_source_sha256','archive')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cauchy-folder',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    sys.path.insert(0,str(ROOT/'src'))
    try:execute(a.cauchy_folder,a.output)
    except Exception as e:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise
