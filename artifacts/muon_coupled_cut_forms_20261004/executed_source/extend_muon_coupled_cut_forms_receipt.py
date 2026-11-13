"""Small-block/complement delivery from saved cut actions; no repeated solve."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def save(p,j):
    p.write_text(json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run(source,out,root):
    if out.exists():raise FileExistsError('new output required')
    out.mkdir(parents=True)
    a=read(source/'coupled_cut_source_actions.npz');low=read(source/'lower_order_cut_blocks.npz')
    r=json.loads((source/'result.json').read_text());d=r['frame']['rank']
    K=a['local_cut_K_Wp_timejet'];J=a['complement_jet_to_Wp'];N=J[:2*d,:2*d]
    Kchi=J.conj().T@K@J
    Mchi=N.conj().T@a['local_cut_M_Wp']@N
    Ms_chi=N.conj().T@a['local_cut_Cauchy_Wp']@N
    G=a['source_Haar_Gram'];S=a['independent_source_map'];c=a['source_coordinates']
    frame_projection=S@S.conj().T@G
    frame_residual=float(np.linalg.norm(G@frame_projection-G))
    gram_scope='actual retained source quotient, not a physical muon state or a complete exterior trial space'
    b=r['bulk_projection']['B'];bt=r['bulk_projection']['B_tau']
    # Material traces of this same full field; no endpoint-evaluation
    # replacement for the normalized wall projection.
    norm=json.loads((root/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/full_normalization.json').read_text())
    from flint import arb
    geometry=read(root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    wallu=np.sin(geometry['rho'][-1]/2)/np.sqrt(float(arb(norm['I_rad']['arb']).mid()))
    material={};direct_energy=0.;direct_mass=0.;raw_reconstruction=0.;weighted_omission=0.
    for n in (1,3):
        # W_n/u provides the very same angular/carrier section, not a
        # new wall column selected by its spectrum or dimension.
        phi=a[f'W_n{n}'][0]/a['radial_u'][0]
        material[f'W_trace_n{n}']=wallu*phi
        material[f'chi_trace_n{n}']=-b*wallu*phi
        material[f'total_trace_n{n}']=b*material[f'W_trace_n{n}']+material[f'chi_trace_n{n}']
        norm2=lambda f:np.sum(abs(f.reshape(len(a['points']),-1))**2,axis=1)
        vw=a['radial_weights']*a['volume_density']
        direct_energy+=float(vw@norm2(a[f'Dp_n{n}']))
        direct_mass+=float(vw@norm2(a[f'p_n{n}']))
        raw_reconstruction+=float(vw@norm2(
            a[f'Dchi_n{n}']+b*a[f'DW_n{n}']+bt*a[f'DtauW_n{n}']-a[f'Dp_n{n}']))
        weighted_omission+=float(vw@norm2(bt*a[f'DtauW_n{n}']))
    rhs_pair=np.vdot(c,a['rhs_K'][d:2*d]).real
    blocks=dict(local_cut_K_Wchi_timejet=Kchi,local_cut_M_Wchi=Mchi,
                local_cut_Cauchy_Wchi=Ms_chi,
                K_WW=Kchi[:d,:d],K_Wchi=Kchi[:d,d:2*d],K_chichi=Kchi[d:2*d,d:2*d],
                source_reconstruction_map=frame_projection,**material)
    np.savez_compressed(out/'coupled_complement_blocks.npz',**blocks)
    comparison={}
    for name,left,right in [('K_WW',K[:d,:d],low['local_cut_K_Wp_timejet'][:d,:d]),
        ('K_Wp',K[:d,d:2*d],low['local_cut_K_Wp_timejet'][:d,d:2*d]),
        ('K_pp',K[d:2*d,d:2*d],low['local_cut_K_Wp_timejet'][d:2*d,d:2*d])]:
        comparison[name]=dict(absolute_difference=float(np.linalg.norm(left-right)),
            relative_difference=float(np.linalg.norm(left-right)/np.linalg.norm(left)),certified_bound=False)
    result=dict(classification='new cut diagonal, interface and moving connected-complement actions',
        scope=gram_scope,source_column=r['source_column'],
        source_local_Dirac_energy_per_tau=r['source_local_Dirac_energy_per_tau'],
        direct_full_output_energy_per_tau=direct_energy,
        direct_energy_vs_weak_output_difference=float(abs(direct_energy-rhs_pair)),
        direct_full_output_mass_per_tau=direct_mass,
        direct_mass_vs_reused_certificate_difference=float(abs(direct_mass-r['source_bulk_mass_per_tau'])),
        source_energy_4_8_point_difference=float(r['source_local_Dirac_energy_per_tau']-
            np.vdot(c,low['rhs_K'][d:2*d]).real),
        block_quadrature_comparison=comparison,
        new_K_chichi_norm=float(np.linalg.norm(blocks['K_chichi'])),
        new_K_Wchi_norm=float(np.linalg.norm(blocks['K_Wchi'])),
        bulk_M_Wchi_offdiagonal_norm=float(np.linalg.norm(Mchi[:d,d:2*d])),
        temporal_Cauchy_Wchi_offdiagonal_norm=float(np.linalg.norm(Ms_chi[:d,d:2*d])),
        actual_source_quotient_reconstruction_residual=frame_residual,
        material_complement_trace_norm=float(np.sqrt(sum(np.linalg.norm(material[f'chi_trace_n{n}'])**2 for n in (1,3)))),
        total_material_trace_residual=float(np.sqrt(sum(np.linalg.norm(material[f'total_trace_n{n}'])**2 for n in (1,3)))),
        raw_large_action_sum_error_weighted=float(np.sqrt(raw_reconstruction)),
        omission_of_B_tau_action_weighted_norm=float(np.sqrt(weighted_omission)),
        physical_source_applied_using='J coefficients cancelled first, then known Dp; not subtraction of large complement quadratic forms',
        solve_attempt=json.loads((source/'solve_attempt.json').read_text()),
        exact_frozen_local=json.loads((source/'frozen_local.json').read_text()),
        continuum_or_full_exterior_error=None,physical_a_mu=None,physical_g_mu=None,
        execution=dict(new_small_block_contractions=True,new_old_endpoint_extractions=0,
                       full_cap_form_replays=0,exterior_solutions=0,heat_evaluations=0))
    save(out/'result.json',result)
    inputs={p.name:dict(path=str(p),sha256=sha(p)) for p in
        (source/'coupled_cut_source_actions.npz',source/'lower_order_cut_blocks.npz',source/'result.json',
         source/'solve_attempt.json',Path(__file__),root/'src/bhsm/interface/muon_coupled_cut_forms.py')}
    save(out/'input_hashes.json',inputs)
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ('source_local_Dirac_energy_per_tau',
        'new_K_chichi_norm','source_energy_4_8_point_difference','bulk_M_Wchi_offdiagonal_norm',
        'temporal_Cauchy_Wchi_offdiagonal_norm','raw_large_action_sum_error_weighted',
        'omission_of_B_tau_action_weighted_norm')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    run(a.source.resolve(),a.output.resolve(),a.repository.resolve())
