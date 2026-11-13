"""Preserve reviewed selected bytes and verify their staged Git blobs.

This utility neither selects science nor stages the checkout wholesale.
An explicit immutable plan supplies each path, size and content hash.
"""
from pathlib import Path
from hashlib import sha256
import argparse, json, subprocess
ROOT = Path(__file__).resolve().parents[1]


def prepare(plan_name, output, *, stage=False):
    plan_path = (ROOT/plan_name).resolve()
    if not plan_path.is_relative_to(ROOT):
        raise ValueError('plan must be in the intended checkout')
    plan = json.loads(plan_path.read_bytes())
    out = (ROOT/output).resolve()
    if not out.is_relative_to(ROOT):
        raise ValueError('verification must stay in the intended checkout')
    if out.exists():
        raise FileExistsError('preserve each publication preparation receipt')
    rows = plan['selected_files']
    if len({row['path'] for row in rows}) != len(rows):
        raise ValueError('duplicate selected path')
    rules = ['.gitattributes text eol=lf']
    for row in rows:
        path = (ROOT/row['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError('selected path left its intended checkout')
        raw = path.read_bytes()
        if len(raw) != row['bytes'] or sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('reviewed selected bytes changed: '+row['path'])
        if len(raw) >= 10*1024**2:
            raise ValueError('selected single file exceeds publication cap')
        if row['path'].endswith('.py') and b'\r\n' not in raw:
            rules.append(row['path']+' text eol=lf')
        elif row['path'].startswith('artifacts/') or row['path'].endswith('.py'):
            # Preserve executed sources with CRLF as well as pinned data.
            # Converting after a numerical run would invalidate provenance.
            rules.append(row['path']+' -text')
        elif row['path'].endswith('.md'):
            rules.append(row['path']+' text eol=lf')
    attrs = ROOT/'.gitattributes'
    raw = attrs.read_bytes()
    old = set(raw.decode('utf8').splitlines())
    additions = [rule for rule in rules if rule not in old]
    if additions:
        attrs.write_bytes(raw+(b'' if raw.endswith(b'\n') else b'\n')+
            b'# Exact reviewed bytes for physical matching action applications.\n'+
            ('\n'.join(additions)+'\n').encode('utf8'))
    out.mkdir(parents=True)
    paths = [row['path'] for row in rows]+['.gitattributes']
    staged = []
    if stage:
        pathspec = out/'selected_paths.nul'
        pathspec.write_bytes(b'\0'.join(name.encode('utf8') for name in paths)+b'\0')
        # The explicit reviewed plan includes regression/audit logs that
        # match the repository's general *.log ignore rule.
        subprocess.run(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', 'add', '-f',
            '--pathspec-from-file='+str(pathspec), '--pathspec-file-nul'], cwd=ROOT, check=True)
        expected = {row['path']:row['sha256'] for row in rows}
        expected['.gitattributes'] = sha256(attrs.read_bytes()).hexdigest()
        for name in paths:
            blob = subprocess.run(['git', 'show', ':'+name], cwd=ROOT, check=True,
                capture_output=True).stdout
            digest = sha256(blob).hexdigest()
            if digest != expected[name]:
                raise ValueError('staged bytes differ from reviewed bytes: '+name)
            staged.append(dict(path=name, bytes=len(blob), sha256=digest))
    receipt = dict(classification='VERIFIED_SELECTED_MATCHING_PUBLICATION_BYTES',
        plan=plan_path.relative_to(ROOT).as_posix(), plan_sha256=sha256(plan_path.read_bytes()).hexdigest(),
        reviewed_file_count=len(rows), reviewed_total_bytes=sum(row['bytes'] for row in rows),
        added_attribute_rules=len(additions), attributes_sha256=sha256(attrs.read_bytes()).hexdigest(),
        stage_requested=stage, staged_blobs=staged,
        raw_outputs_or_unrelated_files_deleted=False,
        numerical_regeneration_or_physical_completion_asserted=False)
    path = out/('staged_verification.json' if stage else 'preparation_verification.json')
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(verification_sha256=sha256(path.read_bytes()).hexdigest(),
        reviewed_files=len(rows), reviewed_bytes=receipt['reviewed_total_bytes'],
        staged_verified_blobs=len(staged), added_attribute_rules=len(additions))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='store_true')
    args = parser.parse_args()
    prepare(args.plan, args.output, stage=args.stage)
