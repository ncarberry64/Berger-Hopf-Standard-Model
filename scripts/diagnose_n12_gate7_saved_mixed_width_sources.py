"""Attribute saved mixed-Hessian width; midpoint substitutions are not proofs."""
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
        # Conditional midpoint substitutions measure enclosure sensitivity only.
        # They are not bounds on the original physical family and cannot be booked.
        psi = arrays.get('normalization_psi', source['paired']['eigenbox'][:61])
        base = [q*source['paired']['full'][37:74], reduced, psi,
                solved[0][:61, 0], solved[0][-1, 0], source['raw_domain'][98],
                *arrays['descriptor_base'], u, v, uv]
        def centered(x):
            if isinstance(x, dict): return {k:centered(v) for k,v in x.items()}
            a=np.asarray(x,dtype=object)
            r=np.array([v.mid() for v in a.flat],dtype=object).reshape(a.shape)
            return r.item() if a.ndim==0 else r
        cases={}
        for label,indices in [('base_psi',[2]),('base_response',[3,4]),
            ('axis_variations',[8]),('ambient_variations',[9]),('mixed_variations',[10]),
            ('all_base_values',list(range(8)))]:
            inputs=list(base)
            for i in indices: inputs[i]=centered(inputs[i])
            value,_=normalization.normalized_mixed(*inputs,coupled_identities_and_variations=True)
            cases[label]=dict(maximum_output_radius=float(max(v.rad() for v in value.flat)),
                              output58_radius=float(value[58,0].rad()))
        for label,jet_index,fields in [('mixed_line',10,['psi']),
            ('mixed_response',10,['hard','border']),('mixed_scalar',10,['cpsi','remainder']),
            ('axis_response',8,['hard','border']),('ambient_response',9,['hard','border'])]:
            inputs=list(base);inputs[jet_index]=dict(base[jet_index])
            for field in fields: inputs[jet_index][field]=centered(inputs[jet_index][field])
            value,_=normalization.normalized_mixed(*inputs,coupled_identities_and_variations=True)
            cases[label]=dict(maximum_output_radius=float(max(v.rad() for v in value.flat)),
                              output58_radius=float(value[58,0].rad()))
        result=dict(endpoint=record['endpoint'],column=record['column'],cases=cases,
            scope='UNCERTAINTY_ATTRIBUTION_ONLY; MIDPOINT_SUBSTITUTIONS_ARE_NOT_CERTIFICATES',
            new_action_contractions=0,new_implicit_solves=0,ledger_debit_added=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False,
            source_SHA256={str(path):sha(path) for path in
                (saved/'record.json',saved/'hessian.npz',Path(__file__),Path(normalization.__file__))})
        with out.open('x',encoding='utf-8') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
        print(json.dumps(cases))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('snapshot', 'saved', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    main(args.snapshot.resolve(), args.saved.resolve(), args.out.resolve())
