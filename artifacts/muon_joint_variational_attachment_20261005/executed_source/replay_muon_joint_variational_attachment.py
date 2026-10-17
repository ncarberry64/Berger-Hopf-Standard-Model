"""Cache-only node3 Green/source first variations; no old producer replay."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np

def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())

def run(root,out):
    if out.exists():raise FileExistsError('new output directory required')
    out.mkdir(parents=True);sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_joint_variational_attachment import (
        material_green_columns,known_bulk_euler_contractions,coupled_variation_contract)
    a=root/'artifacts';s=root/'src/bhsm/interface'
    refs=dict(point=a/'muon_retained_tail_core_20261005/run_1/points/node_03.npz',
        receipt=a/'muon_retained_tail_core_20261005/run_1/points/node_03.json',
        cut=a/'muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz',
        prior=a/'muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz',
        carrier=a/'muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz',
        source_producer=s/'muon_parent_source_contact.py',source_image=s/'muon_wall_source_pairing.py',
        source_contract=s/'aether_common_source_frechet_response_v15_99.py',
        load=s/'muon_retained_tail_core.py',parent=s/'completion/foundational_dirac_spin_glue_v14_45.py',
        boundary=s/'aether_unified_m5_m4_pushforward_v15_69.py',
        intrinsic=s/'ae31_c2_intrinsic_m4_lepton_action.py',chiral=s/'ae31_c2_chiral_green_domain.py',
        reset=s/'action_extension_global_spin_reset_ae2.py',owner=s/'ae4_stratified_dirac_zeta_induced_owner.py',
        incidence=s/'completion/tensor_differential_incidence_v14_69.py',
        old_action_attachment=s/'completion/action_attachment_wentzell_v14_67.py',
        module=s/'muon_joint_variational_attachment.py',script=Path(__file__))
    point,cut,prior,carrier=[read(refs[k]) for k in ('point','cut','prior','carrier')]
    meta=json.loads(refs['receipt'].read_text());r=meta['attachment']
    basis={n:prior[f'normalized_wall_W_input_n{n}'] for n in (1,3)}
    Xi=prior['Xi_full'];G=carrier['common_parent_Gamma'];mu=float(prior['M4'])
    I=float(np.mean(r['I']['interval']));It=float(np.mean(r['I_tau']['interval']))
    green=material_green_columns(G,basis,mu,r['H'],float(prior['material_trace'][0]),I,It)
    bulk=known_bulk_euler_contractions(point,basis,G,cut['radial_weights'],cut['source_coordinates'])
    np.savez_compressed(out/'node3_joint_known_variations.npz',**green,**bulk,
        actual_state=point['actual_state'],actual_Y_tau=point['Y_tau'],
        source_coordinates=cut['source_coordinates'],Gamma=G,source_image_basis=Xi,
        radius=prior['radius'],H=np.array(r['H']),I=np.array(I),I_tau=np.array(It),
        copied_inherited_LR_mass_block_GeV=prior['inherited_LR_mass_block_GeV'])
    result=dict(classification='known action Green/source variations on actual node3 computational directions; joint native prescription unevaluated',
        node=3,action_arc=meta['arc'],branch=meta['first_action']['branch'],source_columns=12,
        H=r['H'],I=I,I_tau=It,Green_coordinate_time_rate=float(green['Green_coordinate_time_rate']),
        W_Dirac_Green_columns_norm=float(np.linalg.norm(green['W_material_Green_Dirac'])),
        W_Dirac_Green_time_columns_norm=float(np.linalg.norm(green['W_material_Green_Dirac_tau'])),
        bulk_Dirac_Euler_amplitude_norm=float(np.linalg.norm(bulk['known_bulk_Dirac_Euler_p_source'])),
        bulk_Dirac_Euler_time_norm=float(np.linalg.norm(bulk['known_bulk_Dirac_time_jet_p_source'])),
        diagnostic_bulk_load_norm=float(np.linalg.norm(bulk['diagnostic_bulk_Riesz_load_original'])),
        actual_body_actions_reused=True,old_reference_wall_actions_recomputed=False,
        new_parent_point_actions=0,new_stationary_solve=False,native_operator_updated=False,
        material_p_Green_is_zero='known geometric compact trace only; no independent-H4 inference',
        unknown_wall_forcing='full insertion image Pi4 Xi_strat[a] phi requires the same joint prescription; no value selected',
        native_R4=None,native_wall_Gram=None,native_uncertainty=None,physical_a_mu=None,physical_g_mu=None,
        error_scope='nominal binary64/nodal cached node; no new continuum, history, interface/domain or native Pauli bound')
    save(out/'result.json',result);save(out/'coupled_variation.json',coupled_variation_contract())
    save(out/'input_hashes.json',{k:dict(path=str(p),sha256=sha(p)) for k,p in refs.items()})
    save(out/'workspace.json',dict(head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
        branch=subprocess.check_output(['git','-C',str(root),'branch','--show-current'],text=True).strip(),
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd'))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve())
