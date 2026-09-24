"""Canonical complete-rate assembly from already certified action balls.

This stage performs no action evaluation. First and repeat each consume their
own independently generated cache. Every cache value follows the same saved
midpoint/radius -> outward Arb decoding path before algebraic assembly, so
fresh in-memory and reloaded balls cannot be mixed in one certificate.
"""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_complete_endpoint_rate_jet as producer

base = producer.base


def require_completed_cache(work):
    manifest = {}
    for receipt_path in sorted((work/'completed').glob('*.json')):
        receipt = json.loads(receipt_path.read_bytes())
        path = work/receipt_path.name
        if (not receipt['completed'] or receipt['key'] != path.stem
                or base.sha(path) != receipt['payload_SHA256']):
            raise ValueError('complete hash-bound action block required')
        manifest[path.stem] = receipt['payload_SHA256']
    if len(manifest) != 19:
        raise ValueError('all 19 endpoint-19 action blocks must already exist')
    return manifest


def forbid_action_evaluation(*args, **kwargs):
    raise RuntimeError('canonical assembly cannot run a missing action contraction')


def run(evidence, work, out):
    manifest = require_completed_cache(work)
    original = base.contract
    try:
        base.contract = forbid_action_evaluation
        producer.run(evidence, work, out)
    finally:
        base.contract = original
    result = json.loads(out.read_bytes())
    used = {item['key']: item['SHA256'] for item in result['new_contraction_receipts']}
    if used != manifest:
        raise ArithmeticError('assembly did not consume exactly the completed cache')
    result.update(
        canonical_assembly_only=True,
        action_contractions_recomputed=False,
        certificate_representation='PERSISTED_EXACT_MIDPOINT_RADIUS_BALLS_OUTWARD_DECODED_BEFORE_ASSEMBLY',
        canonical_rounding='Arb512 arithmetic; the existing exact rational midpoint/radius decoder is applied to every action value before use. No decimal tolerance or threshold snapping.',
        action_cache_manifest_SHA256=base.digest(manifest),
        action_cache_manifest=manifest)
    result['source_SHA256'][str(Path(__file__).resolve())] = base.sha(Path(__file__))
    pending = out.with_suffix('.pending')
    pending.write_bytes(base.encode(result))
    os.replace(pending, out)
    print(json.dumps(dict(canonical_certificate_SHA256=base.sha(out),
        action_contractions_recomputed=False, completed_action_blocks=len(manifest))))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--evidence-root', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    run(a.evidence_root.resolve(), a.work.resolve(), a.out.resolve())
