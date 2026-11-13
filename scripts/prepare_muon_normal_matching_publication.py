"""Select the executed normal-source applications and existing verification.

This only packages explicit receipts and their current pins. It neither
reruns production nor certifies physical matching or a Pauli observable.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]


def prepare(linked_manifest, output):
    out = (ROOT/output).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise ValueError('new explicit publication folder inside this checkout required')
    files, pins, commands = {}, {}, []

    def add(path, expected=None):
        p = (ROOT/path).resolve()
        if not p.is_relative_to(ROOT) or not p.is_file():
            raise ValueError('explicit existing checkout file required: '+str(path))
        data = p.read_bytes()
        value = sha256(data).hexdigest()
        if expected is not None and value != expected:
            raise ValueError('executed evidence changed: '+str(path))
        if len(data) >= 10*1024**2:
            raise ValueError('split scientific publication member required: '+str(path))
        files[p.relative_to(ROOT).as_posix()] = dict(bytes=len(data), sha256=value)
        if p.name == 'result.json':
            d = json.loads(data)
            for name, digest in d.get('input_hashes', {}).items():
                if name in pins and pins[name] != digest:
                    raise ValueError('root input disagreement: '+name)
                pins[name] = digest
        return p

    # Actual tested/replayed root calculations, not a sweep of artifacts.
    folders = (
        'artifacts/muon_mixed_changing_birth_action_20261012/run_6',
        'artifacts/muon_mixed_changing_birth_action_20261012/executed_final_pair',
        'artifacts/muon_stored_fiber_canonical_tangent_20261012/run_2',
        'artifacts/muon_stored_fiber_canonical_tangent_20261012/pair_verification',
        'artifacts/muon_corrected_finite_fiber_work_20261012/run_3',
        'artifacts/muon_coupled_birth_full_application_20261012/run_1',
        'artifacts/muon_positive_parent_material_control_20261012/run_1',
        'artifacts/muon_coupled_birth_matching_verification_20261012',
        'artifacts/muon_coupled_birth_matching_accounting_20261012',
    )
    for folder in folders:
        for p in sorted((ROOT/folder).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                add(p.relative_to(ROOT))
    add('artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/result.json')
    for rel in (
        'artifacts/muon_mixed_changing_birth_action_20261012/executed_final_pair/verification.json',
        'artifacts/muon_coupled_birth_matching_verification_20261012/run_1/verification.json',
        'artifacts/muon_stored_fiber_canonical_tangent_20261012/pair_verification/verification.json',
    ):
        d = json.loads((ROOT/rel).read_bytes())
        commands.extend(d['commands'])
        for name, digest in d.get('checked_source_hashes', {}).items():
            add(name, digest)
    for name, digest in pins.items():
        if sha256((ROOT/name).read_bytes()).hexdigest() != digest:
            raise ValueError('root action/input changed: '+name)
    out.mkdir(parents=True)
    root_manifest = out/'root_publication_manifest.json'
    root_manifest.write_text(json.dumps(dict(
        classification='VERIFIED_EXPLICIT_EXECUTED_ROOT_ACTION_AND_CONTROL_MEMBERS',
        files=files, input_hashes=pins, commands=commands,
        all_physical_observable_outputs_unadmitted=True,
        error_scope='Existing executed action/arithmetic controls and focused verification only; no new solve, complete ancestor regeneration or observable enclosure.'
    ), sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')
    manifests = [
        root_manifest.relative_to(ROOT).as_posix(),
        'artifacts/muon_sigma_normal_consumption_20261012/pair_verification/publication_manifest.json',
        'artifacts/muon_actual_shape_source_final_pairs_20261012/publication_manifest.json',
        'artifacts/muon_d5_actual_shape_source_20261012/pair_verification/publication_manifest.json',
        'artifacts/muon_induced_d5_shape_poisson_20261013/pair_verification/publication_manifest.json',
        'artifacts/muon_incoming_born_shape_pairs_20261013/publication_manifest.json',
        Path(linked_manifest).as_posix(),
    ]
    hashes = {p:sha256((ROOT/p).read_bytes()).hexdigest() for p in manifests}
    spec = dict(manifests=manifests, manifest_hashes=hashes, commands=commands,
        additional_files=[
            'theory/muon_coupled_birth_normal_domain_matching_20261012.md',
            'artifacts/muon_observable_combination_20261011/contribution_error_table.json',
            'artifacts/muon_observable_combination_20261011/contribution_error_table.md',
            Path(__file__).relative_to(ROOT).as_posix(),
            'scripts/update_muon_coupled_birth_matching_accounting.py',
            'scripts/advance_muon_coupled_birth_matching_accounting.py',
            'scripts/record_muon_matching_publication_audits.py',
        ],
        frozen_predictions={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ('docs/frozen_predictions.md','docs/frozen_predictions.json')},
        classifications=dict(
            DERIVED='Source-completed weak normal and common-port/adjoint contraction laws.',
            EVALUATED='Incoming own/child forced action, conditional linked birth and same-background field consumption.',
            CONTROL_ONLY='Unselected trial amplitude, computational far-Cauchy and held-coordinate inverse domains.',
            UNEVALUATED='Complete natural/base/formation/cutoff/exterior matching, pole and normalized native Pauli observable.',
            OWNER_DEFINITION_GAP='None established; the precise remaining action BVP/application is unimplemented.'
        ))
    path = out/'specification.json'
    path.write_text(json.dumps(spec, sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(root_members=len(files), root_pins=len(pins), manifests=len(manifests),
        specification=path.relative_to(ROOT).as_posix(), specification_sha256=sha256(path.read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--linked-manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.linked_manifest, args.output)
