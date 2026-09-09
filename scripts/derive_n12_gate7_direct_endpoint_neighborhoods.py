"""Materialize trial endpoint domains from paired values and frozen frames."""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_direct_physical_jacobians as df
import certify_n12_gate7_direct_physical_residual as residual
from bhsm.interface import direct_physical_neighborhood as neighborhood

THEORY = ROOT/'theory/n12_gate7_direct_endpoint_neighborhoods.md'
TRIAL_RADII = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE.json'
WORK = ROOT/'artifacts/flagship_integration/.direct_endpoint_neighborhood_work'
ALGORITHM = 'DIRECT_PHYSICAL_HS_FROZEN_AFFINE_TRIAL_ENDPOINT_BOXES_ARB512_V1'


def build_payload():
    previous = ctx.prec
    ctx.prec = 512
    try:
        expected = df.binding()  # Paired value inventory; no DF campaign dependency.
        base, inputs, _, axes = residual.load_foundation()
        if df.values.cert.ENDPOINT != residual.center.ENDPOINT:
            raise RuntimeError('value and frozen foundation endpoint sources differ')
        radii = json.loads(TRIAL_RADII.read_text())['stored_polynomial_adjudication']['witness']['radius']
        if len(radii) != 2:
            raise ValueError('two frozen trial radii required')
        radii = [neighborhood.exact_radius(v) for v in radii]
        x, weights, descriptor, _, _ = df.values.operands()
        with np.load(residual.center.JACOBIAN.with_suffix('.npz'), allow_pickle=False) as data:
            tangents = data['endpoint_physical_tangent_action'].copy()
        if tangents.shape != (371, 98, 73) or not np.isfinite(tangents).all():
            raise RuntimeError('complete finite frozen endpoint trial frames required')
        raw = {}
        sources = dict(expected['files'])
        for path in (Path(__file__), THEORY, TRIAL_RADII, Path(neighborhood.__file__),
                     Path(neighborhood.preserve_ball.__code__.co_filename),
                     residual.foundation.RESULT, Path(residual.__file__)):
            residual.merge(sources, {df.file_key(path): df.values.sha(path)})
        manifest = json.loads((df.values.WORK/'manifest.json').read_text())
        # Bind all paired endpoint leaves used to verify the stored centers.
        for i in range(371):
            for ext in ('json', 'npz'):
                key = df.file_key(df.values.WORK/f'endpoint_{i:03d}.{ext}')
                residual.merge(sources, {key: manifest['files'][key]})
        residual.merge_verified_raw_sources(inputs, raw, sources)
        arrays = {key: [] for key in ('weighted_box', 'raw_box', 'coordinate_displacement_radius')}
        for i in range(371):
            df.values.load_cached('endpoint', i, expected['value_binding'], {})
            center = df.values.hs.weighted_endpoint(x[i], descriptor[i], weights)
            with np.load(df.values.WORK/f'endpoint_{i:03d}.npz', allow_pickle=False) as data:
                stored = df.values.hs.restore_balls(data['weighted_state_mid_q'], data['weighted_state_rad_q'])
            if not all(a.contains(b) for a, b in zip(stored, center, strict=True)):
                raise RuntimeError('paired endpoint does not contain exact weighted center')
            frame = residual.center.cert._frame(tangents[i], residual.center.cert.TRIAL_DESCRIPTOR_SCALE)
            box, coordinate_radii = neighborhood.affine_endpoint_box(center, frame, axes[i], *radii, fixed=i == 0)
            arrays['weighted_box'].append(box)
            arrays['raw_box'].append(neighborhood.unweight_box(box, weights))
            arrays['coordinate_displacement_radius'].append(coordinate_radii)
        encoded = {}
        for key, array in arrays.items():
            encoded[key+'_mid_q'], encoded[key+'_rad_q'] = df.values.hs.rational_balls(np.array(array, dtype=object))
        residual.foundation.coordinate._verified_inputs(dict(inputs=inputs))
        df.values.verify_binding(dict(files=raw))
        record = dict(algorithm=ALGORITHM, precision_bits=512,
            scope='FROZEN_AFFINE_TRIAL_ENDPOINT_DOMAIN_GEOMETRY', endpoints=list(range(371)), shape=[371, 99],
            radii_exact_binary64_rationals=[str(v.fmpq()) for v in radii],
            radii_status='TRIAL_RADII_FROM_OLD_CONDITIONAL_POLYNOMIAL_NOT_RECERTIFIED',
            initial_endpoint_fixed=True, transverse_domain='FULL_COORDINATE_SPACE_SUPERSET',
            axis_normalization_assumed=False, weighted_center_product_rounding_enclosed=True,
            axes_SHA256=base['axes_SHA256'], inputs=inputs, raw_input_SHA256=raw,
            input_hash_convention='SHA256_CRLF_TO_LF_FOR_JSON_MD_PY',
            raw_input_hash_convention='SHA256_EXACT_FILE_BYTES',
            uniform_endpoint_rates_enclosed=False, actual_HS_midpoint_neighborhood_enclosed=False,
            neighborhood_remainder_enclosed=False, intrinsic_constraint_chart_certified=False,
            physical_quotient_identified=False, physical_contraction_proved=False,
            Gate7_closed=False, FULL_BHSM_COMPLETE=False)
        return encoded, record
    finally:
        ctx.prec = previous


def encoded(record):
    return (json.dumps(record, indent=2, sort_keys=True)+'\n').encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--recompute', action='store_true')
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK/'endpoints.npz'
    record_path = WORK/'endpoints.json'
    receipt_path = WORK/'reproduction.json'
    previous = json.loads(record_path.read_text()) if record_path.exists() else None
    if args.recompute and previous is None:
        raise RuntimeError('independent repeat requires previous endpoint domains')
    if previous is not None:
        if previous.get('data_SHA256') != df.values.sha(path) or record_path.read_bytes() != encoded(previous):
            raise RuntimeError('previous endpoint domains changed')
        if not args.recompute:
            raise RuntimeError('endpoint domains exist; use explicit independent repeat')
    if receipt_path.exists():
        receipt_path.replace(WORK/f'reproduction.before_attempt_{time.time_ns()}.json')
    arrays, record = build_payload()
    candidate = WORK/f'endpoints.candidate_{time.time_ns()}.npz'
    np.savez_compressed(candidate, **arrays)
    record['data_SHA256'] = df.values.sha(candidate)
    if previous is not None:
        if record != previous:
            candidate.with_suffix('.json').write_bytes(encoded(record))
            raise ArithmeticError('independent endpoint domain differs; candidate preserved')
        candidate.unlink()
        receipt_path.write_bytes(encoded(dict(byte_identical=True, independent_recomputation=True,
            record_SHA256=df.values.sha(record_path), endpoints=371,
            uniform_endpoint_rates_enclosed=False, FULL_BHSM_COMPLETE=False)))
    else:
        candidate.replace(path)
        record_path.write_bytes(encoded(record))
    print(json.dumps(dict(endpoints=371, byte_identical_repeat=args.recompute,
                         uniform_endpoint_rates_enclosed=False, FULL_BHSM_COMPLETE=False)), flush=True)


if __name__ == '__main__':
    main()
