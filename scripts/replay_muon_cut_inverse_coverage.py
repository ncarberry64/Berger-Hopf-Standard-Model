"""New inverse-range contraction only; preserves all earlier production caches."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def git(root,*args):return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false','-C',str(root),*args],text=True)
def read_npz(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def retained_prefix_states(root):
    """Read the chosen state arrays; no old coefficient or duration replay."""
    base=root/'artifacts/flagship_integration';paths=[];states=[]
    def load(name):
        p=base/(name+'.npz');paths.append(p);return read_npz(p)
    z=load('BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION')
    states.extend([z['refined_C2_center'],z['C2_predictor_state']])
    states.append(load('BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT')['C2_predictor_state'])
    for name,key in [
        ('BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT','C2_predictor_centers'),
        ('BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION','C2_compensated_predictor_centers'),
        ('BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION','C2_adaptive_predictor_centers'),
        ('BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION','C2_recentered_adaptive_predictor_centers'),
        ('BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION','C2_descriptor_fiber_predictor_centers'),
        ('BHSM_N12_C2_UNIFORM_GAP_CONTINUATION','C2_uniform_gap_predictor_centers'),
        ('BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION','C2_second_uniform_gap_predictor_centers')]:
        states.extend(load(name)[key])
    for n in range(1215,1223):
        name='BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP' if n==1215 else f'BHSM_N12_C2_LOHNER_STEP_{n}'
        z=load(name);states.extend([z['center_state'],z['endpoint_predictor_center']])
    return np.array(states),paths


def run(root,out,resume_endpoint=None):
    if out.exists():raise FileExistsError('fresh output directory required')
    out.mkdir(parents=True);started=time.perf_counter();sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_cut_inverse_coverage import (
        tail_connection_boxes,prefix_owned_connection_box,family_range_certificate,evaluate_hit,encoded,
        retained_radial_density_conversion)
    old=root/'artifacts/muon_collar_source_coverage_20261003/replay_reference'
    refs=dict(metric=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        source_pairing=root/'artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz',
        chronology=old/'prefix_chronology.json',old_result=old/'result.json',old_arrays=old/'collar_coverage_actions.npz',
        frozen_local=root/'artifacts/muon_collar_source_coverage_20261003/frozen_local.json',
        native_ledger=root/'artifacts/muon_collar_source_coverage_20261003/native_ledger.json',
        module=root/'src/bhsm/interface/muon_cut_inverse_coverage.py',script=Path(__file__),
        metric_producer=root/'src/bhsm/interface/muon_collar_source_coverage.py',
        field_producer=root/'src/bhsm/interface/muon_parent_maxwell_velocity.py',
        radius_producer=root/'src/bhsm/interface/aether_forward_boundary_radius.py',
        velocity_producer=root/'src/bhsm/interface/aether_sobolev_galerkin_pencil_lift_v15_81.py',
        radial_mode_producer=root/'src/bhsm/interface/aether_cartan_shell_crossing_v15_76.py',
        radial_overlap_producer=root/'src/bhsm/interface/aether_invariant_sobolev_schur_pushforward_v15_82.py',
        mode_contract=root/'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        owner=root/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        body=root/'src/bhsm/interface/muon_parent_source_contact.py')
    states,paths=retained_prefix_states(root)
    refs.update({f'prefix_states_{i}':p for i,p in enumerate(paths)})
    if resume_endpoint:
        refs.update(endpoint_cache=resume_endpoint/'endpoint_branch_actions.npz',endpoint_cache_result=resume_endpoint/'endpoint_branch.json')
    save(out/'workspace.json',dict(branch=git(root,'branch','--show-current').strip(),head=git(root,'rev-parse','HEAD').strip(),
         reference='524ed90689bd5923c249bba2e699abf627e703cd',starting_checkpoint='430093f067fb840bc4bfb006bf43abef37c4c308',
         status=git(root,'status','--short')))
    (out/'working_tree.diff').write_bytes(git(root,'diff','--binary').encode())
    save(out/'input_hashes.json',{k:dict(path=str(p.relative_to(root)) if p.is_relative_to(root) else str(p),sha256=digest(p)) for k,p in refs.items()})
    geometry=read_npz(refs['metric']);pair=read_npz(refs['source_pairing']);chron=json.loads(refs['chronology'].read_text())
    tail,cells=tail_connection_boxes(geometry)
    prefix,prefix_receipt=prefix_owned_connection_box(states,geometry)
    save(out/'connection_boxes.json',dict(tail={k:encoded(v) for k,v in tail.items()},tail_cells=cells,
        prefix={k:encoded(v) for k,v in prefix.items()},prefix_receipt=prefix_receipt,prefix_state_count=len(states)))
    cert=family_range_certificate(geometry,tail,prefix,prefix_duration_upper=chron['proper_duration_interval'][1])
    source_rho=np.array(pair['gauss_rho']).ravel();bounds=cert['rho_hit_enclosure']['interval']
    if not np.all(source_rho<bounds[0]):raise RuntimeError('range overlaps source: perform safeguarded actual inverse applications')
    gauss=dict(points=source_rho.tolist(),count=len(source_rho),range=[float(min(source_rho)),float(max(source_rho))],
        hit_enclosure=bounds,minimum_certified_gap=float(np.nextafter(bounds[0]-max(source_rho),-np.inf)),
        classifications=['outside enclosed physical tail branch image']*len(source_rho),
        root_solve_count=0,reason='certified range rejection precedes bracketed root search; not a theorem inferred from missed shots')
    save(out/'family_range.json',cert);save(out/'source_range_rejection.json',gauss)
    save(out/'stage.json',dict(stage='whole-cell family range established; endpoint branch application next',old_checks_replayed=0,old_productions_rerun=0))
    # One endpoint continuation of the existing seed branch. A lower endpoint
    # is the implicit grazing contact, not a small-denominator root call.
    if resume_endpoint:
        arrays=read_npz(refs['endpoint_cache']);endpoint=json.loads(refs['endpoint_cache_result'].read_text())
        previous=json.loads((resume_endpoint/'input_hashes.json').read_text())
        if previous['metric']['sha256']!=digest(refs['metric']):raise ValueError('endpoint metric identity changed')
        if endpoint['y']!=float(geometry['proper_times'][-1]):raise ValueError('endpoint wall parameter changed')
        if endpoint['s0']>cert['normal_length_upper']['interval'][1]:raise ValueError('cached endpoint outside new range enclosure')
    else:
        arrays,endpoint=evaluate_hit(geometry,float(geometry['proper_times'][-1]),s_upper=cert['normal_length_upper']['interval'][1])
    np.savez_compressed(out/'endpoint_branch_actions.npz',**arrays)
    save(out/'endpoint_branch.json',endpoint)
    radial,radial_result=retained_radial_density_conversion(geometry,pair)
    np.savez_compressed(out/'retained_radial_density_conversion.npz',**radial)
    save(out/'retained_radial_density_conversion.json',radial_result)
    oldres=json.loads(refs['old_result'].read_text())
    save(out/'frozen_ledger.json',{k:json.loads(refs[k].read_text()) for k in ('frozen_local','native_ledger')})
    result=dict(family_range=cert,source_range_rejection=gauss,endpoint_branch=endpoint,
        result='source-directed range obstruction for inherited inward Gaussian realization',
        preserved_seed_R_hit=float(oldres['cache_exit_phase'][1]),preserved_local_derivative=-35.34587871146189,
        local_derivative_used_as_global_extrapolation=False,evaluated_source_preimages=0,source_preimages_in_certified_model=0,
        T_required=None,B54_required=None,stationary_exterior_response=None,native_heat_contact=None,
        physical_a_mu=None,physical_g_mu=None,native_physical_transfer_directions=0,
        normalization_integral_full=None,normalization_remainder=None,source_support_contraction=None,
        alternatives=dict(retained_radial_inclusion=True,
            equations=['ds=C_rho d rho','J_rad=(r/R_wall)^3','I_rad=integral_full_cap C_rho sin^2(rho/2) d rho',
            'u_rad=I_rad^-1/2 J_rad^-1/2 sin(rho/2)',
            'J_vol=(nu/nu_wall) J_rad','u_vol=sqrt(nu_wall/nu) u_rad',
            'h4_current-h4_rad=(partial_rho log nu)/(2 C_rho)'],
            historical_producers='v15.76 shell_geometry and v15.82 regular_einstein_cartan_kernel; fixed-time radial application of v14.45',
            current_native_equivalence_established=False,
            reason='different physical image; density conversion alone does not supply spin/shift/time/interface/domain intertwining',
            invented_reset_extension=False,older_snapshot_replayed=False),
        retained_radial_density_conversion=radial_result,
        first_unresolved_operand=dict(
            name='current same-owner Dirac/domain matching for the retained full radial inclusion',
            equation='D5_current W_rad_current = W_rad_current D4 + declared connected normal/temporal remainder, with Gamma0/reset matching and Wsharp M5 W=M4',
            explicit_first_action='current temporal/shift/Spin x SM remainder in D5_current W_rad, including the rho-dependent temporal principal coefficient nu_wall/nu; its trace/reset intertwining',
            normal_density_correction='evaluated Delta h4=(partial_rho log nu)/(2 C_rho), canceled by sqrt(nu_wall/nu) density conversion at actual source nodes; not the missing operand',
            input='current cut lapse/radial metric/shift, adopted daughter rho/2, common-A Spin x SM connection and inherited AE2/AE4 domain',
            output='one same-owner normalized inclusion action on the saved Gauss source support',
            producer='retained v14.45 radial restriction in v15.76/v15.82, matched to current Dirac body and AE4 geometric L2',
            consumer='T=<W e,p>5; M4 B_required=T; coupled exterior K/M',
            classification='current operator/interface implementation and matching to retained effective route; not eta selection, a new physical arm or proof that BHSM has no map'),
        error_scope=dict(tail_range='Arb192 whole-cell enclosure for exact binary64 nodal input and its declared bilinear interpolation',
            prefix_range='Arb192 contracted owned q/v/m hull; assumes same-action continuous gluing and these boxes contain inherited prefix realization',
            prefix_continuum_or_unsampled_state_error=None,tail_continuum_metric_error=None,
            endpoint_absolute_ODE_error=None,previous_Hermite_curve_error_not_used_in_range=True,
            source_support_error='actual saved Gauss nodes at fixed saved source realization',
            inherited_source_H='unchanged; not used as a replacement for metric C_tau',normalization_remainder=None),
        old_checks_replayed=0,old_productions_rerun=0,old_prefix_displacement_refined=False,
        new_endpoint_integrations=int(resume_endpoint is None),endpoint_cache_reused=bool(resume_endpoint),
        elapsed_seconds=time.perf_counter()-started)
    save(out/'result.json',result)
    save(out/'checkpoint.json',dict(id='BHSM_MUON_SOURCE_DIRECTED_CUT_RANGE_20261003',result='result.json',
         mathematical_result='whole-family coefficient-box cut range; actual Gauss sources rejected',next_operand=result['first_unresolved_operand'],physical_prediction=False))
    save(out/'output_hashes.json',{p.name:digest(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(dict(range=bounds,source_range=gauss['range'],gap=gauss['minimum_certified_gap'],
        endpoint_R_hit=endpoint['R_hit'],endpoint_s0=endpoint['s0'],elapsed_seconds=result['elapsed_seconds']),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True);p.add_argument('--resume-endpoint',type=Path)
    a=p.parse_args();run(a.repository,a.output,a.resume_endpoint)
