"""Select and verify the reviewed changing-source publication and its pins.

Pair verifiers own numerical replay. This verifier checks their unchanged
files and explicit input pins, records the new evidence, and produces an
explicit Git path list. It does not certify a physical Pauli observable.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    data = path.read_bytes()
    return dict(bytes=len(data), sha256=sha256(data).hexdigest())


def verify(specification, output):
    spec_path = (ROOT/specification).resolve()
    out = (ROOT/output).resolve()
    if not spec_path.is_relative_to(ROOT) or not out.is_relative_to(ROOT) or out.exists():
        raise ValueError('new output and explicit specification within this checkout required')
    spec = json.loads(spec_path.read_bytes())
    selected, manifests, pins = {}, {}, {}

    def add(relative, expected=None):
        path = (ROOT/relative).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError('publication file escapes intended checkout')
        rel = path.relative_to(ROOT).as_posix()
        row = digest(path)
        target = expected.get('sha256') if isinstance(expected, dict) else expected
        if target is not None and row['sha256'] != target:
            raise ValueError('reviewed file or input pin changed: '+rel)
        if row['bytes'] >= 10*1024**2:
            raise ValueError('individual reviewed artifact exceeds publication cap: '+rel)
        selected[rel] = row
        return row

    for rel in spec['manifests']:
        manifests[rel] = add(rel, spec['manifest_hashes'][rel])
        record = json.loads((ROOT/rel).read_bytes())
        key = next((k for k in ('files','selected_files','selected') if k in record), None)
        if key is None:
            raise ValueError('unrecognized explicit manifest membership: '+rel)
        declared = record[key]
        if isinstance(declared, dict):
            members = declared.items()
        elif isinstance(declared, list):
            members = ((row['path'], row) for row in declared)
        else:
            raise ValueError('explicit manifest members must be a map or path records: '+rel)
        for name, expected in members:
            add(name, expected)
        proof = record.get('verification')
        if isinstance(proof,dict) and 'path' in proof:
            add(proof['path'],proof.get('sha256'))
        if 'verification_path' in record:
            add(record['verification_path'],record.get('verification_sha256'))
        manifest_pins = dict(record.get('input_hashes', {}))
        for name, expected in record.get('current_input_pins', {}).items():
            if name in manifest_pins and manifest_pins[name] != expected:
                raise ValueError('manifest current/input pin disagreement: '+name)
            manifest_pins[name] = expected
        for name, expected in record.get('producer_input_hashes', {}).items():
            if name in manifest_pins and manifest_pins[name] != expected:
                raise ValueError('manifest producer/input pin disagreement: '+name)
            manifest_pins[name] = expected
        for name, expected in manifest_pins.items():
            value = expected.get('sha256') if isinstance(expected, dict) else expected
            if name in pins and pins[name] != value:
                raise ValueError('manifest input disagreement: '+name)
            pins[name] = value

    # The result receipts themselves own input pins in several compact
    # manifests. Verify every selected receipt without inventing a clean
    # ancestor regeneration claim. Already tracked pins need no restaging.
    for rel in list(selected):
        if not rel.endswith('/result.json'):
            continue
        record = json.loads((ROOT/rel).read_bytes())
        for name, expected in record.get('input_hashes', {}).items():
            value = expected.get('sha256') if isinstance(expected, dict) else expected
            if name in pins and pins[name] != value:
                raise ValueError('result input disagreement: '+name)
            pins[name] = value
    tracked = set(subprocess.check_output(['git','-c','gc.auto=0','-c',
        'maintenance.auto=false','ls-files','-z'], cwd=ROOT).decode().split('\0'))
    for rel, expected in pins.items():
        observed = digest(ROOT/rel)
        if observed['sha256'] != expected:
            raise ValueError('executed source/input pin changed: '+rel)
        if rel not in tracked:
            add(rel, expected)
    for rel in spec['additional_files']:
        add(rel)
    add(spec_path.relative_to(ROOT).as_posix())
    add(Path(__file__).relative_to(ROOT).as_posix())
    frozen = {rel:digest(ROOT/rel)['sha256'] for rel in
        ('docs/frozen_predictions.md','docs/frozen_predictions.json')}
    if frozen != spec['frozen_predictions']:
        raise ValueError('frozen predictions changed')
    record = dict(classification='VERIFIED_EXPLICIT_CHANGING_SOURCE_PUBLICATION',
        files=selected, manifests=manifests, input_hashes=pins,
        frozen_predictions=frozen, commands=spec['commands'],
        classifications=spec['classifications'],
        physical_native_remainder_or_a_mu_completed=False,
        complete_clean_ancestor_regeneration_proved=False,
        error_scope='pair replay, unchanged input/source pins and explicit publication membership; actual action, temporal/domain, exterior matching, omitted sectors and normalized Pauli uncertainty retain the scope of each scientific application')
    out.mkdir(parents=True)
    path = out/'verification.json'
    path.write_text(json.dumps(record, sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')
    paths = sorted(set(selected)|{path.relative_to(ROOT).as_posix(),
        (out/'selected_paths.nul').relative_to(ROOT).as_posix()})
    (out/'selected_paths.nul').write_bytes(('\0'.join(paths)+'\0').encode())
    print(json.dumps(dict(files=len(selected), pins=len(pins),
        selected_bytes=sum(row['bytes'] for row in selected.values()),
        verification_sha256=digest(path)['sha256'], physical_observable_completed=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--specification', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    verify(args.specification, args.output)
