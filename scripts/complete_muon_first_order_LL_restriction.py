"""Add the once-owned intrinsic LL action to saved first-order blocks.

No QQ solve, parent action, mode normalization or source response is rerun.
This uses the now-justified physical LL test lift of the unadopted proposal.
"""
from pathlib import Path
import argparse,hashlib,json,os,sys
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def compute(root,base):
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_first_order_complement import bubble_element
    from bhsm.interface.muon_parent_maxwell_velocity import current_parent_fields
    a=read(base/'first_order_compact_reduction.npz')
    # Relocatable paths are established from the preserved repository layout.
    wall_path=root/'artifacts/muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz'
    radial_path=root/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz'
    retained_path=root/'artifacts/muon_retained_tail_core_20261005/run_1/retained_tail_points.npz'
    intrinsic_path=root/'artifacts/action_extension/BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json'
    contact_path=root/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz'
    w=read(wall_path);rad=read(radial_path);history=read(retained_path)
    grid=read(contact_path)['rho']
    G=rad['common_parent_Gamma'];rmap=a['wall_input_in_full_source_coordinates'];moments=[];target=[];points=[]
    for k,node in enumerate((3,4)):
        index=int(np.flatnonzero(history['node_indices']==node)[0]);lr=float(history['log_radius'][index])
        geom=current_parent_fields(history['states'][index:index+1],np.array([lr]),grid)
        R=float(np.exp(lr));bg=float(-geom['B'][0,-1]/(geom['A'][0,-1]*np.hypot(geom['A'][0,-1],geom['B'][0,-1])))
        mu=2*np.pi**2*R**3;cf,ct=a['canonical_maps'][k]
        h=np.zeros((6,6),complex);gram=h.copy()
        for n in (1,3):
            xi=np.einsum('omki,ij->omkj',w[f'normalized_wall_W_input_n{n}'],rmap,optimize=True)
            E=rad[f'angular_E_n{n}']
            angular=sum(np.einsum('oi,imkj,vm->ovkj',1j*G[j+1],xi,E[j],optimize=True) for j in range(3))
            angular+=np.einsum('oi,imkj->omkj',rad['angular_spin'],xi)
            zero=angular/R+bg*np.einsum('oi,imkj->omkj',rad['commonA_gauge_unit'],xi)
            barred=np.einsum('oi,imkj->omkj',G[0],zero)
            x=xi.reshape(-1,6);z=barred.reshape(-1,6)
            h+=mu*(x.conj().T@z+z.conj().T@x)/2
            gram+=mu*x.conj().T@x
        # The pure imaginary time connection / C_tau terms cancel in the
        # bidirectional density. Their Euler measure term remains inherited.
        moments.append((cf*cf*h,1j*cf*cf*gram));target.append((h,1j*gram))
        points.append(dict(node=node,radius=R,wall_commonA=bg,canonical_C=cf,canonical_C_tau=ct,
            proper_clock='same retained point',temporal_density='symmetric: scalar C_tau cancels; Euler measure derivative retained',
            one_owned_LL_Yukawa_block='zero on LL-only test since e_R component=0; full YH bridge unchanged, not zeroed'))
    A4=bubble_element(*moments,a['temporal_jacobians'],6)['A_full']
    target4=bubble_element(*target,a['temporal_jacobians'],6)['A_full']
    ARR=a['A_RR_parent']+A4;eff=ARR+a['restricted_correction']
    data=dict(A_intrinsic_LL_canonical=A4,A_retained_local_LL_reference=target4,
        A_RR_complete_LL=ARR,A_eff_complete_LL_compact=eff,
        A_eff_minus_local_LL_reference=eff-target4,
        intrinsic_point_S0=np.array([p[0] for p in moments]),intrinsic_point_S1=np.array([p[1] for p in moments]))
    result=dict(classification='COMPLETE_PROPOSED_LL_COMPACT_ACTION_WITH_REUSED_Q_CORRECTION_NOT_FULL_RETARDED_MATCHING',
        points=points,QQ_solution_reused=True,QQ_solution_rerun=False,
        parent_plus_intrinsic_plus_seam='same proposed action; seam zero on applicable smooth/compact traces',
        local_reference_difference_norm=float(np.linalg.norm(eff-target4)),
        interpreted_as_required_nonlocal_zero=False,kinetic_low_energy_matching_coefficient=None,
        explicit_YH_bridge='once, unchanged in previous canonical convention; e_R response not realized by LL-only restriction',
        physical_photon_vertex=None,quantum_measure=None,same_owner_subtraction=None,
        full_causal_effective_action=None,native_operator_updated=False,physical_a_mu=None,physical_g_mu=None,
        comparison_scope='difference from adopted local kinetic reference on two temporal bubbles, not a low-energy expansion or proof that permissible nonlocal dressing must vanish')
    inputs=dict(base_arrays=base/'first_order_compact_reduction.npz',base_result=base/'result.json',wall=wall_path,
        radial=radial_path,retained=retained_path,intrinsic=intrinsic_path,contact=contact_path,script=Path(__file__).resolve(),
        module=root/'src/bhsm/interface/muon_first_order_complement.py')
    return data,result,inputs


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    arg=p.parse_args();out=arg.output.resolve()
    if out.exists():raise FileExistsError('new completion directory required')
    data,result,inputs=compute(arg.repository.resolve(),arg.input.resolve());out.mkdir(parents=True)
    np.savez_compressed(out/'complete_LL_action.npz',**data)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    hashes={k:dict(path=str(v),sha256=hashlib.sha256(v.read_bytes()).hexdigest()) for k,v in inputs.items()}
    (out/'input_hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(result,indent=2))
