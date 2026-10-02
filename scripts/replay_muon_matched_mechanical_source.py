"""Replay the actual saved-mode mechanical conversion and weak-row action.

No previous producer, native heat calculation or exterior solve is rerun.
Use a fresh --output. The mechanical/physical attachment is kept explicit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np


HERE=Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p,obj):
    p.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8')


def run(manifest,output):
    refs=json.loads(manifest.read_text())
    root=HERE.parent if (HERE.parent/'src').is_dir() else Path(refs['repository'])
    sys.path.insert(0,str(root/'src'))
    if (HERE/'muon_matched_mechanical_source.py').exists():
        sys.path.insert(0,str(HERE))
        import muon_matched_mechanical_source as impl
    else:
        from bhsm.interface import muon_matched_mechanical_source as impl
    if output.exists():
        raise FileExistsError('Preserve existing evidence; use a new output directory')
    paths={}
    for k,row in refs['inputs'].items():
        p=root/row['repository_path']
        if sha(p)!=row['sha256']:
            raise ValueError('changed input '+k)
        paths[k]=p
    for row in refs['producers']:
        if sha(root/row['repository_path'])!=row['sha256']:
            raise ValueError('changed producer '+row['repository_path'])
    output.mkdir(parents=True)
    save(output/'stage_receipt.json',{'stage':'verified retained inputs and producers','input_refs':refs})
    start=time.perf_counter()
    def load(k):
        with np.load(paths[k],allow_pickle=False) as z:
            return {v:np.array(z[v]) for v in z.files}
    source,frames,parent,principal,weighted,geometry=[load(k) for k in
        ('source','frames','parent','principal','weighted','geometry_inputs')]
    old=json.loads(paths['previous_result'].read_text())
    frozen=json.loads(paths['frozen_local'].read_text())
    rho=parent['rho'];A=parent['A'][0];B=parent['B'][0]
    lam=A*A/(A*A+B*B)
    corner=float(lam[-1])
    x=impl.realize(source['real_mode_coefficients'],frames['angular__curl_unit_N1'],corner)
    H=old['frontier_source']['H'];Tb=old['frontier_source']['T_b']
    e=principal['e'][0];r=principal['r'][0];zeta=principal['shift'][0]
    density=np.zeros_like(r)
    good=parent['base_radius'][0]>0
    density[good]=r[good]*(parent['C_rho'][0,good]/parent['base_radius'][0,good])**2
    # Analytic regular-pole density limit zero; no invented pole boundary.
    if np.any(~good & (rho!=0)):
        raise ValueError('unexpected orbit degeneracy')
    lt,lr=impl.lambda_jets(geometry['states'][0],rho,lam,parent['boundary_lapse'][0])
    actions=impl.primitive_weak_application(x,lam,e,r,zeta,density,H,Tb,lt,lr)
    arrays=dict(rho=rho,mechanical_lambda=lam,lambda_tau=lt,lambda_rho=lr,
                full_pointwise_W=weighted['W_event'][0],electric=e,radial=r,
                shift=zeta,angular_density=density,rotation_coefficients=x['rotation'],
                **actions)
    for family in ('original','transformed','section0_curvature','covariance_rhs',
                   'section1_curvature','mixed_rows','curls','gradients',
                   'gauss_contact','curvature_contacts'):
        for n,val in x[family].items():
            arrays[f'{family}_n{n}']=val
    # Clifford and carrier are factored arrays, not a second spin frame.
    basis=np.concatenate((-1j*weighted['T']/np.sqrt(2),
                          (-1j*weighted['Y']/np.sqrt(10/3))[None]))
    arrays['unit_trace_carrier_basis']=basis
    arrays['saved_gamma_LR']=source['gamma_LR']
    for n,val in x['transformed'].items():
        arrays[f'i_gamma_source_coeff_n{n}']=1j*np.einsum('cij,Acemk->Aijemk',source['gamma_LR'][1:],val)
    # Full mixed rows vs QQ compression: QQ contact must vanish since both
    # columns have the SAME transported generator, but mixed contact need not.
    qq=np.zeros((8,8),complex);qc=np.zeros_like(qq)
    source_gram=np.zeros_like(qq)
    contact_norm=0.;mixed_norm=0.;n3_norm=0.
    for n,val in x['transformed'].items():
        row=x['mixed_rows'][n]
        row=row[0]+corner*row[1]+corner**2*row[2]
        qq+=np.einsum('Acimk,Bcimk->AB',val.conj(),row)/(16/3)
        qc+=np.einsum('Acimk,Bcimk->AB',val.conj(),x['curvature_contacts'][n])/(16/3)
        source_gram+=np.einsum('Acimk,Bcimk->AB',val.conj(),val)/(16/3)
        contact_norm+=np.linalg.norm(x['curvature_contacts'][n])**2
        mixed_norm+=np.linalg.norm(row)**2
        if n==3:
            n3_norm=np.linalg.norm(val)
    arrays['matched_mechanical_QQ_corner']=qq
    arrays['QQ_curvature_contact_corner']=qc
    arrays['transported_source_Gram']=source_gram
    np.savez_compressed(output/'matched_source_and_weak_actions.npz',**arrays)
    checks=dict(source_covariance_absolute=x['covariance_absolute_residual'],
        retained_n5_cancellation=x['connected_n5_cancellation_residual'],
        source_Gram_residual=float(np.linalg.norm(source_gram-np.eye(8))),
        QQ_contact_residual=float(np.linalg.norm(qc)),
        full_mixed_curvature_contact_norm=float(np.sqrt(contact_norm)),
        full_angular_mixed_row_norm=float(np.sqrt(mixed_norm)),
        transported_n3_source_norm=float(n3_norm),
        angular_QQ_Hermitian_residual=float(np.linalg.norm(qq-qq.conj().T)),
        old_curvature_frame_result_reused=False)
    missing=dict(name='total-connection/background source attachment into current D_strat',
        equation='Omega_strat^(0)=Att_current[rho_*(omega_mechanical),A_SM^(0)]; delta_b Omega_strat=T_b Y_A*(-i Q) in that SAME carrier/Clifford section',
        input_spaces='mechanical ad(P_diag) connection and its retained Lorentz M5 geometry; SM rank16 bundle and Q source in saved right-coframe carrier',
        output_spaces='total connection one-form in the current chiral D_L,D_R and positive-parent/interface operator, and the compatible SAME-source tangent',
        producer='v15.50 action_ownership_ledger selects mechanical background; rank16_connection_attachment fixes representation/index; v15.53 hybrid_bundle_gluing selects zero-background SM sector but does not give a total-vs-fluctuation attachment equation; v15.69 fixed-trace Gamma and AE4 owner do not supply it',
        consumer='physical mixed parent weak Hessian and same-source exterior forcing return j_ext; then Xi_plus and finite-E1 source response',
        unresolved_alternatives='Does zero-background mean A_SM,total^(0)=0, or fluctuation a_SM^(0)=0 around rho_*(omega)? If the latter, identify the same Higgs/Q section and any actual background lift.',
        classification='physical connection/background identification absent from the recovered producer chain; resolved within-child coordinate/gauge convention is insufficient',
        not_an_uncomputed_matrix_solve=True)
    result=dict(checkpoint='BHSM_MUON_MATCHED_MECHANICAL_PRIMITIVE_WEAK_ROW_20261002',
        scientific_reference=refs['scientific_reference'],publication_start_HEAD=refs['publication_start_HEAD'],
        classification='EVALUATED_MECHANICAL_PRIMITIVE_REFERENCE_SOURCE_AND_WEAK_ROW; PHYSICAL_SM_TOTAL_ATTACHMENT_UNIDENTIFIED',
        base='w=u*v^-1, sections sigma0=(w,1), sigma1=(1,w^-1)=sigma0*w^-1',
        coframe='theta_R=dw*w^-1=Ad_w theta_L; saved curl=*d=2I+S.2J; oriented right Maurer coframe; volume Haar normalized',
        carrier='U=rho(w), Omega1=U Omega0 U^-1-dU U^-1=(lambda-1)jmath(theta_R)',
        source='a0=T_b b_A Y_A(theta_R)(-iQ), a1=U a0 U^-1; spatial coframe held right throughout; no separate spin-frame rotation',
        source_identification_scope='a0 is the supplied fixed-Q reference source in the canonical sigma0 computation; its identification with the physical SM total connection source remains an explicit missing attachment, not inferred from normalization',
        derivatives='dQ1=[jmath(theta_R),Q1] is included by differentiating complete n1+n3 coefficients; partial_tau U=partial_rho U=delta_b U=0 at fixed w and retained geometry; no temporal/radial one-form generated by this within-child U',
        source_coordinate='b; beta=T_b b; A_Q=sqrt(2) beta; K_Q=(2/3)K_component already in e,r,d; K_trace=K_Q/(16/3)',
        representation='phi_nmk=sqrt(n+1) conjugate D^(n/2)_mk; E coefficients=i2J; saved Gaunt and reality rules; spin1 Ad_w times saved n1 gives n1+n3 exactly',
        common_domain_scope='smooth fixed U preserves within-child H1 form domain and transforms every trace on the same angular base; no new strong DdaggerD domain or reset/interface attachment is asserted',
        angular_mixed_row='H_lambda=(C0+(lambda-1)T)^dagger(C0+(lambda-1)T)+4lambda(lambda-1)B; B_ic,jd=eps_kij eps_kcd. Lorentz weak angular sign is minus.',
        weak_consumption='evaluated -d/Qnorm H_lambda A dual on all n1+n3 spatial/internal tests at 65 supplied cut rho points, plus e/Qnorm A and -r/Qnorm A derivative rows and scalar temporal/radial constraint/contact rows. These are coefficient applications, not an extension or PDE solve.',
        weak_equation='q_mech(v,a)=integral[e <D_tau v,D_tau a>-r <v_rho,a_rho>-d <C_h v,C_h a> + signed F curvature contacts]/Qnorm; D_tau=partial_tau-zeta partial_rho-H/2. Coefficient derivatives remain under weak derivatives; temporal faces carry inherited orientations.',
        scalar_rows='R_tau=-e Gdagger A D_tau b+e(lambda_tau-zeta lambda_rho)J(A)b; R_rho=e zeta Gdagger A D_tau b+r Gdagger A b_rho-(e zeta(lambda_tau-zeta lambda_rho)+r lambda_rho)J(A)b; J=-sum ad_jmath_i A_i',
        preserved_faces=old['orientations'],frontier_H_reused=H,T_b_reused=Tb,
        frontier_lambda=corner,mechanical_QQ_corner_eigenvalues=np.linalg.eigvalsh(qq).tolist(),
        mechanical_spatial_F_unit_trace_norm_squared=96*corner**2*(corner-1)**2,
        checks=checks,first_unresolved_operand=missing,
        ledger=dict(primitive_mechanical_bulk='evaluated source/weak coefficient actions',
            primitive_background_contact='evaluated full mixed angular and scalar temporal/radial rows',
            physical_SM_attachment=None,gauge_fixing_BRST=None,same_owner_induced_matching=None,
            physical_interface_flux=None,exterior_affine_return=None,cut_composition=None,
            completion_and_domain_variations=None),
        actual_execution=dict(actual_saved_mechanical_reference_modes=8,actual_cut_rho_points=65,
            source_support=[1,3],covariance_intermediate_support=[1,3,5],
            weak_coefficient_applications=8,parent_weak_solves=0,exterior_source_responses=0,
            shifted_resolvent_applications=0,native_E1_evaluations=0,physical_transfer_directions=0,
            old_normalization_covariance_contact_replays=0,elapsed_seconds=time.perf_counter()-start),
        error_scope=dict(exact='section/gauge/Hodge identities; finite one-action angular support; signed primitive weak expressions',
            numerical='binary64 retained-input coefficient evaluations and absolute controls; no interval arithmetic in new calculation',
            parent_reconstruction=None,affine_logR_reconstruction=None,lambda_jet_input_error=None,
            exterior_evolution_tail=None,physical_attachment=None,native_uncertainty=None),
        frozen_local=frozen,current_history_reconciliation=refs['current_history_reconciliation'],
        native_ledger={k:None for k in ('native_bulk_heat','state_variation','contact','domain_boundary','completion_counterterm','strong_within_native')},
        strong_is_native_subset=True,physical_a_mu=None,physical_g_mu=None)
    save(output/'result.json',result)
    save(output/'output_hashes.json',{'files':[{'path':p.name,'sha256':sha(p)} for p in
        (output/'matched_source_and_weak_actions.npz',output/'result.json')]})
    save(output/'stage_receipt.json',dict(stage='new matched mechanical actions saved',
        input_manifest_sha256=sha(manifest),implementation_sha256=sha(Path(impl.__file__)),
        replay_sha256=sha(Path(__file__)),old_producers_rerun=False))
    print(json.dumps(dict(output=str(output),checks=checks,QQ=result['mechanical_QQ_corner_eigenvalues'],
        first_unresolved_operand=missing['name'])))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    default=HERE/'input_refs.json'
    if not default.exists():
        default=HERE.parent/'artifacts/muon_matched_mechanical_source_20261002/input_refs.json'
    p.add_argument('--inputs',type=Path,default=default)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.inputs,a.output)
