"""Evaluate node3 intrinsic projected kinetic actions; fail closed at attachment."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run(root,out):
    if out.exists():raise FileExistsError('fresh output directory required')
    out.mkdir(parents=True);sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_wall_input_attachment import normalized_input_maps,intrinsic_reference_rows,intrinsic_reference_gram,graph_complement
    a=root/'artifacts';tail=a/'muon_retained_tail_core_20261005/run_1'
    refs=dict(point=tail/'points/node_03.npz',point_receipt=tail/'points/node_03.json',
        retained=tail/'retained_tail_points.npz',
        cut=a/'muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz',
        radial=a/'muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz',
        contact=a/'muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        corrected=a/'muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        geometry=a/'muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        chiral=a/'action_extension/BHSM_AE31_C2_CHIRAL_GREEN_DOMAIN.json',
        intrinsic=a/'action_extension/BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json',
        owner=root/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        normal_pullback=root/'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        normalized_trace_owner=root/'src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py',
        material_reset=root/'src/bhsm/interface/ae31_c2_chiral_green_domain.py',
        module=root/'src/bhsm/interface/muon_wall_input_attachment.py',script=Path(__file__))
    data={k:read(refs[k]) for k in ('point','retained','cut','radial','contact','corrected','geometry')}
    receipt=json.loads(refs['point_receipt'].read_text());r=receipt['attachment'];point=data['point'];h=data['retained']
    node_index=np.flatnonzero(h['node_indices']==3)[0]
    if not np.array_equal(point['actual_state'],h['states'][node_index]):raise ValueError('different node3 state')
    # Recover the SAME instantaneous radius from the cached source-frame rule;
    # no geometry/action rebuild, rate freezing, physical scale or RADIUS0.
    R=float(data['geometry']['boundary_radius'][0])*(float(data['contact']['T_b'])/r['T_b'])**2
    shape=float(point['actual_state'][25:37]@((-1.)**np.arange(12)))
    maps=normalized_input_maps(point,r,data['cut']['radial_weights'],R)
    basis={};S=data['cut']['independent_source_map'];d=S.shape[1]
    for n in (1,3):
        xi=data['contact'][f'Xi_A_unit_n{n}'][:,:,data['corrected']['source_image_probe_columns']]
        flat=xi.transpose(1,3,4,0,2).reshape(64,n+1,n+1,32)
        basis[n]=np.einsum('omki,ij->omkj',flat,S)
    rows=intrinsic_reference_rows(basis,data['radial'],R,r['H'],shape,maps['B_volume'],maps['B_volume_tau'])
    gram=intrinsic_reference_gram(rows,maps['M4'])
    G=sum(x.reshape(-1,d).conj().T@x.reshape(-1,d) for x in basis.values())
    M5=np.kron(np.array([[maps['volume_moments'][0],maps['volume_moments'][1]],
        [maps['volume_moments'][1],maps['volume_moments'][2]]]),G)
    B=np.hstack((np.eye(d),r['bulk_B']*np.eye(d)));M4=maps['M4']*G
    witness=graph_complement(B,M5,M4,data['cut']['source_coordinates'])
    # Actual source makes factorization through pointwise material trace fail.
    Xi=np.concatenate([x.reshape(-1,d) for x in basis.values()])
    source=data['cut']['source_coordinates'];input_p=r['bulk_B']*Xi@source
    material_p=np.zeros_like(input_p)
    np.savez_compressed(out/'node3_projected_intrinsic_kinetic.npz',**maps,**rows,**gram,
        **witness,source_coordinates=source,Xi_full=Xi,wall_Haar_Gram=G,
        source_input_projection=B,trial_M5=M5,wall_M4=M4,
        actual_state=point['actual_state'],actual_Y_tau=point['Y_tau'],
        material_source_trace=material_p,normalized_source_input=input_p,
        inherited_LR_mass_block_GeV=np.array(json.loads(refs['chiral'].read_text())['chiral_operator_assembly']['LR_zero_order_mass_block_GeV']))
    coefficient=dict(name='Theta_p node3 complement-to-independent-H4 input coefficient',
        defining_equation='Theta_p^(3)=Pi4 iota_p^(3), Pi5 iota_p=p_A; (p_A,Theta_p) must satisfy the action-owned first-order joint trace/domain rule',
        supplied_candidate='B_rad p_A=b Xi_A with b=0.024964485717262674; this is a radial Hilbert projection, not the independent-H4 domain equation',
        required_shape='n1+n3 full64 spin/carrier rows by12 actual photon source columns; preserve chiral/family factors',
        producer='current M5/M4 first-order trace/output realization of the v14.45/v15.69 action inside AE4 D_strat',
        consumer='R4p,tau=c4^tau Theta_p plus prescribed principal interface action; then R4p,0 and complete shared M4 Gram',
        classification='defining off-mode attachment not specified by the examined retained equations; not a completed numerical builder or a new physical boundary choice')
    native=dict(R4W_0=None,R4W_tau=None,R4p_0=None,R4p_tau=None,
        owned_Higgs_Yukawa_actions=None,owned_normal_interface_action=None,complete_wall_Gram=None,
        updated_tail_return=None,updated_stationary_solution=None)
    result=dict(classification='evaluated intrinsic geometric/common-A reference on actual normalized node3 inputs; native wall attachment unresolved',
        node=3,action_arc=float(h['action_lengths'][node_index]),branch=receipt['first_action']['branch'],
        radius=R,radius_saved_log_difference=R-float(np.exp(h['log_radius'][node_index])),
        B_volume_p=r['bulk_B'],B_volume_p_tau=r['bulk_B_tau'],
        B_Cauchy_p=r['Cauchy_B'],B_Cauchy_p_tau=r['Cauchy_B_tau'],
        material_mode_multiplier=float(maps['material_trace'][0]),
        material_source_trace_norm=float(np.linalg.norm(material_p)),
        normalized_source_input_norm=float(np.linalg.norm(input_p)),
        intrinsic_kinetic_p_action_norm=float(np.linalg.norm(rows['F0'][:,d:]@source)),
        intrinsic_kinetic_p_time_action_norm=float(np.linalg.norm(rows['F1'][:,d:]@source)),
        input_map_time_derivative_retained=True,all_n1_n3_and64_rows_retained=True,
        graph_orthogonal_norm_squared=float(witness['graph_orthogonal_norm_squared']),
        graph_annihilator_residual=float(np.linalg.norm(witness['graph_annihilator'])),
        reference_kinetic_Gram_Hermitian_residual=float(np.linalg.norm(gram['kinetic_reference_A']-gram['kinetic_reference_A'].conj().T)),
        native=native,first_missing=coefficient,
        operator_update_applied=False,parent_solution_reused_unchanged=True,new_stationary_solve=False,
        new_parent_point_actions=0,old_tests_rerun=0,
        error_scope='cached numerical node and nominal binary64 reference contractions; no new continuum/history/unit or native-operator enclosure',
        physical_a_mu=None,physical_g_mu=None,native_uncertainty=None)
    save(out/'result.json',result);save(out/'missing_operand.json',coefficient)
    save(out/'input_hashes.json',{k:dict(path=str(p),sha256=sha(p)) for k,p in refs.items()})
    save(out/'workspace.json',dict(head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
        branch=subprocess.check_output(['git','-C',str(root),'branch','--show-current'],text=True).strip(),
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',new_files_uncommitted_at_execution=True))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve())
