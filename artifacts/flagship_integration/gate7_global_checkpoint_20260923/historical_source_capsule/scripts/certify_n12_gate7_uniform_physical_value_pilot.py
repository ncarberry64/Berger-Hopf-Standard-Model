"""Try uniform rates on two frozen endpoint boxes and their actual HS midpoint.

Run only when the numerical pool is available. Preflight reads and verifies
inputs without computing action jets. A failed coordinate-box method is not
a proof that the correlated affine domain is singular.
"""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_direct_endpoint_neighborhoods as geometry
from bhsm.interface import uniform_eigenpair_proposal as proposal

df = geometry.df
values = df.values
hs = values.hs
WORK = ROOT/'artifacts/flagship_integration/.uniform_physical_value_pilot_work'
THEORY = ROOT/'theory/n12_gate7_uniform_physical_value_pilot.md'
ALGORITHM = 'UNIFORM_PHYSICAL_HS_BOX_RATE_PILOT_NORMALIZED_INDEX24_ARB512_V2'


def verify_sources(expected):
    values.verify_binding(dict(files=expected['files']))
    geometry.residual.foundation.coordinate._verified_inputs(dict(inputs=expected['normalized_inputs']))


def load_geometry():
    """Require the complete paired geometry and retain all interval radii."""
    directory = geometry.WORK
    path, data_path, receipt_path = [directory/name for name in ('endpoints.json', 'endpoints.npz', 'reproduction.json')]
    record = json.loads(path.read_text())
    receipt = json.loads(receipt_path.read_text())
    if (record.get('algorithm') != geometry.ALGORITHM or record.get('precision_bits') != 512
            or record.get('scope') != 'FROZEN_AFFINE_TRIAL_ENDPOINT_DOMAIN_GEOMETRY'
            or record.get('endpoints') != list(range(371)) or record.get('shape') != [371, 99]
            or record.get('initial_endpoint_fixed') is not True
            or record.get('transverse_domain') != 'FULL_COORDINATE_SPACE_SUPERSET'
            or record.get('axis_normalization_assumed') is not False
            or record.get('weighted_center_product_rounding_enclosed') is not True
            or record.get('radii_status') != 'TRIAL_RADII_FROM_OLD_CONDITIONAL_POLYNOMIAL_NOT_RECERTIFIED'
            or record.get('data_SHA256') != values.sha(data_path)
            or path.read_bytes() != geometry.encoded(record)
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('endpoints') != 371 or receipt.get('record_SHA256') != values.sha(path)):
        raise RuntimeError('complete independently reproduced endpoint geometry required')
    runtime = dict(python=sys.version, numpy=np.__version__, python_flint=values.flint.__version__)
    if record.get('runtime') != runtime:
        raise RuntimeError('geometry arithmetic runtime differs')
    source_paths = (Path(geometry.__file__), geometry.THEORY, geometry.TRIAL_RADII,
                    Path(geometry.neighborhood.__file__), Path(geometry.neighborhood.preserve_ball.__code__.co_filename))
    if any(record.get('raw_input_SHA256', {}).get(df.file_key(p)) != values.sha(p) for p in source_paths):
        raise RuntimeError('geometry lacks current implementation and radius bindings')
    values.verify_binding(dict(files=record['raw_input_SHA256']))
    geometry.residual.foundation.coordinate._verified_inputs(dict(inputs=record['inputs']))
    wanted = {key+suffix for key in ('weighted_box', 'raw_box', 'coordinate_displacement_radius')
              for suffix in ('_mid_q', '_rad_q')}
    with np.load(data_path, allow_pickle=False) as data:
        if set(data.files) != wanted or any(data[k].shape != (371, 99) for k in wanted):
            raise RuntimeError('complete rational endpoint geometry arrays required')
        restored = {key: hs.restore_balls(data[key+'_mid_q'], data[key+'_rad_q'])
                    for key in ('weighted_box', 'raw_box', 'coordinate_displacement_radius')}
    if any(not v >= 0 for v in restored['coordinate_displacement_radius'].flat):
        raise RuntimeError('nonnegative endpoint displacement radii required')
    radii = json.loads(geometry.TRIAL_RADII.read_text())['stored_polynomial_adjudication']['witness']['radius']
    if record.get('radii_exact_binary64_rationals') != [str(geometry.neighborhood.exact_radius(v).fmpq()) for v in radii]:
        raise RuntimeError('geometry trial radii differ from their bound source')
    sources = dict(record['raw_input_SHA256'])
    for p in (path, data_path, receipt_path):
        geometry.residual.merge(sources, {df.file_key(p): values.sha(p)})
    return record, restored['weighted_box'], sources


def load_inputs():
    ctx.prec = 512
    record, boxes, sources = load_geometry()
    point_binding = df.binding()
    geometry.residual.merge(sources, point_binding['files'])
    for p in (Path(__file__), THEORY, Path(geometry.__file__), Path(hs.__file__),
              Path(values.__file__), Path(values.cert.__file__), Path(proposal.__file__)):
        geometry.residual.merge(sources, {df.file_key(p): values.sha(p)})
    if hashlib.sha256(inspect.getsource(values.cert._rate_enclosure).encode()).hexdigest().upper() != values.RATE_SHA256:
        raise RuntimeError('frozen physical rate function changed')
    expected = dict(algorithm=ALGORITHM, precision_bits=512, runtime=record['runtime'], files=sources,
                    normalized_inputs=record['inputs'], value_point_binding=point_binding,
                    trial_radii_rational=record['radii_exact_binary64_rationals'])
    verify_sources(expected)
    _, weights, _, reference, steps = values.operands()
    return dict(binding=expected, boxes=boxes, weights=weights, reference=reference, steps=steps)


def proof_valid(proof):
    return (proof.get('validation_passed') is True
            and proof.get('normalized_eigenpair_enclosed') is True
            and proof.get('proposal_center_normalized_before_verification') is True
            and proof.get('positive_stored_reference_overlap') is True
            and proof.get('selected_zero_based_index_verified') == 24
            and proof.get('spectral_index_verification', {}).get('validation_passed') is True)


def metadata(stage, index, source, dependencies):
    return dict(algorithm=ALGORITHM, scope='UNIFORM_RATE_ON_SELECTED_FROZEN_AFFINE_HS_BOX',
        stage=stage, index=index, binding=source['binding'], dependencies=dependencies,
        input_domain='OUTER_COORDINATE_BOX_OF_FROZEN_AFFINE_TRIAL_DOMAIN',
        uniform_selected_box_rate_enclosed=True, actual_HS_midpoint_domain=stage == 'midpoint',
        uniform_endpoint_rates_used_for_midpoint=stage == 'midpoint',
        center_rate_overlap_checked=True, state_uncertainty_retained=True,
        floating_spectral_gap_assumed=False, pointwise_rate_substituted_for_uniform_rate=False,
        uniform_derivatives_enclosed=False, neighborhood_remainder_enclosed=False,
        intrinsic_constraint_chart_certified=False, physical_quotient_identified=False,
        physical_contraction_proved=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def read_point(directory, stage, index, source, dependencies):
    path = directory/f'{stage}_{index:03d}.npz'
    record_path = path.with_suffix('.json')
    record = json.loads(record_path.read_text())
    expected = metadata(stage, index, source, dependencies)
    expected.update(data_SHA256=values.sha(path), eigenpair_inclusion=record.get('eigenpair_inclusion', {}))
    if record != expected or record_path.read_bytes() != geometry.encoded(expected) or not proof_valid(expected['eigenpair_inclusion']):
        raise RuntimeError('uniform point source or proof changed')
    wanted = {key+suffix for key in ('value', 'weighted_domain', 'raw_domain') for suffix in ('_mid_q', '_rad_q')}
    with np.load(path, allow_pickle=False) as data:
        if set(data.files) != wanted or any(data[k].shape != (99,) for k in wanted):
            raise RuntimeError('complete rational uniform value and domains required')
        arrays = {key: hs.restore_balls(data[key+'_mid_q'], data[key+'_rad_q']) for key in ('value', 'weighted_domain', 'raw_domain')}
    return arrays, record


def point_domain(directory, stage, index, source):
    dependencies = {}
    if stage == 'endpoint':
        return source['boxes'][index].copy(), dependencies
    if stage != 'midpoint':
        raise ValueError('endpoint or midpoint required')
    rates = []
    for node in (index, index+1):
        arrays, _ = read_point(directory, 'endpoint', node, source, {})
        rates.append(arrays['value'])
        for ext in ('npz', 'json'):
            p = directory/f'endpoint_{node:03d}.{ext}'
            dependencies[df.file_key(p)] = values.sha(p)
    return hs.physical_midpoint(source['boxes'][index], source['boxes'][index+1],
                                *rates, float(source['steps'][index])), dependencies


def evaluate(raw, source):
    """Call the unchanged interval kernel with independent eigenpair checks."""
    ctx.prec = 512
    checks = []
    with proposal.use_uniform_proposal(values.cert), \
            hs.verified_eigenline(values.cert, checks, expected_index=24, normalize_proposal_center=True):
        result = values.cert._rate_enclosure(raw[:98], raw[98], source['weights'], source['reference'], None)
    output = hs.finite_vector(result.value, 99)
    if len(checks) != 1 or not proof_valid(checks[0]):
        raise ArithmeticError('one uniform normalized index24 eigenpair proof required')
    return output, checks[0]


def materialize_point(directory, stage, index, source, recompute=False):
    ctx.prec = 512
    verify_sources(source['binding'])
    weighted, dependencies = point_domain(directory, stage, index, source)
    raw = geometry.neighborhood.unweight_box(weighted, source['weights'])
    path = directory/f'{stage}_{index:03d}.npz'
    previous = None
    if path.exists() or path.with_suffix('.json').exists():
        _, previous = read_point(directory, stage, index, source, dependencies)
        if not recompute:
            return
    elif recompute:
        raise RuntimeError('independent repeat requires prior uniform point evidence')
    arrays = {}
    for name, array in (('weighted_domain', weighted), ('raw_domain', raw)):
        arrays[name+'_mid_q'], arrays[name+'_rad_q'] = hs.rational_balls(array)
    # Keep the exact attempted outer domain even when the kernel fails.
    attempt = directory/f'{stage}_{index:03d}.attempt_{time.time_ns()}.npz'
    np.savez_compressed(attempt, **arrays)
    try:
        output, proof = evaluate(raw, source)
        _, _, _, _, center_rate, point_dependencies = df.point_inputs(stage, index, source['binding']['value_point_binding'])
        # Independent center enclosures can have different rounding widths;
        # overlap is a consistency check, not the uniform inclusion proof.
        if not all(a.overlaps(b) for a, b in zip(output, center_rate, strict=True)):
            raise ArithmeticError('uniform rate does not overlap paired center rate')
        values.verify_binding(dict(files=point_dependencies))
        verify_sources(source['binding'])
        values.verify_binding(dict(files=dependencies))
        ctx.prec = 512
        arrays['value_mid_q'], arrays['value_rad_q'] = hs.rational_balls(output)
        candidate = attempt.with_name(attempt.stem+'.candidate.npz')
        np.savez_compressed(candidate, **arrays)
        record = metadata(stage, index, source, dependencies)
        record.update(data_SHA256=values.sha(candidate), eigenpair_inclusion=proof)
        if previous is not None:
            if record != previous:
                candidate.with_suffix('.json').write_bytes(geometry.encoded(record))
                raise ArithmeticError('independent uniform point differs; candidate preserved')
            candidate.unlink()
        else:
            candidate.replace(path)
            path.with_suffix('.json').write_bytes(geometry.encoded(record))
        attempt.unlink()
    except BaseException as error:
        attempt.with_suffix('.json').write_bytes(geometry.encoded(dict(stage=stage, index=index,
            error=repr(error), eigenpair_inclusion=getattr(error, 'eigenpair_inclusion', None),
            binding=source['binding'], dependencies=dependencies, input_data_SHA256=values.sha(attempt),
            method_failure_does_not_prove_domain_singular=True,
            uniform_selected_box_rate_enclosed=False, FULL_BHSM_COMPLETE=False)))
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=13)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--recompute', action='store_true')
    args = parser.parse_args()
    if not 0 <= args.interval < 370 or (args.preflight and args.recompute):
        raise ValueError('interval in 0..369; preflight and recompute are exclusive')
    source = load_inputs()
    if args.preflight:
        print(json.dumps(dict(interval=args.interval, paired_endpoint_domains_verified=True,
            raw_source_files=len(source['binding']['files']), numerical_field_evaluated=False,
            FULL_BHSM_COMPLETE=False)), flush=True)
        return
    directory = WORK/f'interval_{args.interval:03d}'
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path, receipt_path = directory/'manifest.json', directory/'reproduction.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    if args.recompute and previous is None:
        raise RuntimeError('independent repeat requires complete previous pilot')
    if previous is not None:
        if manifest_path.read_bytes() != geometry.encoded(previous):
            raise RuntimeError('previous pilot manifest encoding changed')
        values.verify_binding(dict(files=previous['files']))
    if receipt_path.exists():
        receipt_path.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    points = [('endpoint', args.interval), ('endpoint', args.interval+1), ('midpoint', args.interval)]
    for stage, index in points:
        materialize_point(directory, stage, index, source, args.recompute)
        print(json.dumps(dict(stage=stage, index=index, uniform_box_rate_evaluated=True,
                             reproduced=args.recompute)), flush=True)
    verify_sources(source['binding'])
    files = {df.file_key(directory/f'{stage}_{index:03d}.{ext}'): values.sha(directory/f'{stage}_{index:03d}.{ext}')
             for stage, index in points for ext in ('npz', 'json')}
    manifest = dict(algorithm=ALGORITHM, interval=args.interval, files=files,
        selected_two_endpoint_and_actual_midpoint_box_rates_enclosed=True,
        complete_741_point_uniform_coverage=False, uniform_derivatives_enclosed=False,
        neighborhood_remainder_enclosed=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    if args.recompute:
        if previous != manifest:
            (directory/f'manifest.mismatch_{time.time_ns()}.json').write_bytes(geometry.encoded(manifest))
            raise ArithmeticError('independent uniform pilot manifest differs')
        receipt_path.write_bytes(geometry.encoded(dict(byte_identical=True, independent_recomputation=True,
            interval=args.interval, points=3, manifest_SHA256=values.sha(manifest_path),
            neighborhood_remainder_enclosed=False, FULL_BHSM_COMPLETE=False)))
    else:
        manifest_path.write_bytes(geometry.encoded(manifest))


if __name__ == '__main__':
    main()
