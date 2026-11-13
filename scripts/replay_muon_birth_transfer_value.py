"""Evaluate retained E1/C2 reset values and expose the first unavailable trace."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT))

from bhsm.interface.muon_birth_transfer_value import (  # noqa: E402
    ARTIFACT_DIRECTORY, evaluate_muon_birth_transfer_value,
)
from scripts.audit_ae4_support_loss_classical_realization import canonical_bytes  # noqa: E402
from scripts.audit_ae4_branch_relative_support_transition import (  # noqa: E402
    referenced_paths, referenced_records, verify_retained_hashes, verify_source_references,
)


def expanded_citations(value):
    """Convert the sector receipt's multi-symbol bounds to AST citations."""
    refs=[]
    if isinstance(value,dict):
        if value.get('path','').endswith('.py'):
            for symbol, bounds in value.get('symbols',{}).items():
                refs.append(dict(path=value['path'],symbol=symbol,
                                 lines=[bounds['start_line'],bounds['end_line']]))
        for item in value.values():
            refs.extend(expanded_citations(item))
    elif isinstance(value,list):
        for item in value:
            refs.extend(expanded_citations(item))
    return refs


def materialize(output: Path):
    value = evaluate_muon_birth_transfer_value(ROOT)
    report = value.report()
    checked, external = verify_retained_hashes(report)
    citations = verify_source_references([report,expanded_citations(report)])
    external_checked=[]
    for ref in referenced_records(report):
        file=Path(ref['path'])
        if file.is_absolute() and ref.get('sha256') and file.is_file():
            data=file.read_bytes()
            if sha256(data).hexdigest()!=ref['sha256']:
                raise ValueError('external numerical input identity mismatch: '+str(file))
            external_checked.append(dict(path=str(file),bytes=len(data),sha256=ref['sha256'],
                scope='Existing operator/metadata evidence only; not a supplied E1 fermion trace'))
    paths = referenced_paths(report)
    paths.update((
        'src/bhsm/interface/muon_birth_reset_evaluation.py',
        'src/bhsm/interface/muon_birth_transfer_value.py',
        'scripts/replay_muon_birth_transfer_value.py',
        'tests/test_muon_birth_transfer_value.py',
        'theory/muon_birth_transfer_value_20261008.md',
        ARTIFACT_DIRECTORY+'/muon_transport/numerical_input_receipt.json',
        ARTIFACT_DIRECTORY+'/sector_values/value_input_receipt.json',
    ))
    # Hash every actually loaded BHSM numerical dependency, not just the
    # public entry point. No numerical action is executed by this loop.
    for module in tuple(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path:
            file = Path(path).resolve()
            try:
                relative = file.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if relative.startswith('src/bhsm/') and file.suffix=='.py':
                paths.add(relative)
    identities = []
    for path in sorted(paths):
        data = (ROOT/path).read_bytes()
        convention = 'raw_binary'
        if Path(path).suffix in {'.py','.json','.md','.txt'}:
            data = data.replace(b'\r\n',b'\n')
            convention = 'canonical_LF_text'
        identities.append(dict(path=path, bytes=len(data), sha256=sha256(data).hexdigest(),
                               hash_convention=convention))
    manifest = dict(classification='MUON_BIRTH_TRANSFER_VALUE_SOURCE_MANIFEST',
                    source_input_identities=identities, checked_retained_identities=checked,
                    verified_citations=citations, contextual_external_references=external,
                    checked_external_input_identities=external_checked,
                    retained_reset_directly_evaluated=True, trajectories=0,new_root_solves=0,
                    semantic_owner_changes=0,old_controls_run=0)
    output.mkdir(parents=True,exist_ok=True)
    hashes = {}
    for name, payload in {'transfer_value':report,'source_manifest':manifest}.items():
        data = canonical_bytes(payload)
        filename = name+'.json'
        (output/filename).write_bytes(data)
        hashes[filename] = dict(bytes=len(data),sha256=sha256(data).hexdigest())
    (output/'output_hashes.json').write_bytes(canonical_bytes(hashes))
    return dict(products=hashes, selected_event_index=23, selected_child_index=24,
                reset_l2_norm=report['reset_residual_norm_or_component_enclosures']['l2_norm'],
                reset_max_abs=report['reset_residual_norm_or_component_enclosures']['max_abs'],
                physical_muon_birth_transfer_identified=False,
                first_unavailable_numerical_operand=report['first_unavailable_numerical_operand']['id'],
                source_input_files=len(identities), checked_retained_identities=len(checked),
                verified_Python_citations=len(citations))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True,type=Path)
    args = parser.parse_args()
    print(json.dumps(materialize(args.out),sort_keys=True))


if __name__=='__main__':
    main()
