"""Selected-node full D5 application on frozen fields; no radial integration."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_REPO=ROOT
sys.path.insert(0,str(ROOT/"src"))
OLD_REL=Path("artifacts/muon_trial_d5_trace_action_20261012/trial_0000_corrected_sigma_energy_0_run_2")
REPORT_SHA="3647c939e8ee150d79483f1e32066e08cee261cac82ef0ef29eecf009a5f75f2"
from bhsm.interface.muon_full_d5_differential_form import (
    full_d5_differential_coefficients,full_d5_weak_trial_action,
)


def encode(a):
    a=np.asarray(a,complex);return dict(real=a.real.tolist(),imag=a.imag.tolist())


def comparison(a,b):
    error=float(np.max(abs(a-b)))
    return dict(absolute=error,scaled=error/max(1.,float(np.max(abs(a))),float(np.max(abs(b)))))


def evaluate(repository,output):
    repo=Path(repository).resolve();out=Path(output)
    if not out.is_absolute():out=repo/out
    out=out.resolve()
    if not out.is_relative_to(repo):raise ValueError("outputs must remain under the repository")
    if out.exists():raise FileExistsError("preserve independent application output")
    sys.path.insert(0,str(repo/'src'))
    from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from bhsm.interface.muon_holomorphic_d5_trace_action import d5_unsquared_weak_trace,d5_sigma_foliation_eta
    from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    pins={}
    def pin(path,expected=None):
        path=Path(path);digest=sha256(path.read_bytes()).hexdigest()
        if expected is not None and digest!=expected:raise ValueError("frozen input changed: "+str(path))
        label=path.relative_to(repo).as_posix()
        pins[label]=digest
    report_path=repo/OLD_REL/'result.json';pin(report_path,REPORT_SHA)
    report=json.loads(report_path.read_bytes())
    if report['eta_realization']!='sigma':raise ValueError("same actual sigma-eta archive required")
    energy=complex(*report['explicit_off_shell_energy'])
    full=full_d5_localized_lepton_trace();records=[]
    base_names=('lapse','radial_coframe','radius','coordinate_shift',
        'geometric_time_contact','geometric_radial_contact','surface_proper_clock_rate',
        'volume_density','eta_radial_contact','gauge_connection_material',
        'sigma_radial','sigma_coordinate_time','eta_profile','eta_profile_radial',
        'eta_profile_coordinate_time')
    for stage in range(2):
        path=repo/OLD_REL/f'stage_{stage:04d}_current_geometry_normal_and_material_trace.npz'
        pin(path,report['archives'][path.name]['sha256'])
        with np.load(path,allow_pickle=False) as z:a={k:z[k] for k in z.files}
        stage_path=repo/report['trial']/f'stage_{stage:04d}.npz'
        pin(stage_path,report['input_hashes'][stage_path.relative_to(repo).as_posix()])
        with np.load(stage_path,allow_pickle=False) as z:
            frozen_raw=z['stage_raw'].copy();coordinate_time=z['coordinate_time'].item()
        rho=np.asarray(a['radial_points'])
        if np.any(abs(rho.imag)>1e-15) or np.any(rho.real<=0) or np.any(rho.real>=WALL):
            raise ValueError("all selected source nodes must be interior, never the wall")
        indices=np.array([0,len(rho)//2,len(rho)-1],int)
        c={name:np.asarray(a[name])[indices].copy() for name in base_names}
        for name in base_names:
            first=name+'_first'
            if first in a:c[first]=np.asarray(a[first])[:,indices].copy()
        u=np.asarray(a['original_normal_inclusion'])[indices]
        ur=np.asarray(a['original_normal_inclusion_radial'])[indices]
        ut=np.asarray(a['original_normal_inclusion_first'])[0,indices]
        # One frozen, disclosed algebraic test-column scale bounds all three
        # supplied trial maps. It does not change coefficients or normalize
        # a physical state, and is never differentiated as a source law.
        trial_scale=1/max(1.,float(np.max(abs(u))),float(np.max(abs(ur))),float(np.max(abs(ut))))
        coordinate_weights=np.ones(3)
        for n in (0,1):
            angular=scalar_s3_discretization(n)
            E=angular['angular_derivative_matrices'];h=E.shape[-1];d=64*h;D=6*d
            rows=np.arange(1,D+1)[:,None];columns=np.arange(2,5)[None,:]
            base=(np.cos(rows*columns*.173)+1j*np.sin(rows*(columns+.37)*.119))/np.sqrt(D)
            tests=np.arange(2,6)[:,None];lr=np.arange(1,D+1)[None,:]
            left_base=(np.cos(tests*lr*.131)+1j*np.sin((tests+.23)*lr*.157))/np.sqrt(D)
            V=(trial_scale*u)[:,None,None]*base[None]
            Vr=(trial_scale*ur)[:,None,None]*base[None]
            Vt=(trial_scale*ut)[:,None,None]*base[None]
            L=np.array([(1+(.07+.03j)*j)*left_base for j in range(3)])
            for eps in (1,-1):
                coefficients=full_d5_differential_coefficients(c,E,sheet_orientation=eps,full_representation=full)
                result=full_d5_weak_trial_action(coefficients,V,Vr,Vt,L,coordinate_weights,energy=energy)
                point=np.empty_like(V);pointE=np.empty_like(V)
                legacy_action=np.zeros((4,3),complex);legacyE=np.zeros_like(legacy_action)
                branch_records=[]
                for family in range(3):
                    for branch_index,branch in enumerate(('particle','conjugate')):
                        sl=slice((2*family+branch_index)*d,(2*family+branch_index+1)*d)
                        gamma=full['gamma5D_'+branch];generators=full['unitTr16_gauge_particle']
                        if branch=='conjugate':generators=generators.conj()
                        eta=d5_sigma_foliation_eta(c,gamma=gamma,carrier_count=16,angular_count=h,
                            sheet_orientation=eps)['sigma_normal_eta_contact']
                        legacy=d5_unsquared_weak_trace(c,coordinate_weights,gamma=gamma,
                            carrier_generators=generators,angular_derivatives=E,right_values=V[:,sl],
                            right_radial=Vr[:,sl],right_coordinate_time=Vt[:,sl],literal_left_values=L[:,:,sl],
                            energy=energy,sheet_orientation=eps,eta_clifford_contact=eta)
                        acted=legacy['original_D5_on_trial'];actedE=legacy['original_D5_energy_on_trial']
                        point[:,sl]=acted;pointE[:,sl]=actedE
                        legacy_action+=legacy['unsquared_trace_action'];legacyE+=legacy['unsquared_trace_action_energy_first']
                        branch_action=np.einsum('q,qij,qjk->ik',c['volume_density'],L[:,:,sl],result['point_expression_on_trial'][:,sl])
                        branch_records.append(dict(family=family,branch=branch,
                            point_expression_comparison=comparison(result['point_expression_on_trial'][:,sl],acted),
                            ordered_action_comparison=comparison(branch_action,legacy['unsquared_trace_action']),
                            legacy_action=encode(legacy['unsquared_trace_action']),legacy_phase_first=encode(legacy['unsquared_trace_action_energy_first']),
                            sigma_eta_norm=float(np.linalg.norm(eta))))
                point_actions=np.einsum('q,qij,qjk->qik',c['volume_density'],L,result['point_expression_on_trial'])
                legacy_point_actions=np.einsum('q,qij,qjk->qik',c['volume_density'],L,point)
                literal_phase=np.einsum('q,qij,qjk->ik',c['volume_density'],L,pointE)
                records.append(dict(stage=stage,coordinate_time=encode(coordinate_time),max_haar_scalar_level=n,
                    complete_scalar_Haar_angular_count=h,full_retained_fibre_count=D,
                    six_repeated_family_branch_blocks_applied=6,eta_sheet_orientation=eps,
                    original_radial_node_indices=indices.tolist(),original_radial_nodes=encode(rho[indices]),
                    actual_wall_rho=float(WALL),actual_wall_included=False,last_Gauss_node_called_wall=False,
                    selected_coordinate_weights=coordinate_weights.tolist(),
                    weights_are_radial_quadrature_or_convergence_test=False,
                    declared_right_trial='three fixed algebraic full-fibre columns times supplied saved u,ur,u_time',
                    declared_independent_left='four fixed complex full-fibre weak test rows; never conjugate right source',
                    frozen_algebraic_trial_scale=trial_scale,
                    maximum_trial_map_magnitude=float(max(np.max(abs(V)),np.max(abs(Vr)),np.max(abs(Vt)))),
                    saved_radial_inclusion_called_sigma_normalized=False,
                    original_Lorentz_phase_frequency=encode(energy),
                    complete_angular_derivative_norm=float(np.linalg.norm(E)),
                    original_material_gauge_norm=float(np.linalg.norm(c['gauge_connection_material'])),
                    original_coordinate_time_trial_norm=float(np.linalg.norm(Vt)),
                    action=encode(result['action']),legacy_action=encode(legacy_action),
                    phase_frequency_first=encode(result['phase_frequency_first']),legacy_phase_frequency_first=encode(legacyE),
                    selected_point_actions=encode(point_actions),
                    ordered_action_comparison=comparison(result['action'],legacy_action),
                    phase_first_comparison=comparison(result['phase_frequency_first'],legacyE),
                    phase_literal_point_comparison=comparison(result['phase_frequency_first'],literal_phase),
                    all_fibre_point_expression_comparison=comparison(result['point_expression_on_trial'],point),
                    selected_point_action_comparison=comparison(point_actions,legacy_point_actions),
                    family_branch_records=branch_records,
                    retained_block_norms={branch:{name:float(np.linalg.norm(coefficients['blocks'][branch][name]))
                        for name in ('time','radial','body','energy','sigma_eta_contact','W_body','A_body')}
                        for branch in ('particle','conjugate')},
                    full_384h_differential_square_assembled=False,largest_branch_square_width=d,
                    independent_left_source_conjugated=False,physical_native_or_AE4_identification=False,
                    physical_total_E_or_B_derivative=False))
                del coefficients,result,point,pointE
    for path in (Path(__file__).resolve(),repo/'src/bhsm/interface/muon_full_d5_differential_form.py',repo/'tests/test_muon_full_d5_differential_form.py'):pin(path)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and path and Path(path).is_relative_to(repo):pin(Path(path))
    payload=dict(classification='FULL_D5_SELECTED_NODE_APPLICATION_ON_FROZEN_COMPLEX_FIELDS',records=records,
        input_and_source_sha256=dict(sorted(pins.items())),
        frozen_stage_raw_or_canonical_time_recomputed=False,new_history_profile_D5_or_radial_integrations=0,
        selected_node_action_is_radial_quadrature=False,radial_or_angular_convergence_claimed=False,
        same_finite_band_zero_vs_one_is_not_an_angular_convergence_certificate=True,
        sigma_eta_from_original_owner=True,all_original_time_shift_spin_gauge_and_eta_terms_retained=True,
        physical_outgoing_operator_state_or_positive_pairing_selected=False,
        physical_native_or_AE4_operator_identified=False,full_physical_derivative_at_2e_minus10_passed=False,
        coupled_corrections=0,normalized_physical_spins=None,physical_muon_magnetic_moment=None)
    out.mkdir(parents=True);result=out/'result.json'
    result.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    errors=[r[name] for r in records for name in ('ordered_action_comparison','phase_first_comparison','all_fibre_point_expression_comparison','selected_point_action_comparison')]
    print(json.dumps(dict(result_sha256=sha256(result.read_bytes()).hexdigest(),records=len(records),
        max_comparison_absolute=max(a['absolute'] for a in errors),max_comparison_scaled=max(a['scaled'] for a in errors),
        full_physical_derivative_pass=False,coupled_corrections=0),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',default=str(DEFAULT_REPO));p.add_argument('--output',required=True)
    args=p.parse_args();evaluate(args.repository,args.output)
