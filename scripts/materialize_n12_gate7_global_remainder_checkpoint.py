"""Reproduce the global checkpoint from the consolidated evidence receipt.

No frozen producer, imported numerical campaign, or recursive hash audit runs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.global_physical_remainder_checkpoint import evaluate

PACKAGE = ROOT/'artifacts/flagship_integration/gate7_global_checkpoint_20260923'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main(out):
    ledger_path = PACKAGE/'current_history_budget.json'
    inventory_path = PACKAGE/'evidence_inventory.json'
    ledger = json.loads(ledger_path.read_bytes())
    inventory = json.loads(inventory_path.read_bytes())
    result = evaluate(ledger, sha(ledger_path))
    result.update(evidence_inventory_SHA256=sha(inventory_path),
        coverage_summary=inventory['coverage_summary'],
        source_SHA256={p.relative_to(ROOT).as_posix():sha(p) for p in
            (ledger_path, inventory_path, Path(__file__),
             ROOT/'src/bhsm/interface/global_physical_remainder_checkpoint.py')},
        frozen_calculations_recomputed=False,
        endpoint071_diagnostic_excluded=True,
        historical_uniform_cap_substituted=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('xb') as stream:
        stream.write((json.dumps(result, sort_keys=True, indent=2)+'\n').encode())
    print(json.dumps(dict(classification=result['classification'],
        strict_kappa_targets=[k['lower'] for k in result['uniform_kappa_strict_targets']],
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
