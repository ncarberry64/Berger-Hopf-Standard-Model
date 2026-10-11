"""Executed magnetic first-jet source Hessian on its reached causal fields.

The causal magnetic turn-on and local curvature normalization are retained.
Only the three inserted Cartesian axes are active. Their bare source
Hessian is an integrated boundary form; it is not the bilocal virtual
photon propagator consumed by an open lepton loop.
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
from .muon_electromagnetic_soft_magnetic_source import magnetic_turn_on_profile


def executed_magnetic_photon_quadratic_action(directory,*,repository):
    """Apply the full Maxwell/Higgs quadratic action on its solved fields.

    Scalar forms already have the relative factor eight.  Multiplying
    by MAXWELL_TO_CAP once therefore gives the inherited scalar1/V^2.
    The full canonical temporal contact is retained separately.  The
    source action is not replaced by an angular density or spectral shift.
    """
    root=Path(repository);folder=Path(directory);folder=folder if folder.is_absolute() else root/folder
    receipt=json.loads((folder/'result.json').read_text(encoding='utf8'))
    allowed=('EVALUATED_HIGGS_ALIGNED_LOCAL_MAGNETIC_JET_FULL488_RESPONSE',
             'EVALUATED_COMMON_BIRTH_LOCAL_MAGNETIC_JET_FULL488_CONTINUATION')
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
    active=receipt['active_source_indices'];inactive=receipt['inactive_source_indices']
    if active!=[0,1,2] or inactive!=[3,4,5,6,7]:raise ValueError('literal three-axis magnetic support required')
    for a in (phase['state'],velocity['velocity'],contacts['A_tau'],source['Q'],source['Qdot']):
        if np.any(a[...,inactive]):raise ValueError('padded magnetic columns must be construction-derived exact zero')
    q=[];qs=[]
    for j,t in enumerate(times):
        if receipt['source_temporal_profile']=='constant_magnetic_trace_inherited_from_incoming_birth':
            if receipt['side']!='outgoing' or not receipt['birth_source_matching']['actual_source_initial_state_supplied_from_incoming_birth']:
                raise ValueError('outgoing plateau requires actual incoming canonical birth data')
            p,pt=1.,0.
        elif receipt['source_temporal_profile']=='smooth_retarded_turn_on_then_constant_magnetic_trace':
            p,pt,_=magnetic_turn_on_profile(t,receipt['turn_on_duration'])
        else:raise ValueError('owned chronological magnetic profile required')
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
        active_source_indices=active,inactive_source_indices=inactive,
        inactive_source_provenance=receipt['inactive_source_reason'],
        input_hashes=hashes,action_parameters=receipt['action_parameters'],
        side=receipt['side'],coordinate_time_interval=[float(source['coordinate_times'][0]),float(source['coordinate_times'][-1])],
        normalization='complete unreduced quadratic action times1/[8*(2pi²)^2] once; intrinsic relative8 already included',
        source_Higgs_aligned_electromagnetic=True,source_mode_or_soft_transfer_selected=False,physical_free_wall_domain_certified=False,
        error_scope='executed retarded magnetic ramp/plateau source and radial action and full canonical contacts; finite Simpson/ODE/interpolation arithmetic, no physical current, continuum or Pauli bound')


# The exact stored inverse/return identity is shared without modification.
from .muon_causal_source_photon_action import stable_native_photon_return


def stable_magnetic_source_return(bare,native,*,precision_bits=192):
    """Apply only the exactly inserted three-axis source support.

    Five absent input axes are construction zeros. They are neither
    physical photon null modes nor coordinates to pseudoinvert. The
    exact inclusion E selects their proved complementary zero columns.
    """
    A=np.asarray(bare);R=np.asarray(native)
    if A.shape!=(8,8) or R.shape!=(8,8) or not np.isfinite(A).all() or not np.isfinite(R).all():
        raise ValueError('same eight-column padded source forms required')
    if np.any(A[3:]) or np.any(A[:,3:]) or np.any(R[3:]) or np.any(R[:,3:]):
        raise ValueError('three-axis reduction requires exact absent-axis provenance in both forms')
    result=stable_native_photon_return(A[:3,:3],R[:3,:3],precision_bits=precision_bits)
    result.update(active_source_indices=[0,1,2],
        absent_axis_provenance='only B1,B2,B3 were inserted; E is the exact first-three-coordinate inclusion',
        consumer='boundary-source return on inserted magnetic tests; bilocal loop photon action remains separate',
        eight_dimensional_inverse_claimed=False)
    return result
