"""Replay actual E1 moving-normal sector action applications without mode selection."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_moving_geometric_action import retained_state, moving_cap_action_jet, weak_action_blocks, STATE_RECEIPT, STATE_SOURCE
from bhsm.interface.muon_moving_material_response import identity_material_trial_jet, response_constraint_jet, proper_length_material_trial, orbit_length_pullback_jet
from bhsm.interface.muon_birth_candidate_geometry_action import evaluate_retained_candidate_geometry
from bhsm.interface.ae4_branch_relative_support_transition import branch_relative_cutoff_contract
from bhsm.interface.geometric_material_port import geometric_trace_jet
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0


def serial(value):
    if isinstance(value,np.ndarray): return value.tolist()
    if isinstance(value,np.generic): return value.item()
    if isinstance(value,dict): return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [serial(v) for v in value]
    return value


def write(path,value):
    path.write_text(json.dumps(serial(value),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')


def hash_file(relative):
    return dict(path=relative,sha256=sha256((ROOT/relative).read_bytes()).hexdigest())


def evaluate(output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    summaries={}; results={}
    for side,orientation in (('outgoing_C2',1.),('incoming_C1_E1',-1.)):
        state=retained_state(ROOT,side); refinements={}
        for points in (96,128,192):
            d=moving_cap_action_jet(12,*state,points=points,trial_normal=orientation)
            b=weak_action_blocks(d)
            refinements[str(points)]={k:float(b[k]) for k in ('S','normal_first_variation','D_ss','eta_FR_kinetic_component')}
            if points==128: data=d; blocks=b
        surface=dict(data,total=data['surface_per_gamma'])
        surface_blocks=weak_action_blocks(surface)
        payload=dict(geometry_weak_action=blocks,surface_weak_action_per_gamma=surface_blocks,
                     coordinate_layout=dict(q=[0,37],qdot=[37,74],lapse_shift=[74,98],s=98,sdot=99),
                     normal_orientation=orientation,
                     domain='Retained cap pullback chi=y*(pi/4+s*v/Cstar(q)); anchored response on [0,pi/2]',
                     same_action_clock='retained coordinate time; proper time at the wall is d_tau=Nstar dt',
                     weak_B='Bq=S_qs-Dt(S_qdot,s); Bm=S_ms, with endpoint momentum contact',
                     weak_H='qq,qv,vq,vv,qm,vm,mm weak coefficients before the temporal/domain and gauge reduction',
                     surface_gamma='alpha_FSC ell_s^(-7); symbolic owner coefficient, never fitted',
                     full_stationary_KKT=False, complete_formation_operator=False)
        write(output/(side+'_weak_action.json'),payload)
        proper={}; q=state[0]
        for count in (8193,16385,32769):
            grid=np.linspace(0,np.pi/2,count)
            ck=np.cos(4*np.arange(1,13)[:,None]*grid)
            cj=np.cos(4*np.arange(12)[:,None]*grid)
            Cprofile=RADIUS0*np.exp(q[0]+q[1:13]@ck+np.sin(2*grid)**2*(q[13:25]@cj))
            cov=proper_length_material_trial(grid,Cprofile,C_star=float(data['Cstar'].value),normal_velocity=orientation)
            resp=cov['response']
            proper[str(count)]=dict(Z=resp['Z'],Z_s=resp['Z_x'],Z_ss=resp['Z_xy'],J1=cov['J1'],J3=cov['J3'],
                eta_trial_coefficients=cov['eta_trial_coefficients'],
                wall_sigma_eulerian=cov['wall_sigma_eulerian_x'],wall_sigma_embedding=cov['wall_sigma_embedding_x'],
                material_rows={key:cov[key] for key in ('wall_eta_material_x','wall_eta_material_xx','wall_sigma_material_x','wall_sigma_material_xx')},
                constraint_max=np.max(np.abs(cov['response_constraint_rows']),axis=1),
                max_profile_difference_from_retained=float(np.max(np.abs(resp['sigma']-identity_material_trial_jet(grid,normal_velocity=orientation,C_star=float(data['Cstar'].value))['sigma']))))
            if count==32769:
                sample=np.arange(0,count,256)
                ks=np.arange(1,13)[:,None]; js=np.arange(12)[:,None]
                up=q[1:13]@(-4*ks*np.sin(4*ks*grid))
                upp=q[1:13]@(-16*ks**2*ck)
                poly=q[13:25]@cj
                polyp=q[13:25]@(-4*js*np.sin(4*js*grid))
                polypp=q[13:25]@(-16*js**2*cj)
                win=np.sin(2*grid)**2; winp=2*np.sin(4*grid)
                logcp=up+winp*poly+win*polyp
                logcpp=upp+8*np.cos(4*grid)*poly+2*winp*polyp+win*polypp
                velocity=orientation/float(data['Cstar'].value)*np.sin(2*grid)
                velocityp=2*orientation/float(data['Cstar'].value)*np.cos(2*grid)
                pull=orbit_length_pullback_jet(C=Cprofile,C_prime=Cprofile*logcp,
                    C_second=Cprofile*(logcp**2+logcpp),coordinate_velocity=velocity,
                    velocity_prime=velocityp,coordinate_acceleration=0,acceleration_prime=0)
                proper[str(count)]['metric_pullback_max']={key:float(np.max(np.abs(pull[key])))
                    for key in ('length_density_x','length_density_xx','orbit_derivative_coefficient_x','orbit_derivative_coefficient_xx')}
                write(output/(side+'_proper_response.json'),dict(chart=cov['chart'],coordinate=grid[sample],
                    pulled_length_density_s=pull['length_density_x'][sample],
                    pulled_length_density_ss=pull['length_density_xx'][sample],
                    pulled_response_D_s=pull['orbit_derivative_coefficient_x'][sample],
                    pulled_response_D_ss=pull['orbit_derivative_coefficient_xx'][sample],
                    pullback_extension='F_s=chi+s*v/Cstar*sin2chi; fixed anchors; representation choice, not a physical mode',
                    proper_length_density=Cprofile[sample],sigma=resp['sigma'][sample],
                    sigma_s=resp['sigma_x'][sample],sigma_ss=resp['sigma_xy'][sample],
                    sigma_gradient=resp['coordinate_sigma_gradient'][sample],
                    normalization_derivatives=[resp['Z'],resp['Z_x'],resp['Z_xy']],
                    complete_normalization_integrated_nodes=count,
                    Eulerian_geometry_fixed=True,physical_mode_selected=False,
                    replaces_retained_action_profile=False,error_scope='Composite quadrature refinement diagnostic only'))
        source=98; rate=99
        sectors={name:dict(value=float(data[name].value),
                 normal_first=float(data[name].gradient[source]),
                 normal_second=float(data[name].hessian[source,source]),
                 normal_rate_first=float(data[name].gradient[rate]),
                 normal_rate_second=float(data[name].hessian[rate,rate]),
                 internal_source_norm=float(np.linalg.norm(data[name].hessian[:98,source])),
                 internal_hessian_norm=float(np.linalg.norm(data[name].hessian[:98,:98])))
                 for name in ('bulk','FR','retained_local_Casimir','moving_GHY_Hayward','surface_per_gamma')}
        c=float(data['Cstar'].value)
        trial=identity_material_trial_jet(np.linspace(0,np.pi/2,1025),normal_velocity=orientation,C_star=c)
        constraint=[]
        for j in range(len(trial['f'])):
            constraint.append(response_constraint_jet(
                response_normal_jet=([1.],[0.],[0.],[0.]),
                sigma_gradient_jet=([trial['sigma_coordinate_gradient'][j]],
                  [trial['sigma_coordinate_gradient_x'][j]],[trial['sigma_coordinate_gradient_x'][j]],
                  [trial['sigma_coordinate_gradient_xx'][j]]),
                weight_jet=(trial['W'][j],trial['W_x'][j],trial['W_x'][j],trial['W_xx'][j]),
                normalization_jet=(trial['Z'],0.,0.,trial['Z_xx'])))
        # Existing three-port operation, at this explicit Eulerian-fixed geometry.
        # Arb carries arithmetic of supplied binary64 coefficients only here.
        ctx.prec=128
        shape=arb_mat([[0],[-orientation/c],[orientation/c]])
        three=geometric_trace_jet(arb_mat(3,37),arb_mat(37,1),shape)
        summaries[side]=dict(refinement_values=refinements,promoted_proper_length_response_refinement=proper,
            max_refinement_128_to_192={k:abs(refinements['128'][k]-refinements['192'][k]) for k in refinements['128']},
            Cstar=c,inverse_Cstar=1/c,increasing_normal_sigma_rate=4/(np.pi*c),oriented_normal_sigma_coefficient=orientation*4/(np.pi*c),
            corrected_endpoint_mode_indices=dict(u_lapse='k=1..12',w_b_shift='j=0..11'),
            sectors=sectors,
            multiplier_constraint_max=float(np.max(np.abs(blocks['multiplier_constraint_residual']))),
            added_surface_lapse_constraint_per_gamma=surface_blocks['multiplier_constraint_residual'][:12],
            normal_source_norms={key:float(np.linalg.norm(blocks[key])) for key in ('B_q_direct','B_q_momentum_contact','B_m')},
            response_constraint_max={key:max(abs(row[key]) for row in constraint) for key in ('C_sigma','C_sigma_x','C_sigma_xy')},
            response_trace_rows={key:trial[key] for key in ('wall_eta_material_x','wall_sigma_material_x','wall_eta_material_xx','wall_sigma_material_xx','Z_xx')},
            evaluated_geometric_three_port=[str(three[j,0]) for j in range(3)],
            material_four_port_completed=False,
            material_four_port_consumer='required_material_jet needs actual momentum, force, conormal, momentum_mixed and momentum_rate_direction on the complete action source',
            whole_seven_port_selected=False)
    result=dict(classification='EVALUATED_MOVING_NORMAL_GEOMETRIC_RESPONSE_AND_SURFACE_ACTION_APPLICATIONS',
      cutoff_owner=branch_relative_cutoff_contract(),retained_candidate_geometry=evaluate_retained_candidate_geometry(ROOT),
      applications=summaries,
      owner_action_definition_gap_inferred=False,
      full_physical_prediction_completed=False,
      scientific_scope=dict(DERIVED=['anchored normalized response and two material trace equations',
          'Eulerian-fixed relative eta normal trial and separate common-advection identity',
          'moving EH/GHY/Hayward weak completion -theta*Dt(rho)',
          'same-signed-sector internal and mixed weak action blocks; proper kinetic area pairing'],
        EVALUATED=['actual incoming/outgoing retained cap normal action applications','GHY mixed and momentum contacts',
          'area action internal Hessian and normal/rate blocks per symbolic gamma','response base/first/second residuals',
          'existing three geometric trace-port image','actual metric-weighted promoted response candidate and admissible normal trial'],
        CONTROL_ONLY=['finite differences and arbitrary test multipliers used to verify differentiation'],
        UNEVALUATED=['complete interacting stationary base and physical response multiplier',
          'action-selected psi_mu+ and nonlinear/simple oriented crossing',
          'total impedance, inertia and their v/J/vJ jets; native Pauli and final a_mu/g_mu'],
        OWNER_DEFINITION_GAP=[]),
      first_unexecuted_interacting_application=dict(term='b_H[phi]=D_s(delta_H S_full)[phi]',
          producer='ae31_c2_intrinsic_m4_lepton_action.first_variation_and_pole_gate',
          equation='E_H=-D^2 H-2 lambda_H (H^dagger H-nu^2)H-J_H',
          consumer='complete stationary Euler row and same-action mixed KKT source before internal response elimination',
          resolution='actual coupled retarded weak solve or an action-owned projected response/cancellation; no complete P_F export required',
          independent_unsupplied_datum_proved=False),
      error_scope='Binary64 retained center and finite N12/Gauss arithmetic; quadrature refinement is a diagnostic, not a rounding/continuum/branch-response/soft-Pauli enclosure',
      source_identities=[hash_file(p) for p in (STATE_RECEIPT,STATE_SOURCE,
          'src/bhsm/interface/muon_moving_geometric_action.py',
          'src/bhsm/interface/muon_moving_material_response.py',
          'src/bhsm/interface/muon_birth_candidate_geometry_action.py',
          'scripts/evaluate_muon_moving_interface_action.py')])
    write(output/'result.json',result)
    print(json.dumps(dict(output=str(output),normal_first=summaries['outgoing_C2']['refinement_values']['128']['normal_first_variation'],
           response_residual_max=summaries['outgoing_C2']['response_constraint_max'],
           hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(output.glob('*.json'))}),sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output-dir',required=True)
    evaluate(parser.parse_args().output_dir)
