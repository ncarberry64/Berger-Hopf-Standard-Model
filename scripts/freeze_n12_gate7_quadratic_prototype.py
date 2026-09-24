"""Materialize compact prototype evidence twice; never run scientific producers."""
import argparse
import gzip
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from flint import arb,ctx,fmpq
from bhsm.interface.shared_expression_graph import restore
from bhsm.interface.sparse_quadratic_enclosure import QuadraticDomain
from bhsm.interface.quadratic_group_support import grouped_range
SOURCES=[
    'src/bhsm/interface/sparse_quadratic_enclosure.py',
    'src/bhsm/interface/frozen_quadratic_compiler.py',
    'src/bhsm/interface/quadratic_frontier_cache.py',
    'src/bhsm/interface/shared_quadratic_booking.py',
    'src/bhsm/interface/block_quadratic_expansion.py',
    'src/bhsm/interface/quadratic_group_support.py',
    'src/bhsm/interface/quadratic_circuit_identity.py',
    'scripts/index_n12_gate7_frozen_quadratic_graph.py',
    'scripts/prototype_n12_gate7_sparse_quadratic.py',
    'scripts/screen_n12_gate7_quadratic_targets.py',
    'scripts/checkpoint_n12_gate7_quadratic_worker.py',
    'scripts/support_n12_gate7_quadratic_checkpoint.py',
    'scripts/reuse_n12_gate7_descriptor_support.py',
    'scripts/freeze_n12_gate7_quadratic_prototype.py',
    'tests/test_sparse_quadratic_enclosure.py',
]


def encoded(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
def sha(value):return hashlib.sha256(value).hexdigest().upper()


def materialize(args):
    descriptor=json.loads(args.descriptor.read_bytes())
    targets=json.loads(args.targets.read_bytes())
    screen=json.loads(args.screen.read_bytes())
    first=descriptor['dominant_descriptor_combined']
    second=targets['dominant_descriptor_combined']
    # The full selected pass independently repeats the descriptor ancestors.
    # Scalar tail equality is checked separately from output expansion, which
    # may use two outward accumulation orders (scalar and block).
    checkpoint=args.checkpoint.read_bytes();repeat=args.repeat_checkpoint.read_bytes()
    if checkpoint!=repeat or sha(checkpoint)!=descriptor['checkpoint_SHA256']:
        raise ValueError('independent descriptor forward checkpoints must be byte-identical')
    tail_classes_equal=all(
        descriptor['descriptor_assignments'][n]['residual_sources']==targets['descriptor_assignments'][n]['residual_sources']
        for n in descriptor['descriptor_assignments'])
    if not tail_classes_equal:raise ValueError('independent per-assignment tail classes changed')
    target_checkpoint=args.target_checkpoint.read_bytes()
    target_forward=json.loads(target_checkpoint);descriptor_forward=json.loads(checkpoint)
    for name in descriptor_forward['models']:
        for key in ('c','a','qb','tails'):
            if descriptor_forward['models'][name][key]!=target_forward['models'][name][key]:
                raise ValueError('selected forward checkpoint changed a descriptor model')
    roots=json.loads(gzip.open(ROOT/'artifacts/flagship_integration/gate7_shared_models_20260924/models/middle/metadata.json.gz','rt').read())['roots']
    coefficients={}
    ctx.prec=512
    domain=QuadraticDomain([tuple(g) for g in descriptor['groups']],len(descriptor['parameter_order']))
    def supported_summary(model):
        result={k:v for k,v in model.items() if k!='quadratic'}
        interval,blocks=grouped_range(domain,restore(model['c']),
            {i:restore(v) for i,v in model['a']},{(i,j):restore(v) for i,j,v in model['quadratic']})
        support=(abs(interval).upper()+arb(fmpq(model['residual_scalar_tail']))).upper()
        result.update(support_upper=str(support.fmpq()),support_approximate=float(support),blocks=blocks)
        return result
    summary={k:v for k,v in descriptor.items() if k not in ('descriptor_assignments','dominant_descriptor_combined')}
    summary['descriptor_assignments']={}
    for name,model in descriptor['descriptor_assignments'].items():
        node=roots[name]
        coefficients[str(node)]=dict(c=model['c'],a=model['a'],quadratic=model['quadratic'])
        summary['descriptor_assignments'][name]=supported_summary(model)
        summary['descriptor_assignments'][name]['frozen_node']=node
    coefficients['combined']=dict(c=first['c'],a=first['a'],quadratic=first['quadratic'])
    summary['dominant_descriptor_combined']=supported_summary(first)
    summary['reduction_factor']=float(arb(fmpq(summary['OLD_sum_frozen_affine_scalar_tails']))
                                      /arb(fmpq(summary['dominant_descriptor_combined']['support_upper'])))
    summary['coefficient_archive']='descriptor_coefficients.json.gz'
    summary['selected_target_compile_stats']=targets['stats']
    summary['independent_descriptor_forward_checkpoints_byte_identical']=True
    summary['independent_descriptor_tail_classes_byte_identical']=True
    packet=dict(parameter_order=descriptor['parameter_order'],groups=descriptor['groups'],models=coefficients)
    buffer=io.BytesIO()
    with gzip.GzipFile(filename='',mode='wb',fileobj=buffer,mtime=0) as z:z.write(encoded(packet))
    output={'prototype.json':encoded(summary),'descriptor_coefficients.json.gz':buffer.getvalue(),
            'selected_screen.json':args.screen.read_bytes(),
            'selected_polynomial.json.gz':args.screen.with_name(args.screen.stem+'_polynomial.json.gz').read_bytes(),
            'descriptor_forward_checkpoint.json':checkpoint,
            'selection.json':encoded({n:roots[n] for n in targets['target_circuit_models']}),
            'selected_scalar_tails.json':encoded({n:row['tails'] for n,row in targets['target_circuit_models'].items()})}
    packed=io.BytesIO()
    with gzip.GzipFile(filename='',mode='wb',fileobj=packed,mtime=0) as z:z.write(target_checkpoint)
    output['selected_forward_checkpoint.json.gz']=packed.getvalue()
    if targets.get('descriptor_support_reused_after_exact_circuit_identity'):
        reuse_path=args.targets.with_name(args.targets.stem+'_reuse_proof.json')
        proof_bytes=reuse_path.read_bytes();proof=json.loads(proof_bytes)
        if (sha(proof_bytes)!=targets['reuse_proof_SHA256'] or not proof['verified']
                or proof['descriptor_checkpoint_SHA256']!=sha(checkpoint)
                or proof['target_checkpoint_SHA256']!=sha(target_checkpoint)):
            raise ValueError('exact circuit-reuse evidence mismatch')
        output['descriptor_support_reuse_proof.json']=proof_bytes
    for name in SOURCES:output['source_capsule/'+name]=(ROOT/name).read_bytes()
    output['reproduction.json']=encoded(dict(
        frozen_checkpoint='cef38b6b',scientific_producers_run=False,
        descriptor_input_SHA256=sha(args.descriptor.read_bytes()),
        targets_input_SHA256=sha(args.targets.read_bytes()),screen_input_SHA256=sha(args.screen.read_bytes()),
        independent_descriptor_forward_checkpoints_byte_identical=True,
        independent_descriptor_tail_classes_byte_identical=True,
        numerical_forward_passes=dict(descriptor=3,complete_selected_targets=1),
        materialization_repeated=True,materialization_byte_identical=True,
        note='Two descriptor-only forward passes and the selected-target pass share the descriptor ancestors. Only one full selected-target forward pass was run.'))
    output['manifest.json']=encoded(dict(format='FROZEN_QUADRATIC_PROTOTYPE_PACKAGE_V1',
        files={n:dict(bytes=len(b),SHA256=sha(b)) for n,b in sorted(output.items())}))
    return output


def main():
    p=argparse.ArgumentParser()
    for name in ('descriptor','targets','screen','checkpoint','repeat-checkpoint','target-checkpoint','out'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    first=materialize(args);second=materialize(args)
    if first!=second:raise ValueError('non-deterministic materialization')
    args.out.mkdir(parents=True,exist_ok=True)
    for name,data in first.items():
        path=args.out/name;path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.read_bytes()!=data:raise FileExistsError('different retained artifact '+str(path))
        path.write_bytes(data)
    print(json.dumps(dict(files=len(first),bytes=sum(map(len,first.values())),byte_identical=True)))


if __name__=='__main__':main()
