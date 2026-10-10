"""Checks on the new quotient and weak coefficients, using evaluated caches."""
from functools import lru_cache
from pathlib import Path
import numpy as np
try:
    import muon_source_weak_extension as impl
except ModuleNotFoundError:
    from bhsm.interface import muon_source_weak_extension as impl

ROOT=Path(__file__).resolve().parent.parent
if not (ROOT/'artifacts').is_dir():
    import json
    ROOT=Path(json.loads((Path(__file__).parent/'input_refs.json').read_text())['standalone_repository'])


def load(path):
    with np.load(path, allow_pickle=False) as z:
        return {k:np.array(z[k]) for k in z.files}


@lru_cache(None)
def data():
    a=ROOT/'artifacts'
    d=load(a/'muon_source_jet_20261002/source_inputs.npz')
    old=load(a/'muon_source_jet_20261002/replay_reference/evaluated_child_forms.npz')
    source=load(a/'muon_source_jet_20261002/replay_reference/local_source_actions.npz')
    f=impl.independent_source_frame(d)
    forms=impl.transport_cached_forms(f,old)
    return d,old,source,f,forms


def test_actual_function_quotient_and_positive_independent_pairing():
    d,old,s,f,forms=data()
    E=d['mixed__external_n0_test_frame_E0']
    Phi=np.concatenate((np.broadcast_to(E,(48,20,4)),old['generated_profile_node_values']),axis=2)
    C=f['coefficient_map'];J=f['right_inverse']
    assert np.linalg.norm(f['independent_profile_nodes']@C-Phi)<2e-14
    assert np.linalg.norm(C@J-np.eye(16))<5e-15
    assert np.linalg.eigvalsh(forms['M']).min()>7e-6
    assert np.linalg.cond(forms['M'])<21
    # The exact rank follows from the inherited angular representation.
    # This check verifies that its 20 redundant columns are annihilated.
    assert abs(np.trace(np.eye(36)-J@C).real-20)<2e-14
    assert np.linalg.norm(old['child_M_test_Gram']@(np.eye(36)-J@C))<2e-18
    assert np.linalg.norm(C.conj().T@forms['M']@C-old['child_M_test_Gram'])<2e-18


def test_all_cached_forms_and_full_source_action_descend_to_same_quotient():
    d,old,s,f,forms=data()
    C=f['coefficient_map']
    for name,key in [('q_A','child_q_A_integrated'),('q_AB','child_q_AB_integrated'),
                     ('q_AB_connected','child_q_AB_connected_complement')]:
        restored=np.einsum('ki,...kl,lj->...ij',C.conj(),forms[name],C)
        assert np.linalg.norm(restored-old[key])<2e-17
    actions=impl.transport_cached_source_actions(f,s,d)
    assert np.linalg.norm(actions[:,:,:,:4]-old['Xi_actions_E0_nodes'])<1e-14
    J=f['right_inverse'][4:,4:]
    old_mid=np.concatenate([old['Xi_actions_generated_midpoint_profiles'][:,:,b]
                            for b in range(8)],axis=-1)
    mid=d['mixed__physical_volume_source_factor'][:,None,None,None]**2*np.einsum(
        'aoi,ic->aoc',s['Xi_complete'],f['generated_angular_frame'])[None]
    assert np.linalg.norm(old_mid@J-mid)<2e-14
    mask=np.ones(56,bool);mask[s['retained_output_indices']]=False
    assert np.linalg.norm(actions[:,:,mask,4:])>0.1
    # This reuses the saved connected output; it reruns no angular contact.


def test_actual_lorentz_parent_flux_and_weak_principle_boundary():
    a=ROOT/'artifacts'
    p=load(a/'muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    w=load(a/'muon_connection_weight_20261001/replay_reference/attachment_and_weighted_density.npz')
    q=impl.inherited_parent_principal_form(p,w)
    S=q['lorentz_principal_tau_rho_per_kappa1'];e=q['e'];r=q['r'];z=q['shift']
    mask=(e>0)&(r>0)
    det=S[...,0,0]*S[...,1,1]-S[...,0,1]**2
    assert np.max(np.abs((det+e*r)[mask]/(e*r)[mask]))<3e-15
    assert np.all(det[mask]<0)
    # A diagnostic derivative vector, not a proposed parent extension.
    v=np.asarray([.2,-.3,.7])
    flux=q['temporal_radial_flux_map_per_kappa1']@v
    temporal=e*(v[0]-z*v[1]-.5*q['boundary_H']*v[2])
    assert np.allclose(flux[...,0],temporal,rtol=3e-15,atol=1e-14)
    radial=-z*temporal-r*v[1]
    # Bound rounding by the terms before cancellation, not by the small
    # resulting traction.  This is a numerical algebra check only.
    scale=(np.abs(z*temporal)+np.abs(r*v[1])+
           np.sum(np.abs(q['temporal_radial_flux_map_per_kappa1'][...,1,:]*v),axis=-1))
    assert np.all(np.abs(flux[...,1]-radial)<=32*np.finfo(float).eps*scale+1e-30)
    contract=impl.weak_extension_contract()
    assert contract['supplied_value'] is None
    assert contract['parent_extension_evaluated'] is False
    assert contract['cache_endpoint_promoted_to_physical_boundary'] is False
