"""Materialize the inspected definition contract; run no numerical producer."""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from bhsm.interface.ae4_support_loss_classical_realization import (  # noqa: E402
    ARTIFACT_DIRECTORY, inspected_support_loss_realization,
)


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode('utf8')


def source_paths(value):
    """Find exact repository file references in the reviewed provenance."""
    paths = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ('path', 'source_path') and isinstance(item, str):
                paths.add(item)
            else:
                paths.update(source_paths(item))
    elif isinstance(value, list):
        for item in value:
            paths.update(source_paths(item))
    return paths


def source_references(value):
    """Collect concrete Python symbol/line references from the reviewed audit."""
    refs = []
    if isinstance(value, dict):
        path = value.get('path', value.get('source_path'))
        symbol = value.get('symbol')
        lines = value.get('lines', value.get('line_refs'))
        if lines is None and 'start_line' in value and 'end_line' in value:
            lines = [value['start_line'], value['end_line']]
        if isinstance(path, str) and path.endswith('.py') and symbol and lines:
            ref = dict(path=path, symbol=symbol, lines=lines)
            if 'canonical_LF_sha256' in value:
                ref['canonical_LF_sha256'] = value['canonical_LF_sha256']
            refs.append(ref)
        for item in value.values():
            refs.extend(source_references(item))
    elif isinstance(value, list):
        for item in value:
            refs.extend(source_references(item))
    return refs


def verify_source_references(audits):
    """Verify cited symbols/line bounds with AST; execute no owner functions."""
    unique = {}
    for ref in source_references(audits):
        unique[json.dumps(ref, sort_keys=True)] = ref
    verified = []
    parsed = {}
    for key in sorted(unique):
        ref = unique[key]
        path = ref['path']
        if 'canonical_LF_sha256' in ref:
            digest = sha256((ROOT / path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
            if digest != ref['canonical_LF_sha256']:
                raise ValueError('reviewed producer source hash changed: ' + path)
        if path not in parsed:
            parsed[path] = ast.parse((ROOT / path).read_text(encoding='utf8'))
        # A reviewed equation group may cite several functions in one file.
        # Every cited line must belong to one of those declared symbols.
        symbols = [item.strip() for item in ref['symbol'].split(';')]
        spans = []
        for symbol in symbols:
            if symbol == 'module owner statement':
                first = parsed[path].body[0]
                if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                        and isinstance(first.value.value, str)):
                    spans.append((symbol, first.lineno, first.end_lineno))
            else:
                spans.extend((symbol, node.lineno, node.end_lineno)
                             for node in ast.walk(parsed[path])
                             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                             and node.name == symbol.split('.')[-1])
        if not all(any(start <= line <= end for _, start, end in spans)
                   for line in ref['lines']):
            raise ValueError('cited symbol/line reference no longer valid: ' + str(ref))
        verified.append(dict(**ref, status='EVALUATED__AST_SYMBOL_AND_LINE_BOUNDS_VERIFIED',
                             declared_symbol_spans=[dict(symbol=symbol, start_line=start, end_line=end)
                                                    for symbol, start, end in spans]))
    return verified


def materialize(output: Path):
    """Bind the contract and hash its inspected sources without executing them."""
    realization = inspected_support_loss_realization(ROOT)
    audits = [realization.classical_audit, realization.outward_audit, realization.physical_audit]
    paths = source_paths(audits)
    references = verify_source_references(audits)
    paths.update((
        'src/bhsm/interface/ae4_support_loss_classical_realization.py',
        'tests/test_ae4_support_loss_classical_realization.py',
        'scripts/audit_ae4_support_loss_classical_realization.py',
        'theory/ae4_support_loss_classical_realization_20261007.md',
        ARTIFACT_DIRECTORY + '/classical_owner_audit.json',
        ARTIFACT_DIRECTORY + '/outward_support_audit.json',
        ARTIFACT_DIRECTORY + '/physical_questions_audit.json',
    ))
    hashes = []
    for relative in sorted(paths):
        path = ROOT / relative
        # Canonical LF text hashes survive the repository's Windows checkout
        # conversion. The historical NPZ is neither loaded nor regenerated.
        data = path.read_bytes().replace(b'\r\n', b'\n')
        hashes.append(dict(path=relative, canonical_LF_bytes=len(data),
                           canonical_LF_sha256=sha256(data).hexdigest()))
    report = realization.report()
    manifest = dict(classification='SUPPORT_LOSS_DEFINITION_AUDIT_SOURCE_MANIFEST',
                    hash_convention='UTF-8 source bytes with CRLF normalized to LF',
                    numerical_producers_executed=False,
                    historical_arrays_loaded=False, sources=hashes,
                    verified_source_references=references)
    output.mkdir(parents=True, exist_ok=True)
    products = dict(realization_report=report, source_manifest=manifest)
    product_hashes = {}
    for name, payload in products.items():
        data = canonical_bytes(payload)
        filename = name + '.json'
        (output / filename).write_bytes(data)
        product_hashes[filename] = dict(bytes=len(data), sha256=sha256(data).hexdigest())
    (output / 'output_hashes.json').write_bytes(canonical_bytes(product_hashes))
    return product_hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(materialize(args.out), sort_keys=True))


if __name__ == '__main__':
    main()
