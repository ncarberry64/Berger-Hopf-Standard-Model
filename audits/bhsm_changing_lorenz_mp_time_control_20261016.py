"""Same real cell, radial128/anchor96, changing-coefficient time8 and12.

Completed MP80 time6 entries are reused with explicit conservative float
conversion envelopes.  This bounds arithmetic-reference rule changes, not
upstream physical accuracy, native completion or a physical derivative.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np
import mpmath as mp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'audits'))
import bhsm_changing_lorenz_mp_coefficient_values_20261016 as owner

OWNER_SHA = '1b0a9713749feb062fecdb664598a7a5b3528bd72ec5aa18176ae88eb5b88eff'


def conversion_envelope(float_reference, new):
    """Enclose each original MP value represented by a nearest float64.

    Half the larger adjacent spacing is conservative even at binade
    boundaries and zero/subnormals.  All gap arithmetic is MP-valued.
    """
    if float_reference.shape != new.shape or not np.isfinite(float_reference).all():
        raise ValueError('Finite same-coordinate baseline required')
    maximum, index, max_absolute = mp.mpf(0), 0, mp.mpf(0)
    selected = None
    for k, (value, other) in enumerate(zip(float_reference.flat, new.flat)):
        lo = np.nextafter(value, -np.inf)
        hi = np.nextafter(value, np.inf)
        if not np.isfinite(lo) or not np.isfinite(hi):
            raise ArithmeticError('Finite neighboring float spacings required')
        center = owner.m(value)
        radius = max(center - owner.m(lo), owner.m(hi) - center) / 2
        bound = abs(other - center) + radius
        denominator = max(mp.mpf(1), abs(center) - radius, abs(other))
        scaled = bound / denominator
        max_absolute = max(max_absolute, bound)
        if selected is None or scaled > maximum:
            maximum, index = scaled, k
            selected = (center, radius, other)
    return dict(max_absolute_upper=mp.nstr(max_absolute, 65),
        max_entry_scaled_upper=mp.nstr(maximum, 65),
        index=list(map(int, np.unravel_index(index, new.shape))),
        reference_float=mp.nstr(selected[0], 65),
        reference_half_max_neighbor_gap=mp.nstr(selected[1], 65),
        new_MP_entry=mp.nstr(selected[2], 65),
        denominator_lower_bound='max(1,abs(reference_float)-radius,abs(new_MP))',
        bound_scope='Original MP80 arithmetic value before its correctly rounded float conversion; not upstream uncertainty')


def pack_moments(arrays, moments):
    """Exact working-binary MP tuples, not truncated decimal coefficients."""
    for name, a in moments.items():
        strings = []
        for value in a.flat:
            sign, mantissa, exponent, bits = value._mpf_
            strings.append(f'{sign}:{int(mantissa):x}:{exponent}:{bits}')
        arrays['moment_' + name + '_exact_MP_tuple'] = np.array(strings).reshape(a.shape)


def integrate(phase, reference, frozen, E, time_order, dps, c):
    length = abs(owner.m(phase['span']))
    origin = min(owner.m(phase['span']), mp.mpf(0))
    times, tw = owner.time_nodes(phase, frozen, 'mp', time_order, dps)
    rho, rw = owner.radial_nodes(frozen, 'mp', 128, dps, c)
    bases = [owner.radial_basis(r, reference, c) for r in rho]
    snapshots = []
    for u, weight in zip(times, tw):
        t = u + origin
        raw = owner.raw_at(phase, t)
        g = owner.geometry(raw, c['WALL'] / 2, c)
        chart = owner.response_chart(g['delta'], c, 96, 'mp', dps)
        snapshots.append(dict(u=u, t=t, raw=raw, weight=weight, chart=chart,
                             temporal=owner.temporal_values(u, length),
                             tent=2 * min(u / length, 1 - u / length)))
    total = owner.tensor.tensors()
    indices = [(284, 924), (0, 0), (20, 183), (40, 823)]
    literal = [mp.mpf(0) for _ in indices]
    point_controls = []
    for ri, (r, wr, basis) in enumerate(zip(rho, rw, bases)):
        for ti in range(len(times) // 2):
            group = []
            for time_index in (ti, len(times) - 1 - ti):
                s = snapshots[time_index]
                side = phase['side']
                val = owner.coefficient(s['raw'], s['t'], r, side, phase.get('parent_reference'),
                    reference, c, s['chart'], basis_data=basis)
                point = owner.native_point(val['A'], val['metric'], s['temporal'], val['radial'], s['tent'], c)
                weight = wr * s['weight']
                group.append((weight, point))
                for k, (i, j) in enumerate(indices):
                    independent = owner.native_literal(i, j, val['A'], E, val['metric'],
                                                        s['temporal'], val['radial'], s['tent'], c)
                    literal[k] += weight * independent
                    if ri in (0, 64, 127) and time_index in (0, len(times) // 2, len(times) - 1):
                        expanded = owner.tensor.tensor_entry(point, E, i, j)
                        point_controls.append(dict(radial_index=ri, time_index=time_index,
                            row=i, column=j, literal=mp.nstr(independent, 65),
                            tensor=mp.nstr(expanded, 65), absolute=mp.nstr(abs(independent - expanded), 10)))
            for name in total:
                total[name] += group[0][0] * group[0][1][name] + group[1][0] * group[1][1][name]
        if ri % 8 == 0 or ri == 127:
            print(json.dumps(dict(side=phase['side'], time_order=time_order,
                                 radial_index=ri + 1, radial_count=128, dps=dps)), flush=True)
    B = owner.tensor.assemble(total, E)
    F = owner.tensor.apply_inverse(owner.tensor.inverse4(total['ghost_G4']), B)
    fixing = owner.tensor.full_fixing(B, F)
    controls = [dict(row=i, column=j, literal_MP_integral=mp.nstr(a, 65),
        tensor_MP_integral=mp.nstr(B[i, j], 65), absolute=mp.nstr(abs(a - B[i, j]), 10))
        for (i, j), a in zip(indices, literal)]
    return dict(B=B, F=F, fixing=fixing), total, snapshots, rho, rw, controls, point_controls


def execute(refinement, application, baseline, output, dps):
    baseline, out = Path(baseline), Path(output)
    if out.exists():
        raise FileExistsError('Preserve every earlier time rule')
    if sha256(Path(owner.__file__).read_bytes()).hexdigest() != OWNER_SHA:
        raise ValueError('Peer-reviewed MP value owner must remain frozen')
    report = json.loads((baseline / 'result.json').read_text())
    if report['source_and_owner_sha256'].get(Path(owner.__file__).relative_to(ROOT).as_posix()) != OWNER_SHA:
        raise ValueError('Same final source baseline required')
    if report['temporal_order_per_half'] != 6 or report['anchored_response_order'] != 96 or report['quadrature_rule_mode'] != 'mp':
        raise ValueError('Same actual MP time6/radial128/anchor96 protocol required')
    phases, reference, frozen, E, pins = owner.load_inputs(refinement, application)
    out.mkdir(parents=True)
    inputs, records = {}, []
    with mp.workdps(dps):
        c = owner.constants()
        # Exact edge cases guard the conversion envelope without requiring
        # an unavailable extended-precision NumPy scalar type.
        minsub = np.nextafter(0., np.inf)
        envelope_controls = [conversion_envelope(np.array([[x]]), np.array([[owner.m(x)]], dtype=object))
                             for x in (0., minsub, -minsub, 1., -1.)]
        for side in ('incoming', 'outgoing'):
            phase = dict(phases[side], side=side)
            p = baseline / f'{side}_radial128/forms.npz'
            digest = sha256(p.read_bytes()).hexdigest()
            expected = next(r['numerical_sha256'] for r in report['records'] if r['side'] == side and r['radial_order'] == 128)
            if digest != expected:
                raise ValueError('Completed time6 baseline bytes changed')
            inputs[f'time6/{side}_radial128/forms.npz'] = digest
            with np.load(p, allow_pickle=False) as z:
                six = {name: owner.tensor.load_matrix(z, name) for name in ('B', 'F', 'fixing')}
            previous = None
            for order in (8, 12):
                matrices, moments, snapshots, rho, rw, literal, point_controls = integrate(
                    phase, reference, frozen[side, 128], E, order, dps, c)
                comparisons = ({name: conversion_envelope(six[name], a) for name, a in matrices.items()}
                               if previous is None else {name: owner.mp_compare(previous[name], a) for name, a in matrices.items()})
                threshold_values = [mp.mpf(a['max_entry_scaled_upper'] if previous is None else a['max_entry_scaled'])
                                    for a in comparisons.values()]
                folder = out / f'{side}_time{order}'
                folder.mkdir()
                arrays = dict(ghost_Gram4=owner.tensor.as_float(moments['ghost_G4']),
                    temporal_u=np.array([float(s['u']) for s in snapshots]),
                    temporal_coordinate_time=np.array([float(s['t']) for s in snapshots]),
                    temporal_coordinate_weights=np.array([float(s['weight']) for s in snapshots]),
                    raw=np.array([owner.tensor.as_float(s['raw']) for s in snapshots]),
                    rawtime=phase['rate'], source_midpoint=phase['midpoint'],
                    radial_points=np.array(list(map(float, rho))), radial_coordinate_weights=np.array(list(map(float, rw))))
                for name, a in matrices.items():
                    owner.tensor.save_matrix(arrays, name, owner.tensor.as_float(a))
                pack_moments(arrays, moments)
                owner._compressed_npz(folder / 'forms.npz', arrays)
                record = dict(side=side, previous_time_order=6 if previous is None else 8,
                    time_order_per_half=order, radial_order=128, anchored_response_order=96,
                    arithmetic_dps=dps, comparisons=comparisons,
                    comparison_kind='Conservative whole-entry MP6 float-conversion envelope versus MP8' if previous is None else 'Every unrounded MP8 versus MP12 entry',
                    finite_Lorenz_component_time_rule_pass=all(x <= mp.mpf('2e-10') for x in threshold_values),
                    integrated_literal_MP_controls=literal, point_literal_MP_controls=point_controls,
                    root_residuals=[dict(time=mp.nstr(s['t'], 65),
                        coefficients=[mp.nstr(a, 65) for a in s['chart']['a']],
                        maximum=mp.nstr(max(map(abs, s['chart']['residual'])), 10),
                        chart_Z=mp.nstr(s['chart']['chart_Z'], 65), production_Z=mp.nstr(s['chart']['Z'], 65),
                        delta_zero_override=s['chart']['delta_zero_Z_override']) for s in snapshots],
                    moment_encoding='Exact working-binary MP tuple sign:hex_mantissa:exponent:bitcount; no decimal truncation',
                    numerical_sha256=sha256((folder / 'forms.npz').read_bytes()).hexdigest(),
                    physical_derivative_pass=False, coupled_corrections=0)
                (folder / 'result.json').write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf8', newline='\n')
                records.append(record)
                previous = matrices
    pins[Path(__file__).relative_to(ROOT).as_posix()] = sha256(Path(__file__).read_bytes()).hexdigest()
    pins[Path(owner.__file__).relative_to(ROOT).as_posix()] = OWNER_SHA
    for rel, digest in pins.items():
        if sha256((ROOT / rel).read_bytes()).hexdigest() != digest:
            raise ValueError('Owner changed: ' + rel)
    result = dict(classification='CHANGING_REAL_CELL_MP_TIME6_8_12_LORENZ_COMPONENT_CONTROL',
        records=records, float_conversion_edge_controls=envelope_controls,
        input_archive_sha256=inputs, source_and_owner_sha256=dict(sorted(pins.items())),
        completed_time6_receipt_sha256=sha256((baseline / 'result.json').read_bytes()).hexdigest(),
        source_clock_protocol='Incoming t=u-L; child t=u; same affine midpoint/rate, independent proper lapses',
        completed_time6_fields_recomputed=False, constant_coefficients_substituted=False,
        upstream_interval_accuracy_or_physical_source_derivative_certified=False,
        full15_forms_native_outgoing_or_physical_derivative_pass=False,
        coupled_corrections=0, physical_muon_moment=None)
    (out / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf8', newline='\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refinement', required=True)
    parser.add_argument('--application', required=True)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--dps', type=int, default=80)
    args = parser.parse_args()
    if args.dps < 80:
        raise ValueError('Declared MP80 or higher arithmetic required')
    execute(args.refinement, args.application, args.baseline, args.output, args.dps)
