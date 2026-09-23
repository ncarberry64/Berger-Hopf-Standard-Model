"""Exact inventory and serial raw-operand replay of fourteen midpoint terms."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ROWS = (28, 30, 33, 36, 38, 41, 44, 46, 49, 52, 54, 57, 59, 61)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def encoded(data):
    return (json.dumps(data, sort_keys=True, indent=2)+'\n').encode()


def inventory(work, out):
    first = work/'interval14_midpoint14_base_taylor_first'
    repeat = work/'interval14_midpoint14_base_taylor_repeat_schedule'
    records = []
    for i in ROWS:
        name = f'response_{i:02d}_source'
        paths = [folder/(name+'.json') for folder in (first, repeat)]
        pair = [json.loads(path.read_bytes()) for path in paths]
        values = []
        for j, (a, b) in enumerate(zip(pair[0]['values'], pair[1]['values'], strict=True)):
            def ball(v):
                m, r = map(Fraction, v)
                if r < 0:
                    raise ValueError('Nonnegative exact radius required')
                return dict(midpoint=str(m), radius=str(r), lower=str(m-r), upper=str(m+r))
            values.append(dict(slot=j, role='constant' if j == 0 else ('nonlinear_tail' if j == 250 else f'parameter_{j-1}'),
                               first=ball(a), repeat=ball(b), identical=a == b))
        records.append(dict(term=name, input_binding_first=pair[0]['binding'], input_binding_repeat=pair[1]['binding'],
            source_SHA256={str(path.resolve()): sha(path) for path in paths}, values=values,
            differing_slots=[v['slot'] for v in values if not v['identical']]))
    out.write_bytes(encoded(dict(algorithm='MIDPOINT14_EXACT_SOURCE_TERM_DIFFERENCE_INVENTORY_V1',
        comparison='Exact rational midpoint/radius and m-r,m+r; no decimal conversion', terms=records)))
    print(json.dumps({'inventory': str(out), 'terms': [r['term'] for r in records]}), flush=True)


def run(root, work, out):
    sys.path[:0] = [str(root/'scripts'), str(root/'src')]
    import numpy as np
    import flint
    from flint import arb, ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(ROOT/'src/bhsm/interface'))
    from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain, scalar_taylor_action
    ctx.prec = 512
    ctx.threads = 1
    p = engine.p
    cert = p.values.cert
    out.mkdir(exist_ok=False)
    operands = work/'interval14_midpoint14_point_first'
    predictors = work/'interval14_midpoint14_seven_first'
    source_paths = [operands/'record.json', operands/'operands.npz', predictors/'record.json', predictors/'predictors.npz']
    raw_hashes = {str(path.resolve()): sha(path) for path in source_paths}

    def load(folder, filename):
        record = json.loads((folder/'record.json').read_bytes())
        if sha(folder/filename) != record['data_SHA256']:
            raise ValueError('Raw operand archive changed')
        with np.load(folder/filename, allow_pickle=False) as z:
            arrays = {k[:-6]: p.hs.restore_balls(z[k], z[k[:-6]+'_rad_q']) for k in z.files if k.endswith('_mid_q')}
        return record, arrays

    ore, a = load(operands, 'operands.npz')
    pre, s = load(predictors, 'predictors.npz')
    if pre['interval'] != 14 or pre['stage'] != 'midpoint' or pre['binding'] != ore['binding']:
        raise ValueError('Original interval-14 midpoint required')
    p.verify_sources(ore['binding'])
    _, weights, _, _, _ = p.values.operands()
    qw, rw, _, _ = cert.metric_data()
    weights, qw, rw = [[arb(float(v)) for v in items] for items in (weights, qw, rw)]
    n = s['weighted_tube_directions'].shape[1]
    domain = TaylorDomain(pre['parameter_groups'], n)

    def ball(value):
        return [str(value.mid().fmpq()), str(value.rad().fmpq())]

    def scalar(value):
        if isinstance(value, Taylor):
            return ['Taylor', [ball(v) for v in (value.c, *value.a.entries(), value.r)]]
        return ['Arb', ball(arb(value))]

    modules = {str(Path(module.__file__).resolve()): sha(Path(module.__file__))
               for module in tuple(sys.modules.values()) if getattr(module, '__file__', None)
               and str(Path(module.__file__).resolve()).startswith((str(root), str(ROOT)))
               and Path(module.__file__).is_file()}
    modules[str(Path(__file__).resolve())] = sha(Path(__file__))
    records = []
    for i in ROWS:
        # Reconstruct fresh common-parameter objects for every term. No saved
        # action value, derived Taylor ball, solve error, or worker cache is read.
        state = [domain.affine(s['center_state'][j], [s['weighted_tube_directions'][j,k]/weights[j]
                 for k in range(n)]) for j in range(98)]
        if any(not a['raw_domain'][j].contains(v.enclosure()) for j, v in enumerate(state)):
            raise ValueError('Original domain containment failed')
        v = list(a['paired_rm'][i, :61])
        c = [arb(0)]*37+[v[j]*rw[j]/weights[37+j] for j in range(61)]
        d = [qw[j]*state[37+j]/weights[j] for j in range(37)]+[arb(0)]*61
        maps = [cert._dense_mapping(cert._integrand(s['center_state'], node, 0).maps) for node in range(cert.POINTS)]
        inputs = dict(term=f'response_{i:02d}_source', precision_bits=ctx.prec, arb_threads=ctx.threads,
            flint_version=flint.__version__, original_parameter_groups=pre['parameter_groups'],
            raw_operand_SHA256=raw_hashes, implementation_SHA256=modules,
            normalized_original_binding=ore['binding'],
            state=[scalar(x) for x in state], covector=[scalar(x) for x in c],
            configuration_leg=[scalar(x) for x in d],
            maps=[dict(shape=list(np.asarray(m).shape), dtype=str(np.asarray(m).dtype),
                       exact_float_hex=[float(x).hex() for x in np.asarray(m).flat]) for m in maps])
        name = inputs['term']
        input_bytes = encoded(inputs)
        (out/(name+'_inputs.json')).write_bytes(input_bytes)
        input_hash = hashlib.sha256(input_bytes).hexdigest().upper()
        with scalar_taylor_action(cert):
            value = cert._contracted_action(np.array(state, dtype=object),
                    [np.array(c, dtype=object), np.array(d, dtype=object)], maps)
        if isinstance(value, arb):
            value = domain.affine(value)
        values = [ball(x) for x in (value.c, *value.a.entries(), value.r)]
        record = dict(term=name, complete_input_SHA256=input_hash, values=values,
            exact_endpoints=[[str(Fraction(m)-Fraction(r)), str(Fraction(m)+Fraction(r))] for m,r in values],
            stage='raw action source-Hessian contraction, before response solve or normalization',
            cached_derived_balls_read=False, original_domain_unchanged=True, interval13_recomputed=False)
        (out/(name+'.json')).write_bytes(encoded(record))
        records.append(dict(term=name, input_SHA256=input_hash, output_SHA256=sha(out/(name+'.json'))))
        print(json.dumps({'serial_term_complete': name, 'count': len(records), 'total': len(ROWS)}), flush=True)
    if any(sha(Path(path)) != digest for path, digest in {**raw_hashes, **modules}.items()):
        raise ValueError('Input/source changed during serial replay')
    (out/'record.json').write_bytes(encoded(dict(algorithm='MIDPOINT14_FOURTEEN_RAW_SERIAL_TERMS_V1',
        terms=records, full_entry_certified=False, transverse_ledger_debited=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('inventory', 'run'))
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'inventory':
        inventory(args.work.resolve(), args.out.resolve())
    else:
        run(args.evidence_root.resolve(), args.work.resolve(), args.out.resolve())
