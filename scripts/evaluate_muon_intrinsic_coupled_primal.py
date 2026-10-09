#!/usr/bin/env python
"""Evaluate retained off-shell common-vector primal residual applications.

No scalar initial condition or full-field stationary base is selected.
Measured tree matching fixes lambda and the physical-unit nu squared;
the common geometric action unit is kept explicit. Numerical mesh/zero
field iterates are off shell and are not retarded boundary conditions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_intrinsic_scalar_discretization import (
    scalar_s3_discretization,polynomial_temporal_discretization,
)
from bhsm.interface.muon_intrinsic_coupled_primal import (
    coupled_coefficient_layout,set_block,branch_fields_from_coefficients,
    geometry_euler_from_local_jet,temporal_momentum_contraction,
    require_physical_solve_binding,UnboundPhysicalApplication,
)
from bhsm.interface.muon_moving_geometric_action import retained_state,moving_cap_action_jet
from bhsm.interface.muon_coupled_temporal_weak_action import temporal_geometry_weak_application
from bhsm.interface.muon_moving_geometric_action import weak_action_blocks
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.aether_unified_m5_m4_pushforward_v15_69 import common_derivative_ledger
from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import action_composition_contract
from bhsm.interface.muon_intrinsic_worldvolume_scalar_transport import current_scalar_time_and_load_contract
from bhsm.interface.muon_calibrated_matching import calibrated_tree_matching


def encode(value):
    if isinstance(value,np.ndarray):
        if np.iscomplexobj(value):return dict(real=value.real.tolist(),imag=value.imag.tolist())
        return value.tolist()
    if isinstance(value,(np.integer,np.floating)):return value.item()
    if isinstance(value,complex):return dict(real=value.real,imag=value.imag)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(x) for x in value]
    return value


def write(path,value):
    path.write_text(json.dumps(encode(value),sort_keys=True,separators=(',',':'),allow_nan=False)+'\n',encoding='utf8',newline='\n')


def evaluated_birth_rows(side,q,v,m,*,points):
    a=moving_cap_action_jet(12,q,v,m,points=points)
    w=intrinsic_m4_weight_jet(12,q,v,m)
    # At the numeric H=p=0 starting iterate the retained local Higgs
    # action is -lambda_H*nu^4 * integral(wV).  No vacuum subtraction
    # has been assumed.  alpha below is this symbolic coefficient in
    # the action's units, not a fitted/dynamical coefficient.
    sectors={'retained_geometry':a['total'],
             'surface_per_gamma':a['surface_per_gamma'],
             'higgs_potential_per_lambda_nu4':-(2*np.pi**2)*w['wV']}
    rows={name:geometry_euler_from_local_jet(j,v,np.zeros_like(v),np.zeros_like(m))
          for name,j in sectors.items()}
    for name,row in rows.items():
        row['norm_F_q']=float(np.linalg.norm(row['F_q']))
        row['norm_F_m']=float(np.linalg.norm(row['F_m']))
        row['max_abs_F_q']=float(np.max(abs(row['F_q'])))
        row['max_abs_F_m']=float(np.max(abs(row['F_m'])))
    # HH momentum-operator pencil at this actual geometry and H=0.
    # Projection uses every scalar basis column, including weak components.
    angular=scalar_s3_discretization(1); V=angular['basis_values'];EV=angular['basis_derivative_values']
    phi=np.einsum('an,ij->ainj',V,np.eye(2)).reshape(len(V),2,-1)
    dp=np.einsum('amn,ij->aminj',EV,np.eye(2)).reshape(len(V),3,2,-1)
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]])
    R=np.broadcast_to(np.eye(3),angular['adjoint_rotations'].shape) if side=='parent' else angular['adjoint_rotations']
    kap=w['mechanical_connection_lambda'].value-(side=='parent')
    Ai=kap*np.einsum('pad,dij->paij',R,-1j*sigma)
    dp=dp+np.einsum('paij,pjn->pain',Ai,phi)
    quad=angular['unit_s3_weights']
    M=np.einsum('ain,aim,a->nm',phi.conj(),phi,quad)
    K=w['wS'].value*np.einsum('pain,paim,p->nm',dp.conj(),dp,quad)
    mass=-2*w['wV'].value*M # multiply lambda_H*nu_squared, not a numeric choice
    pencils=dict(angular_Gram=M,kinematic_DtH=w['wT'].value*M,
                 kinematic_pH=-M,momentum_DtpH=M,
                 momentum_H_spatial=K,momentum_H_per_lambda_nu2=mass,
                 angular_band=1,weak_component_count=2,complex_channel_count=len(M),
                 hermiticity_defect=float(np.max(abs(K-K.conj().T))),
                 scalar_higgs_zero_is_iterate=True)
    return rows,pencils,sectors


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--points',type=int,default=128)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    angular=scalar_s3_discretization(1)
    temporal={'parent':polynomial_temporal_discretization(-.01,0.,2),
              'child':polynomial_temporal_discretization(0.,.01,2)}
    layout=coupled_coefficient_layout(angular,temporal)
    c=np.zeros(layout['size']);states={}
    for side,receipt in (('parent','incoming_C1_E1'),('child','outgoing_C2')):
        q,v,m=retained_state(ROOT,receipt);states[side]=(q,v,m)
        ts=temporal[side]['interpolation_times']
        set_block(c,layout,f'{side}.q',q[None]+ts[:,None]*v[None])
        set_block(c,layout,f'{side}.m',np.broadcast_to(m,(3,len(m))))
    rows={};pencils={};contracts={};weak={};refinements={}
    for side,(q,v,m) in states.items():
        rows[side],pencils[side],sectors=evaluated_birth_rows(side,q,v,m,points=args.points)
        lower,_,_=evaluated_birth_rows(side,q,v,m,points=96)
        refinements[side]={name:dict(
            max_abs_Fq_difference=float(np.max(abs(rows[side][name]['F_q']-lower[name]['F_q']))),
            max_abs_Fm_difference=float(np.max(abs(rows[side][name]['F_m']-lower[name]['F_m']))))
            for name in rows[side]}
        f=branch_fields_from_coefficients(c,layout,angular,temporal,side)
        test=np.zeros((3,angular['scalar_count'],2),complex)
        test[:,0,0]=temporal[side]['interpolation_times']
        contracts[side]=dict(temporal_contraction=temporal_momentum_contraction(f,angular,temporal[side],test),
            H_norm=float(np.linalg.norm(f['H'])),pH_norm=float(np.linalg.norm(f['p_H'])),
            scalar_source=f['source_provenance'],
            scope='EVALUATED_OFF_SHELL_STARTING_ITERATE; zero H/p values are not primal boundary conditions',
            stationary=False)
        # Temporal weak residual at the SAME coefficient iterate, not an
        # inversion of the local q/qdot/m matrix.  No endpoint load is
        # removed or replaced by a periodic condition.
        t=temporal[side];B,Bt=t['basis_values'],t['basis_time_derivatives']
        nt,nq,nm=3,37,24;ng=nt*(nq+nm)
        Tq=np.zeros((len(B),nq,ng));Tv=np.zeros_like(Tq);Tm=np.zeros((len(B),nm,ng))
        for i in range(nt):
            Tq[:,:,i*nq:(i+1)*nq]=B[:,i,None,None]*np.eye(nq)
            Tv[:,:,i*nq:(i+1)*nq]=Bt[:,i,None,None]*np.eye(nq)
            Tm[:,:,nt*nq+i*nm:nt*nq+(i+1)*nm]=B[:,i,None,None]*np.eye(nm)
        allblocks={name:[] for name in sectors}
        for k,(x,y,z) in enumerate(zip(f['q'],f['qdot'],f['m'])):
            a=moving_cap_action_jet(12,x,y,z,points=args.points)
            w=f['weight_nodes'][k]
            local={'retained_geometry':a['total'],'surface_per_gamma':a['surface_per_gamma'],
                   'higgs_potential_per_lambda_nu4':-2*np.pi**2*w['wV']}
            for name,jet in local.items():
                allblocks[name].append(weak_action_blocks(dict(total=jet,qdim=37,mdim=24,source_indices=(98,99))))
        weak[side]={}
        for name,blocks in allblocks.items():
            endpoints=[]
            for e,sign in ((0,-1),(1,1)):
                te=t['t_start'] if e==0 else t['t_end'];x=q+te*v
                a=moving_cap_action_jet(12,x,v,m,points=args.points);w=intrinsic_m4_weight_jet(12,x,v,m)
                jet={'retained_geometry':a['total'],'surface_per_gamma':a['surface_per_gamma'],
                     'higgs_potential_per_lambda_nu4':-2*np.pi**2*w['wV']}[name]
                eq=np.zeros((nq,ng));ev=np.zeros_like(eq);em=np.zeros((nm,ng))
                for i in range(nt):
                    eq[:,i*nq:(i+1)*nq]=t['endpoint_values'][e,i]*np.eye(nq)
                    ev[:,i*nq:(i+1)*nq]=t['endpoint_time_derivatives'][e,i]*np.eye(nq)
                    em[:,nt*nq+i*nm:nt*nq+(i+1)*nm]=t['endpoint_values'][e,i]*np.eye(nm)
                endpoints.append(dict(orientation=sign,block=weak_action_blocks(dict(total=jet,qdim=37,mdim=24,source_indices=(98,99))),
                    q_tests=eq,q_test_rates=ev,m_tests=em,normal=0.,normal_rate=0.))
            app=temporal_geometry_weak_application(blocks,t['quadrature_weights'],Tq,Tv,Tm,np.zeros(len(B)),np.zeros(len(B)),endpoints=endpoints)
            weak[side][name]=dict(action_residual=app['action_residual'],euler_volume_pairing=app['euler_volume_pairing'],
                endpoint_momentum_pairing=app['endpoint_momentum_pairing'],action_hessian=app['action_hessian'],
                hessian_symmetry_defect=float(np.max(abs(app['action_hessian']-app['action_hessian'].T))),
                norm_action_residual=float(np.linalg.norm(app['action_residual'])),
                norm_euler_volume_pairing=float(np.linalg.norm(app['euler_volume_pairing'])))
    config_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    config=json.loads(config_path.read_text(encoding='utf8'))
    values={k:v['value'] for k,v in config['selected_consumer_values'].items()}
    matched=calibrated_tree_matching(fermi_constant_GeV_inverse_squared=values['G_F_GeV_minus2'],
        higgs_mass_GeV=values['m_h_GeV'],pole_masses_GeV=[values['m_tau_GeV'],values['m_mu_GeV'],values['m_e_GeV']])
    unit_coefficients=dict(lambda_H=matched['lambda_H'],nu_squared_GeV_squared=matched['nu_squared_GeV_squared'],
        lambda_nu4_GeV_fourth=matched['lambda_H']*matched['nu_squared_GeV_squared']**2,
        lambda_nu2_GeV_squared=matched['lambda_H']*matched['nu_squared_GeV_squared'],
        action_unit_conversion='nu_chart_squared=nu_GeV_squared/E_kappa_GeV^2; potential coefficient=lambda_nu4_GeV_fourth/E_kappa_GeV^4',
        E_kappa_GeV=None,unit_value_fitted_to_muon=False,
        scope='calibrated tree matching; radiative and BHSM matching corrections are not bounded')
    scalar_spatial_applications={}
    for side,pencil in pencils.items():
        # The neutral constant broken-phase local reference has unit shape
        # (0,1).  Its magnitude in this chart is nu_GeV/E_kappa, not one.
        # Apply the actual retained spatial covariant pencil to that shape.
        # This is one exact finite-band operator action at the retained
        # off-shell connection, not a selected E0/birth initial condition.
        shape=np.zeros(nc_shape:=2*angular['scalar_count'],complex);shape[1]=1.
        image=pencil['momentum_H_spatial']@shape
        scalar_spatial_applications[side]=dict(unit_neutral_shape=shape,
            spatial_momentum_row_per_neutral_amplitude=image,
            norm_spatial_row_per_neutral_amplitude=float(np.linalg.norm(image)),
            neutral_test_spatial_pairing_per_amplitude=float(np.vdot(shape,image).real),
            action_magnitude='sqrt(nu_squared_GeV_squared)/E_kappa_GeV',
            neutral_reference_potential_force=0.,
            zero_provenance='tree broken-reference H_dagger_H=nu_squared; only local potential derivative vanishes',
            temporal_momentum_and_event_cotangents_not_eliminated=True,
            E1_stationary_base=False,physical_Higgs_trace_selected=False)
    try:require_physical_solve_binding({'lambda_H':matched['lambda_H']})
    except UnboundPhysicalApplication as error:
        stopped=dict(operand=error.operand,consumer=error.consumer,producer=error.producer,
            classification='UNEVALUATED_EXISTING_ACTION_APPLICATION',theory_definition_gap=False,
            independent_datum_claim=False,Newton_correction=None,updated_physical_residual=None,
            reason='Physical nu squared and lambda are tree matched. Their conversion to the retained dimensionless geometric action requires the common unit matching application; no lepton mass is silently used as that unit.')
    nc=2*angular['scalar_count'];nt=3
    closure=dict(complex_H_and_p_unknowns_two_branches=4*nt*nc,
        complex_interior_evolution_rows_two_branches=4*(nt-1)*nc,
        complex_common_birth_trace_and_flux_rows=2*nc,
        complex_past_Cauchy_rows_required=2*nc,real_past_Cauchy_rows_required=4*nc,
        premise='First-order scalar linearization at H=0; canonical birth map on its exact test image; not a full nonlinear uniqueness proof',
        actual_load='b_E0[phi]=2 Re <phi,epsilon_E0 p_H,E0> plus owned event/constraint H cotangents',
        producer='coupled parent/E0 event Euler and environment B_s Cauchy/Noether application',
        homogeneous_component_set_to_zero=False,physical_initial_state_selected=False,
        scope='The past rows remain unknown event equations, not requested ready-made traces.')
    inputs=[]
    for path in ('src/bhsm/interface/muon_intrinsic_coupled_primal.py',
        'src/bhsm/interface/muon_intrinsic_scalar_discretization.py',
        'src/bhsm/interface/muon_intrinsic_lepton_primal.py',
        'src/bhsm/interface/muon_intrinsic_worldvolume_scalar_transport.py',
        'src/bhsm/interface/muon_moving_geometric_action.py',
        'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',
        'src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py',
        'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        'artifacts/muon_birth_transfer_value_20261008/retained_reset/run_1/result.json',
        'artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz',
        'scripts/evaluate_muon_intrinsic_coupled_primal.py',
        'src/bhsm/interface/muon_calibrated_matching.py',
        'artifacts/muon_calibrated_pauli_20261009/inputs.json'):
        inputs.append(dict(path=path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()))
    write(args.output/'primal_action_applications.json',dict(layout=layout,coefficient_iterate=c,
        evaluated_birth_rows=rows,scalar_operator_pencils=pencils,temporal_weak_applications=weak))
    write(args.output/'result.json',dict(classification='EVALUATED_COUPLED_OFF_SHELL_PRIMAL_APPLICATION_WITH_PRECISE_NUMERIC_COEFFICIENT_BINDING',
        base_head='914505d4f4e649be8a62bf066f01b09e01586b04',
        cutoff_owner='BHSM-AE4-BRANCH-BIRTH-CUTOFF-2026-10-08',
        evaluation_side='MUON_CHILD_PLUS_SIDE_AT_BIRTH',birth_time=0.,finite_plus_offset=0.,
        iterate='retained q/m at common birth; q(t)=q_birth+t*qdot_birth; H=p=gauge=0 numerical iterate',
        temporal_mesh=dict(degree=2,parent=[-.01,0.],child=[0.,.01],
            physical_duration_selected=False,physical_boundary_conditions_selected=False,
            purpose='computational local future-oriented test chart, not an event-time assignment'),
        source_and_temporal_contractions=contracts,normal_clock_contract=current_scalar_time_and_load_contract(),
        coupling_owner=common_derivative_ledger(),composition_owner=action_composition_contract(),
        physical_solve_first_unbound_application=stopped,calibrated_unit_coefficients=unit_coefficients,
        calibrated_reference_spatial_applications=scalar_spatial_applications,scalar_domain_closure=closure,
        residual_formula='F=F_geometry+gamma*F_surface_per_gamma+(lambda_H*nu^4)*F_H_potential_per_lambda_nu4',
        production_states_stationary=False,normal_section_selected=False,
        physical_T_evaluated=False,T_producer_implemented=True,
        downstream=dict(h_psi=None,z_psi=None,r=None,i=None,c=None,disjoint_native=None,a_mu=None,g_mu=None,
            reason='No closed physical stationary base or formation section has yet been evaluated.'),
        error_scope=dict(cap_quadrature_refinement_96_to_128=refinements,
            enclosure=False,temporal_and_angular_continuum_error=None,
            physical_response_error=None,soft_limit_error=None,anomaly_enclosure=False),
        claim_classes=dict(DERIVED=['classical body J_H=0 only; quantum ledger retained',
             'same-vector canonical equations and oriented endpoint pairing',
             'fixed-geometry direct area/response H contacts vanish'],
             EVALUATED=['actual incoming/outgoing retained-candidate off-shell geometry/surface/potential Euler rows',
                        'common temporal weak residuals and Hessians; full finite scalar linearized operator pencil'],
             CONTROL_ONLY=['numerical meshes and zero scalar/gauge iterate; software test fixtures'],
             UNEVALUATED=['radiative/BHSM correction to measured scalar matching and common geometric action unit matching',
                         'physical event scalar Cauchy projection and worldvolume/bundle conditions',
                         'complete interacting stationary base and native Pauli observable'],
             OWNER_DEFINITION_GAP=[]),input_identities=inputs))
    print(json.dumps(dict(output=str(args.output),classification='EVALUATED_OFF_SHELL_COUPLED_PRIMAL',
        first_unbound=stopped['operand'],
        residual_norms={s:{k:[v['norm_F_q'],v['norm_F_m']] for k,v in r.items()} for s,r in rows.items()},
        physical_Newton_executed=False,a_mu=None,g_mu=None),sort_keys=True))


if __name__=='__main__':main()
