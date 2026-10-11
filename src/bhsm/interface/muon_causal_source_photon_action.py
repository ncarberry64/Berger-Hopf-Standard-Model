"""Executed source quadratic action and stable induced photon return.

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


def executed_reached_photon_quadratic_action(directory,*,repository):
    """Apply the full Maxwell/Higgs quadratic action on its solved fields.

    Scalar forms already have the relative factor eight.  Multiplying
    by MAXWELL_TO_CAP once therefore gives the inherited scalar1/V^2.
    The full canonical temporal contact is retained separately.  The
    source action is not replaced by an angular density or spectral shift.
    """
    root=Path(repository);folder=Path(directory);folder=folder if folder.is_absolute() else root/folder
    receipt=json.loads((folder/'result.json').read_text(encoding='utf8'))
    allowed=('EVALUATED_FRESH_COUPLED_REACHED_RESPONSE_ON_ACTUAL_ENRICHED_PHASE',
        'EVALUATED_FRESH_COUPLED_REACHED_RESPONSE_ON_ACTUAL_ATTACHED_PHASE')
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
        side=receipt['side'],coordinate_time_interval=receipt['coordinate_time_interval'],
        normalization='complete unreduced quadratic action times1/[8*(2pi²)^2] once; intrinsic relative8 already included',
        source_mode_or_soft_transfer_selected=False,physical_free_wall_domain_certified=False,
        error_scope='executed compact-source/radial action and full canonical contacts; finite Simpson/ODE/interpolation arithmetic, no physical current, continuum or Pauli bound')


def stable_native_photon_return(bare_action,native_form,*,precision_bits=192):
    """Solve A=A0+R and evaluate the exact stable basis return.

    The identity is U-U0=-U0 R U.  A is added inside Acb, so a native
    correction below binary64 spacing is retained.  Current contractions
    are obtained by J^dagger(return)J without choosing J or a CAR state.
    The supplied R must retain its actual subtraction/completion scope.
    """
    if bare_action is None or native_form is None:raise ValueError('executed bare action and native form required')
    B=np.asarray(bare_action,complex);R=np.asarray(native_form,complex)
    if B.ndim!=2 or B.shape[0]!=B.shape[1] or R.shape!=B.shape or not np.isfinite(B).all() or not np.isfinite(R).all():
        raise ValueError('complete finite same-domain square forms required')
    if type(precision_bits) is not int or precision_bits<128:raise ValueError('Acb precision>=128 required')
    previous=ctx.prec
    try:
        ctx.prec=precision_bits
        convert=lambda a:acb_mat([[acb(arb(float(x.real)),arb(float(x.imag))) for x in row] for row in a])
        A0=convert(B);native=convert(R);A=A0+native;I=acb_mat(np.eye(len(B)).tolist())
        U0=A0.solve(I);U=A.solve(I);delta=-U0*native*U
        defect=(U-U0)-delta
        if not all(defect[i,j].contains(0) for i in range(len(B)) for j in range(len(B))):
            raise ArithmeticError('exact stored photon return identity failed')
        up=lambda x:float(np.nextafter(float(x.upper()),np.inf)) if not x.is_zero() else 0.
        lo=lambda x:float(np.nextafter(float(x.lower()),-np.inf)) if not x.is_zero() else 0.
        midpoint=lambda a:np.array([[complex(float(a[i,j].real.mid()),float(a[i,j].imag.mid())) for j in range(a.ncols())] for i in range(a.nrows())])
        lower=lambda a:np.array([[lo(a[i,j]) for j in range(a.ncols())] for i in range(a.nrows())])
        upper=lambda a:np.array([[up(a[i,j]) for j in range(a.ncols())] for i in range(a.nrows())])
        real=arb_mat([[delta[i,j].real for j in range(len(B))] for i in range(len(B))])
        imag=arb_mat([[delta[i,j].imag for j in range(len(B))] for i in range(len(B))])
        residual=A*U-I
        return dict(full_basis_response=midpoint(U),bare_basis_response=midpoint(U0),stable_native_return=midpoint(delta),
            stable_native_return_real_lower=lower(real),stable_native_return_real_upper=upper(real),
            stable_native_return_imag_lower=lower(imag),stable_native_return_imag_upper=upper(imag),
            exact_stored_inverse_residual_upper=max(up(abs(residual[i,j])) for i in range(len(B)) for j in range(len(B))),
            exact_stored_return_identity_defect_upper=max(up(abs(defect[i,j])) for i in range(len(B)) for j in range(len(B))),
            native_form_lost_in_binary64_addition=bool(np.array_equal(B+R,B) and np.any(R)),
            spectral_conditioning_shift_added=False,precision_bits=precision_bits,
            current_covariance_or_physical_Pauli_selected=False,
            error_scope='exact supplied finite stored A0 and R, Acb source inverse and return; formation, physical-domain, overlap and softPauli errors excluded')
    finally:ctx.prec=previous
