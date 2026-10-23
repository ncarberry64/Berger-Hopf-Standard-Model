#!/usr/bin/env python
"""Apply the common full-field action to both corrected E1 endpoints."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.muon_pointwise_full_field_action import (
    pointwise_full_field_action, pointwise_wall_gauge_conormal,
)
from bhsm.interface.muon_parent_gauge_geometry_correction import (
    correction_representation, _deterministic_npz,
)

DEFAULT = 'artifacts/muon_parent_gauge_geometry_correction_20261010/two_arm_assigned_run_1'


def evaluate(source, output):
    source, output = Path(source), Path(output)
    if not source.is_absolute(): source = ROOT/source
    if not output.is_absolute(): output = ROOT/output
    if output.exists(): raise FileExistsError('preserve prior evidence; choose a new output')
    receipt_raw = (source/'result.json').read_bytes()
    receipt = json.loads(receipt_raw)
    archive = source/'application.npz'
    if sha256(archive.read_bytes()).hexdigest() != receipt['numerical_sha256']:
        raise ValueError('corrected two-arm input hash mismatch')
    with np.load(archive, allow_pickle=False) as a:
        states, H, Ht = a['updated_states'], a['H_real'], a['H_rate']
    rep = correction_representation(radial_points=48, radial_order=2, cap_points=48,
                                    include_wall_lift=True, include_scalar_mean=True)
    inputs = dict(receipt['input_hashes'])
    paths = (
        'src/bhsm/interface/muon_pointwise_full_field_action.py',
        'src/bhsm/interface/muon_parent_mean_causal_action.py',
        'src/bhsm/interface/muon_parent_maxwell_full_weak.py',
        'src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',
        'scripts/evaluate_muon_pointwise_full_field_action.py',
    )
    inputs.update({p: sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
    for p, h in inputs.items():
        if sha256((ROOT/p).read_bytes()).hexdigest() != h:
            raise ValueError(f'consumed input changed: {p}')
    raw = np.zeros((2, 228))
    raw[:, :98] = states
    raw[:, 220:224], raw[:, 224:228] = H, Ht
    # These are the zero independent-gauge initialization coefficients
    # recorded by this specific input producer. Their Euler rows are kept.
    applications = [pointwise_full_field_action(x, rep,
        nu_squared_action=receipt['action_parameters']['nu_squared_action'],
        surface_gamma=receipt['action_parameters']['surface_gamma']) for x in raw]
    faces = [pointwise_wall_gauge_conormal(x, rep) for x in raw]
    arrays = dict(raw_endpoint_coefficients=raw)
    for key in ('raw_gradient', 'raw_hessian', 'gradient', 'hessian',
                'surface_gradient_per_gamma', 'surface_hessian_per_gamma'):
        arrays[key] = np.array([a[key] for a in applications])
    arrays['master_coordinate_lift'] = applications[0]['coordinates']['lift']
    arrays['wall_radial_action_covector'] = np.array([f['radial_action_covector'] for f in faces])
    arrays['wall_geometry_conormal_derivative'] = np.array([f['geometry_derivative'] for f in faces])
    rows = []
    for side, a, f in zip(('incoming23', 'outgoing24'), applications, faces):
        g, h = a['raw_gradient'], a['raw_hessian']
        rows.append(dict(side=side, common_event_time=0., action_value=a['value'],
            multiplier_constraint_norm=float(np.linalg.norm(g[74:98])),
            At_Gauss_value_cotangent_norm=float(np.linalg.norm(a['constraint_rows'][24:])),
            gauge_value_cotangent_norm=float(np.linalg.norm(g[100:160])),
            gauge_canonical_cotangent_norm=float(np.linalg.norm(g[160:220])),
            H_value_cotangent=g[220:224].tolist(), H_canonical_cotangent=g[224:228].tolist(),
            material_normal_value_cotangent=float(g[98]), material_normal_canonical_cotangent=float(g[99]),
            geometry_gauge_mixed_norm=float(np.linalg.norm(h[:100, 100:220])),
            geometry_H_mixed_norm=float(np.linalg.norm(h[:100, 220:228])),
            gauge_H_mixed_norm=float(np.linalg.norm(h[100:220, 220:228])),
            wall_radial_conormal_norm=float(np.linalg.norm(f['radial_action_covector'])),
            surface_value_per_gamma=a['surface_value_per_gamma'],
            hessian_symmetry_max=float(np.max(abs(h-h.T)))))
    if inputs != {p:sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}:
        raise RuntimeError('an owner changed during endpoint application')
    output.mkdir(parents=True)
    _deterministic_npz(output/'application.npz', arrays)
    result = dict(classification='EVALUATED_TWO_ARM_POINTWISE_FULL_FIELD_ACTION_APPLICATION',
        action='cap EH/GHY/carrier minus its already counted Maxwell reference, independent full5 Maxwell, material intrinsic Higgs; one shared per-gamma membrane',
        raw_order='q37,v37,m24,normal,normal_rate,gauge60,gauge_rate60,Hreal4,Hrate4',
        master_order='x90,v90,y36; all multiplier24 and At12 Gauss rows retained',
        endpoint_applications=rows, action_parameters=receipt['action_parameters'],
        action_normalization=applications[0]['action_normalization'],
        prescribed_initial_independent_gauge='recorded zero initializer; active first/second field derivatives retained',
        endpoint_geometry_scope='corrected assigned56 C/E/trace/canonical rows, not full interacting stationary base',
        temporal_normal_is_material_wall_normal=False,
        physical_unit_or_cutoff_selected=False,
        native_Pauli_or_complete_observable=False,
        event_drive_defined_equal_to_resistance=False,
        acceleration_consumer='D_(v,y)[acceleration,ydot]=[L_x-L_vx*v,-L_yx*v] on the same action/gauge/domain; full gauge quotient and paired boundary rows still apply',
        exact_missing_application='coupled primal Euler continuation and paired event/boundary rows at this coefficient vector; this producer does not set acceleration or multiplier motion to zero',
        input_hashes=inputs, incoming_receipt_sha256=sha256(receipt_raw).hexdigest(),
        incoming_application_sha256=receipt['numerical_sha256'],
        numerical_sha256=sha256((output/'application.npz').read_bytes()).hexdigest(),
        error_scope='binary64 weak-action derivatives at48 cap/radial quadrature points and homogeneous angular restriction; no truncation, physical base, mode, native or anomaly enclosure')
    (output/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',
                                   encoding='utf8',newline='\n')
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',default=DEFAULT)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    print(json.dumps(evaluate(a.source,a.output),sort_keys=True,allow_nan=False))
