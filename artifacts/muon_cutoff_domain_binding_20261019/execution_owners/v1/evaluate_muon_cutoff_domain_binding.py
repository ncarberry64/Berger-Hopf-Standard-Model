"""Consume new surface/domain/whole-overlap operands without native0 replay."""
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
from bhsm.interface.muon_cutoff_domain_binding import (
    surface_inertia_forms,cutoff_inertia_coefficient,remove_recorded_local,
    recorded_local_value,past_future_weyl,consume_comparison_domain,
)
from bhsm.interface.muon_coupled_reference_replacement import MULTIPLIER_ROWS
from bhsm.interface.retained_response.finite_time_response import write_npz


def pin(path):return sha256(path.read_bytes()).hexdigest()


def load_application(path):
    receipt=path.with_name('result.json');md=json.loads(receipt.read_bytes())
    if pin(path)!=md['arrays']['sha256']:raise ValueError('saved arrays changed: '+str(path))
    for rel,h in md['input_sha256'].items():
        if pin(ROOT/rel)!=h:raise ValueError('saved input identity changed: '+rel)
    with np.load(path,allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
    return a,md,{path.relative_to(ROOT).as_posix():pin(path),receipt.relative_to(ROOT).as_posix():pin(receipt)}


def residuals(g,area,active,held):
    m=g[MULTIPLIER_ROWS];a=area[MULTIPLIER_ROWS]
    return dict(partial_original150_max=float(np.max(abs(g[:150]))),
        geometry62_max=float(np.max(abs(g[:62]))),
        multiplier_outside_area_max=float(np.max(abs(m-a*np.dot(a,m)/np.dot(a,a)))),
        held_wall_radial32_max=float(np.max(abs(g[62+held]))),
        active52_partial_max=float(np.max(abs(g[62+active]))),
        Higgs4_max=float(np.max(abs(g[146:150]))),complete_physical_residual=None)


def run(output):
    if output.exists():raise FileExistsError('preserve completed runs')
    native,nmd,pins=load_application(ROOT/'artifacts/muon_stationary_native_reference_load_20261019/run_4/native_reference_load.npz')
    coupled,cmd,more=load_application(ROOT/'artifacts/muon_coupled_reference_replacement_20261019/run_2/coupled_replacement.npz');pins.update(more)
    x=coupled['provisional_iterate151']
    if not np.array_equal(x,native['input_iterate151']):raise ValueError('background identity mismatch')
    reference=ROOT/'artifacts/muon_adopted_incoming_reference_20261018/run_5/reference_application.npz'
    with np.load(reference,allow_pickle=False) as z:rho=z['radial_points48'].copy();rw=z['radial_weights48'].copy()
    pins[reference.relative_to(ROOT).as_posix()]=pin(reference)
    local=remove_recorded_local(coupled)
    value=recorded_local_value(coupled,rho,rw)
    before=native['known_plus_native0_gradient151'];beforeK=native['known_plus_native0_Hessian151']
    after=before-local['local_gradient151'];afterK=beforeK-local['local_Hessian151']
    expected=local['bare_gradient151']+native['actual_gradient']
    identity=float(np.max(abs(after-expected)))
    if identity>5e-12:raise ArithmeticError('whole local replacement identity failed')
    ng=np.r_[native['actual_gradient'],nmd['load']['cutoff_cotangent']]
    nk=np.zeros((152,152));nk[:151,:151]=native['actual_hessian']
    nk[:151,151]=native['actual_field_cutoff_mixed'];nk[151,:151]=nk[:151,151]
    nk[151,151]=nmd['load']['cutoff_second']
    partialJac=np.c_[afterK[:150],native['actual_field_cutoff_mixed'][:150]]
    forms=surface_inertia_forms(coupled['after_raw_geometry100'])
    folder=ROOT/'artifacts/muon_retained_response_20261018/inputs'
    history=folder/'outgoing_history.npz';metadata_path=folder/'history_metadata.json';prov=folder/'PROVENANCE.json'
    provenance=json.loads(prov.read_bytes());metadata=json.loads(metadata_path.read_bytes())
    if pin(history)!=provenance['files']['inputs/outgoing_history.npz']['sha256']:
        raise ValueError('retained outgoing history identity changed')
    incidence=next(r for r in metadata['sides']['outgoing'] if r['label']=='lo')
    if incidence['time']!=0. or metadata['histories']!='PROVISIONAL_NOT_COLLIDER_SOLUTIONS':
        raise ValueError('retained child-side incidence scope changed')
    with np.load(history,allow_pickle=False) as z:child_raw=z['lo_raw_fields'].copy()
    child=surface_inertia_forms(child_raw[:100])
    for p in (history,metadata_path,prov):pins[p.relative_to(ROOT).as_posix()]=pin(p)
    domain=past_future_weyl(native['actual_theta'],spectral_parameter=-1.)
    consumed=consume_comparison_domain(domain,native['actual_theta_gradient'],native['actual_theta_hessian'])
    arrays=dict(comparison_iterate151=x,retained_child_plus_raw268=child_raw,
        preserved_worsened_partial_rows151=before,preserved_worsened_partial_Hessian151=beforeK,
        recorded_local_gradient151=local['local_gradient151'],recorded_local_Hessian151=local['local_Hessian151'],
        after_whole_local_removal_partial_rows151=after,after_whole_local_removal_partial_Hessian151=afterK,
        saved_native0_augmented_covector152=ng,saved_native0_augmented_Hessian152=nk,
        original150_by_field_and_c_partial_Jacobian=partialJac,
        boundary_W=domain['W'],boundary_Omega=domain['Omega'],
        boundary_native_system36=domain['system'])
    arrays.update({k:v for k,v in consumed.items() if isinstance(v,np.ndarray)})
    surface_report={}
    for label,data,is_child in [('comparison',forms,False),('retained_child_plus',child,True)]:
        sr={}
        for name,item in data['forms'].items():
            for key,v in item.items():
                if hasattr(v,'gradient'):
                    arrays[label+'_'+name+'_'+key+'_value']=np.array(v.value)
                    arrays[label+'_'+name+'_'+key+'_gradient100']=v.gradient
                    arrays[label+'_'+name+'_'+key+'_Hessian100']=v.hessian
            d=7 if name=='M8' else 4
            piece=cutoff_inertia_coefficient(item['proper_inertia_per_gamma'],dimension=d,
                cutoff_anchor=nmd['executed']['cutoff']['value'],full_geometry=is_child)
            arrays[label+'_'+name+'_cutoff_row_coefficient_value']=np.array(piece.value)
            arrays[label+'_'+name+'_cutoff_row_coefficient_gradient']=piece.gradient
            arrays[label+'_'+name+'_cutoff_row_coefficient_Hessian']=piece.hessian
            sr[name]=dict(proper_inertia_coefficient_per_gamma=float(item['proper_inertia_per_gamma'].value),
                coordinate_sdot_inertia_per_gamma=float(item['coordinate_sdot_inertia_per_gamma'].value),
                source_momentum_per_gamma=float(item['coordinate_source_momentum_per_gamma'].value),
                proper_clock_projection_identity_defect=float(item['identity_twojet_defect']),
                original_area_kinetic_defect=float(item['independent_area_kinetic_defect']),
                original_momentum_kinetic_defect=float(item['independent_momentum_kinetic_defect']),
                cutoff_row_inertia_coefficient=float(piece.value),
                cutoff_coordinate_first=float(piece.gradient[-1]),cutoff_coordinate_second=float(piece.hessian[-1,-1]))
        surface_report[label]=dict(ambient_lapse=float(data['ambient_lapse'].value),
            induced_lapse=float(data['induced_lapse'].value),proper_normal_projection=float(data['proper_normal_projection'].value),
            wall_velocity=float(data['wall_velocity'].value),separate_forms=sr)
    for side,a in domain['maps'].items():
        arrays.update({'boundary_'+side+'_'+k:v for k,v in a.items() if isinstance(v,np.ndarray)})
    output.mkdir(parents=True);ap=output/'cutoff_domain_binding.npz';write_npz(ap,arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and path and Path(path).resolve().is_relative_to(ROOT):
            p=Path(path).resolve();pins[p.relative_to(ROOT).as_posix()]=pin(p)
    for rel in ('scripts/evaluate_muon_cutoff_domain_binding.py',
        'src/bhsm/interface/ae4_branch_relative_support_transition.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        'artifacts/muon_adopted_incoming_reference_20261018/adoption_v1.json',
        'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'):
        pins[rel]=pin(ROOT/rel)
    active=coupled['original_active52_indices84'].astype(int);held=coupled['original_held32_indices84'].astype(int)
    area=coupled['after_area_gradient_per_gamma']
    checks={side:{k:v for k,v in a.items() if isinstance(v,(int,float))} for side,a in domain['maps'].items()}
    record=dict(schema='bhsm.cutoff-domain-binding.v1',parent_head='bf894be3f93de0c6faffff492a1220a730222d2b',
        classification='EVALUATED_SURFACE_INERTIA_FORMS_PAST_NATIVE_DOMAIN_RETURN_AND_WHOLE_RECORDED_LOCAL_REPLACEMENT',
        input_sha256=pins,arrays=dict(path=ap.name,sha256=pin(ap)),
        runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        preserved=dict(native0_heat_recomputed=False,native0_precision_repeated=False,
            native0_value=nmd['load']['full_native0_Lorentz_density'],native0_cutoff_cotangent=ng[-1],
            native0_cutoff_second=nk[-1,-1],native0_field_cutoff_mixed_norm=float(np.linalg.norm(nk[:151,-1])),
            old52_solve_repeated=False,partial_minimization=False,background_changed=False,
            old_worsened_residuals=nmd['residuals_after_partial_native'],old52_factorization_used=False),
        full_local_replacement=dict(equation='S_loc=MAXWELL_TO_CAP*(S_M[Abar+a]-S_M[Abar])+S_H,material/(2*pi^2)^2; REMOVE ENTIRE S_loc once, not a single-block allocation',
            values=value,new_action_value_bare_plus_native0=local['bare_action_value']+nmd['load']['full_native0_Lorentz_density'],
            removal_load151_max=float(np.max(abs(local['local_gradient151']))),
            removal_Hessian151_norm=float(np.linalg.norm(local['local_Hessian151'])),
            replacement_identity_defect=identity,mechanical_Maxwell_in_cap_retained=True,
            physical_native_coefficient_calibration_matching='still a required check; no extra unknown counterterm or fitted subtraction chosen',
            remainder='all complementary angular/species/strata, phase, actual event/boundary and matched inherited-state difference remain unevaluated. The full recorded local term has now been removed once.'),
        cutoff_binding=dict(equation='F(c)=c R_bulk-I_bulk+sum_s alpha_FSC c^(-d_s/2)*(c J_restoring,s-I_s)=0 on SAME formed child-plus birth branch/domain',
            newly_evaluated='bare surface proper-normal kinetic coefficients rho8=A^3 B^3 and rho5=R4^3/(2*pi^2), their complete geometry100 jets, canonical source/qdot contacts and cutoff-row inertia coefficients',
            consumed='new -c^(-d/2)*rho coefficient plus its field/c and second-c jets inserted into the implicit cutoff-row ledger per unassigned alpha and formed-mode norm/pairing; distinct151-comparison and100-child charts are not glued',
            local_proof='Q=sqrt(1-U^2), p=C/(Cstar Q), l=N Q; L=-N rho Q, L_sdot,sdot=rho C^2/(Cstar^2 N Q^3); I_proper=l L_sdot,sdot/p^2=rho; Pi_s=rho p U; Pi_qdot=-s Pi_s D_q log Cstar',
            restoring='J_restoring is the kinetic-separated constrained worldvolume restoring form, not raw area S_ss, not a spatial-slice Jacobi coefficient and not the full time-derivative operator',
            formed_mode='rho is a form coefficient, not <psi,I psi>. Actual mode, state/domain/stratum pullbacks and their total jets remain required; no psi=1 or unit norm inferred',
            alpha_FSC='symbolic positive primitive; not assigned1/137, alpha_EM or fitted from the anomaly',
            actual_birth_condition='<psi_mu_plus,(R_mu_plus-H_event,drive)psi_mu_plus>=0 remains unevaluated',
            physical_c=None,physical_Dc=None,physical_D2c=None,
            saved_native_chain='D L=L_y+L_c Dc; D2L=L_yy+L_yc tensor Dc+Dc tensor L_cy+L_cc Dc tensor Dc+L_c D2c; saved all native coefficients consumed in augmented152 jet, no Dc/D2c substituted as zero',
            coupled_rule='For a simple full root F=0, Dc=-F_y/F_c and D2c=-(F_yy+F_yc tensor Dc+Dc tensor F_cy+F_cc Dc tensor Dc)/F_c; bulk, mode, domain and explicit-c partials must all enter',
            numerical_anchor='same saved c=1 function coordinate only, never a solved or selected physical cutoff',
            surface_forms=surface_report,
            retained_child_incidence=dict(label='outgoing lo at t=0',time=incidence['time'],histories=metadata['histories'],
                scope='retained provisional child-side local geometry at the export event; not collider solution or complete realized muon transfer')),
        domain_application=dict(equation="u'=-C u+v; v'=B v-lambda u, C=W+z Omega, B=W-z Omega; L2 past selects positive-real exponents; z=-i analytic branch reused",
            domain='past half-line stationary comparison, H1(R_proper) constant-angular full18. Product Calderon graph is not the incoming particle/antiparticle selector or CAR state',
            spectral_parameter=-1.,spectral_parameter_is_cutoff_or_energy=False,
            conormal='v=A_z u; exterior past outward +v, core left outward -v, row -v_core+M_past u=0 with no extra N,Haar,R3,charge or pair weight',
            actual_consumer='G(tau,0)=exp((M_past/future-C)tau)*(M_past-M_future)^(-1); original equations and delta*I18 conormal jump consumed at the artificial cut of ONE operator',
            identity_glue_of_cap_histories=False,future_comparison_is_physical_child=False,
            future_comparison_role='only verify the already-used whole-line native0 factorization; actual event/future map remains a separate operand',
            current_contraction='beta_past,a=Tr(G_boundary D_a M_past), beta_future,a=-Tr(G_boundary D_a M_future); complete ordered derivatives retained; individual pieces need not be symmetric',
            past_contraction151_max=float(np.max(abs(consumed['past_cut_covector152'][:151]))),
            past_Higgs_Re2_contraction=[float(consumed['past_cut_covector152'][147].real),float(consumed['past_cut_covector152'][147].imag)],
            added_to_heat_or_current_as_new_force=False,domain_rows_do_not_replace_physical_E1_join=True,
            actual_event_binding_remaining='full moving trace/normal/phase and interacting C1-to-child transmission plus Cauchy incidence at the same fields; no U=identity imposed',
            dichotomy_real_gap=domain['dichotomy_real_gap'],original_Riccati_jet_checks=checks,
            original_first_order_rows_max=consumed['original_first_order_rows_max'],
            conormal_jump_max=float(np.max(abs(consumed['conormal_jump_rows']))),
            past_core_seam_max=float(np.max(abs(consumed['past_core_seam_rows']))),
            new_resolvent_frequency_identity_defect=consumed['frequency_Green_identity_defect'],
            full_gluing_derivative_symmetry_defect=consumed['full_gluing_Hessian_symmetry_defect']),
        residuals_preserved_before= residuals(before,area,active,held),
        residuals_after_whole_local_removal=residuals(after,area,active,held),
        equations_not_closed=dict(physical_unit='GF exp(2e)-cF[fields,Cauchy incidence,normalized external legs]=0 remains independent of dS/de',
            cutoff='F=0 is NOT dS/dc=0; alpha, formed-mode contraction, bulk resistance/inertia and worldvolume restoring/domain remain unevaluated',
            native_remainder='complementary angular/species/strata, relative phase, actual moving/event-boundary completion and matched inherited-state difference, all at common c/domain',
            state='no C_plus=occupation, new vacuum, fitted20 state contractions, or duplicated reference current',
            local_matching='full recorded subtraction evaluated; native asymptotic coefficient/calibration matching still must pass'),
        error_scope='binary local/action jets and ordered-Schur/Sylvester comparison-domain application only; no outward-rounded continuum/time/domain/phase error enclosure or physical cutoff/mode evaluation. Historical gauge7.29e-10/6.33e-10 and membrane9.34e-8 nonpasses retained.',
        physical_guard=2e-10,physical_derivative_admitted=False,complete_physical_residual=None,
        coupled_correction=None,magnetic_readout_or_uncertainty=None,
        NEXT_OPERAND='Evaluate the formed child-plus normal/constraint and interacting event-domain pullback on the retained moving data, producing same-branch bulk R/I and restoring forms with total mode/pairing/domain/c jets. Use the new past return in that event graph; solve F with the fields rather than choosing c. Then complete native/state/phase matching before physical admission, coupled correction and fresh Maxwell/all226 checks.')
    (output/'result.json').write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(output=str(output),local=record['full_local_replacement'],surfaces=surface_report,
        domain=record['domain_application'],residuals=record['residuals_after_whole_local_removal']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output.resolve())
