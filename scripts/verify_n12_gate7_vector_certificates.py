"""Replay all stored shared vector supports and reject incomplete certificates."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from flint import arb,arb_mat,ctx
import certify_n12_gate7_projected_vector_lift as common


def validate_rows(models,rows,groups,dimension,field):
    if len(models)!=74 or len(rows)!=74:
        raise ValueError('all 74 projected rows required')
    if [r['component'] for r in rows]!=[f'projected_row_{i:02d}' for i in range(74)]:
        raise ValueError('complete ordered physical rows required')
    domain=common.TaylorDomain([tuple(g) for g in groups],dimension)
    supports=[]
    for values,row in zip(models,rows,strict=True):
        if len(values)!=dimension+2:raise ValueError('all shared coefficients required')
        balls=[common.restore(v) for v in values]
        model=common.Taylor(domain,balls[0],arb_mat(1,dimension,balls[1:-1]),balls[-1])
        bound=model.support()
        if str(bound.fmpq())!=row[field]['exact']:
            raise ArithmeticError('stored support does not replay exactly')
        if str(model.r.fmpq())!=row['nonlinear_remainder']['exact']:
            raise ArithmeticError('nonlinear remainder changed')
        supports.append(bound)
    return common.norm(supports)


def verify(midpoint_path,endpoint_path):
    midpoint=json.loads(midpoint_path.read_bytes())
    endpoint=json.loads(endpoint_path.read_bytes())
    if midpoint['parameters']!=497 or endpoint['parameters']!=323:
        raise ValueError('original midpoint and endpoint parameter dimensions required')
    mnorm=validate_rows(midpoint['shared_models'],midpoint['components'],midpoint['groups'],497,'total_radius')
    archive=endpoint_path.parent/endpoint['shared_models_archive']['file']
    compressed=archive.read_bytes()
    if hashlib.sha256(compressed).hexdigest().upper()!=endpoint['shared_models_archive']['SHA256']:
        raise ValueError('shared coefficient archive changed')
    models=json.loads(gzip.decompress(compressed))
    if len(models['endpoint_raw'])!=99 or any(len(v)!=325 for v in models['endpoint_raw']):
        raise ValueError('all original endpoint rate coordinates required')
    enorm=validate_rows(models['endpoint_projected'],endpoint['components'],endpoint['groups'],323,'total_radius')
    transport=endpoint['transport']
    if transport['endpoint_parameter_embedding']!=[1]+list(range(76,150))+list(range(497,745)):
        raise ValueError('original right-endpoint parameter embedding required')
    tnorm=validate_rows(models['transported_column'],transport['rows'],transport['groups'],745,'norm_support')
    for norm,stored in ((mnorm,midpoint['vector_norm']['anchor_deviation']),
                        (enorm,endpoint['vector_norm']['anchor_deviation']),
                        (tnorm,transport['norm_upper'])):
        if norm>arb(stored['exact']):raise ArithmeticError('vector norm exceeds stored bound')
    if bool(tnorm<1)!=transport['strict_local_gain_below_one']:
        raise ArithmeticError('local gain verdict mismatch')
    if arb(transport['margin_lower_exact'])>1-tnorm:
        raise ArithmeticError('local margin overclaimed')
    if any(r.get('Gate7_closed') or r.get('FULL_BHSM_COMPLETE') for r in (midpoint,endpoint,transport)):
        raise ValueError('one input direction cannot promote a global gate')
    return dict(all_vector_supports_replayed=True,all_endpoint_raw_coordinates_present=True,
        original_parameter_embedding_preserved=True,midpoint_rows=74,endpoint_rows=74,transport_rows=74,
        local_norm_upper=common.upper(tnorm),local_margin_lower_exact=transport['margin_lower_exact'],
        midpoint_SHA256=common.saved.sha(midpoint_path),endpoint_SHA256=common.saved.sha(endpoint_path),
        verifier_SHA256=common.saved.sha(Path(__file__)),Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--midpoint',type=Path,required=True)
    parser.add_argument('--endpoint',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();ctx.prec=512
    result=verify(args.midpoint,args.endpoint)
    with args.out.open('xb') as f:f.write(common.saved.encoded(result))
    print(json.dumps(result))


if __name__=='__main__':main()
