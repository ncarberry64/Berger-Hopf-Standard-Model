"""Materialize the branch-birth audit from retained evidence; no producer replay."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT))

from bhsm.interface.ae4_branch_relative_support_transition import (  # noqa: E402
    ARTIFACT_DIRECTORY, current_muon_birth_realization,
)
from scripts.audit_ae4_support_loss_classical_realization import (  # noqa: E402
    canonical_bytes, verify_source_references,
)

PREFIXES = ('src/', 'scripts/', 'tests/', 'theory/', 'artifacts/')
TEXT_SUFFIXES = {'.py', '.md', '.json', '.toml', '.txt', '.csv'}


def referenced_records(value):
    """Collect explicit citation records, including path-keyed receipt maps."""
    records = []
    if isinstance(value, dict):
        path = value.get('path', value.get('source_path'))
        if isinstance(path, str):
            records.append(dict(value, path=path))
        for key, item in value.items():
            if key.startswith(PREFIXES) and isinstance(item, dict):
                records.append(dict(item, path=key))
            records.extend(referenced_records(item))
    elif isinstance(value, list):
        for item in value:
            records.extend(referenced_records(item))
    return records


def referenced_paths(value):
    """Find retained repository paths without interpreting array contents."""
    paths = set()
    if isinstance(value, str) and value.startswith(PREFIXES) and (ROOT / value).is_file():
        paths.add(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            paths.update(referenced_paths(key))
            paths.update(referenced_paths(item))
    elif isinstance(value, list):
        for item in value:
            paths.update(referenced_paths(item))
    return paths


def verify_retained_hashes(audits):
    """Check cited identities; canonicalize only source text, never NPZ bytes.

    Some reused raw-text receipts were made on Windows. Their historical
    hashes are checked against raw/LF/CRLF encodings of identical text, with
    the matching convention recorded. New source identities use canonical LF.
    """
    checked = {}
    external = []
    for ref in referenced_records(audits):
        path = ref['path']
        if not path.startswith(PREFIXES):
            external.append(dict(path=path, status='HISTORICAL_EXTERNAL_DELIVERY_REFERENCE_ONLY',
                                 repository_equivalent=ref.get('repository_equivalent')))
            continue
        data = (ROOT / path).read_bytes()
        expected = ref.get('canonical_LF_sha256', ref.get('sha256'))
        if not expected:
            continue
        candidates = {'raw': data}
        if Path(path).suffix in TEXT_SUFFIXES:
            lf = data.replace(b'\r\n', b'\n')
            candidates.update(canonical_LF=lf, Windows_CRLF=lf.replace(b'\n', b'\r\n'))
        if 'canonical_LF_sha256' in ref:
            candidates = {'canonical_LF': candidates['canonical_LF']}
        matches = [convention for convention, content in candidates.items()
                   if sha256(content).hexdigest() == expected
                   and ('bytes' not in ref or len(content) == ref['bytes'])]
        if not matches:
            raise ValueError('retained source/artifact identity mismatch: ' + path)
        key = (path, expected)
        checked[key] = dict(path=path, expected_sha256=expected,
                            matching_hash_conventions=matches,
                            status='EVALUATED__RETAINED_BYTES_VERIFIED')
    return [checked[key] for key in sorted(checked)], sorted(external, key=lambda x:x['path'])


def materialize(output: Path):
    report = current_muon_birth_realization(ROOT)
    audits = report['retained_evidence']
    references = verify_source_references(audits)
    checked, external = verify_retained_hashes(audits)
    paths = referenced_paths(report)
    paths.update((
        'src/bhsm/interface/ae4_branch_relative_support_transition.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        'src/bhsm/interface/ae4_support_loss_classical_realization.py',
        'tests/test_ae4_branch_relative_support_transition.py',
        'tests/test_ae4_support_loss_classical_realization.py',
        'tests/test_ae4_mode_frequency_cutoff_owner.py',
        'tests/test_ae4_stratified_dirac_zeta_induced_owner.py',
        'scripts/audit_ae4_branch_relative_support_transition.py',
        'scripts/audit_ae4_support_loss_classical_realization.py',
        'theory/ae4_branch_relative_support_transition_20261008.md',
        'theory/ae4_support_loss_classical_realization_20261007.md',
        *(ARTIFACT_DIRECTORY + '/' + name for name in audits),
    ))
    hashes = []
    for path in sorted(paths):
        data = (ROOT / path).read_bytes()
        convention = 'raw_binary'
        if Path(path).suffix in TEXT_SUFFIXES:
            data = data.replace(b'\r\n', b'\n')
            convention = 'canonical_LF_text'
        hashes.append(dict(path=path, bytes=len(data), sha256=sha256(data).hexdigest(),
                           hash_convention=convention))
    manifest = dict(classification='BRANCH_RELATIVE_SUPPORT_TRANSITION_SOURCE_MANIFEST',
                    sources=hashes, verified_source_references=references,
                    verified_retained_identities=checked, external_reference_scope=external,
                    numerical_producers_executed=False, historical_arrays_loaded=False,
                    binary_bytes_hashed_only=True, old_receipts_regenerated=False)
    output.mkdir(parents=True, exist_ok=True)
    products = dict(realization_report=report, source_manifest=manifest)
    product_hashes = {}
    for name, payload in products.items():
        data = canonical_bytes(payload)
        filename = name + '.json'
        (output / filename).write_bytes(data)
        product_hashes[filename] = dict(bytes=len(data), sha256=sha256(data).hexdigest())
    (output / 'output_hashes.json').write_bytes(canonical_bytes(product_hashes))
    return dict(products=product_hashes, verified_Python_references=len(references),
                retained_hash_identities=len(checked), source_input_files=len(hashes),
                physical_birth_evaluated=False,
                first_missing_operand=report['first_missing_operand']['name'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(materialize(args.out), sort_keys=True))


if __name__ == '__main__':
    main()
