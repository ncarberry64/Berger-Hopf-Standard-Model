"""Retain a user-requested Git stopping point before signed target support."""
import gzip
import hashlib
import json
from pathlib import Path
from freeze_n12_gate7_quadratic_prototype import SOURCES

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'tmp/gate7_quadratic_20260924'
OUT=ROOT/'artifacts/flagship_integration/gate7_quadratic_models_20260924'


def sha(b):return hashlib.sha256(b).hexdigest().upper()
def encode(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()


def materialize():
    first=(WORK/'descriptor_first/compiled_roots.json').read_bytes()
    repeat=(WORK/'descriptor_repeat/compiled_roots.json').read_bytes()
    if first!=repeat:raise ValueError('independent descriptor checkpoints differ')
    raw=(WORK/'descriptor_supported.json').read_bytes();report=json.loads(raw)
    if report['checkpoint_SHA256']!=sha(first):raise ValueError('descriptor binding mismatch')
    target=(WORK/'targets_first/compiled_roots.json').read_bytes()
    saved=json.loads(target);reference=json.loads(first)
    for name,row in reference['models'].items():
        for key in ('c','a','qb','tails'):
            if row[key]!=saved['models'][name][key]:raise ValueError('target descriptor forward mismatch')
    if saved['stats']['selected_nodes']!=3607128 or len(saved['models'])!=405:
        raise ValueError('selected forward compilation incomplete')
    output={
        'descriptor_supported.json.gz':gzip.compress(raw,mtime=0),
        'descriptor_forward_checkpoint.json':first,
        'selected_forward_checkpoint.json.gz':gzip.compress(target,mtime=0),
        'descriptor_metrics.json':(WORK/'descriptor_metrics.json').read_bytes(),
        'selected_scalar_tails.json':encode({n:r['tails'] for n,r in saved['models'].items()}),
        'selection.json':encode(sorted(saved['models'])),
        'checkpoint.json':encode(dict(
            frozen_checkpoint='cef38b6b',Gate7_closed=False,physical_budget_debit=False,
            scientific_producers_run=False,full_kappa_recomputed=False,
            reason='User requested a clean Git update point at 10% remaining usage.',
            descriptor_OLD=report['OLD_approximate'],descriptor_NEW_upper_rounded=5.004286125,
            descriptor_monomials=22500,classification='CASE_1 = NUMERICAL_COMPILER_CORRELATION_LOSS',
            descriptor_forward_reproduced_byte_identically=True,
            descriptor_checkpoint_SHA256=sha(first),selected_checkpoint_SHA256=sha(target),
            selected_forward_stats=saved['stats'],selected_named_targets=405,
            signed_booking_screen_complete=False,booking_cancellation='NOT_YET_MEASURED',
            selected_circuit_cache='tmp/gate7_quadratic_20260924/targets_first/quadratics.sqlite',
            descriptor_circuit_cache='tmp/gate7_quadratic_20260924/descriptor_repeat/quadratics.sqlite',
            caches_retained_locally_not_in_git=True,
            next_steps=['Verify descriptor numerical circuit reuse with reuse_n12_gate7_descriptor_support.py.',
                        'Run screen_n12_gate7_quadratic_targets.py from the completed selected checkpoint.',
                        'Record signed LL/LT cancellation and projected residual ledger; do not expand full interval DAG.'],
            missing_object='shared mixed bordered-resolvent correction jet preserving u/v and common-border row coupling'))}
    for name in SOURCES+['scripts/freeze_n12_gate7_quadratic_pause.py']:
        output['source_capsule/'+name]=(ROOT/name).read_bytes()
    output['manifest.json']=encode(dict(format='FROZEN_QUADRATIC_PAUSE_CHECKPOINT_V1',
        materialized_twice_byte_identically=True,
        files={n:dict(bytes=len(b),SHA256=sha(b)) for n,b in sorted(output.items())}))
    return output


def main():
    first=materialize();second=materialize()
    if first!=second:raise ValueError('non-deterministic checkpoint materialization')
    for name,data in first.items():
        path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.read_bytes()!=data:raise FileExistsError(path)
        path.write_bytes(data)
    print(json.dumps(dict(files=len(first),bytes=sum(map(len,first.values())),byte_identical=True)))


if __name__=='__main__':main()
