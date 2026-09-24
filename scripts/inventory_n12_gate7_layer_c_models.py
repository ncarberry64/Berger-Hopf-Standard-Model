"""Inspect retained Layer-C schemas and border positivity without action calls."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from flint import arb, ctx, fmpq

ROOT = Path(__file__).resolve().parents[1]


def run(out):
    if out.exists():
        raise FileExistsError('fresh output required')
    ctx.prec = 512
    sources = {}
    def bind(p):
        sources[str(p.resolve())] = hashlib.sha256(p.read_bytes()).hexdigest().upper()
        return p
    def read(p):
        return json.loads(bind(p).read_bytes())
    package = ROOT/'artifacts/flagship_integration/gate7_physical_tube_20260924/rate_and_remainder'
    sites = []
    for site in ('left', 'middle', 'right'):
        z = read(package/f'interval13_inherited2rate_{site}_first.json')
        path = next(Path(p) for p in z['source_SHA256'] if p.endswith('value.npz'))
        if hashlib.sha256(path.read_bytes()).hexdigest().upper() != z['source_SHA256'][str(path)]:
            raise ValueError('frozen value source changed')
        with np.load(bind(path), allow_pickle=False) as data:
            m, r = data['response_box_mid_q'][-1], data['response_box_rad_q'][-1]
            b = arb(fmpq(str(m))) + arb(0, arb(fmpq(str(r))))
        sites.append(dict(site=site,rate_keys=sorted(z['rate_jets']),
            components_per_jet={k:len(v) for k,v in z['rate_jets'].items()},
            complete_mixed_shared_coefficients_serialized=False,
            positive_primal_border_proved=bool(b.lower()>0),
            border_lower_exact=str(b.lower().fmpq()),border_upper_exact=str(b.upper().fmpq()),
            border_lower_approximate=float(b.lower()),
            retained_rate_schema='coordinate midpoint/radius pairs, no parameter coefficients'))
    archives = []
    for relative in ('tmp/gate7_shared_action_20260919/endpoint_first.json',
                     'tmp/gate7_shared_action_20260919/midpoint_v3.json',
                     'artifacts/flagship_integration/gate7_mixed_response_20260923/certificate.json',
                     'artifacts/flagship_integration/gate7_complete_rate_20260923/certificate.json'):
        z = read(ROOT/relative)
        archives.append(dict(path=relative,endpoint=z.get('endpoint'),family=z.get('family'),
            parameters=z.get('parameters'),algorithm=z.get('algorithm'),
            missing=z.get('missing'),covector_kind=z.get('covector_kind'),
            full_stacked_adjoint_certified=z.get('full_stacked_adjoint_certified'),
            eligible_as_interval13_complete_mixed_graph=False,
            exclusion=('First-order covector residual proposal; no complete mixed physical joint graph.'
                if relative.startswith('tmp/') else 'Endpoint-19 domain; no interval-13 promotion authority.')))
    bind(Path(__file__))
    result = dict(algorithm='INTERVAL13_RETAINED_MODEL_SCHEMA_AUDIT_V1',
        frozen_checkpoint='baf41b96',sites=sites,inspected_archives=archives,
        scope='Explicit retained packages listed here; not a claim about unavailable external archives.',
        complete_interval13_shared_mixed_graph_found=False,
        discarded_evaluator_cache_recoverable_from_rate_balls=False,
        new_action_evaluations=0,physical_budget_debit=False,Gate7_closed=False,source_SHA256=sources)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes((json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps(dict(border_lower=[s['border_lower_approximate'] for s in sites],
                         complete_graph_found=False)))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    run(p.parse_args().out.resolve())
