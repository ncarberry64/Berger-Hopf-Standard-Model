"""Reuse saved seven-solve jets; cancel the common border before normalization.

This is a width diagnostic, not a reproduced neighborhood certificate. No action
contractions, point Hessians, or implicit solves are recomputed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main(snapshot, saved, out):
    sys.path[:0] = [str(snapshot/'scripts'), str(snapshot/'src')]
    import numpy as np
    from flint import arb, ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm_immutable_input_hash_cache as cache
    from bhsm.interface import coupled_physical_normalization_second as normalization
    ctx.prec = 512
    p = engine.p
    record = json.loads((saved/'record.json').read_bytes())
    if record['data_SHA256'] != sha(saved/'hessian.npz'):
        raise ValueError('Saved jet data changed')
    report = record['report']
    for field in ('complete_original_seven_solve_graph_used',
                  'complete_original_scalar_contractions_used',
                  'complete_signed_mixed_line_and_response_residuals_used'):
        if report.get(field) is not True:
            raise ValueError('Complete original mixed variation identities required')
    residual = p.geometry.residual
    targets = [(p.values, 'sha'), (residual.center, '_sha'),
               (residual.foundation.coordinate.center, '_sha')]
    with cache.cache_hashes(targets, excluded_roots=[out]):
        source = engine.load_inputs(record['endpoint'])
        for key, value in source['binding'].items():
            if key == 'files':
                if any(record['binding']['files'].get(k) != v for k, v in value.items()):
                    raise ValueError('Saved jets and value family differ')
            elif record['binding'].get(key) != value:
                raise ValueError('Saved jet geometry differs: '+key)
        with np.load(saved/'hessian.npz', allow_pickle=False) as data:
            domain_mid, domain_rad = p.hs.rational_balls(source['raw_domain'])
            if not (np.array_equal(domain_mid, data['raw_domain_mid_q']) and
                    np.array_equal(domain_rad, data['raw_domain_rad_q'])):
                raise ValueError('Original domain must be identical')
            arrays = {key[:-6]: p.hs.restore_balls(data[key], data[key[:-6]+'_rad_q'])
                      for key in data.files if key.endswith('_mid_q')}
        solved = arrays['uniform_solutions']
        if solved.shape != (7, 62, 1):
            raise ValueError('Seven complete mixed-column solutions required')
        _, weights, _, _, _ = p.values.operands()
        w = np.array([arb(float(v)) for v in weights], dtype=object)
        qw, rw, _, _ = p.values.cert.metric_data()
        q = np.array([arb(float(v)) for v in qw], dtype=object)
        reduced = np.array([arb(float(v)) for v in rw], dtype=object)
        axis, directions = arrays['weighted_axis'], arrays['weighted_transverse']
        raw_axis = axis.copy(); raw_axis[:98] /= w
        raw_v = directions[:98]/w[:, None]
        def jet(line, response, configuration, descriptor, values):
            return dict(configuration=configuration, psi=solved[line][:61],
                        hard=solved[response][:61], border=solved[response][-1],
                        descriptor=descriptor, cpsi=values[:, 0], remainder=values[:, 1])
        u = jet(1, 2, (q*raw_axis[37:74])[:, None], axis[98:99],
                arrays['descriptor_first_axis'][None, :])
        v = jet(3, 4, q[:, None]*raw_v[37:74], directions[98], arrays['descriptor_first_transverse'])
        uv = jet(5, 6, np.full((37, 1), arb(0), dtype=object),
                 np.full(1, arb(0), dtype=object), arrays['descriptor_mixed'])
        normalized, proof = normalization.normalized_mixed(
            q*source['paired']['full'][37:74], reduced, source['paired']['eigenbox'][:61],
            solved[0][:61, 0], solved[0][-1, 0], source['raw_domain'][98],
            *arrays['descriptor_base'], u, v, uv, coupled_identities_and_variations=True)
        if not all(a.overlaps(b) for a, b in zip(normalized.flat, arrays['uniform_hessian'].flat)):
            raise ArithmeticError('Equivalent normalizations disagree')
        if not all(a.contains(b) for a, b in zip(normalized.flat, arrays['point_hessian'].flat)):
            raise ArithmeticError('Verified point column not contained')
        arrays['generic_uniform_hessian'] = arrays['uniform_hessian']
        arrays['uniform_hessian'] = normalized
        encoded = {}
        for name, array in arrays.items():
            encoded[name+'_mid_q'], encoded[name+'_rad_q'] = p.hs.rational_balls(array)
        out.mkdir(parents=True, exist_ok=False)
        np.savez_compressed(out/'hessian.npz', **encoded)
        result = dict(record)
        result.update(data_SHA256=sha(out/'hessian.npz'),
                      saved_jet_record_SHA256=sha(saved/'record.json'),
                      saved_jet_data_SHA256=sha(saved/'hessian.npz'),
                      normalization_source_SHA256=sha(Path(normalization.__file__)),
                      producer_SHA256=sha(Path(__file__)))
        result['report'] = dict(report, normalization_proof=proof,
            saved_seven_solve_jets_reused=True, new_action_contractions=0, new_implicit_solves=0,
            maximum_uniform_absolute=float(max(abs(v).upper() for v in normalized.flat)),
            maximum_uniform_radius=float(max(v.rad() for v in normalized.flat)),
            independent_recomputation=False, ledger_debit_added=False)
        (out/'record.json').write_bytes(p.geometry.encoded(result))
        print(json.dumps(result['report']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('snapshot', 'saved', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    main(args.snapshot.resolve(), args.saved.resolve(), args.out.resolve())
