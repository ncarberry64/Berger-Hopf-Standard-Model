"""Replay the actual birth-side intrinsic scalar action coefficients.

Export the evaluated nonlinear operator coefficient map and its insertion
slots.  Supplied-field verification witnesses are explicitly CONTROL_ONLY.
This script does not select a primal Higgs solution or formation section.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))

from bhsm.interface.ae4_branch_relative_support_transition import branch_relative_cutoff_contract
from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator
from bhsm.interface.muon_intrinsic_m4_normal_pullback import retained_intrinsic_m4_application
from bhsm.interface.muon_intrinsic_higgs_weak_action import (
    diagonal_kinetic_density,higgs_action,higgs_explicit_weak_variation,
    retained_higgs_spin_charge_representation,
)
from bhsm.interface.muon_coupled_temporal_weak_action import (
    scalar_monomial_coefficients,real_scalar_weak_coefficient_map,
    coupled_scalar_geometry_application,temporal_geometry_weak_application,
    mechanical_scalar_action_coefficients,
)
from bhsm.interface.muon_intrinsic_higgs_connection import (
    mechanical_higgs_connection_from_weight_jet,PARENT_PATCH,CHILD_PATCH,CHILD_PATCH_OWNER,
)


def serial(value):
    if isinstance(value,np.ndarray):
        if np.iscomplexobj(value): return dict(real=value.real.tolist(),imag=value.imag.tolist())
        return value.tolist()
    if isinstance(value,np.generic): return value.item()
    if isinstance(value,dict): return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [serial(v) for v in value]
    return value


def write(path,value):
    indent=None if path.name=='intrinsic_m4_action_coefficients.json' else 2
    path.write_text(json.dumps(serial(value),indent=indent,sort_keys=True,allow_nan=False,
                              separators=(',',':') if indent is None else None)+'\n',
                    encoding='utf8',newline='\n')


def identity(relative):
    return dict(path=relative,sha256=sha256((ROOT/relative).read_bytes()).hexdigest())


def jet(value):
    return dict(value=float(value.value),gradient=value.gradient,hessian=value.hessian)


def scalar_control(weights,mechanical_patch=None):
    """Nonphysical fields check the assembled derivative consumer, not a base."""
    rng=np.random.default_rng(1009); points=2
    H=rng.normal(size=(points,2))+1j*rng.normal(size=(points,2))
    DH=rng.normal(size=(points,4,2))+1j*rng.normal(size=(points,4,2))
    J=rng.normal(size=(points,2))+1j*rng.normal(size=(points,2))
    values=np.zeros((4,points,2),complex)
    for j in range(4): values[j,:,j%2]=1 if j<2 else 1j
    derivatives=np.zeros((4,points,4,2),complex)
    maps=np.zeros((points,100,2)); maps[:,25,0]=1.; maps[:,74,1]=1.
    quad=np.array([.4,.6]); lam=.7; nu=.4
    kwargs=dict(weight_nodes=[weights]*points,quadrature=quad,metric_maps=maps,
        H=H,DH=DH,J=J,test_values=values,test_derivatives=derivatives,
        lambda_H=lam,nu_squared=nu,normal=np.ones(points),normal_rates=np.zeros(points))
    if mechanical_patch is not None:
        kwargs.update(mechanical_patch=mechanical_patch,mechanical_rotation=np.eye(3))
    data=coupled_scalar_geometry_application(**kwargs)
    eps=2e-6
    plus=coupled_scalar_geometry_application(**dict(kwargs,H=H+eps*values[2]))
    minus=coupled_scalar_geometry_application(**dict(kwargs,H=H-eps*values[2]))
    residual_fd=(plus['scalar_action_residual']-minus['scalar_action_residual'])/(2*eps)
    G=diagonal_kinetic_density(dict(time=weights['wT'].value,spatial=weights['wS'].value))
    dG=diagonal_kinetic_density(dict(time=weights['wT'].gradient[98],
                                   spatial=weights['wS'].gradient[98]))
    covDH=DH.copy(); Dphi=derivatives[0].copy(); dDH=np.zeros_like(DH); dDphi=np.zeros_like(Dphi)
    if mechanical_patch is not None:
        c=mechanical_scalar_action_coefficients(weights,patch=mechanical_patch,rotation=np.eye(3))
        AH=np.einsum('iab,pb->pia',c['unit_connection_generators'],H)
        Aphi=np.einsum('iab,pb->pia',c['unit_connection_generators'],values[0])
        covDH[:,1:]+=c['kappa'].value*AH; Dphi[:,1:]+=c['kappa'].value*Aphi
        dDH[:,1:]=c['kappa'].gradient[98]*AH; dDphi[:,1:]=c['kappa'].gradient[98]*Aphi
    expected=higgs_explicit_weak_variation(quadrature=quad,kinetic_density=G,
        volume_density=weights['wV'].value,H=H,DH=covDH,J=J,phi=values[0],
        Dphi=Dphi,lambda_H=lam,nu_squared=nu,delta_kinetic_density=dG,
        delta_volume_density=weights['wV'].gradient[98],delta_DH=dDH,delta_Dphi=dDphi)
    source=data['scalar_partial_metric_normal_source'][2]
    return dict(classification='CONTROL_ONLY',primal_is_physical=False,
        scalar_residual=data['scalar_action_residual'],common_scalar_jacobian=data['scalar_action_jacobian'],
        partial_normal_source=data['scalar_partial_metric_normal_source'],
        HH_column_fd_max_error=float(np.max(np.abs(residual_fd-data['scalar_action_jacobian'][:,4]))),
        symmetric_closed_partial_H_max_error=float(np.max(np.abs(data['scalar_action_jacobian']-
            data['scalar_action_jacobian'].T))),
        partial_normal_vs_independent_weak_error=abs(float(source-expected)),
        fixture=dict(seed=1009,lambda_H=lam,nu_squared=nu,reference_quadrature=quad),
        mechanical_background=mechanical_patch,
        scope='Supplied nonphysical off-shell fields, owned mechanical background where named, remaining connection fixed; no physical temporal domain or stationary solve')


def evaluate(output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    applications={}; summaries={}; controls={}
    previous='artifacts/muon_moving_interface_action_20261009/run_1/'
    for side,orientation in (('outgoing_C2',1.),('incoming_C1_E1',-1.)):
        data=retained_intrinsic_m4_application(ROOT,side,trial_normal=orientation)
        w=data['weights']; metric=data['normal_metric']; ns,nr=w['source_indices']
        patch='child' if side=='outgoing_C2' else 'parent'
        mechanical=mechanical_higgs_connection_from_weight_jet(w,rotation=np.eye(3),
            rotation_first=np.zeros((3,3)),rotation_second=np.zeros((3,3)),
            patch=CHILD_PATCH if patch=='child' else PARENT_PATCH,
            child_patch_owner=CHILD_PATCH_OWNER if patch=='child' else None)
        mechanical_action=mechanical_scalar_action_coefficients(w,patch=patch,rotation=np.eye(3))
        # Reuse the reviewed geometric derivative arrays without a new cap solve.
        retained=json.loads((ROOT/(previous+side+'_weak_action.json')).read_text(encoding='utf8'))
        block={k:np.asarray(v,dtype=float) if isinstance(v,list) else v
               for k,v in retained['geometry_weak_action'].items()}
        # This is the exact local weak test-jet coefficient map at the saved node.
        # It has no invented temporal history and is not a stationary residual.
        tq=np.zeros((1,37,98)); tv=np.zeros_like(tq); tm=np.zeros((1,24,98))
        tq[0,:,:37]=np.eye(37); tv[0,:,37:74]=np.eye(37); tm[0,:,74:]=np.eye(24)
        local_map=temporal_geometry_weak_application([block],[1.],tq,tv,tm,[1.],[0.])
        applications[side]=dict(
            source=identity(previous+side+'_weak_action.json'),geometry=data['geometry'],
            normal_orientation=orientation,
            weights={key:jet(w[key]) for key in ('wT','wS','wV')},
            normal_metric_two_jet=metric,
            mechanical_higgs_connection_two_jet=mechanical,
            mechanical_scalar_action_coefficients=dict(
                kappa=jet(mechanical_action['kappa']),
                generators=mechanical_action['unit_connection_generators'],
                D0H_connection_cross_coefficient=jet(mechanical_action['D0H_connection_cross_coefficient']),
                H_norm_coefficient=jet(mechanical_action['H_norm_coefficient']),
                patch=patch,coefficient_owner=mechanical_action['coefficient_owner'],
                scope='Actual mechanical background term in S4; D0 retains the remaining connection. Body coframe is a representation, not a physical mode.'),
            scalar_action_monomial_coefficients=dict(time_kinetic=dict(weight='wT',sign=1),
                spatial_kinetic=dict(weight='wS',sign=-1),
                potential_and_explicit_source=dict(weight='wV',sign=-1)),
            real_scalar_weak_operator_coefficients=real_scalar_weak_coefficient_map(w),
            partial_normal_weak_operator_coefficients=real_scalar_weak_coefficient_map(w,derivative_index=ns),
            partial_normal_rate_weak_operator_coefficients=real_scalar_weak_coefficient_map(w,derivative_index=nr),
            connection_coefficient_jets={key:jet(w[key]) for key in (
                'mechanical_connection_lambda','section0_orthonormal_connection_coefficient',
                'section1_orthonormal_connection_coefficient')},
            reused_geometry_weak_test_jet_map=dict(action_residual=local_map['action_residual'],
                action_source=local_map['action_source'],
                action_hessian_shape=local_map['action_hessian'].shape,
                action_hessian_binary64_sha256=sha256(local_map['action_hessian'].astype('<f8').tobytes()).hexdigest(),
                action_hessian_norm=float(np.linalg.norm(local_map['action_hessian'])),
                action_hessian_source=previous+side+'_weak_action.json',
                physical_domain_instantiated=False),
            local_weak_test_jet_map_scope='Pointwise (phi,D_t phi,test_m) coefficient map; no physical temporal history/domain or independent qdot Euler variable',
            internal_coordinate_layout=dict(q=[0,37],qdot=[37,74],lapse_shift=[74,98],s=98,sdot=99),
            scalar_geometry_row_role='Add unreduced intrinsic scalar action derivatives to these same geometry rows; add connection/frame/source/constraint applications before solving',
            scalar_pairing='2 Re in unscaled complex doublet; coordinate time and unit S3 measure',
            intrinsic_H_normal_extension_introduced=False,full_stationary_base=False)
        comparison=max(abs(float(w['wT'].gradient[ns]-metric['kinetic_density_first'][0,0])),
                       abs(float(-w['wS'].gradient[ns]-metric['kinetic_density_first'][1,1])),
                       abs(float(w['wV'].gradient[ns]-metric['volume_density_first'])),
                       abs(float(w['wT'].hessian[ns,ns]-metric['kinetic_density_second'][0,0])),
                       abs(float(-w['wS'].hessian[ns,ns]-metric['kinetic_density_second'][1,1])),
                       abs(float(w['wV'].hessian[ns,ns]-metric['volume_density_second'])))
        if comparison>2e-12:
            raise ValueError('independent intrinsic metric coefficient applications disagree')
        summaries[side]=dict(Cstar=float(w['Cstar'].value),R4=float(w['R4'].value),
            weights={key:float(w[key].value) for key in ('wT','wS','wV')},
            first_normal={key:float(w[key].gradient[ns]) for key in ('wT','wS','wV')},
            second_normal={key:float(w[key].hessian[ns,ns]) for key in ('wT','wS','wV')},
            rate_second={key:float(w[key].hessian[nr,nr]) for key in ('wT','wS','wV')},
            scalar_lapse_monomial_rows={key:scalar_monomial_coefficients(w)[key].gradient[74:86]
                for key in scalar_monomial_coefficients(w)},
            independent_dense_vs_100_coordinate_max_abs=comparison,
            mechanical_H_norm_action_coefficient=dict(
                value=float(mechanical_action['H_norm_coefficient'].value),
                first_normal=float(mechanical_action['H_norm_coefficient'].gradient[ns]),
                second_normal=float(mechanical_action['H_norm_coefficient'].hessian[ns,ns]),
                weak_real_linear_matrix_coefficient=2*float(mechanical_action['H_norm_coefficient'].value)),
            full_stationary_base=False)
        controls[side]=scalar_control(w,patch)
        if controls[side]['HH_column_fd_max_error']>2e-7:
            raise ValueError('common scalar Jacobian control failed')
    sources=[
        'src/bhsm/interface/muon_intrinsic_higgs_weak_action.py',
        'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        'src/bhsm/interface/muon_coupled_temporal_weak_action.py',
        'src/bhsm/interface/muon_intrinsic_higgs_connection.py',
        'src/bhsm/interface/muon_owned_connection_application.py',
        'scripts/evaluate_muon_intrinsic_higgs_weak_action.py',
        'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',
        'src/bhsm/interface/aether_diagonal_sp1_m4_attachment_v15_50.py',
        'src/bhsm/interface/muon_birth_candidate_geometry_action.py',
        'src/bhsm/interface/muon_moving_geometric_action.py',
        'src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py',
        'src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py',
        'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        'src/bhsm/interface/muon_local_source_jet.py',
        'src/bhsm/interface/bhsm_standard_model_gauge_vertices.py',
        'src/bhsm/interface/aether_hybrid_standard_model_bundle_v15_53.py',
        'src/bhsm/interface/muon_birth_fermion_event_kkt_inputs.py',
        'artifacts/muon_birth_transfer_value_20261008/retained_reset/run_1/result.json',
        'artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz',
        previous+'result.json']
    result=dict(classification='EVALUATED_INTRINSIC_SCALAR_WEAK_OPERATOR_COEFFICIENTS_AND_COMMON_ACTION_APPLICATION_BACKEND',
        cutoff_owner=branch_relative_cutoff_contract(),baseline_commit='181c869d1547c03c3661bf0072363eb9119e0aad',
        applications=summaries,fixed_family_yukawa=charged_lepton_yukawa_operator(),
        higgs_spin_charge_representations=retained_higgs_spin_charge_representation(),
        source_identities=[identity(p) for p in sources],
        scientific_scope=dict(
            DERIVED=['Nonlinear real Higgs weak residual and HH with conjugate-h dependence',
                'Explicit partial shape derivative of off-shell residual, with measure, source, connection and transported-test terms',
                'Same-action scalar/lapse/geometric mixed blocks and full fixed-field action two-jet',
                'Temporal geometry differential weak assembly and endpoint/source contacts',
                'Inherited scalar trace/paired flux-return application and moving product rule'],
            EVALUATED=['Receipt-bound M4 weight 100-coordinate two-jets on both retained sides',
                'Dense induced metric and measure normal two-jets including graph contacts',
                'Nonlinear real weak polynomial coefficient tensor and scalar/lapse cotangent coefficients',
                'Action-owned fixed-family Yukawa coefficients',
                'Inherited Higgs SU2/hypercharge matrices and actual common LR spin frame',
                'Owned Sp1 Higgs background connection and its scalar-action quadratic/mixed coefficient application',
                'Existing geometric derivative arrays consumed in local weak test-jet coefficient map'],
            CONTROL_ONLY=['Supplied off-shell scalar fields for residual/Jacobian and partial-source consistency',
                'Independent polynomial temporal histories and trace-pairing tests'],
            UNEVALUATED=['Interacting intrinsic scalar/lepton retarded primal boundary-value solution',
                'Complete stationary KKT base, physical formation section, total impedance/inertia',
                'Disjoint physical native Pauli remainder and final a_mu/g_mu'],
            OWNER_DEFINITION_GAP=[]),
        precise_remaining_application=dict(
            consumer='higgs_weak_residual and coupled_scalar_geometry_application',
            first_field_pairing='2 Re integral (R4^3/N) (D_t phi)^dagger D_t H_star',
            producer='Coupled E_H=0, Euler_L=0, Euler_e=0 with intrinsic connection and inherited scalar/lepton temporal trace and conormal applications',
            newly_implemented='Nonlinear scalar weak residual, realified Jacobian, all explicit supplied-data variations and common scalar/geometry insertion; inherited scalar trace/flux matching application',
            supplied_values_used='Receipt-pinned q,qdot,m, intrinsic quotient geometry and moving metric/action arrays, frozen Y_l',
            solve_attempt_scope='Coefficient applications and nonlinear coupled-row derivative controls executed. A physical Newton step was not formed: the actual covariant field/domain and trace producer application is still unimplemented, rather than supplied by the geometric reset.',
            independent_datum_not_fixed_by_problem_proven=False,
            theory_definition_gap_proven=False),
        numerical_error_scope=dict(arithmetic='binary64 retained inputs and coefficient applications',
            diagnostics='Independent metric/determinant/finite-difference and weak-action checks',
            continuum_or_stationary_enclosure=False,physical_anomaly_enclosure=False),
        final_accounting=dict(a_mu='frozen selected local + disjoint native remainder after owned overlap',
            g_mu='2*(1+a_mu)',native_remainder_evaluated=False,final_observables_evaluated=False,
            strong_native_ledger_count=1,frozen_predictions_changed=False),
        full_physical_prediction_completed=False)
    write(output/'intrinsic_m4_action_coefficients.json',applications)
    write(output/'control_checks.json',controls)
    write(output/'result.json',result)
    print(json.dumps(dict(classification=result['classification'],applications=summaries,
        full_physical_prediction_completed=False),default=serial,sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',required=True)
    evaluate(parser.parse_args().output)
