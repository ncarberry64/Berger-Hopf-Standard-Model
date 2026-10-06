"""Execute NEW signed primitive angular responses; never replay old producers.

This does not fulfill the full native photon solve. Use a fresh output path.
Saved checkpoints separate the evaluated component from the absent owner
remainder. No heat length, physical scale or boundary condition is selected.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bhsm.interface import muon_native_photon_response as impl


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: np.array(z[k]) for k in z.files}


def run(output):
    if output.exists():
        raise FileExistsError('Preserve saved evidence; use a fresh output directory')
    output.mkdir(parents=True)
    start = time.perf_counter()
    refs = dict(
        primitive=ROOT/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz',
        geometry=ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        family=ROOT/'artifacts/muon_native_family_difference_20261006/run_1/family_source_actions.npz',
        frozen=ROOT/'artifacts/muon_source_jet_20261002/frozen_local.json',
        component_builder=Path(impl.__file__),
        angular_builder=ROOT/'src/bhsm/interface/muon_matched_mechanical_source.py',
        owner=ROOT/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        heat_kernel=ROOT/'src/bhsm/interface/arb_heat_pencil_contractions.py',
        stop=ROOT/'src/bhsm/interface/ae4_current_c2_canonical_stop_domain_bridge.py',
        source_builder=ROOT/'src/bhsm/interface/muon_local_source_jet.py',
        replay=Path(__file__))
    hashes={k:dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for k,p in refs.items()}
    git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    save(output/'input_hashes.json',hashes)
    save(output/'starting_revision.json',dict(HEAD=git('rev-parse','HEAD'),branch=git('branch','--show-current'),
        reference='524ed90689bd5923c249bba2e699abf627e703cd',status=git('status','--short')))
    save(output/'checkpoint.json',dict(stage='saved input identities; old producers not replayed'))
    action=impl.primitive_cut_action(load(refs['primitive']),load(refs['geometry']))
    current=impl.reached_current(action,load(refs['family']))
    np.savez_compressed(output/'component_action_and_current.npz',
        **{k:v for k,v in action.items() if isinstance(v,(np.ndarray,float,int))},
        **{k:v for k,v in current.items() if isinstance(v,(np.ndarray,float,int))})
    response=impl.source_directed_component_response(action,current)
    save(output/'checkpoint.json',dict(stage='component shifted solves complete; arithmetic certification pending',
        enrichment=response['stages'],native_solve=False))
    certificates=[]
    for i,record in enumerate(response['records']):
        np.savez_compressed(output/f'response_{i}.npz',**{k:v for k,v in record.items() if isinstance(v,np.ndarray)})
        certificate=impl.certify_frozen_component(action,current,record)
        certificate['zeta_over_kappa1']=record['zeta_over_kappa1']
        certificates.append(certificate)
        save(output/f'certificate_{i}.json',certificate)
        save(output/'checkpoint.json',dict(stage=f'arithmetic certificate {i+1}/3 saved',native_solve=False))
    np.savez_compressed(output/'enriched_frame.npz',M_orthonormal_frame=response['independent_frame'])
    native_error=None
    try:
        impl.require_native_photon_action()
    except NotImplementedError as e:
        native_error=str(e)
    required=dict(
        name='completed same-owner polarization action on the reached current/response directions',
        equation='R_ind(v,j)=delta_v delta_j Gamma_AE4[0]-H_local,already_owned(v,j)',
        contact='(1/2) integral_[ell_star^2,infinity] dt STr(exp(-t P0) P_vj)',
        paired='-(1/2) integral_[ell_star^2,infinity] dt integral_[0,t] du STr(exp(-(t-u) P0) P_v exp(-u P0) P_j)',
        completion='relative-zeta/eta, moving Gram/length/domain and source-pullback terms required by the same owner',
        producer='AE4 microscopic_owner_contract and its realized source/contact jets on the inherited BRST/reset/material/stop domain',
        consumer='native K0Q action on current dual basis and action-generated complement before (K0Q+zeta M0Q) solve; then graded family-mixed heat',
        input_space='these b-source/current directions plus the connected response, with temporal/radial continuation and quotient traces retained',
        output_space='geometric photon form dual in the same domain',
        status='UNEVALUATED prescribed action application; no missing jmath, common-A coefficient, or new seam postulate asserted',
        native_spectral_length='ell_star remains symbolic; it enters the induced Hessian integral lower limit before its numerical photon form can be computed',
        all_native_missing_terms_resolved=False)
    entries={k:dict(classification='UNEVALUATED',paired_contribution=None) for k in
        ('native_bulk_heat','state_variation','contact','domain_boundary','completion_counterterm','strong_within_native')}
    entries['contact']['evaluated_subterm']='previous fixed-frame direct mass/photon contact only; unchanged'
    result=dict(
        classification='ACTUAL_CURRENT_FULL_AMBIENT_PRIMITIVE_ANGULAR_RESPONSE__NOT_NATIVE_PHOTON_SOLUTION',
        requested_native_target_reached=False,acceptable_native_partial_claimed=False,
        new_object='signed 240-dimensional angular density resolvent on actual retained current duals',
        point=dict(rho=action['rho'],history='C2 step1222 artificial cut; first retained parent node',radial_index=64,
            lambda_value=action['mechanical_lambda'],W=action['full_pointwise_weight']),
        source=dict(coordinate='b_A, beta=T_b b, A_Q=sqrt(2) beta; not physical signed transfer',
            current='f_R Gamma_bar_complete, 8 by (4*56); dual load satisfies Sdagger J=current',
            f_R=action['f_R'],full_fermion_columns=224,
            nonzero_fermion_columns=int(np.count_nonzero(np.linalg.norm(current['mode_current_covector'],axis=0)>0)),
            source_coordinate_conversion_count=1,vertex_action_index_factor=False,
            duality_residual=current['duality_residual'],charged_conjugate_trace_doubled=False),
        pairing=dict(M_geometric_scalar=action['M_geometric_scalar'],
            equation='M_geom=2 pi^2 nu C r T_b^2=nu C r/Rb; geometric one-form angular density',
            photon_M_is_lepton_mass=False,source_load_multiplied_by_M=False),
        operator=dict(ambient_dimension=240,levels=[1,3],internal_basis='unit primitive Tr16 weak-adjoint plus hypercharge',
            equation='Khat_angular=-d/(16/3) [(C+(lambda-1)T)dagger(C+(lambda-1)T)+4lambda(lambda-1)B]',
            Lorentz_angular_sign=-1,kappa1='symbolic; K_primitive=kappa1*Khat and zeta=kappa1*zeta_hat',
            index_factor='K_Q=(2/3)K_component already inside d; undo Tr16 Q^2 once for the unit-trace basis',
            M_scalar_identity=True,quotient='ambient spatial component; native BRST/constraint quotient NOT claimed',
            primitive_angular_closed_levels=True,native_propagated_complement_certified=False,
            full_positive_K_claimed=False,physical_scale_selected=False),
        checks=action['checks'],
        shifts=[dict(zeta_over_kappa1=x['zeta_over_kappa1'],
            spectral_parameter_only=True,ambient_solve_difference_norm=x['ambient_solve_difference_norm'],
            ambient_return_difference_norm=x['ambient_return_difference_norm'],
            max_current_equation_residual=float(np.max(x['full_current_residuals'])),
            current_return_frobenius_norm=float(np.linalg.norm(x['current_return'])),
            current_return_trace_real=float(np.trace(x['current_return']).real),
            current_return_Hermiticity_residual=float(np.linalg.norm(x['current_return']-x['current_return'].conj().T))) for x in response['records']],
        enrichment=response['stages'],conditioning_frobenius_bound=response['conditioning_frobenius_bound'],
        final_frame_M_Gram_residual=float(np.linalg.norm(action['M_geometric_scalar']*
            response['independent_frame'].conj().T@response['independent_frame']-np.eye(response['independent_frame'].shape[1]))),
        certificates=certificates,
        ownership=dict(evaluated='primitive signed angular kinetic and curvature-contact density, full source-reached ambient complement; geometric one-form pairing',
            known_but_not_assembled='temporal/radial/shift/moving-frame weak rows; inherited domain traces',
            unknown_not_zero='completed induced photon polarization with native domain/constraint/completion actions',
            old_parent_solve_reused_as_photon=False,primitive_added_to_full_owner=False),
        native_action_attempt=dict(reached=False,first_unavailable_action=required,error=native_error),
        heat_consumer=dict(invocations=0,ell_star_numerical=None,default_length_used=False,
            reason='This component retains the Lorentz angular sign and omits native contributions; it is not an established positive native boson branch.',
            family_mass_jets_replayed=False,paired_native_mu_e=None),
        errors=dict(certified='residual and consumed-current contraction error for EXACT stored angular-component matrices only',
            geometry_source_float_representation=None,history_interpolation=None,temporal_radial_quadrature=None,
            BRST_domain_and_completion=None,continuum=None,native_error=None),
        ledger=entries,frozen_local=json.loads(refs['frozen'].read_text()),
        physical_a_mu=None,physical_g_mu=None,physical_transfer_directions=0,
        execution=dict(old_production_replays=0,primitive_component_shifted_solves=3,full_native_shifted_solves=0,
            new_operator_eigenspectra=0,elapsed_seconds=time.perf_counter()-start))
    save(output/'result.json',result)
    save(output/'missing_action.json',required)
    save(output/'checkpoint.json',dict(id='BHSM_MUON_ACTUAL_CURRENT_PRIMITIVE_ANGULAR_RESPONSE_20261006',
        stage='component response and outward arithmetic bounds saved; native owner application not executable',
        result='result.json',next_action=required,native_solve=False,physical_a_mu=None,physical_g_mu=None))
    save(output/'output_hashes.json',{p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file()})
    print(json.dumps(dict(output=str(output),dimension=240,enrichment=response['stages'],
        max_residual=max(x['max_current_equation_residual'] for x in result['shifts']),
        max_consumed_bound=max(x['current_return_frobenius_error_upper'] for x in certificates),
        native_target_reached=False,seconds=result['execution']['elapsed_seconds'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
