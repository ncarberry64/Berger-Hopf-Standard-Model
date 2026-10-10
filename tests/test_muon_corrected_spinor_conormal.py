"""New source-dependent cut-form action; no exterior solve assertion."""
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/'artifacts/muon_parent_source_rate_20261003'


def test_corrected_trial_conormal_rate_change_from_independent_source_value():
    H=json.loads((ROOT/'artifacts/muon_exterior_face_source_20261002/replay_reference/result.json').read_text())['frontier_source']['H']
    with np.load(NEW/'conormal_reference/corrected_canonical_trial_conormal.npz') as flux, np.load(NEW/'replay_reference/parent_source_rate_corrected.npz') as new, np.load(ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_metric_dirac_actions.npz') as old, np.load(ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz') as contact:
        columns=new['source_image_probe_columns'];points=new['gauss_rho'];cells=new['gauss_cells']
        with np.load(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz') as g:
            x=(points-g['rho'][cells])/np.diff(g['rho'])[cells]
            r=g['base_radius'][0,cells]*(1-x)+g['base_radius'][0,cells+1]*x
            C=g['C_rho'][0,cells]*(1-x)+g['C_rho'][0,cells+1]*x
            nu=g['proper_lapse'][0,cells]*(1-x)+g['proper_lapse'][0,cells+1]*x
        chi=np.interp(points,contact['rho'],contact['spinor_probe_hat_nodes'])
        f=contact['T_b']*chi/r
        gamma0=np.kron(new['parent_gamma'][0],np.eye(16))
        for n in (1,3):
            old_flux=np.einsum('oi,gAicmk->gAocmk',-1j*gamma0,old[f'D5_on_same_source_image_b_coefficient_n{n}'])
            new_flux=flux[f'canonical_exterior_future_conormal_b_n{n}']
            expected=-(H/2*f/nu)[:,None,None,None,None,None]*contact[f'Xi_A_unit_n{n}'][:,:,columns][None]
            np.testing.assert_allclose(new_flux-old_flux,expected,atol=2e-14,rtol=2e-14)
            np.testing.assert_array_equal(flux[f'canonical_core_past_conormal_b_n{n}'],-new_flux)
        np.testing.assert_allclose(flux['temporal_trace_pairing_density_per_normalized_Haar'],2*np.pi**2*C*r**3,atol=0,rtol=2e-15)
