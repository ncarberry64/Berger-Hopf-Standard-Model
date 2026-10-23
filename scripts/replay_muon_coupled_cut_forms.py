"""New cut diagonals, moving complement and guarded exterior assembly.

Consumes the endpoint packet; it never calls its extraction/replay producers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np


def read(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: np.array(z[k]) for k in z.files}


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(root, out):
    if out.exists():
        raise FileExistsError('new dedicated output required')
    out.mkdir(parents=True)
    began = time.perf_counter()
    sys.path.insert(0, str(root/'src'))
    from flint import arb
    from bhsm.interface.muon_coupled_cut_forms import (
        endpoint_form, endpoint_scalars, field_actions, source_frame,
        require_exterior_history_action, ExteriorActionUnavailable)
    refs = dict(
        geometry=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        contact=root/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        corrected=root/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        radial=root/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz',
        endpoint=root/'artifacts/muon_endpoint_clock_20261004/replay_reference/endpoint_clock_source_and_interface.npz',
        endpoint_receipt=root/'artifacts/muon_endpoint_clock_20261004/replay_reference/result.json',
        pairing=root/'artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz',
        norm=root/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/full_normalization.json',
        T=root/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/source_scalar_integral.json',
        Ts=root/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/cut_trace_scalar_integral.json',
        frozen=root/'artifacts/muon_endpoint_clock_20261004/frozen_local.json',
        ledger=root/'artifacts/muon_endpoint_clock_20261004/contribution_ledger.json',
        domain=root/'src/bhsm/interface/action_extension_global_spin_reset_ae2.py',
        effective_action=root/'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        assembly_consumer=root/'src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py',
        current_clock_producer=root/'scripts/certify_n12_c2_cancelled_field_lohner_step.py',
        current_field_producer=root/'scripts/audit_n12_c2_exact_center_fixed_s_field_matrix.py',
        history_geometry_producer=root/'src/bhsm/interface/muon_parent_maxwell_velocity.py',
        module=root/'src/bhsm/interface/muon_coupled_cut_forms.py', script=Path(__file__))
    save(out/'input_hashes.json', {k:dict(path=str(p.relative_to(root)),sha256=sha(p)) for k,p in refs.items()})
    git=lambda *a:subprocess.check_output(['git','-C',str(root),*a],text=True).strip()
    save(out/'workspace.json', dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),
        status=git('status','--short'),reference='524ed90689bd5923c249bba2e699abf627e703cd',
        requested_start='9425d997258a39f9d06ad95a32f7edf0eebe0684'))
    data={k:read(refs[k]) for k in ('geometry','contact','corrected','radial','endpoint','pairing')}
    norm=json.loads(refs['norm'].read_text()); end=json.loads(refs['endpoint_receipt'].read_text())
    mid=lambda x:float(arb(x['arb']).mid())
    rates=dict(I=mid(norm['I_rad']),Idot=mid(end['action_I_dot']),H=mid(end['action_H']),
        T=mid(json.loads(refs['T'].read_text())['scalar']),Ts=mid(json.loads(refs['Ts'].read_text())['scalar']))
    save(out/'stage.json',dict(stage='saved endpoint and instantaneous certificates loaded; new full-cap cut forms next',
                              endpoint_extractions=0,old_replays=0))
    arrays,result=endpoint_form(**data,rates=rates,order=8)
    np.savez_compressed(out/'coupled_cut_source_actions.npz',**arrays)
    save(out/'stage.json',dict(stage='new full-cap diagonals and connected source actions saved; quadrature and assembly attempt next',
                              endpoint_extractions=0,old_replays=0))
    # A single lower-order comparison measures a NEW weak-form quadrature
    # discrepancy; it is not a rigorous remainder or a repeat endpoint solve.
    low,low_result=endpoint_form(**data,rates=rates,order=4)
    np.savez_compressed(out/'lower_order_cut_blocks.npz',**{k:low[k] for k in
        ('local_cut_K_Wp_timejet','local_cut_M_Wp','local_cut_Cauchy_Wp','rhs_K','rhs_M')})
    result['quadrature_comparison']={k:dict(absolute_difference=float(np.linalg.norm(arrays[k]-low[k])),
        relative_difference=float(np.linalg.norm(arrays[k]-low[k])/max(np.linalg.norm(arrays[k]),1e-300)),certified_bound=False)
        for k in ('local_cut_K_Wp_timejet','rhs_K','local_cut_Cauchy_Wp')}
    result['projection_derivative_comparison']={p:{k:float(result[p][k]-low_result[p][k])
        for k in ('B_tau','T_tau')} for p in ('bulk_projection','temporal_Cauchy_projection')}
    # Actual-array comparison of this NEW full-cap action builder against the
    # consumed immutable endpoint source actions, without rerunning them.
    raw,_,_,_,_=source_frame(data['contact'],data['corrected'])
    pp=data['pairing']['gauss_rho']; cc=data['pairing']['gauss_cells']
    scalar=endpoint_scalars(data['geometry'],data['contact'],data['endpoint'],data['radial'],rates,pp,cc)
    action_match={}
    for n in (1,3):
        fields=field_actions(scalar,raw[n],n,data['radial'])
        def flat(k):
            a=data['endpoint'][k]
            return a.transpose(0,2,4,5,1,3).reshape(len(pp),64,n+1,n+1,32)
        action_match[f'n{n}']={kind:dict(absolute_difference=float(np.linalg.norm(a-b)),
            relative_difference=float(np.linalg.norm(a-b)/np.linalg.norm(b))) for kind,a,b in
            [('DW',fields[0],flat(f'updated_D5W_source_action_n{n}')),
             ('Dp',fields[1],flat(f'updated_D5p_source_action_n{n}'))]}
    result['new_builder_saved_action_comparison']=action_match
    missing=dict(block='connected_history_weak_action: K_ext,chi-chi and coupled trace rows',
        equation='q_ext,0^owner(v_chi,chi)=integral_Iext <D5,0 v_chi,D5,0 chi>_5 d tau + owned interface/seam/domain terms; m_ext=integral_Iext <v_chi,chi>_5 d tau',
        first_coefficient='a0(tau,rho)=[-I_tau/(2I)-L_nu/2+3H/2+C_tau/(2C)-zeta C_rho/(2C)-zeta_rho/2+zeta nu_rho/(2nu)-zeta cot(rho/2)/2]/nu',
        first_unavailable_action='this coefficient and B_tau in D5 chi on a non-cut, source-reached part of the inherited exterior history, with full coupled traces',
        input_space='source-reached connected spinor sections in the inherited AE2 reset/material/past-prefix/canonical-stop form domain; not the child16 or the whole exterior space',
        output_space='dual weak functional on those same sections and their coupled temporal traces',
        producer='same v14.45 common-A + radial-eta Dirac action; current action-field rows74:86 and q_tau=v/N_b from audit_n12_c2_exact_center_fixed_s_field_matrix.py and certify_n12_c2_cancelled_field_lohner_step.py, consumed at the actual exterior states',
        current_data='endpoint rates and right-cell nodal geometric reconstructions available; no owned non-cut action-jet family was supplied to this assembly',
        consumer='(K_ext+s M_ext)u=p with total inclusion-plus-complement reset/material traces, then Gamma1^owner u and the stratified fermion-family retarded response',
        status='uncomputed prescribed history action/domain realization, not an unselected new physical boundary parameter',
        endpoint_constant_extension=False,new_boundary_law=False)
    try:
        require_exterior_history_action(dict(cut_K=arrays['local_cut_K_Wp_timejet'],
                                             cut_M=arrays['local_cut_M_Wp'],connected_history_weak_action=None))
    except ExteriorActionUnavailable as exc:
        solve=dict(status='assembly stopped before inversion',reason=str(exc),
            local_form_applied_to_actual_source=True,
            local_operator_applied_to_actual_source=False,
            amplitude_timejet_form_cotangent='coupled_cut_source_actions.npz::rhs_K',
            cut_amplitude_source_pairing='coupled_cut_source_actions.npz::rhs_M',
            full_shifted_source_rhs='p is the saved continued source; its history/test pairing is not yet materialized',
            solution=None,stationary_residual=None,stationary_conormal=None,
            output_contraction_available='q_cut(p,p)=integral_cap mu5 (D5p)^dagger D5p; no temporal integration by parts or Gamma1 u evaluated',
            missing=missing,cut_matrix_inverted=False,heat_of_cut_matrix_taken=False)
    save(out/'solve_attempt.json',solve)
    save(out/'missing_action.json',missing)
    result['errors']=dict(endpoint_point=end['endpoint_point']['error_scope'],
        inherited_tube='preserved endpoint tube; not propagated through the new full-cap quadratic forms',
        direct_vs_nodal='direct Fourier L_nu used; earlier interpolation receipts preserved, not identified with continuum error',
        quadrature='one 4/8-point per-cell comparison; no certified weak-form remainder',
        matrix_roundoff=None,continuum=None,history_action=None,interface_domain=None,native_theory=None)
    result['solve_attempt']=solve['status']
    result['execution']=dict(old_endpoint_extractions=0,old_replays=0,old_test_campaigns=0,
        new_local_form_evaluations=2,new_native_or_exterior_solutions=0,new_heat_evaluations=0)
    result['elapsed_seconds']=time.perf_counter()-began
    save(out/'result.json',result)
    save(out/'checkpoint.json',dict(id='BHSM_MUON_SOURCE_REACHED_COUPLED_CUT_FORMS_20261004',
        starting_revision=git('rev-parse','HEAD'),arrays='coupled_cut_source_actions.npz',
        result='result.json',solve='solve_attempt.json',next=missing,physical_prediction=False))
    save(out/'frozen_local.json',json.loads(refs['frozen'].read_text()))
    ledger=json.loads(refs['ledger'].read_text())
    save(out/'inherited_contribution_ledger.json',ledger)
    save(out/'cut_contribution_ledger.json',dict(
        local_Dirac_cut='evaluated with same common-A, spin, radial-eta and correlated endpoint updates',
        bulk_and_Cauchy_pairings='separate evaluated cut forms',
        connected_complement='full n1/n3 and 64 output rows retained; differentiated bulk projection evaluated',
        exterior_history=None,reset_material_canonical_stop_action=None,Higgs_seam=None,
        induced_Dirac_heat=None,gauge_constraint=None,grading_BRST=None,
        length_completion=None,physical_a_mu=None,physical_g_mu=None))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ('frame','bulk_projection','temporal_Cauchy_projection',
        'source_local_Dirac_energy_per_tau','source_bulk_mass_per_tau',
        'new_builder_saved_action_comparison','solve_attempt','elapsed_seconds')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    run(a.repository.resolve(),a.output.resolve())
