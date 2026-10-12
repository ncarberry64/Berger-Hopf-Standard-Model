"""The frozen original-wall action's declared complex coefficient extension.

This evaluates the SAME five-node cubic M/B/K used by the literal-wall
Green.  It does not feed complex fields through a real Maxwell builder,
substitute a positive reference square, or identify a connector boundary
graph.  The proper-At coordinate conversion is returned separately.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_profile_preserving_phase_sample import load_profile_preserving_phase
from .muon_continued_action_reality import action_reality_coefficient
from .muon_literal_euclidean_higgs_green import literal_proper_euclidean_forms


def saved_original_wall_coefficient_family(*, repository=ROOT,
        folder='artifacts/muon_literal_euclidean_wall_action_20261011/run_2'):
    """Pin both original n1 action families, orders and interpolation checks."""
    root=Path(repository).resolve();path=Path(folder)
    path=path if path.is_absolute() else root/path
    receipt_bytes=(path/'result.json').read_bytes();receipt=json.loads(receipt_bytes)
    if receipt['classification']!='EVALUATED_LITERAL_CONTINUED_NATURAL_WALL_COUPLED_GAUGE_H_CURRENT':
        raise ValueError('the original full natural-wall action receipt is required')
    refs=dict(receipt['input_hashes'])
    for rel,h in refs.items():
        if sha256((root/rel).read_bytes()).hexdigest()!=h:
            raise ValueError('original action owner changed: '+rel)
    refs[(path/'result.json').relative_to(root).as_posix()]=sha256(receipt_bytes).hexdigest()
    arms={}
    for side in ('incoming','outgoing'):
        name=side+'_original_nodes.npz';p=path/name;raw=p.read_bytes()
        h=sha256(raw).hexdigest()
        if h!=receipt['archives'][name]['sha256']:raise ValueError('original action nodes changed')
        refs[p.relative_to(root).as_posix()]=h
        with np.load(p,allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
        times=np.asarray(a['times'],float);forms=tuple(np.asarray(a[k],complex) for k in ('M','B','K'))
        if (times.shape!=(5,) or np.any(np.diff(times)<=0) or times[0]!=0.
                or any(v.shape!=(5,336,336) or not np.isfinite(v).all() for v in forms)
                or a['E'].shape!=(3,4,4) or a['wall_trace_map'].shape!=(96,336)
                or len(a['central_radial_frame_indices'])!=16
                or a['value_permutation'].shape!=(336,)):
            raise ValueError('the complete original84 x n1harmonic4 coefficient order is required')
        phase_folder=('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'
            if side=='incoming' else 'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        phase=load_profile_preserving_phase(phase_folder,repository=root);refs.update(phase['input_hashes'])
        span=float(phase['receipt']['span'])
        if (span<0)!=(side=='incoming') or abs(span)!=times[-1]:
            raise ValueError('saved action times must be the same chronological numerical phase')
        record=next(r for r in receipt['records'] if r['side']==side)
        arms[side]=dict(arrays=a,polynomials=tuple(CubicSpline(times,v) for v in forms),
            phase=phase,span=span,
            fresh_original_action_interpolation_checks=record['fresh_original_action_interpolation_checks'])
    for name in (__file__,
            Path(__file__).with_name('muon_continued_action_reality.py'),
            Path(__file__).with_name('muon_literal_euclidean_higgs_green.py')):
        p=Path(name);refs[p.relative_to(root).as_posix()]=sha256(p.read_bytes()).hexdigest()
    return dict(repository=root,arms=arms,input_hashes=refs,
        extension='saved five-node cubic original Lorentz M/B/K, anchored real interval piece',
        interpolation_error_is_a_diagnostic_not_an_enclosure=True)


def forms_at_complex_offset(side,anchor,offset=0j,*,family=None,repository=ROOT):
    """Return literal forms at a physical-coordinate anchor plus offset.

    Incoming anchors are in [-L,0], outgoing anchors in [0,L].  A complex
    offset stays on the polynomial piece selected by that REAL anchor.
    ``Lorentz_forms`` retain the original At_L coordinate. ``forms`` use
    At_E=(-i/N)At_L and L_E=-L_L/N exactly once, with an analytic transpose.
    The wall map stays in original coordinates, so a caller must transform
    a proper-At trace with the returned inverse coordinate rotation once.
    """
    if side not in ('incoming','outgoing'):raise ValueError('actual incoming or outgoing arm required')
    if family is None:family=saved_original_wall_coefficient_family(repository=repository)
    t=float(anchor);z=complex(offset)
    if not np.isfinite([t,z.real,z.imag]).all():raise ValueError('finite actual anchor and offset required')
    arm=family['arms'][side];a=arm['arrays'];times=a['times'];span=arm['span']
    u=t+abs(span) if span<0 else t
    tol=16*np.finfo(float).eps*max(abs(span),np.finfo(float).tiny)
    if u < -tol or u > abs(span)+tol:raise ValueError('anchor is outside the retained chronological arm')
    u=min(max(u,0.),abs(span));j=min(max(np.searchsorted(times,u,side='right')-1,0),len(times)-2)
    delta=complex(u)+z-times[j]
    raw=tuple(sum(p.c[k,j]*delta**(3-k) for k in range(4)) for p in arm['polynomials'])
    geo=action_reality_coefficient(arm['phase'],t,z)['geometry'];N=geo['N']
    continued=literal_proper_euclidean_forms(raw,N,64)
    inverse_rotation=1/continued['coordinate_rotation']
    return dict(forms=continued['forms'],Lorentz_forms=raw,N=N,geometry=geo,
        wall_trace_map=a['wall_trace_map'],central_radial_frame_indices=a['central_radial_frame_indices'],
        value_permutation=a['value_permutation'],At_count=64,
        coordinate_rotation=continued['coordinate_rotation'],
        inverse_coordinate_rotation=inverse_rotation,
        proper_Euclidean_wall_trace_map=a['wall_trace_map']*inverse_rotation[None,:],
        anchor_coordinate_time=t,complex_coordinate_offset=z,
        chronological_source_time=u,polynomial_interval_index=int(j),
        source_pins=family['input_hashes'],
        fresh_original_action_interpolation_checks=arm['fresh_original_action_interpolation_checks'],
        complete_original_Gauss_and_frame_rows_retained=True,
        complex_coefficient_parameters_conjugated=False,
        original_Lorentz_At_to_proper_Euclidean_At_count=1,
        restored_connector_or_physical_relative_domain_identified=False,
        extension_error_scope='original fresh real-node interpolation diagnostics; no complex-domain or physical enclosure')
