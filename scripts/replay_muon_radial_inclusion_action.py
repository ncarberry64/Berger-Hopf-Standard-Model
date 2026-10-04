"""Full radial norm, current candidate action and source overlap; no old replay."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path
import numpy as np


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def git(root,*a):return subprocess.check_output(['git','-C',str(root),*a],text=True).strip()


def owned_prefix_receipt(root,path):
    inputs=json.loads((path/'input_hashes.json').read_text())
    for key in ('field','field_report','metric','pairing','contact','corrected'):
        entry=inputs[key];p=Path(entry['path']);p=p if p.is_absolute() else root/p
        if sha(p)!=entry['sha256']:raise ValueError(f'owned-prefix input identity changed: {p}')
    return dict(result=json.loads((path/'result.json').read_text()),path=str(path),
        physical_input_identities_matched=True,physical_endpoint_substitution=False,
        executed_code_hashes={key:inputs[key] for key in ('module','script','producer','clock_producer')},
        consumer='isolated lapse-time action on the actual source directions, kept separate from the endpoint candidate interface')


def run(root,out,resume_scalars=None,owned_prefix_jet=None):
    if out.exists():raise FileExistsError('new output required; previous scientific data are immutable')
    out.mkdir(parents=True);began=time.perf_counter();sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_radial_inclusion_action import full_normalization,certified_source_scalar,projected_means,source_actions_and_interface
    from bhsm.interface.muon_cut_inverse_coverage import encoded
    refs=dict(metric=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        source=root/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz',
        contact=root/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        corrected=root/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        pairing=root/'artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz',
        rate=root/'artifacts/muon_parent_source_rate_20261003/replay_reference/cut_rate_record.json',
        frozen=root/'artifacts/muon_cut_inverse_coverage_20261003/frozen_local.json',
        ledger=root/'artifacts/muon_cut_inverse_coverage_20261003/native_ledger.json',
        module=root/'src/bhsm/interface/muon_radial_inclusion_action.py',script=Path(__file__),
        action=root/'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        radial_producer=root/'src/bhsm/interface/aether_cartan_shell_crossing_v15_76.py',
        radial_consumer=root/'src/bhsm/interface/aether_invariant_sobolev_schur_pushforward_v15_82.py',
        body=root/'src/bhsm/interface/muon_parent_source_contact.py',
        domain=root/'src/bhsm/interface/action_extension_global_spin_reset_ae2.py',
        chiral_domain=root/'src/bhsm/interface/ae31_c2_chiral_green_domain.py')
    if resume_scalars:refs['scalar_cache_inputs']=resume_scalars/'input_hashes.json'
    if owned_prefix_jet:
        refs['owned_prefix_result']=owned_prefix_jet/'result.json'
        refs['owned_prefix_inputs']=owned_prefix_jet/'input_hashes.json'
    save(out/'input_hashes.json',{k:dict(path=str(p.relative_to(root)) if p.is_relative_to(root) else str(p),sha256=sha(p)) for k,p in refs.items()})
    save(out/'workspace.json',dict(branch=git(root,'branch','--show-current'),head=git(root,'rev-parse','HEAD'),
        reference='524ed90689bd5923c249bba2e699abf627e703cd',starting_commit='ebe53e9037b88fce5885934f7424d4f7801270b6',
        status=git(root,'status','--short')))
    geometry,source,contact,corrected,pairing=[read(refs[k]) for k in ('metric','source','contact','corrected','pairing')]
    rate=json.loads(refs['rate'].read_text())
    if resume_scalars:
        from flint import arb,ctx
        ctx.prec=192;prior=json.loads(refs['scalar_cache_inputs'].read_text())
        for key in ('metric','source','contact','corrected','pairing','rate'):
            if prior[key]['sha256']!=sha(refs[key]):raise ValueError(f'{key} input changed; scalar cache cannot be reused')
        norm=json.loads((resume_scalars/'full_normalization.json').read_text())
        I=arb(norm['I_rad']['arb']);Idot=arb(norm['I_rad_dot']['arb'])
        scalar_receipt=json.loads((resume_scalars/'source_scalar_integral.json').read_text());scalar=arb(scalar_receipt['scalar']['arb'])
        means={k:arb(v['arb']) for k,v in json.loads((resume_scalars/'projected_means.json').read_text()).items()}
        save(out/'scalar_cache_receipt.json',dict(path=str(resume_scalars),input_identities_matched=True,
            reused_norm=True,reused_source_scalar=True,reused_projected_means=True,new_scalar_integrations=0,
            files={n:sha(resume_scalars/n) for n in ('full_normalization.json','source_scalar_integral.json','projected_means.json')}))
    else:
        I,Idot,norm=full_normalization(geometry)
        save(out/'full_normalization.json',norm)
        save(out/'stage.json',dict(stage='full64-cell norm and consumed time derivative evaluated; validated source integral next',old_productions_rerun=0))
        scalar,scalar_receipt=certified_source_scalar(geometry,contact,I)
        save(out/'source_scalar_integral.json',scalar_receipt)
        means=projected_means(geometry,I,Idot,rate)
    save(out/'full_normalization.json',norm);save(out/'source_scalar_integral.json',scalar_receipt)
    trace_cache=resume_scalars/'cut_trace_scalar_integral.json' if resume_scalars else None
    if trace_cache and trace_cache.exists():
        trace_receipt=json.loads(trace_cache.read_text());trace_scalar=arb(trace_receipt['scalar']['arb'])
    else:
        trace_scalar,trace_receipt=certified_source_scalar(geometry,contact,I,cauchy_trace=True)
    save(out/'cut_trace_scalar_integral.json',trace_receipt)
    save(out/'projected_means.json',{k:encoded(v) for k,v in means.items()})
    save(out/'stage.json',dict(stage='new full-cap scalar contractions saved; current source actions/interface next',old_productions_rerun=0))
    arrays,action=source_actions_and_interface(geometry,source,contact,corrected,pairing,rate,I,Idot,means,scalar,trace_scalar)
    np.savez_compressed(out/'radial_source_action_and_interface.npz',**arrays)
    dt=float(geometry['proper_times'][1]-geometry['proper_times'][0]);Rb=float(geometry['base_radius'][0,-1]);nb=float(geometry['proper_lapse'][0,-1])
    nodalH=float((geometry['base_radius'][1,-1]-geometry['base_radius'][0,-1])/dt/Rb)
    nodalnu=float((geometry['proper_lapse'][1,-1]-geometry['proper_lapse'][0,-1])/dt)
    material_log_jet_defect=1.5*(float(rate['value'])-nodalH)-nodalnu/(2*nb)
    uw=np.sin(float(geometry['rho'][-1])/2)/np.sqrt(float(I.mid()))
    lr0=float((geometry['base_radius'][0,1]-geometry['base_radius'][0,0])/(geometry['rho'][1]-geometry['rho'][0]))
    clock=dict(coordinate='retained boundary proper tau, fixed rho derivatives',
        metric_interior='exact saved right first-cell nodal derivatives; unchanged current Dirac body reconstruction',
        normalization_I_dot='full-cap integral of the SAME C_tau; f_child=rho/2 is fixed at fixed rho',
        wall_Rb_dot_over_Rb_owned=rate['value'],owned_interval=rate['interval'],
        wall_nu_b_dot=0,why='boundary proper-lapse normalization, not the cached tiny difference quotient',
        nodal_boundary_Rb_dot_over_Rb=nodalH,nodal_boundary_nu_b_dot=nodalnu,
        nodal_minus_owned_H=nodalH-float(rate['value']),
        material_log_u_tau_plus_I_dot_over_2I=material_log_jet_defect,
        reconstructions_identified=False,placeholder_H_used=False,affine_logR_slope_used=False,
        consistency='the same geometric-L2 density isometry differentiates to M4_tau=3 H_owned M4 even with distinct interior metric reconstruction; material trace derivative mismatch remains explicit')
    save(out/'clock_derivative_contract.json',clock)
    domain=dict(center=dict(r_zero=float(geometry['base_radius'][0,0]),r_first_cell_slope=lr0,
        exact_nodal_powers='r~rho, sin(rho/2)~rho/2: u~rho^-1/2, mu5 |u|^2~rho^2, mu5 |D5W|^2 bounded',
        green_flux_limit=0,meaning='finite first-order local graph closure; no smoothness or strong squared-domain claim'),
        material=dict(trace_multiplier=uw,trace_is_wall_coefficient=False,
            matching='gamma0_plus=u_plus|wall psi_plus; gamma0_minus=S_cw u_minus|wall psi_minus; opposite normal Green forms cancel when these full traces agree',
            same_scalar_two_sheet_trial_flux_cancels=True,physical_material_extension_evaluated=False),
        reset=dict(equation='Gamma0_child W_child T_R = U_R Gamma0_event W_event',
            full_coupled_graph='Gamma0_child(W_child psi_child+chi_child)=U_R Gamma0_event(W_event psi_event+chi_event)',
            zero_reset_complement_required=False,reduced_mode_invariance_required=False,
            cut_trace_pairing='mu_Sigma=2*pi^2 C r^3; G_Sigma=M4 <1/nu>; NOT the bulk geometric-L2 Gram',
            cut_trace_Gram_scalar=encoded(means['time']),
            common_frame='U_R=I up to the fixed Spin sign and inherited gauge frame, not a new radial parallel transport',
            child_current_cut_trace_evaluated=True,actual_event_child_reset_trace_arrays_evaluated=False,
            first_order_graph_required=True,strong_flux_condition='Gamma1_child=-U_R Gamma1_event only when strong squared domain is asserted'),
        future='inherited canonical-stop domain unchanged; no future tail',
        spin='scalar frame-component W; actual spin connection retained in D5W, no Euclidean-unitary boost assumed',
        oriented_chiral_sectors='both saved LR spin coordinates and full64 carrier outputs retained; normal reversal changes derivative/mass/frame signs together',
        normal_insertion=dict(equation='i epsilon Gamma_perp m_eta; ds=C_rho d rho and current radial coframe identify plus-sheet Gamma_perp=gamma4=i gamma5',
            geometric_action_separate=True,radial_eta_action_separate=True,
            Gaussian_normal_direction_or_mass_replaced=False,normal_eta_not_physical_LR_mass=True))
    save(out/'domain_and_endpoint.json',domain)
    result=dict(classification='evaluated action-provenanced radial candidate, full-cap normalization, current local Dirac action and saved-source weak interface',
        full_normalization=norm,source_scalar_integral=scalar_receipt,action=action,clock_derivatives=clock,domain=domain,
        local_normal_action_residual=float(max(abs(arrays['normal_cancellation_residual']))),
        time_formula_equivalence_residual=float(max(abs(arrays['time_expression_equivalence_residual']))),
        source_coordinate='b; beta=T_b b, independent Q retained; no action-index2/3 multiplier',
        normalization_isometry='integral mu5 |u_vol|^2 d rho=M4; differentiated integral=M4_tau, not kinetic renormalization',
        local_interface_consumed=True,candidate_B_only=True,coupled_global_exterior_K_M=None,stationary_conormal=None,
        physical_a_mu=None,physical_g_mu=None,native_heat_contact=None,physical_transfer_directions=0,
        first_unresolved_operand=dict(name='action-owned lapse temporal jet at the cut endpoint or on its inherited tube',
            equation='partial_tau log nu_cut = Delta_cut/(N_b_cut sigma_cut) sum_k [F_sigma(endpoint)_74+k/weight_74+k] [cos(2k rho)-(-1)^k]',
            input='same cancellation-preserving action-field lapse rows74:86 at endpoint_predictor_center, or a controlled inherited tube enclosure; sigma is the signed descriptor',
            output='owned nu_tau on the saved source support, with center-to-endpoint and spatial-reconstruction errors separated',
            producer='audit_n12_c2_exact_center_fixed_s_field_matrix.build_payload and certify_n12_c2_cancelled_field_lohner_step proper-clock conversion',
            consumer='radial half-density temporal D5W and full coupled inherited exterior K/M with its trace complement',
            status='uncomputed endpoint action coefficient; cached preceding center action recovered and evaluated separately, no new physical profile or state selection'),
        errors=dict(scalar_nodal_integrals='Arb/acb validated at declared precision; source quadrature correction explicitly recorded',
            matrix_roundoff=None,weak_interface_4_point_quadrature_error=None,
            input_H='inherited interval; shared signed H jets saved, other reconstructed inputs fixed',
            continuum_history_or_metric_reconstruction=None,global_domain_and_operator=None,
            strong_or_heat_complement=None,native_theory_uncertainty=None),
        execution=dict(old_productions_rerun=0,old_checks_replayed=0,Gaussian_searches=0,
            scalar_full_cap_norms=int(resume_scalars is None),scalar_cache_reused=bool(resume_scalars),candidate_saved_source_overlaps=2,local_source_interface_contractions=2,
            native_operator_evaluations=0),elapsed_seconds=time.perf_counter()-began)
    if owned_prefix_jet:
        result['recovered_owned_prefix_action']=owned_prefix_receipt(root,owned_prefix_jet)
    save(out/'result.json',result)
    save(out/'checkpoint.json',dict(id='BHSM_MUON_RADIAL_CANDIDATE_ACTION_INTERFACE_20261004',result='result.json',
        arrays='radial_source_action_and_interface.npz',next_operand=result['first_unresolved_operand'],physical_prediction=False))
    save(out/'frozen_ledger.json',{k:json.loads(refs[k].read_text()) for k in ('frozen','ledger')})
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(dict(I=norm['I_rad']['interval'],I_dot=norm['I_rad_dot']['interval'],source_scalar=scalar_receipt['scalar']['interval'],
        projected_means={k:encoded(v)['interval'] for k,v in means.items()},wall_trace_multiplier=uw,norms=action['norms'],elapsed_seconds=result['elapsed_seconds']),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True);p.add_argument('--resume-scalars',type=Path);p.add_argument('--owned-prefix-jet',type=Path)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve(),a.resume_scalars,a.owned_prefix_jet)
