"""Actual intrinsic wall connection images of the finite two-arm trace graph.

The independent child coefficient vector alone omits the active affine
mechanical-connection image when geometry changes.  This binder exposes
that image directly on the twenty wall components and their joint jets.
It neither projects the bulk profile nor chooses fermion/scalar states.
"""
from __future__ import annotations
import numpy as np
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL
from .muon_birth_finite_normal_trace_graph import affine_connection_profile_two_jet
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet


def finite_wall_connection_two_jet(raw_pair, reference_pair, representation, *, second_derivatives=True):
    """Apply the full graph to value/time/radial wall one-forms.

    Axes: (arm, profile=[value,tau,rho],field=[At,Ar,A1,A2,A3],internal4).
    tau/rho are material-coordinate derivatives; At_ref is used once by
    the intrinsic temporal trace.  All geometric/internal joint first and
    second derivatives are retained in the raw incoming+child coordinates.
    The spin coframe/physical clock remains the owned induced metric, not
    an extra gauge or scalar density.  This is an exact intrinsic wall
    restriction of the represented graph, not a replacement bulk basis.
    """
    raw, ref = np.asarray(raw_pair, float), np.asarray(reference_pair, float)
    n = len(representation['gauge_labels']); nr = 108+2*n; dim = 2*nr
    if raw.shape != (2, nr) or ref.shape != raw.shape or not np.isfinite(raw).all() or not np.isfinite(ref).all():
        raise ValueError('finite full two-arm coefficient/reference pair required')
    profile = affine_connection_profile_two_jet(raw, np.array([WALL]))
    anchor = affine_connection_profile_two_jet(ref, np.array([WALL]))
    value = np.zeros((2, 3, 5, 4)); first = np.zeros(value.shape+(dim,))
    second = np.zeros(value.shape+(dim, dim)) if second_derivatives else None
    geometry_indices = np.r_[np.arange(100), nr+np.arange(100)]
    maps = (representation['wall_trace_map'], representation['wall_trace_map'],
            representation['wall_radial_derivative_map'])
    for arm in range(2):
        rows = profile['applications'][arm]['rows'][0]
        geo = arm*nr+np.arange(100)
        for k, (name, trace) in enumerate(zip(('connection_lambda', 'lambda_tau', 'lambda_rho'), maps)):
            start = 100+n if k == 1 else 100
            value[arm, k] = np.einsum('fcj,j->fc', trace, raw[arm, start:start+n])
            first[arm, k, :, :, arm*nr+np.arange(start, start+n)] = np.moveaxis(trace, -1, 0)
            j = rows[name]; body = j.value-1 if k == 0 else j.value
            value[arm, k, 2:] += body*M
            first[arm, k, 2:, :, geo] += j.gradient[:, None, None]*M
            if second_derivatives:
                block = j.hessian[:, :, None, None]*M
                for i, g in enumerate(geo):
                    second[arm, k, 2:, :, g, geo] += block[i]
            if arm == 1:
                value[arm, k, 2:] += (profile['value'][0, k]-anchor['value'][0, k])*M
                first[arm, k, 2:, :, geometry_indices] += profile['first'][0, k, :, None, None]*M
                if second_derivatives:
                    for i, g in enumerate(geometry_indices):
                        second[arm, k, 2:, :, g, geometry_indices] += profile['second'][0, k, i, :, None, None]*M
    weights = [intrinsic_m4_weight_jet(12, x[:37], x[37:74], x[74:98],
        source_value=x[98], source_rate=x[99]) for x in raw]
    return dict(value=value, first=first, second=second, intrinsic_geometry=weights,
        child_affine_profile_increment=profile['value']-anchor['value'],
        child_increment_not_omitted=True, bulk_profile_projected=False,
        scope='exact twenty-component intrinsic wall restriction of the finite numerical two-arm graph',
        coordinate_convention='material At_ref/Ar_ref; coordinate-time tau derivatives; no second wall advection',
        physical_stationary_state_or_formation_selected=False)


def materialize_finite_wall_fields(endpoint_application, reference_application, output, *, repository=None):
    """Consume pinned solved trial coefficients and export their actual wall images."""
    from pathlib import Path
    from hashlib import sha256
    import json
    from .muon_parent_gauge_geometry_correction import ROOT
    from .muon_birth_attached_phase import load_attached_endpoint
    from .muon_birth_phase_continuation import _compressed_npz
    root = ROOT if repository is None else Path(repository)
    endpoint = Path(endpoint_application); endpoint = endpoint if endpoint.is_absolute() else root/endpoint
    out = Path(output)
    if out.exists():raise FileExistsError('preserve prior field applications')
    rb = (endpoint/'result.json').read_bytes(); receipt = json.loads(rb)
    if receipt['scope'] != 'EVALUATED_FINITE_ANCHORED_TRIAL_GEOMETRIC_NORMAL_TEMPORAL_TRACE_ENDPOINT_CORRECTION':
        raise ValueError('consume the exact finite trial endpoint application')
    hashes = dict(receipt['input_hashes'])
    for path, digest in hashes.items():
        if sha256((root/path).read_bytes()).hexdigest() != digest:raise ValueError('action changed: '+path)
    hashes['src/bhsm/interface/muon_birth_finite_wall_fields.py'] = sha256(Path(__file__).read_bytes()).hexdigest()
    nb = (endpoint/'application.npz').read_bytes()
    if sha256(nb).hexdigest() != receipt['numerical_sha256']:raise ValueError('trial coefficients changed')
    initial = load_attached_endpoint(reference_application, side='incoming', repository=root)
    if initial['receipt_sha256'] != receipt['consumed_receipt_sha256']:
        raise ValueError('preserve the exact reference frame and basis')
    with np.load(endpoint/'application.npz', allow_pickle=False) as saved:
        raw, reference = saved['updated_raw_pair'].copy(), saved['reference_raw_pair'].copy()
    a = finite_wall_connection_two_jet(raw, reference, initial['representation'])
    names = ('R4', 'induced_lapse', 'wall', 'wall_rate', 'Cstar', 'U', 'wT', 'wS', 'wV')
    arrays = dict(raw_pair=raw, reference_raw_pair=reference, wall_connection=a['value'],
        wall_connection_first=a['first'], wall_connection_second=a['second'],
        child_affine_profile_increment=a['child_affine_profile_increment'],
        geometry_values=np.array([[w[k].value for k in names] for w in a['intrinsic_geometry']]),
        geometry_first=np.array([[w[k].gradient for k in names] for w in a['intrinsic_geometry']]),
        geometry_second=np.array([[w[k].hessian for k in names] for w in a['intrinsic_geometry']]))
    out.mkdir(parents=True); _compressed_npz(out/'application.npz', arrays)
    md = dict(scope='EVALUATED_EXACT_INTRINSIC_WALL_FIELDS_ON_SOLVED_FINITE_TRIAL_GRAPH',
        endpoint_receipt_sha256=sha256(rb).hexdigest(), endpoint_numeric_sha256=sha256(nb).hexdigest(),
        input_hashes=hashes, numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        value_shape=list(a['value'].shape), first_shape=list(a['first'].shape), second_shape=list(a['second'].shape),
        connection_order=['value', 'material_tau', 'material_rho'], geometry_order=list(names),
        full_wall_connection_jump_norm=float(np.linalg.norm(a['value'][1, 0]-a['value'][0, 0])),
        spatial_wall_connection_jump_norm=float(np.linalg.norm(a['value'][1, 0, 2:]-a['value'][0, 0, 2:])),
        child_affine_profile_increment=a['child_affine_profile_increment'].tolist(),
        material_At_reference_advection_count=1, bulk_profile_projected=False,
        physical_stationary_birth_or_formation_selected=False, physical_native_heat_closed=False,
        physical_Pauli_value=False, coordinate_convention=a['coordinate_convention'],
        error_scope='binary64 same-action coefficient/implicit-chart derivatives; no continuum or physical-state certificate')
    if hashes != {p:sha256((root/p).read_bytes()).hexdigest() for p in hashes}:raise RuntimeError('action changed during evaluation')
    (out/'result.json').write_text(json.dumps(md, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    return md


if __name__ == '__main__':
    import argparse,json
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--endpoint-application', type=Path, required=True)
    p.add_argument('--reference-application', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args=p.parse_args()
    print(json.dumps(materialize_finite_wall_fields(args.endpoint_application, args.reference_application, args.output), sort_keys=True))
