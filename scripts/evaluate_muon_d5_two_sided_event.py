"""Reproduce the new two-sided rows from immutable executed applications.

This consumes the saved operator/state applications. It never reruns their
radial solves, birth shoots, native calculations or nonlinear value solve.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
from bhsm.interface.muon_d5_two_sided_constraint_rows import assemble_two_sided_rows
from bhsm.interface.retained_response.finite_time_response import write_npz

BASE = ROOT / 'artifacts/muon_d5_two_sided_event_20261019'
CORES = ('SPATIAL_BUNDLE_v2', 'CHILD_SAME_DIRECTION_v1',
         'CHILD_SPATIAL_SOURCE_v1', 'CONSTRAINT_TWOJET_v1',
         'HIGGS_TEMPORAL_v1', 'JOINT_CONNECTION_HIGGS_v1',
         'JOINT_MAP_SOURCE_v1', 'CONSTRAINT_TWOJET_APPEND_v1',
         'PARENT_H_SOURCE_v1', 'PARENT_H_CONSUMER_v1',
         'CHILD_JOINT_SOURCE_v1', 'CHILD_HIGGS_SEAM_v1',
         'TWO_SIDED_ROWS_v1', 'TWO_SIDED_ROWS_v2')


def pin(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_bytes((json.dumps(value, sort_keys=True, indent=2,
                                      allow_nan=False) + '\n').encode())


def load_arrays(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k].copy(order='K') for k in z.files}


def verified_cores():
    """Require exact repository bindings and all frozen application bytes."""
    receipts = {}
    pins = {}
    for name in CORES:
        folder = BASE / 'core' / name
        binding_path = folder / 'canonical_binding.json'
        binding = json.loads(binding_path.read_bytes())
        if binding['application'] != name:
            raise ValueError('application identity changed: ' + name)
        for group in ('input_sha256', 'files_sha256'):
            for rel, expected in binding[group].items():
                p = Path(rel)
                if p.is_absolute() or '..' in p.parts:
                    raise ValueError('binding escaped repository: ' + rel)
                if pin(ROOT / p) != expected:
                    raise ValueError('executed application input changed: ' + rel)
                if rel in pins and pins[rel] != expected:
                    raise ValueError('inconsistent input identity: ' + rel)
                pins[rel] = expected
        pins[binding_path.relative_to(ROOT).as_posix()] = pin(binding_path)
        receipts[name] = json.loads((folder / 'result.json').read_bytes())
    return receipts, pins


def run(output):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError('preserve prior checkpoints: ' + str(output))
    reports, pins = verified_cores()
    core = BASE / 'core'
    arrays, rows = assemble_two_sided_rows(
        load_arrays(core / 'CONSTRAINT_TWOJET_APPEND_v1/application.npz'),
        load_arrays(core / 'JOINT_MAP_SOURCE_v1/application.npz'),
        load_arrays(core / 'HIGGS_TEMPORAL_v1/application.npz'))
    expected = load_arrays(core / 'TWO_SIDED_ROWS_v2/application.npz')
    if arrays.keys() != expected.keys():
        raise ValueError('executed row array identities changed')
    differences = {}
    for key in sorted(arrays):
        if arrays[key].shape != expected[key].shape:
            raise ValueError('executed array axes changed: ' + key)
        differences[key] = float(np.max(abs(arrays[key] - expected[key])))
        if differences[key] > 2e-14:
            raise ValueError('saved row reproduction changed: ' + key)
    output.mkdir(parents=True)
    write_npz(output / 'application.npz', arrays)
    for rel in ('scripts/evaluate_muon_d5_two_sided_event.py',
                'scripts/verify_muon_d5_two_sided_event.py',
                'src/bhsm/interface/muon_d5_two_sided_constraint_rows.py'):
        pins[rel] = pin(ROOT / rel)
    result = dict(
        schema='bhsm.two-sided-event-consumption.v1',
        parent_head='67c113ea5ba2d1558e694a2db02d9e3b245a1e1b',
        input_sha256=pins,
        arrays=dict(sha256=pin(output / 'application.npz'), keys=sorted(arrays)),
        reproduced_rows=rows, saved_row_reproduction_difference=differences,
        executed_applications=reports,
        source_equations=dict(
            child='original inherited D5 and finite birth chart, Xi_prescribed+Bnormal*psi_child+nu_child*Bnormal_rate; source and time derivatives separate',
            parent='L H_Xi = -delta(L) H10, H_Xi(wall)=0; L Z=0, Z(wall)=I; source=H_Xi W+Z W_Xi',
            connection='C_child-O.T C_parent R.T=0; y_child-O.T y_parent=0',
            Higgs='H_child-U_H H_parent=0',
            temporal='D_t U=-A_child,0 U+kappa U A_parent,0 (local E1 jet)',
            seam='J deltaN Gamma + Gamma0 deltaSbar Gamma=0; ordered physical density/normal maps remain ports'),
        remaining_parent_homogeneous_coordinates=3660,
        homogeneous_state_selected=False, homogeneous_variation_selected=False,
        independent_normal_rates_selected=False,
        correspondence_scope='two retained local connection/Higgs map families; right translation, global lift, normal/density maps and physical outer data remain unresolved',
        error_scope='finite original differential and source rows at independent nine probes and six original times; no continuum or physical trace stability bound',
        physical_error_combination='R_part*a+R_h*h and its complete amplitude/profile/state/source variation; unit-column maxima are not errors of a selected physical state',
        physical_event_equation='Gamma0_child-U_R*(Gamma0_parent composed with F_B)=0',
        physical_event_Jacobi='deltaGamma_child-deltaU_R*(Gamma_parent composed with F_B)-U_R*((deltaGamma_parent composed with F_B)+(dGamma_parent composed with F_B)*deltaF_B)=0',
        physical_event_residual=None, physical_outer_residual=None,
        normal_profile_normalization=None, full_formation_residual=None,
        complete_action_Hessian=None, original_physical_norm_residual=None,
        local_native_accounting_changed=False, complete_physical_derivative=False,
        physical_admission=False, physical_guard=2e-10,
        NEXT_OPERAND='consume corrected child bulk/once-only seam and full parent Q/Q_Xi through the actual ordered event normal/density and bundle maps; jointly determine physical outer/profile/formation data and pending multiplier Hessians; use their consumed residual sensitivities to target refinement')
    dump(output / 'result.json', result)
    return dict(result_sha256=pin(output / 'result.json'),
                arrays_sha256=result['arrays']['sha256'],
                saved_row_reproduction_max=max(differences.values()),
                physical_admission=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.output), sort_keys=True, indent=2))
