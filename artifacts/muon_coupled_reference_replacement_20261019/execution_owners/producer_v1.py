"""Consume the exact zeta-reference replacement on the saved incoming block."""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from hashlib import sha256
import argparse,json,platform,sys
import numpy as np
import scipy

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from bhsm.interface.muon_coupled_reference_replacement import (
    coupled_seed,assemble_known_coupled,coupled_subtraction_step,
    GAUGE,HIGGS,LOG_UNIT,MULTIPLIER_ROWS,EULER_ROWS,
)
from bhsm.interface.muon_adopted_incoming_reference import reference_endpoint_data
from bhsm.interface.muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from bhsm.interface.retained_response.finite_time_response import write_npz


def endpoints(x,application,saved):
    """Reevaluate changed original conormals without another interior solve."""
    raw=saved['incoming_seed_raw268'].copy()
    raw[:100]=application['raw_geometry100'];raw[100:180]=x[GAUGE][:80]
    raw[180:260]=0.;raw[260:264]=x[HIGGS];raw[264:268]=0.
    base=dict(raw=raw,rho=saved['radial_points48'],radial_quadrature=saved['radial_weights48'],
              densities=application['densities'])
    realization=dict(base=base,value_map=application['value_map'],enrich_temporal=True)
    final=dict(gauge=application['total_connection'],gauge_rho=application['total_connection_radial'],
               gradient=application['known_gradient'][GAUGE])
    return reference_endpoint_data(dict(realization=realization,coefficients=x[GAUGE],final=final))


def vertices(application):
    v=canonical_open_field_vertices(application['R4'],application['induced_lapse'])
    a=np.r_[v['gauge'].reshape(20,18,18),v['scalar']]
    matrix=np.c_[a.real.reshape(24,-1),a.imag.reshape(24,-1)]
    return a,int(np.linalg.matrix_rank(matrix))


def area_complement(application):
    c=application['known_gradient'][MULTIPLIER_ROWS]
    a=application['area_gradient_per_gamma'][MULTIPLIER_ROWS]
    return c-a*np.dot(a,c)/np.dot(a,a)


def residuals(application,active,held):
    g=application['known_gradient']
    return dict(known_original150_max=float(np.max(abs(g[EULER_ROWS]))),
        known_geometry62_max=float(np.max(abs(g[:62]))),
        known_multiplier24_max=float(np.max(abs(g[MULTIPLIER_ROWS]))),
        known_multiplier_outside_area_max=float(np.max(abs(area_complement(application)))),
        known_active_interior52_max=float(np.max(abs(g[62+active]))),
        known_held_radial_wall32_max=float(np.max(abs(g[62+held]))),
        known_Higgs4_max=float(np.max(abs(g[HIGGS]))),
        complete_physical_residual=None,
        complete_physical_residual_reason='native-minus-local-overlap, inherited-state, exterior/interface and physical unit/domain rows remain unevaluated; no zero substituted')


def run(output):
    if output.exists():raise FileExistsError('preserve completed applications; choose a new run')
    source=ROOT/'artifacts/muon_adopted_incoming_reference_20261018/run_5/reference_application.npz'
    receipt_path=source.with_name('result.json');receipt=json.loads(receipt_path.read_bytes())
    if sha256(source.read_bytes()).hexdigest()!=receipt['arrays']['sha256']:
        raise ValueError('saved52 application identity changed')
    for rel,h in receipt['input_sha256'].items():
        if sha256((ROOT/rel).read_bytes()).hexdigest()!=h:raise ValueError('saved input changed: '+rel)
    with np.load(source,allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
    seed=coupled_seed(saved)
    arguments=dict(rho=saved['radial_points48'],radial_weights=saved['radial_weights48'],cap_points=32)
    before=assemble_known_coupled(seed,**arguments,saved=saved,seed=seed)
    step=coupled_subtraction_step(seed,before,saved,evaluate=lambda x:assemble_known_coupled(x,**arguments))
    after=step['after'];candidate=step['candidate']
    active=saved['active_interior_rows52'].astype(int);held=saved['held_radial_and_wall_rows32'].astype(int)
    eb,ea=endpoints(seed,before,saved),endpoints(candidate,after,saved)
    vb,rankb=vertices(before);va,ranka=vertices(after)
    old_m=saved['multiplier_at_classical_unit_no_area24']
    original_m_defect=float(np.max(abs(before['original_gradient'][MULTIPLIER_ROWS]-old_m)))
    if original_m_defect>2e-11:raise ValueError('old original multiplier identity changed')
    arrays=dict(seed151=seed,provisional_iterate151=candidate,
        original_active52_indices84=active,original_held32_indices84=held,
        reused_classical_inverse52=-saved['reference_native_load_partial_response52'],
        reused_initial_endpoint_temporal_momentum84=saved['temporal_gauge_momentum'],
        original_multiplier_before_replacement24=old_m,
        source_counterterm_original150=before['subtraction_gradient'][EULER_ROWS],
        multiplier_outside_area_before24=area_complement(before),
        multiplier_outside_area_after24=area_complement(after),
        intrinsic_wall_Higgs_vertices_before24=vb,intrinsic_wall_Higgs_vertices_after24=va)
    for label,application in [('before',before),('after',after)]:
        arrays.update({label+'_'+k:v for k,v in application.items() if isinstance(v,np.ndarray)})
    arrays.update({k:v for k,v in step.items() if isinstance(v,np.ndarray)})
    for label,endpoint in [('before',eb),('after',ea)]:
        arrays.update({label+'_endpoint_'+k:v for k,v in endpoint.items() if isinstance(v,np.ndarray)})
    output.mkdir(parents=True)
    numerical=output/'coupled_replacement.npz';write_npz(numerical,arrays)
    pins={source.relative_to(ROOT).as_posix():sha256(source.read_bytes()).hexdigest(),
          receipt_path.relative_to(ROOT).as_posix():sha256(receipt_path.read_bytes()).hexdigest()}
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and path and Path(path).resolve().is_relative_to(ROOT):
            p=Path(path).resolve();pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for rel in ('scripts/evaluate_muon_coupled_reference_replacement.py',
        'src/bhsm/interface/aether_quantum_functional_accounting_v16_00.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        'src/bhsm/interface/universal_gf_scale.py',
        'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    record=dict(schema='bhsm.coupled-reference-replacement.v1',
        classification='EVALUATED_EXACT_REFERENCE_SUBTRACTION_AND_PROVISIONAL_COUPLED_OFF_SHELL_LOAD_APPLICATION',
        parent_head='42ce332a54a12ea8a8944bc535cee12c6518ff28',input_sha256=pins,
        arrays=dict(path=numerical.name,sha256=sha256(numerical.read_bytes()).hexdigest()),
        runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        missing_contribution=dict(equation='Delta L=+(59/30)*N_ambient/R4 = -L_retained_SM_zeta',
            role='exact removal of the zero-source SM determinant already in the attached action; full sourced heat minus retained local overlap remains required',
            initial_value=before['subtraction_value'],
            initial_geometry62_covector_norm=float(np.linalg.norm(before['subtraction_gradient'][:62])),
            initial_multiplier24_max=float(np.max(abs(before['subtraction_gradient'][MULTIPLIER_ROWS]))),
            initial_Hessian151_norm=float(np.linalg.norm(before['subtraction_hessian'])),
            original_independent_twojet_defect=before['subtraction_original_twojet_defect'],
            independent_gauge_Higgs_unit_partial='exact zero because this original term depends only on dimensionless geometry; total background/unit derivatives still chain through the geometry'),
        original_inputs_reused=dict(interior52_solve_repeated=False,initial_field84_gradient_Hessian=before['cache_reused'],
            initial_field_cache_defect=before['cache_defect'],initial_multiplier_identity_defect=original_m_defect,
            classical52_inverse_used_only_at_unchanged_seed=True,
            moved_fields_geometry_and_endpoints_reevaluated=True),
        coupled_equations=dict(full='g_original+g_subtraction+gamma*g_area+ell_native_minus_local_overlap+ell_reference/exterior/interface=0; all total derivatives required',
            full_Jacobian='K_original+K_subtraction+gamma*K_area+D ell_native/reference/exterior/interface; K_known is not its inverse',
            executed='g_original(z)-g_original(seed)+d(Delta L)(z)=0 on150 original rows; one damped linearized off-shell load-homotopy step, original residual retained',
            physical_unit='GF*exp(2e)-cF[y,Sigma_in,domain,normalized_external_legs]=0; derivative=2GF*exp(2e)de-DcF',
            unit_row_is_Euler_e=False,
            collider_incidence='I_y^*h_Sigma=(hbar*c/exp(e))^2*(pulled-back action metric); geodesic chart and spin/gauge transport on the SAME assembled Sigma, with trace/traction/domain matching to the cap boundary',
            collider_incidence_resolved=False),
        numerical_step=dict(accepted=step['accepted'],condensed_rows=98,condensed_columns=99,
            numerical_rank=step['numerical_rank'],rank_relative_tolerance=step['rank_relative_tolerance'],
            metric='minimum Euclidean y in delta_b=diag(max(1,abs(seed_b)))*y; rows scaled by max(1,norm(K_schur*variable_scale)); this is a reduced99-coordinate metric, not full151 norm or a physical gauge quotient',
            max_scaled_step=.02,trial_history=step['trial_history'],
            full_linearized_unscaled_residual_max=float(np.max(abs(step['linearized_unscaled_original_rows150']))),
            scaled_left_null_load_norm=float(np.linalg.norm(step['scaled_left_null_load'])),
            geometry_step_norm=float(np.linalg.norm(step['actual_step'][:62])),
            held32_step_norm=float(np.linalg.norm(step['actual_step'][62+held])),
            eliminated52_step_norm=float(np.linalg.norm(step['actual_step'][62+active])),
            Higgs_step=step['actual_step'][HIGGS].tolist(),log_unit_initializer_step=float(step['actual_step'][LOG_UNIT])),
        residuals_before=residuals(before,active,held),residuals_after=residuals(after,active,held),
        held_and_unevaluated=dict(ordinary_reference_rates='zero only in this stationary comparison ansatz; nonzero original canonical momenta exported',
            surface_gamma='unassigned; coefficient gradient/Hessian preserved, not adjusted to cancel a residual',
            intrinsic_wall_Higgs_reference_span=dict(rank_before=rankb,rank_after=ranka,
                values_of_required20_state_contractions=None,
                equation='ell_wall/H,a=Tr(C_reference V_a), with density/domain/time contacts; D ell=Tr(D C_reference V_a+C_reference D V_a)',
                higher_correlations='interacting response and pair conversion can require higher state correlations; rank20 is not a bound on those requirements'),
            separate_bulk_native_remainder='retained independently; zero intrinsic zero-trace vertices do not set bulk load or D bulk load to zero',
            quantum_replacement='Gamma_heat minus already-retained local Maxwell/Higgs overlap plus state/domain/relative completion; rank20 contractions are a represented part, not another determinant',
            native_heat_load_or_complete_Dell_evaluated=False,
            physical_cF_before=None,physical_cF_after=None,physical_GF_residual_before=None,physical_GF_residual_after=None,
            required_cF_at_initializer_before=before['required_cF'],required_cF_at_initializer_after=after['required_cF'],
            common_energy_GeV_initializer_before=before['unit_initializer_GeV'],common_energy_GeV_initializer_after=after['unit_initializer_GeV'],
            physical_unit_admitted=False,cap_boundary_identified_with_entire_collider=False,
            adopted_preparation='unchanged500MeV/beam,100fm peraxis RMS,+/-1000fm centers, exact pair',
            physical_four_sections_or_current_evaluated=False),
        errors=dict(finite='48 radial /32 cap quadrature; finite inherited n0 weak field chart and stationary off-shell ansatz',
            numerical_rank='all left/right nullspaces and unscaled linear residuals exported; no physical quotient or discarded physical row inferred',
            incomplete_Jacobian='D ell, gamma*K_area, physical-unit DcF and complete incidence/domain/state derivatives remain; their effect on this particular is unknown, not zero',
            continuum_time='unresolved; no outward or continuum bound from this finite application',
            native_continuation='no unproved proper-Euclidean finite heat load inserted into Lorentz cap rows',
            existing='gauge reconstruction7.29e-10/6.33e-10, membrane finite step9.34e-8 and calibrated ancestry retained'),
        physical_guard=2e-10,physical_derivative_admitted=False,coupled_physical_correction=False,
        fresh_physical_Maxwell_all226=False,magnetic_moment_or_uncertainty=None,
        NEXT_OPERAND='Evaluate the sourced native-minus-local-overlap/reference stress and wall/Higgs contractions with their same-action Lorentz continuation/domain and field derivatives; complete the common Cauchy incidence and normalized charged-current cF equation. Apply those actual loads to the retained coupled rows; do not infer their values from this off-shell particular or its Schur matrix.')
    path=output/'result.json';temp=path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n');temp.replace(path)
    print(json.dumps(dict(missing_contribution=record['missing_contribution'],step=record['numerical_step'],
        before=record['residuals_before'],after=record['residuals_after'],sha256=sha256(path.read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output.resolve())
