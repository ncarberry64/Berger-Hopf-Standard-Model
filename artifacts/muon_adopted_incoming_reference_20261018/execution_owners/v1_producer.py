"""Checkpoint the adopted selector's actual inherited-reference block solve."""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT)]
from bhsm.interface.muon_adopted_incoming_reference import (
    solve_classical_reference_block, stationary_parent_field_realization,
    reference_endpoint_data, assigned_reference_constraint_polynomial,
)
from bhsm.interface.retained_response.finite_time_response import write_npz
from bhsm.interface.retained_response.retained_magnetic_application import wall_data
from bhsm.interface.muon_magnetic_open_lepton_vertex import canonical_open_field_vertices


def run(output):
    if output.exists():
        raise ValueError('new output required; resume saved completed applications')
    source = ROOT/'artifacts/muon_retained_response_20261018/inputs/incoming_history.npz'
    with np.load(source, allow_pickle=False) as z:
        raw = z['lo_raw_fields'].copy()
        raw_rate = z['lo_raw_coordinate_time_derivative'].copy()
    adoption = ROOT/'artifacts/muon_adopted_incoming_reference_20261018/adoption_v1.json'
    decision = json.loads(adoption.read_bytes())
    if decision['selector_approval_pending'] or decision['manufactured_control_adopted']:
        raise ValueError('current conditional adoption, without manufactured background, required')
    application = solve_classical_reference_block(raw, radial_points=48)
    reference = application['realization']
    active, frozen = application['active'], reference['frozen']
    endpoint = reference_endpoint_data(application)
    constraint = assigned_reference_constraint_polynomial(application, cap_points=32)
    # Independent quadrature check at the solved coefficients; do not solve
    # every old background or conceal this remaining quadrature difference.
    fine = stationary_parent_field_realization(raw, radial_points=96)
    fine_result = fine['evaluate'](application['coefficients'])
    quadrature_defect = fine_result['gradient']-application['final']['gradient']
    # The scalar polynomial supplies a classical unit INITIALIZER. Native/
    # reference scalar loads and the independent GF equation are not erased.
    h0, h1, h2 = constraint['scalar_nu_polynomial3x4']
    if np.max(abs(h2)) != 0 or np.dot(h1,h1) == 0:
        raise ValueError('inspect changed scalar stationarity polynomial')
    nu2 = -np.dot(h1,h0)/np.dot(h1,h1)
    if nu2 <= 0:
        raise ArithmeticError('no positive classical Higgs/unit initializer')
    classical_higgs = h0+nu2*h1
    matching = constraint['matching']
    scale = float(np.sqrt(matching['nu_squared_GeV_squared']/nu2))
    required_cF = matching['G_F_GeV_minus2']*scale**2
    unit_source_response = -h1/np.dot(h1,h1)
    multiplier_known = (constraint['multiplier_nu_polynomial3x24'][0]
        +nu2*constraint['multiplier_nu_polynomial3x24'][1]
        +nu2**2*constraint['multiplier_nu_polynomial3x24'][2])
    area = constraint['multiplier_area_per_gamma24']
    area_independent = multiplier_known-area*np.dot(area,multiplier_known)/np.dot(area,area)
    # Current contractions relevant to this block. Intrinsic fermions see
    # only wall values, so all48 zero-trace interior variations have zero
    # intrinsic open-current vertex, independently of reference occupation.
    v = canonical_open_field_vertices(endpoint['R4'], endpoint['proper_lapse'])
    vertices = np.r_[v['gauge'].reshape(20,18,18),v['scalar']]
    rank = np.linalg.matrix_rank(np.c_[vertices.real.reshape(24,-1),vertices.imag.reshape(24,-1)])
    stationary_raw = raw.copy()
    stationary_raw[37:74] = 0.
    stationary_raw[99] = 0.
    stationary_raw[100:180] = application['coefficients']
    stationary_raw[180:260] = 0.
    stationary_raw[264:268] = 0.
    before = application['initial']['gradient']
    after = application['final']['gradient']
    arrays = dict(incoming_seed_raw268=raw, incoming_seed_coordinate_rate268=raw_rate,
        stationary_comparison_iterate_raw268=stationary_raw,
        initial_field_coefficients80=reference['initial'],
        solved_classical_field_coefficients80=application['coefficients'],
        active_interior_rows48=active, held_radial_and_wall_rows32=frozen,
        initial_original_field_rows80=before, final_original_field_rows80=after,
        final_original_field_Hessian80=application['final']['hessian'],
        reference_native_load_partial_response48=application['unresolved_load_response'],
        held_row_load_partial_response32x48=application['frozen_row_load_response'],
        higher_quadrature_original_field_rows80=fine_result['gradient'],
        quadrature_row_difference80=quadrature_defect,
        multiplier_nu_polynomial3x24=constraint['multiplier_nu_polynomial3x24'],
        multiplier_area_per_gamma24=area, multiplier_at_classical_unit_no_area24=multiplier_known,
        multiplier_component_orthogonal_to_area24=area_independent,
        scalar_nu_polynomial3x4=constraint['scalar_nu_polynomial3x4'],
        scalar_native_load_unit_partial_response4=unit_source_response,
        original_open_wall_vertices24=vertices,
        **{k:v for k,v in endpoint.items() if isinstance(v,np.ndarray)})
    output.mkdir(parents=True)
    numerical = output/'reference_application.npz'
    write_npz(numerical, arrays)
    pins = {source.relative_to(ROOT).as_posix():sha256(source.read_bytes()).hexdigest(),
            adoption.relative_to(ROOT).as_posix():sha256(adoption.read_bytes()).hexdigest()}
    for name,module in sorted(sys.modules.items()):
        path = getattr(module,'__file__',None)
        if name.startswith('bhsm.') and path and Path(path).resolve().is_relative_to(ROOT):
            p = Path(path).resolve(); pins[p.relative_to(ROOT).as_posix()] = sha256(p.read_bytes()).hexdigest()
    for rel in ('scripts/evaluate_muon_adopted_incoming_reference.py',
                'src/bhsm/interface/muon_parent_gauge_geometry_correction.py',
                'artifacts/muon_calibrated_pauli_20261009/inputs.json',
                'artifacts/muon_calibrated_weak_decay_20261010/run_1/weak_decay.json',
                'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'):
        pins[rel] = sha256((ROOT/rel).read_bytes()).hexdigest()
    record = dict(
        classification='ADOPTED_SELECTOR__PROVISIONAL_INHERITED_REFERENCE_NONLINEAR_CLASSICAL_BLOCK_APPLICATION',
        input_sha256=pins, arrays=dict(path=numerical.name,sha256=sha256(numerical.read_bytes()).hexdigest()),
        runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        seed=dict(path=source.relative_to(ROOT).as_posix(), label='lo', side='incoming C1 history only; not electron/positron branches',
            status='published provisional history, used only as numerical initializer',
            stored_geometry_rate_norm=float(np.linalg.norm(raw_rate[:37])),
            stored_geometry_not_stationary=True, reconstructed_connection='raw268 independent four radial profiles plus the explicit original mechanical lambda(q); no child inherited-profile map invoked'),
        comparison_iterate='q,m,s,H and all wall values inherited; ordinary rates set stationary in inherited material clock/gauge. Nonzero covariant electric fields and momenta retained. This is not an established asymptotic background.',
        equations_executed=dict(
            field='d/d a_active [S_Maxwell(Abar+a)-S_Maxwell(Abar)+S_H_fixed_H]=0 for48 interior At/Ai coordinates',
            Gauss='All12 interior temporal rows retained inside the48 nonlinear equations',
            wall='All20 inherited Dirichlet traces held for this initializer; actual wall-lift reactions, literal radial conormals and temporal momenta returned separately',
            scalar='H0+nu_action_squared*H1=0 only as a classical unit initializer; reference/native scalar load retained',
            unit='G_F*exp(2e)-c_F[complete same-action low-energy contraction]=0 remains an independent equation',
            multiplier=constraint['polynomial_equation']),
        numerical_parameters=dict(radial_profiles=4,radial_quadrature=48,validation_quadrature=96,cap_quadrature=32),
        status=application['status'], nonlinear_history=application['history'],
        residuals=dict(initial_active_original_max=float(np.max(abs(before[active]))),
            final_active_original_max=float(np.max(abs(after[active]))),
            validation_active_original_max=float(np.max(abs(fine_result['gradient'][active]))),
            full80_quadrature_difference_max=float(np.max(abs(quadrature_defect))),
            held_radial_and_wall_original_max=float(np.max(abs(after[frozen]))),
            parent_radial_conormal_max=float(np.max(abs(endpoint['parent_outward_radial_gauge_conormal']))),
            temporal_gauge_momentum_max=float(np.max(abs(endpoint['temporal_gauge_momentum80']))),
            classical_Higgs_unit_initializer_max=float(np.max(abs(classical_higgs))),
            multiplier_coefficient_max=np.max(abs(constraint['multiplier_nu_polynomial3x24']),axis=1).tolist(),
            multiplier_area_independent_component_max=float(np.max(abs(area_independent)))),
        provisional_unit=dict(nu_action_squared=float(nu2), common_energy_GeV_initializer=scale,
            required_cF_from_GF_at_initializer=float(required_cF), physical_cF_evaluated=None,
            full_GF_residual=None, full_GF_residual_reason='physical charged-current contraction/pole normalization not executed on a solved incoming comparison',
            independent_calibration='same authorized GF and Higgs tree matching; no muon anomaly/lifetime fit or sector unit introduced', physical_unit_admitted=False),
        required_reference_contractions=dict(
            intrinsic_fermion_interior48_vertex_zero='EXACT: these variations vanish at the intrinsic wall, so reference occupations do not enter this particular block through the intrinsic first-order wall action',
            open_wall_and_Higgs_vertex_span_rank=int(rank),
            surviving_bulk_remainder='ell_j=delta(complete native/reference action minus already retained local overlap)/delta a_j, j in active48; not assigned zero',
            response_operator_norm=float(np.linalg.norm(application['unresolved_load_response'],2)),
            response_scope='Classical partial implicit response only. Complete Jacobian is K_classical+D_a ell, with geometry/scalar/state/domain/clock derivatives and endpoint contacts.',
            no_complete_cosmic_history_required_by_this_block=True,
            inherited_transverse_fields_and_correlations='retained; no empty or quasifree reference selected'),
        errors=dict(domain='finite inherited cap radial profiles and angular n0 sector; not complete collider Cauchy domain',
            continuum='radial complement and angular sectors unresolved; quadrature difference is a diagnostic, not an outward bound',
            physical_preparation='500MeV/100fm/+/-1000fm adopted specification unchanged; four physical Gaussian sections and their moments not yet evaluated',
            incoming_cutoff='no physical finite-past transport executed before complete constrained comparison and collider-domain incidence; no cutoff error declared zero',
            remaining_rows='held Ar/wall, scalar/native/state, area/geometric constraints, GF matching and exterior/domain equations remain'),
        physical_guard=2e-10, physical_derivative_admitted=False, coupled_physical_correction=False,
        fresh_physical_Maxwell_all226=False, physical_incoming_four_sections=False,
        pair_conversion_or_outgoing_occupation_evaluated=False, magnetic_moment_or_uncertainty=None,
        NEXT_OPERAND='Consume returned reference radial/wall/temporal covectors and the scalar/unit initializer in the coupled comparison geometry/Higgs/GF/native remainder equations; construct the actual collision-domain Cauchy incidence before four Gaussian incoming sections. The selector is adopted; no permission question remains.')
    path = output/'result.json'
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    temporary.replace(path)
    print(json.dumps(dict(status=record['status'],residuals=record['residuals'],
        unit_initializer=record['provisional_unit'],sha256=sha256(path.read_bytes()).hexdigest()),sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output.resolve())
