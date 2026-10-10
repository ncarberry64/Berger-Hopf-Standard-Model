"""New common-A lepton background/source action; reuse all older caches."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_bytes((json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())

def run(manifest,output,reuse=None):
    refs=json.loads(manifest.read_text())
    root=HERE.parent if (HERE.parent/'src').is_dir() else Path(refs['repository'])
    if output.exists():raise FileExistsError('Fresh output directory required')
    for row in refs['inputs']:
        if sha(root/row['repository_path'])!=row['sha256']:raise ValueError('changed input '+row['repository_path'])
    sys.path[:0]=[str(root/'src'),str(root/'scripts')]
    from bhsm.interface import muon_owned_connection_application as impl
    from replay_muon_connection_attachment import source_equations
    output.mkdir(parents=True)
    equations=[]
    for row in refs['inputs']:
        for name in row.get('functions',[]):
            equations.append(dict(path=row['repository_path'],sha256=row['sha256'],**source_equations(root/row['repository_path'],name)))
    save(output/'action_equations.json',equations)
    with np.load(root/'artifacts/muon_source_jet_20261002/replay_reference/local_source_actions.npz') as p:
        labels=p['input_labels'];sigma=p['sigma'];V=p['V_complete'];source_out_labels=p['output_labels']
    with np.load(root/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz') as p:R=p['rotation_coefficients']
    with np.load(root/'artifacts/muon_source_weak_extension_20261002/replay_reference/independent_source_quotient.npz') as p:
        U=p['angular_frame'];F=p['independent_profile_nodes']
    with np.load(root/'artifacts/muon_source_jet_20261002/source_inputs.npz') as p:
        times=p['frame__proper_times'];radius=np.exp(p['frame__log_radius']);Tb=p['frame__coordinate_oneform_per_canonical_b_nodes']
    with np.load(root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz') as p:
        A=p['A'];B=p['B'];parent_times=p['proper_times'];Rb=p['boundary_radius']
    assert np.array_equal(times,parent_times)
    lam=A[:,-1]**2/(A[:,-1]**2+B[:,-1]**2)
    if reuse:
        old_receipt=json.loads((reuse/'receipt.json').read_text())
        if old_receipt['module_sha256']!=sha(Path(impl.__file__)):raise ValueError('background implementation changed')
        expected=next(r['sha256'] for r in old_receipt['files'] if r['path']=='owned_connection_actions.npz')
        if sha(reuse/'owned_connection_actions.npz')!=expected:raise ValueError('changed background cache')
        action_keys=['input_labels','output_labels','full_weak_background_unit_action','charged_input_embedding','charged_output_embedding','charged_background_unit_action','spin_sigma','weak_sigma']
        applied_keys=['unit_independent_background_actions','unit_independent_background_compression','unit_independent_connected_background_actions','node_background_actions','child_background_prefactor','node_left_neutrino_background_actions','node_n2_n3_background_actions']
        with np.load(reuse/'owned_connection_actions.npz') as p:
            action={k:p[k] for k in action_keys};applied={k:p[k] for k in applied_keys}
        checks=json.loads((reuse/'result.json').read_text())['checks']
    else:
        action=impl.mechanical_background_action(labels,sigma,R)
        applied=impl.apply_saved_child_profiles(action,U,F,lam,radius)
        checks=applied.pop('checks')
    checks['saved_child_parent_radius_relative_residual']=float(np.max(abs(Rb-radius)/radius))
    source_embedding=impl.charged_embedding(source_out_labels,action['output_labels'])
    # The saved V is B_H=-delta H; preserve its sign and complete output.
    Vfull=np.einsum('oi,Aij,jk->Aok',source_embedding,V,action['charged_input_embedding'].conj().T)
    Bfull=action['full_weak_background_unit_action']
    full_cross=-np.einsum('oi,Aoj->Aij',Bfull.conj(),Vfull)-np.einsum('Aoi,oj->Aij',Vfull.conj(),Bfull)
    Vu=np.einsum('Aoi,ij->Aoj',source_embedding@V,U)
    BU=applied['unit_independent_background_actions']
    cross=-np.einsum('oi,Aoj->Aij',BU.conj(),Vu)-np.einsum('Aoi,oj->Aij',Vu.conj(),BU)
    Uout=action['charged_output_embedding']@U
    Bc=Uout.conj().T@BU;Vc=np.einsum('io,Aoj->Aij',Uout.conj().T,Vu)
    cross_c=-np.einsum('ki,Akj->Aij',Bc.conj(),Vc)-np.einsum('Aki,kj->Aij',Vc.conj(),Bc)
    # New background/source cross only; not the complete q_A or heat jet.
    Bnode=applied['node_background_actions']
    Vnode=(Tb/radius)[:,None,None,None]*np.einsum('Aoi,tij->tAoj',source_embedding@V,F)
    node_cross=-np.einsum('toi,tAoj->tAij',Bnode.conj(),Vnode)-np.einsum('tAoi,toj->tAij',Vnode.conj(),Bnode)
    checks.update(source_cross_Hermitian_residual=float(np.linalg.norm(cross-cross.conj().transpose(0,2,1))),
        full_weak_source_cross_norm=float(np.linalg.norm(full_cross)),
        full_weak_source_cross_Hermitian_residual=float(np.linalg.norm(full_cross-full_cross.conj().transpose(0,2,1))),
        unit_source_cross_norm=float(np.linalg.norm(cross)),
        unit_source_cross_complement_norm=float(np.linalg.norm(cross-cross_c)),
        first_node_source_cross_norm=float(np.linalg.norm(node_cross[0])),
        pole_regular_parent_background_prefactor=float(impl.regular_parent_background_prefactor(A,B)[0,0]))
    arrays=dict(**action,**applied,proper_times=times,mechanical_lambda_boundary=lam,
        source_B_H_unit_full_weak=Vfull,source_B_H_on_unit_independent_frame=Vu,
        background_source_cross_full_weak_unit=full_cross,
        background_source_cross_unit=cross,background_source_cross_connected=cross-cross_c,
        background_source_cross_node=node_cross,
        parent_sigma1_background_prefactor=impl.regular_parent_background_prefactor(A,B),
        effective_family_Gram=np.eye(3),effective_family_K=np.zeros((3,3)))
    np.savez_compressed(output/'owned_connection_actions.npz',**arrays)
    result=dict(checkpoint='BHSM_MUON_COMMON_A_CONNECTION_AND_ACTUAL_CHILD_ACTION_20261002',
        start_HEAD=refs['start_HEAD'],scientific_reference=refs['scientific_reference'],
        corrected_prior_claim='The common-A canonical Dirac prescription is adopted; lack of an expanded current D5 builder does not demonstrate an unselected new matter coupling.',
        identity='nabla5_total=nabla5_spin tensor I16 tensor I3 + I_spin tensor rho16_*(A5) tensor I3; A5=iota_*omega_mech+a5 in the retained mechanical fluctuation sector',
        effective_internal_factor='AE3.1 fixed family T_l in Yukawa endomorphism; Spin and independent SM factor in canonical kinetic action. No k5 Clebsch injection is needed or selected.',
        normalized_overlap=dict(G_family='I3',K_family='0 in the retained fixed family basis',S_family='I3',
            B='B_Spin_SM tensor I3; no arbitrary g_u/g_v is inserted',
            source_derivative='delta_b B_SM=T_b Y_A(-iQ); family derivative zero'),
        operator_conventions='Child sigma0/right coframe; H_L,bg=(lambda/R4) sigma_spin^a R_ad sigma_weak^d; H_R,weak=0. D_bg=-gamma0 H_bg into the dual-spin codomain. Saved V=B_H=-delta H, D_source=gamma0 V.',
        same_source='beta=T_b b; Q_L=diag(0,-1), Q_eR=-1; no shape variation, action-index or family-count factor. Source-dependent wall lift/domain jets still required globally.',
        physical_primitive_row_use='Previously evaluated mechanical gauge and conditional Higgs mixed rows now match the common-A mechanical reference; reused without recalculation. Full induced/gauge-constraint response is not supplied by these rows.',
        additional_evaluated_piece='Actual weak background action and its connected lepton/angular output; additive background/source cross in the canonical child q_A, not complete q_A or native P.',
        domain='Existing child H1 and reset trace prescription preserved; globally smooth mechanical principal connection, regular parent sigma1 coefficient -B/(A sqrt(A^2+B^2)); parent SOURCE extension not inferred from child zero order.',
        checks=checks,input_packet_access=refs['input_packet_access'],
        execution=dict(old_production_runs=0,old_six_precursor_checks_rerun=0,new_child_input_columns=16,
            child_profile_nodes=len(times),background_application=True,background_actions_reused=bool(reuse),native_E1_evaluations=0,
            physical_transfer_directions=0,exterior_response_applications=0),
        first_next_operand=dict(name='owned causal prefix zero-trace response on the SAME photon source',
            equation='j_ext,A^R=f_gamma,A-K_gammaZ (K_ZZ^R)^(-1) f_Z,A, with f_Z,A=q5_AE4(v_Z,a_ext,A); canonical future stop unchanged',
            precise_unevaluated_contraction='The q5_AE4 zero-trace/source block f_Z,A and causal inverse on its connected domain, including induced Dirac heat/gauge-constraint terms. Saved primitive rows and local continued source are components, not j_ext.',
            producer='same-owner AE4 mixed form from the now-identified common-A D5 realization on inherited prefix',
            consumer='fixed-trace parent photon extension E_plus_54_Q, then shifted resolvent/native source jet',
            classification='uncomputed prescribed operator/source response; no new physical coupling or precursor state selection imposed'),
        frozen_local=json.loads((root/'artifacts/muon_connection_attachment_20261002/frozen_local.json').read_text()),
        native_ledger=json.loads((root/'artifacts/muon_connection_attachment_20261002/native_ledger.json').read_text()),
        physical_a_mu=None,physical_g_mu=None,
        error_scope='Exact action/factor/finite support identities; binary64 Gaunt actions and cached geometric/profile inputs. No certified continuum/history/quadrature/domain tail or native error enclosure.')
    save(output/'result.json',result)
    save(output/'checkpoint.json',dict(checkpoint_id=result['checkpoint'],start_HEAD=result['start_HEAD'],
        one_next_operand=result['first_next_operand'],result='result.json',actions='owned_connection_actions.npz',
        native_ledger=result['native_ledger'],frozen_local=result['frozen_local']))
    save(output/'receipt.json',dict(script_sha256=sha(Path(__file__)),input_refs_sha256=sha(manifest),
        module_sha256=sha(Path(impl.__file__)),old_producers_called=False,
        reused_new_background_cache=str(reuse) if reuse else None,
        files=[dict(path=p.name,sha256=sha(p)) for p in sorted(output.iterdir())]))
    print(json.dumps(dict(output=str(output),checks=checks,native_E1_evaluations=0)))


if __name__=='__main__':
    p=argparse.ArgumentParser();default=HERE/'input_refs.json'
    if not default.exists():default=HERE.parent/'artifacts/muon_owned_connection_20261002/input_refs.json'
    p.add_argument('--inputs',type=Path,default=default);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--reuse-background',type=Path)
    a=p.parse_args();run(a.inputs,a.output,a.reuse_background)
