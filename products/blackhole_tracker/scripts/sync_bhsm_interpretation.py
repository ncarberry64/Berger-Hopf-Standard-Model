"""Pin reviewed BHSM theory bytes from an immutable formal Git commit.

This changes source attribution/assumptions, never the optical likelihood.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1] / 'bhtracker/theory'
REPOSITORY = 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True, type=Path)
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.commit):
        raise ValueError('an immutable full Git commit is required')
    manifest_path = ROOT / 'BHSM_INTERPRETATION_MANIFEST.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf8'))
    for entry in manifest['sources']:
        if entry.get('original_path', '').startswith(('docs/BHSM_NORMAN', 'artifacts/current_semantics/BHSM_NORMAN')):
            original = entry['original_path']
            blob = subprocess.check_output(['git', '-C', str(args.repository), 'show', args.commit + ':' + original])
            (ROOT / entry['path']).write_bytes(blob)
            entry.update(sha256=hashlib.sha256(blob).hexdigest(), commit=args.commit,
                url=REPOSITORY + '/blob/' + args.commit + '/' + original,
                role='Reviewed core/surface derivations, explicit radial membrane background/pressure assumptions, and reconciled original source versions. Terminal core matching remains unresolved.')
    adapter = ROOT / 'BHSM_CORE_SURFACE_CONTRACT.json'
    contract = json.loads(adapter.read_text(encoding='utf8'))
    contract['radial_membrane_assumptions'] = {
        'status': 'CONDITIONAL_REGULAR_SIDE_EQUATION_NOT_A_FITTED_CORE_LAW',
        'background': 'Round p-sphere in fixed Minkowski spacetime, constant positive tension, coordinate time t, c=1, |dR/dt|<1.',
        'pressure_source': 'Specified normal stress/traction difference Delta P. Constant pressure can come from its explicit volume-work term; a pure membrane action alone has Delta P=0.',
        'qualification': 'Curved/self-gravitating backgrounds require their metric and stress matching. Variable tension has additional terms. No core mode, lifetime or conversion rate is inferred.'}
    contract['source_reconciliation'] = {
        'status': 'BOTH_HANDOFF_VERSIONS_AND_TWO_ORIGINAL_DOCUMENTS_PRESERVED',
        'formal_commit': args.commit,
        'comparison_path': 'docs/source_recovery/20261022/README.md',
        'old_handoff_sha256': 'd604c8c48f66d6753bbf0b95bbb3d0953fd7d5e0d2d134b4288e2eeed38c5240',
        'named_handoff_sha256': '149ba5efafd46be01bde9fe9513c1c83788b8a5f41c2127a4e2e5e6ce358517c',
        'qualification': 'Original bytes and contextual claims are retained in the formal repository. Source reconciliation does not supply missing terminal matching or astrophysical coefficients.'}
    adapter.write_text(json.dumps(contract, indent=2) + '\n', encoding='utf8')
    for entry in manifest['sources']:
        if entry['path'] == adapter.name:
            entry['sha256'] = hashlib.sha256(adapter.read_bytes()).hexdigest()
    amendment = next(e for e in manifest['sources'] if e['path'].endswith('AMENDMENT_20261022.md'))
    manifest['theory_amendment'].update(commit=args.commit, sha256=amendment['sha256'])
    manifest['theory_amendment'].pop('draft_pr', None)
    manifest['interpretation_revision'] = '2026-10-22-reviewed-corrections'
    note = ' Reviewed corrections update source assumptions and provenance only; the frozen native-magnitude likelihood is unchanged.'
    if note not in manifest['packaging_note']:
        manifest['packaging_note'] += note
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'formal_commit': args.commit, 'sources_verified': len(manifest['sources'])}))


if __name__ == '__main__':
    main()
