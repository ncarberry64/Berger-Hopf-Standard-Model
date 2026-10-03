"""Apply the canonical cut conormal to repaired actual source images.

This is a trial-form conormal, not the stationary exterior N_out(s) value.
No extension, resolvent, boundary load or native heat operator is fabricated.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_bytes((json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())


def run(root,corrected,output):
    if output.exists():raise FileExistsError('fresh output directory required')
    geometry=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz'
    with np.load(corrected) as p:
        gamma0=p['parent_gamma'][0]
        G=np.kron(gamma0,np.eye(16))
        # The Cauchy trace pairing has density C*r^3, while the five-
        # dimensional action density is nu*C*r^3. The factor nu cancels
        # its derivative coefficient i gamma0/nu in the temporal conormal.
        arrays={};checks={}
        for n in (1,3):
            for label in ('b','b_tau'):
                D=p[f'D5_on_same_source_image_{label}_coefficient_n{n}']
                outward=np.einsum('oi,gAicmk->gAocmk',-1j*G,D,optimize=True)
                arrays[f'canonical_exterior_future_conormal_{label}_n{n}']=outward
                arrays[f'canonical_core_past_conormal_{label}_n{n}']=-outward
                checks[f'n{n}_{label}']=dict(norm=float(np.linalg.norm(outward)),
                    opposite_outward_residual=float(np.linalg.norm(outward+(-outward))))
        cells=p['gauss_cells'];points=p['gauss_rho']
        with np.load(geometry) as g:
            x=(points-g['rho'][cells])/np.diff(g['rho'])[cells]
            C=g['C_rho'][0,cells]*(1-x)+g['C_rho'][0,cells+1]*x
            r=g['base_radius'][0,cells]*(1-x)+g['base_radius'][0,cells+1]*x
            arrays['temporal_trace_pairing_density_per_normalized_Haar']=2*np.pi**2*C*r**3
        arrays['gauss_rho']=points;arrays['temporal_clifford_conormal']=-1j*G
        arrays['source_image_probe_columns']=p['source_image_probe_columns']
        unitary_residual=float(np.linalg.norm(G.conj().T@G-np.eye(64)))
    output.mkdir(parents=True)
    np.savez_compressed(output/'corrected_canonical_trial_conormal.npz',**arrays)
    save(output/'result.json',dict(
        classification='evaluated canonical M5 cut trial conormal on corrected SAME source image',
        start_HEAD='c6c4be76609f0f005f2b827a13a16d01f37a5c83',
        equation='Gamma1_tau,can u=epsilon_tau (-i gamma0 D5 u), paired in 2*pi^2 C r^3 d_rho normalized_Haar',
        derivation='Boundary integration of q_can(v,u)=integral nu C r^3 (D5v)^dagger D5u; partial_tau coefficient i gamma0/nu',
        orientations=dict(past_core=-1,future_exterior=1),
        interpretation='same local cut frame; no new reset lift chosen, radial/material conormal is distinct',
        checks=checks,Clifford_trace_map_unitarity_residual=unitary_residual,
        connected_output='full n1+n3, all 64 outputs, 8 source directions, 4 input spin coordinates retained',
        error_scope='binary64 canonical trial actions; inherits repaired finite-array H uncertainty, plus unresolved body/interpolation/trace matching errors. Not native or exterior-response error bound.',
        stationary_exterior_solution=None,N_out_application=None,full_shifted_source_solution=None,
        execution=dict(corrected_source_arrays_reused=True,body_recomputed=False,
            canonical_trial_conormal_applications=4,stationary_exterior_response_applications=0,
            native_heat_evaluations=0,physical_transfer_directions=0),
        physical_a_mu=None,physical_g_mu=None))
    save(output/'input_hashes.json',[dict(path=str(p),sha256=sha(p)) for p in (corrected,geometry,Path(__file__))])
    save(output/'receipt.json',dict(files=[dict(path=p.name,sha256=sha(p)) for p in sorted(output.iterdir())]))
    print(json.dumps(dict(output=str(output),checks=checks,native_heat_evaluations=0,stationary_exterior_response_applications=0)))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--corrected',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.corrected.resolve(),a.output.resolve())
