"""First-order compact complementary solve; no old production replay."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np


def load(p):
    with np.load(p,allow_pickle=False) as d:return {k:np.array(d[k]) for k in d.files}


def save(p,d):p.write_bytes((json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def references(root):
    a=root/'artifacts';b=a/'muon_retained_tail_core_20261005/run_1'
    return dict(node3=b/'points/node_03.npz',node4=b/'points/node_04.npz',
        receipt3=b/'points/node_03.json',receipt4=b/'points/node_04.json',
        retained=b/'retained_tail_points.npz',
        wall=a/'muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz',
        cut=a/'muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz',
        contact=a/'muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        radial=a/'muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz',
        matching=a/'muon_proposed_seam_matching_20261005/run_2/localized_matching_maps.npz',
        frozen=a/'muon_proposed_seam_matching_20261005/frozen_locals.json',
        proposed_equations=a/'muon_proposed_dynamic_seam_20261005/run_2/equations.json',
        terminal=b/'terminal_core_element.json',
        raw_producer=root/'src/bhsm/interface/muon_coupled_cut_forms.py',
        metric_producer=root/'src/bhsm/interface/muon_parent_maxwell_velocity.py',
        point_producer=root/'src/bhsm/interface/muon_prefix_time_element.py',
        green_domain=root/'src/bhsm/interface/ae31_c2_chiral_green_domain.py',
        reset_domain=root/'src/bhsm/interface/action_extension_global_spin_reset_ae2.py',
        stop_domain=root/'src/bhsm/interface/ae4_current_c2_canonical_stop_domain_bridge.py',
        boundary_prescription=root/'src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py',
        module=root/'src/bhsm/interface/muon_first_order_complement.py',
        proposal_producer=root/'src/bhsm/interface/muon_proposed_dynamic_seam.py',
        script=Path(__file__).resolve())


def calculate(root):
    sys.path.insert(0,str(root/'src'))
    from flint import ctx
    ctx.prec=192
    from bhsm.interface.muon_first_order_complement import (
        point_coefficients,canonical_map,first_order_moments,bubble_element,restricted_solve)
    from bhsm.interface.muon_proposed_dynamic_seam import charged_left_projector
    refs=references(root)
    d={k:load(refs[k]) for k in ('node3','node4','retained','wall','cut','contact','radial','matching')}
    receipts=[json.loads(refs[f'receipt{n}'].read_text()) for n in (3,4)]
    xi={n:d['wall'][f'normalized_wall_W_input_n{n}'] for n in (1,3)}
    source=d['wall']['source_coordinates'];G0=d['radial']['common_parent_Gamma'][0]
    if not np.array_equal(d['node3']['actual_state'],d['wall']['actual_state']):raise ValueError('source/state provenance mismatch')
    gram=np.zeros((12,12),complex);cross=gram.copy();gram_L=gram.copy()
    PL=charged_left_projector()
    for a in xi.values():
        x=a.reshape(-1,12);y=np.einsum('oi,imkj->omkj',G0,a).reshape(-1,12)
        gram+=x.conj().T@x;cross+=x.conj().T@y
        lx=np.einsum('oi,imkj->omkj',PL,a).reshape(-1,12)
        gram_L+=lx.conj().T@lx
    transport=np.linalg.solve(gram,cross)
    closure=sum(np.linalg.norm(np.einsum('oi,imkj->omkj',G0,a)-np.einsum('omki,ij->omkj',a,transport))**2 for a in xi.values())**.5
    if closure>1e-12:raise ValueError('Gamma0 reached source image requires an additional independent frame')
    ev,U=np.linalg.eigh(gram_L);keep=ev>1e-12*ev[-1]
    if sum(keep)!=6:raise ValueError('physical LL source frame rank differs from saved representation')
    TL=U[:,keep]/np.sqrt(ev[keep])[None,:]
    r_transform=np.linalg.solve(gram,gram_L@TL)
    r_source=TL.conj().T@gram_L@source
    r_frame_error=sum(np.linalg.norm(np.einsum('omki,ij->omkj',a,r_transform)-
        np.einsum('oi,imkj,jv->omkv',PL,a,TL))**2 for a in xi.values())**.5
    if r_frame_error>1e-12:raise ValueError('physical wall restriction not contained in supplied source image')
    fields={};proofs=[];moment_list=[];maps=[];point_ids=[]
    for k,node in enumerate((3,4)):
        p=d[f'node{node}'];rc=receipts[k];index=int(np.flatnonzero(d['retained']['node_indices']==node)[0])
        if not np.array_equal(p['actual_state'],d['retained']['states'][index]):raise ValueError('retained point mismatch')
        logr=float(d['retained']['log_radius'][index]);grid=d['contact']['rho']
        s,pf=point_coefficients(p,rc['attachment'],logr,grid,d['cut'],d['contact'])
        C,Ct=canonical_map(p,rc['attachment'],np.exp(logr),d['cut'],s,d['matching'] if node==3 else None)
        m0,m1,actions,checks=first_order_moments(p,s,xi,d['radial'],d['cut'],C,Ct,source,r_transform)
        fields.update({f'node{node}_{a}':v for a,v in s.items()})
        fields.update({f'node{node}_{a}':v for a,v in actions.items()})
        moment_list.append((m0,m1));maps.append([C,Ct]);proofs.append(dict(coefficient_proof=pf,action_proof=checks))
        point_ids.append(dict(node=node,arc=rc['arc'],clock_density=float(p['clock_density']),
            branch=rc['first_action']['branch'],signed_descriptor=rc['first_action']['signed_descriptor'],
            canonical_C=C,canonical_C_tau=Ct,normalization='cached I/I_tau/u and WW Cauchy matrix; no mode re-normalization'))
    width=float(receipts[1]['arc']-receipts[0]['arc'])
    jac=width*np.array([float(d[f'node{n}']['clock_density']) for n in (3,4)])
    blocks=bubble_element(*moment_list,jac,6)
    direction=np.r_[r_source,np.zeros_like(r_source)]
    solved,status=restricted_solve(blocks,direction)
    status['restricted_correction_contraction']=[status['restricted_correction_contraction'].real,status['restricted_correction_contraction'].imag]
    arrays=dict(**fields,**blocks,**solved,source_R_direction=direction,
        node_moments_S0=np.array([m[0] for m in moment_list]),node_moments_S1=np.array([m[1] for m in moment_list]),
        canonical_maps=np.array(maps),Gamma0_source_coordinates=transport,source_coordinates=source,
        source_image_Gram=gram,physical_left_projector=PL,wall_projected_source_Gram=gram_L,
        wall_frame_TL=TL,wall_input_in_full_source_coordinates=r_transform,
        wall_test_source_coordinates=r_source,temporal_jacobians=jac)
    result=dict(classification='DOMAIN_VALID_COMPACT_FIRST_ORDER_GALERKIN_REDUCTION_NOT_RETARDED_OR_NATIVE',
        first_order_B='Gamma0 D5 raw; A5=(B+Bformal)/2 for literal symmetric proposal',
        first_order_eta='B_eta=i Gamma0 Gamma4 eta is skew; formal sign reverses; A5W=B5W-B_eta W on interior compacts',
        source_frame=dict(Q_columns=12,R_physical_LL_columns=6,Gamma0_closure_residual=closure,
            wall_input_frame_residual=r_frame_error,wall_projected_Gram_eigenvalues=ev.tolist(),
            wall_test_original_load_projection_norm=float(np.linalg.norm(r_source)),
            dependent_Gamma0_columns_not_added=True,
            unmatched_right_spin_LL_retained=True,physical_e_R_realization=False),
        domain=dict(material='P G0 chi=0,Q_boundary G1 chi=0; each compact p trace is zero',
            temporal='phi0=x(1-x),phi1=x(1-x)(2x-1), extended by zero on inherited arc6..8 interior segment',
            other_faces='zero trace on reset,past-prefix,true stop,pole by compact support; not new physical endpoint conditions',
            seam='all mixed material seam terms zero for these compact Q tests, not zero on general Q domain',
            complement='not p-W Bvol p; actual bulk-only Q variations in independent H5+H4',
            wall='R_L=(W Phi_L,w_L), Phi_L=Pi_L Xi T_L; P G0 R_L=E w_L, G1 R_L=0; no right-spin LL declared e_R',
            test_role='wall basis and original-load projection are diagnostic test directions, not Theta_p, prescribed wall forcing or external muon state'),
        evaluated_points=point_ids,first_order_column_checks=proofs,restricted_solve=status,
        same_owner_terms=dict(parent_symmetric_first_order='evaluated on compact trial subspace',
            proposed_seam='included, zero by applicable traces',intrinsic_wall='Q component zero; intrinsic term remains in A_RR once, not omitted from proposed action',
            Yukawa='once-owned wall bridge unchanged; no explicit Y/H term in compact QQ,QR,RQ at this fixed background/frame order',
            quantum_measure=None,completion_and_subtraction=None),
        matching=dict(direct_result_preserved=True,complete_A_eff=None,
            correction_scope='24 Q and12 physical LL R coordinates, two bubbles; not the full Q domain or e_R realization; parent contribution only in A_eff_parent_restricted',
            kinetic_coefficients_of_full_effective_action=None,
            Yukawa_in_previous_canonical_convention='unchanged once-owned C_L^sharp YH C_R; elimination has no extra explicit YH bridge here',
            nonlocal_kernel_not_discarded=True,full_matching_outcome='unevaluated; direct restriction remains nonmatching at its preserved scope'),
        source_jet=dict(coordinate='same photon b_A; beta=T_b b; A_Q=sqrt(2)beta; no rescaling or index2/3',
            total_AQQ_A=None,total_AQR_A=None,total_ARQ_A=None,physical_source_stationary_return=None,
            auxiliary_photon_result='previous corrected L contraction preserved; not substituted for physical vertex'),
        missing_action=dict(name='retarded complementary first-order Green action on reached normal/temporal/angular outputs',
            equation='a_QQ(eta,X_Q^R w)=a_QR(eta,w) for every eta in Q_domain; support(X_Q^R w) in J_plus support(a_QR w)',
            material='P G0 X=0,Q_boundary G1 X=0',reset='same inherited U_R trace graph',
            producer='first-order Euler of proposed S5sym plus proposed material domain and inherited causal/reset continuation; numerical realization not supplied by squared-action tail cache',
            consumer='a_RQ(v,X_Q^R w) in A_eff and total same-photon derivative',
            stop_scope='saved stop supplies a nonnegative Friedrichs form closure, not an evaluated first-order retarded terminal relation; no new endpoint parameter asserted',
            category='unevaluated causal realization of unadopted proposal, not inferred physical absence or new vacuum datum'),
        error_scope='binary64 model: existing512-point nodal spatial quadrature, linear interpolants of FIRST-ORDER weak moment densities on one retained element, exact degree-polynomial temporal quadrature; no interpolation/history/continuum bound',
        old_production_rerun=False,old_checks_repeated=False,accepted_parent_solution_changed=False,
        historical_run1='unaccepted full-carrier R attempt preserved; corrected run2 restricts physical wall LL while keeping unmatched outputs and full Q',
        native_operator_updated=False,proposal_adopted=False,frozen_locals_changed=False,physical_a_mu=None,physical_g_mu=None)
    return refs,arrays,result


def run(root,out):
    if out.exists():raise FileExistsError('dedicated new output directory required')
    start=time.perf_counter();refs,arrays,result=calculate(root);out.mkdir(parents=True)
    np.savez_compressed(out/'first_order_compact_reduction.npz',**arrays)
    save(out/'result.json',result)
    save(out/'input_hashes.json',{k:dict(path=str(p),sha256=sha(p)) for k,p in refs.items()})
    git=lambda *a:subprocess.check_output(['git','-C',str(root),*a],text=True).strip()
    save(out/'workspace.json',dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),status=git('status','--short'),
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd'))
    save(out/'execution.json',dict(command='replay_muon_first_order_complement.py --output '+str(out),
        wall_seconds=time.perf_counter()-start,old_production_repeated=False,new_Q_solve='first-order compact Galerkin only',
        full_causal_Q_solve=False,native_heat_evaluations=0,physical_transfer_directions=0))
    save(out/'checkpoint.json',dict(id='BHSM_MUON_FIRST_ORDER_COMPACT_COMPLEMENT_20261006',
        new='first-order Green-cancelled forcing and domain-valid restricted stationary solve',
        next=result['missing_action'],native_adoption=False))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(dict(frame=result['source_frame'],points=result['evaluated_points'],
        solve=result['restricted_solve'],point_actions=result['first_order_column_checks']),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve())
