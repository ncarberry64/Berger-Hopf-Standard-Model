"""Executed moving-Higgs-frame electromagnetic source Hessian.

The declared compact temporal source and finite radial restriction are
kept explicit.  They do not select a physical soft momentum.  A source
return matrix is an operator on the eight formal covectors; it selects
neither a fermionic covariance nor an external spinor.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.integrate import simpson
from flint import arb,arb_mat,acb,acb_mat,ctx
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_parent_retarded_hypercharge import compact_trace_pulse


def executed_electromagnetic_photon_quadratic_action(directory,*,repository):
    """Apply the full Maxwell/Higgs quadratic action on its solved fields.

    Scalar forms already have the relative factor eight.  Multiplying
    by MAXWELL_TO_CAP once therefore gives the inherited scalar1/V^2.
    The full canonical temporal contact is retained separately.  The
    source action is not replaced by an angular density or spectral shift.
    """
    root=Path(repository);folder=Path(directory);folder=folder if folder.is_absolute() else root/folder
    receipt=json.loads((folder/'result.json').read_text(encoding='utf8'))
    allowed=('EVALUATED_HIGGS_ALIGNED_ELECTROMAGNETIC_FULL488_SAME_ACTION_RESPONSE',)
    if receipt['classification'] not in allowed:raise ValueError('executed complete same-background first response required')
    hashes=dict(receipt['input_hashes']);arrays={}
    for name,digest in hashes.items():
        if sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('consumed action owner changed: '+name)
    for name in ('primal_and_source.npz','phase.npz','velocity.npz','contacts.npz','operators.npz'):
        data=(folder/name).read_bytes();info=receipt['array_archives'][name]
        if len(data)!=info['bytes'] or sha256(data).hexdigest()!=info['sha256']:
            raise ValueError('executed first response changed: '+name)
        hashes[(folder/name).relative_to(root).as_posix()]=info['sha256']
        with np.load(folder/name,allow_pickle=False) as f:arrays[name]={k:f[k] for k in f.files}
    hashes[(folder/'result.json').relative_to(root).as_posix()]=sha256((folder/'result.json').read_bytes()).hexdigest()
    source=arrays['primal_and_source.npz'];phase=arrays['phase.npz'];velocity=arrays['velocity.npz'];contacts=arrays['contacts.npz'];operators=arrays['operators.npz']
    times=phase['times']
    if not all(np.array_equal(times,a['times']) for a in (velocity,contacts)):
        raise ValueError('same chronological first-response grid required')
    forms=[CubicSpline(source['times'],operators['raw_'+name]) for name in ('M','B','K')]
    scalar=[CubicSpline(source['times'],operators['scalar_'+name]) for name in ('M','B','K')]
    if np.any(operators['raw_M'][:,:,:80]) or np.any(operators['raw_B'][:,:,:80]):
        raise ValueError('At-rate placeholder allowed only for action-derived nondynamical coordinates')
    q=[];qs=[]
    for j,t in enumerate(times):
        p,pt,_=compact_trace_pulse(t,receipt['source_pulse_duration'])
        z=np.r_[contacts['A_tau'][j],phase['state'][j,:400],p*np.eye(8)]
        zd=np.r_[np.zeros((80,8)),velocity['velocity'][j],pt*np.eye(8)]
        def apply(values):
            M,B,K=[f(t) for f in values]
            return zd.T@M@zd+z.T@B@zd+zd.T@B.T@z+z.T@K@z
        q.append(apply(forms));qs.append(apply(scalar))
    if hashes!={name:sha256((root/name).read_bytes()).hexdigest() for name in hashes}:
        raise RuntimeError('consumed source or action changed during application')
    raw=simpson(np.array(q),x=times,axis=0)
    scalar_pair=simpson(np.array(qs),x=times,axis=0)
    inherited=contacts['action_temporal_endpoint']-contacts['action_boundary_pairing']
    discrepancy=float(np.linalg.norm(raw-inherited))
    unrounded=MAXWELL_TO_CAP*raw;symmetric=(unrounded+unrounded.T)/2
    return dict(source_quadratic_action=symmetric,raw_source_quadratic_action=raw,
        scalar_source_quadratic_action=MAXWELL_TO_CAP*scalar_pair,
        Maxwell_source_quadratic_action=MAXWELL_TO_CAP*(raw-scalar_pair),
        canonical_temporal_endpoint=MAXWELL_TO_CAP*contacts['action_temporal_endpoint'],
        source_conormal_work=MAXWELL_TO_CAP*contacts['wall_trace_reaction_pairing'],
        full_raw_vs_reduced_action_absolute_difference=discrepancy,
        full_raw_vs_reduced_action_relative_difference=discrepancy/(1+np.linalg.norm(raw)),
        source_action_symmetry_rounding_norm=float(np.linalg.norm(symmetric-unrounded)),
        source_quadratic_eigenvalues=np.linalg.eigvalsh(symmetric),
        input_hashes=hashes,action_parameters=receipt['action_parameters'],
        side=receipt['side'],coordinate_time_interval=[float(source['coordinate_times'][0]),float(source['coordinate_times'][-1])],
        normalization='complete unreduced quadratic action times1/[8*(2pi²)^2] once; intrinsic relative8 already included',
        source_Higgs_aligned_electromagnetic=True,source_mode_or_soft_transfer_selected=False,physical_free_wall_domain_certified=False,
        error_scope='executed compact-source/radial action and full canonical contacts; finite Simpson/ODE/interpolation arithmetic, no physical current, continuum or Pauli bound')


# The exact stored inverse/return identity is shared without modification.
from .muon_causal_source_photon_action import stable_native_photon_return
