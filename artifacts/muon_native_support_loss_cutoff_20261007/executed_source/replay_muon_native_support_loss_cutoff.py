"""Adopted cutoff composition and narrow retained-history reconciliation.

One new small arithmetic control is evaluated. No history, parent solve,
local contact, normalization or old test producer is replayed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import native_spectral_length_contract
from bhsm.interface.muon_native_support_loss_cutoff import lower_limit_coefficients
from bhsm.interface.muon_native_induced_polarization import lower_limit_mixed
from control_muon_support_loss_quotient import execute_control


def save(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output,history_repository):
    if output.exists():raise FileExistsError('Fresh output required; preserve older work')
    output.mkdir(parents=True);start=time.perf_counter()
    history=history_repository/'artifacts/current_runtime'
    paths=dict(owner=ROOT/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        builder=ROOT/'src/bhsm/interface/muon_native_support_loss_cutoff.py',
        replay=Path(__file__),control=ROOT/'scripts/control_muon_support_loss_quotient.py',
        existing_heat_identity=ROOT/'src/bhsm/interface/muon_native_induced_polarization.py',
        formation=ROOT/'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        fixed_trace=ROOT/'src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py',
        mode_arrays=history/'current_physical_mode_response/arrays.npz',
        mode_report=history/'current_physical_mode_response/report.json',
        backreaction_arrays=history/'current_child_parent_backreaction/arrays.npz',
        backreaction_report=history/'current_child_parent_backreaction/report.json',
        mode_producer=history_repository/'scripts/run_n12_current_physical_mode_response.py',
        backreaction_producer=history_repository/'scripts/run_n12_current_child_parent_backreaction.py',
        graph_producer=history_repository/'src/bhsm/interface/aether_hybrid_c2_graph_jacobian.py',
        incidence=history_repository/'src/bhsm/interface/aether_forward_c2_geometry_incidence.py',
        frozen=ROOT/'artifacts/muon_source_jet_20261002/frozen_local.json',
        prior_source_receipt=ROOT/'artifacts/muon_native_induced_polarization_20261006/run_1/input_hashes.json')
    # Source identities include read-only local handoffs, not Git alone.
    mode=json.loads(paths['mode_report'].read_text(encoding='utf8'))
    back=json.loads(paths['backreaction_report'].read_text(encoding='utf8'))
    paths['retained_center']=Path(mode['center'])
    identities={k:dict(path=str(p.resolve()),sha256=sha(p),
                       canonical_LF_sha256=hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
                       if p.suffix in ('.py','.json') else None) for k,p in paths.items()}
    if identities['retained_center']['sha256'].upper()!=mode['center_SHA256'].upper():
        raise ValueError('retained mode center changed')
    if back['center_SHA256'].upper()!=mode['center_SHA256'].upper():
        raise ValueError('retained histories refer to different centers')
    save(output/'input_hashes.json',identities)
    git=lambda where,*args:subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*args],cwd=where,text=True).strip()
    save(output/'starting_revision.json',dict(HEAD=git(ROOT,'rev-parse','HEAD'),branch=git(ROOT,'branch','--show-current'),
        working_tree_status=git(ROOT,'status','--short'),scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',
        read_only_history_HEAD=git(history_repository,'rev-parse','HEAD'),
        read_only_history_branch=git(history_repository,'branch','--show-current')))
    save(output/'owner_contract.json',native_spectral_length_contract())
    shape_keys={
        'mode_arrays':('graph_Jacobian_action','physical_tangent_action','normalized_constraint_action','initial_mode_action','initial_mode_coefficients','physical_fundamental','node_indices','action_lengths'),
        'backreaction_arrays':('states','action_rates','state_action_first_jet','transition_jacobians_action','state_clock_transition_jacobians','terminal_hit_state_action_first_jet','proper_times','proper_time_density','log_radius_first_jet')}
    shapes={}
    for key,selected in shape_keys.items():
        with np.load(paths[key],allow_pickle=False) as z:
            shapes[key]={name:list(z[name].shape) for name in selected if name in z.files}
    history_scope=dict(mode_domain=mode['domain'],mode_norm=mode['norm'],mode_transport=mode['transport'],
        mode_declared_external_response=mode['external_environment_response'],
        backreaction_domain=back['domain'],backreaction_first_hit=back['first_hit'],
        arrays=shapes,
        current_mode_meaning='73 constrained state tangent gain vectors from SVD, NOT a selected interface-displacement formation/support-loss eigenline',
        current_endpoint_meaning='signed_descriptor=0 and proper_time_density=0 at the canonical stop, NOT an evaluated AE4 support-loss event',
        graph_action_meaning='98-coordinate derivative of normalized cancelled evolution field; no normal-interface displacement input or constrained bulk zero-trace test',
        geometry_incidence_meaning='state covectors D_y log R4 and D_y log N, not a normal-displacement-to-field injection',
        source_role='existing b-source connection insertions are retained photon inputs; they are not variations of the interface embedding X',
        numerical_actions_replayed=False)
    save(output/'retained_history_scope.json',history_scope)
    next_operand=dict(name='interface-normal/bulk-field mixed response forcing',
        symbol='f_psi(eta)=D_Phi D_X S_bulk^owner[eta,xi_psi]',
        input_space='xi_psi in the selected normal-interface harmonic trace space; eta in V0, allowed constrained bulk variations with zero interface trace on the inherited domain',
        output_space='V0 dual; only the source-connected covector/application is needed',
        producer='same-action bulk/interface second variation, including owned moving-trace/contact/domain terms; mechanics harmonic_modes.Z_lambda names its environmental Hessian but does not evaluate this forcing',
        consumer='H_etaeta deltaPhi_psi=-f_psi on V0, followed by the contracted constrained bulk impedance and F(tau)=<psi,(gamma J+Himp-Hdrive)psi>',
        defining_weak_equation='Q_bulk^owner((eta,0),(deltaPhi_psi,xi_psi))=0 for every allowed eta in V0',
        impedance_contraction='z_psi=Q_bulk^owner((deltaPhi_psi,xi_psi),(deltaPhi_psi,xi_psi)) in a justified stationary-response realization',
        stationary_matching_scope='the gauge fixed-trace tree reduction exhibits this method; it does NOT by itself identify the full all-sector mechanical response. The SAME total-action/interface matching is required.',
        observed_implementation_gap='the inspected graph/time response accepts state, weights, reference and signed_descriptor; no xi_psi injection, X-variation or V0 action-dual map is supplied by those arrays/producers',
        all_relevant_science_absence_theorem=False,
        value=None,status='UNEVALUATED_ACTION_REQUIRED_RESPONSE',
        not_a_new_constitutive_or_scalar_energy_postulate=True)
    save(output/'next_operand.json',next_operand)
    save(output/'event_locator.json',dict(
        equality='F(tau,b)=<psi_tau,(gamma_tau J_Sigma+H_impedance-H_event,drive)psi_tau>=0',
        inertia_cancels_from_same_mode_energy_equality=True,
        extra_condition='outward spacetime support ceases under the inherited action; no zero-flux/descriptor/endpoint surrogate adopted',
        selected_branch='continuous physical branch from the action-selected formation event, not a new SVD gain or convenient eigenvalue minimizer',
        formation_event_not_substituted=True,canonical_stop_not_substituted=True,
        locator_executed=False,reason='the source-restricted mixed bulk/interface action above is not evaluated; the independent cessation test is also unevaluated'))
    report,arrays=execute_control()
    save(output/'branch_control.json',report);np.savez_compressed(output/'branch_control_actions.npz',**arrays)
    r,i=sp.symbols('r i',positive=True)
    rx,ry,rxy,ix,iy,ixy=sp.symbols('r_v r_J r_vJ i_v i_J i_vJ')
    T,Hp,Hx,Hy=sp.symbols('T H_P H_v H_J')
    coefficients=lower_limit_coefficients(r=r,i=i,r_x=rx,r_y=ry,r_xy=rxy,i_x=ix,i_y=iy,i_xy=ixy)
    c=i/r;cv=ix/r-i*rx/r**2;cj=iy/r-i*ry/r**2
    cvj=ixy/r-(ix*ry+iy*rx+i*rxy)/r**2+2*i*rx*ry/r**3
    composed=(coefficients['coefficient_T']*T+coefficients['coefficient_H_P']*Hp+
              coefficients['coefficient_H_x']*Hx+coefficients['coefficient_H_y']*Hy)
    residual=sp.simplify(composed-lower_limit_mixed(c,cv,cj,cvj,T,Hp,Hx,Hy))
    if residual!=0:raise AssertionError('adopted quotient/heat composition mismatch')
    save(output/'composed_heat_length_term.json',dict(classification='EXACT_SYMBOLIC_CONSUMPTION__NOT_PHYSICAL_HEAT_EVALUATION',
        c=str(c),c_v=str(cv),c_J=str(cj),c_vJ=str(cvj),
        coefficients={k:str(v) for k,v in coefficients.items()},composed_term=str(composed),
        identity_residual=str(residual),T_coefficient='[(log i)_vJ-(log r)_vJ]/2',
        heat_trace_meanings=dict(T='STr exp(-cP)',H_P='STr(P exp(-cP))',H_v='STr(exp(-cP)P_v)',H_J='STr(exp(-cP)P_J)'),
        native_cotangents_evaluated=False))
    ownership={key:dict(status='UNEVALUATED',value=None) for key in (
        'primitive_Maxwell','common_A_background','Higgs_gauge_local_mixed','gauge_fixing_ghost',
        'induced_heat','relative_zeta_eta','domain_interface','completion')}
    ownership['primitive_Maxwell'].update(already_owned_operand='earlier same-frame local angular Maxwell/curvature rows remain cached; subtraction from complete Gamma not yet evaluated',whole_primitive_diagnostic_subtracted=False)
    ownership['common_A_background'].update(shared_dependency='subset of same-owner local angular/background terms; not an extra addend')
    result=dict(classification='ADOPTED_CUTOFF_TOTAL_JETS_COMPOSED__PHYSICAL_BRANCH_ACTION_UNEVALUATED',
        owner_definition_adopted=True,new_result='full branch contraction two-jets and exact i/r substitution into existing AE4 moving-lower-limit term',
        physical={k:None for k in ('r','i','r_v','r_J','r_vJ','i_v','i_J','i_vJ','support_loss_event','psi_star','c','c_v','c_J','c_vJ','heat_length_contribution','R_ind','native_photon_response','paired_family_heat','a_mu','g_mu')},
        next_operand=next_operand,ownership=ownership,frozen_local=json.loads(paths['frozen'].read_text(encoding='utf8')),
        formation_zero_used_as_support_loss=False,canonical_stop_used_as_support_loss=False,
        default_physical_length_used=False,physical_eigenline_selected_from_control=False,
        error_scope=dict(symbolic='exact supplied-form/quotient/heat identities',control=report['error_scope'],physical_numerical=None,physical_theoretical=None),
        execution=dict(old_production_replays=0,old_source_or_parent_solves=0,physical_branch_actions=0,physical_heat_applications=0,new_control_dimension=2,elapsed_seconds=time.perf_counter()-start))
    save(output/'result.json',result)
    save(output/'checkpoint.json',dict(id='BHSM_MUON_SUPPORT_LOSS_TOTAL_CONTRACTION_AND_HEAT_COMPOSITION_20261007',
        stage='adopted owner implemented; total branch/heat algebra evaluated; physical assembly stops at first mixed bulk/interface response forcing',
        next_operand='next_operand.json',result='result.json',physical_a_mu=None,physical_g_mu=None))
    save(output/'output_hashes.json',{p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file()})
    print(json.dumps(dict(output=str(output),classification=result['classification'],
        control_c_xy=report['c']['c_xy'],symbolic_heat_identity_residual=str(residual),physical_heat_applications=0,seconds=result['execution']['elapsed_seconds'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--history-repository',type=Path,default=Path(r'C:\Users\carbe\OneDrive\Documents\CODEX\Berger-Hopf-Standard-Model'))
    a=parser.parse_args();run(a.output,a.history_repository)
