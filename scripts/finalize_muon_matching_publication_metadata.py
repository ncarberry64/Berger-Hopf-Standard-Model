"""Stage explicit publication receipts and verify every selected index blob.

The scientific plan remains immutable. This adds only its manifest,
publication/audit receipts and this byte-verification utility.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'artifacts/muon_common_domain_publication_plan_expanded_20261012/'
CONTROL = 'artifacts/muon_common_domain_selected_publication_20261012/'


def git(*args, **kwargs):
    return subprocess.run(['git', '-c', 'gc.auto=0', '-c',
        'maintenance.auto=false', *args], cwd=ROOT, check=True,
        capture_output=True, **kwargs).stdout


def materialize(output):
    out = (ROOT/output).resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise ValueError('new verification directory inside checkout required')
    plan_path = ROOT/(BASE+'publication_plan.json')
    plan = json.loads(plan_path.read_bytes())
    audit = json.loads((ROOT/(CONTROL+'final_audits_run_1/verification.json')).read_bytes())
    before = git('write-tree').decode().strip()
    if not audit['all_passed'] or before != audit['checked_index_tree']:
        raise ValueError('reviewed science index must still equal the audited index')
    metadata = [BASE+name for name in (
        'publication_plan.json', 'publication_plan.txt',
        'selected_publication_paths.txt', 'selected_test_paths.txt',
        'reproduction_commands.txt',
        'final_publication_selection_verification.json',
        'final_publication_selection_refresh_verification.json')]
    metadata += [CONTROL+'final_stage_run_2/staged_verification.json']
    metadata += [CONTROL+'final_audits_run_1/'+name for name in
        ['verification.json']+[label+'.'+stream+'.txt'
        for label in ('status','claims','frozen','precision','public')
        for stream in ('stdout','stderr')]]
    metadata += [Path(__file__).relative_to(ROOT).as_posix()]
    expected = {r['path']:r['sha256'] for r in plan['selected_files']}
    receipts = []
    for name in metadata:
        path = ROOT/name
        raw = path.read_bytes()
        if len(raw) >= 10*1024**2:
            raise ValueError('publication metadata size cap exceeded')
        digest = sha256(raw).hexdigest()
        if name in expected and expected[name] != digest:
            raise ValueError('metadata disagrees with science plan')
        expected[name] = digest
        receipts.append(dict(path=name,bytes=len(raw),sha256=digest))
    out.mkdir(parents=True)
    receipt_path = out/'verification.json'
    receipt = dict(classification='VERIFIED_EXPLICIT_SCIENCE_AND_PUBLICATION_METADATA_INDEX',
        science_plan_sha256=sha256(plan_path.read_bytes()).hexdigest(),
        scientific_file_count=len(plan['selected_files']),
        previous_audited_science_index=before,
        five_science_audits_passed=True,metadata_files=receipts,
        verification_method='single git cat-file batch; exact SHA256 and no unselected staged changes',
        self_digest_scope='fresh receipt bytes verified against its index blob; digest reported in command stdout',
        physical_matching_or_observable_completion_asserted=False,
        no_reset_delete_or_scientific_recalculation=True)
    receipt_path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    self_name = receipt_path.relative_to(ROOT).as_posix()
    expected[self_name] = sha256(receipt_path.read_bytes()).hexdigest()
    attrs = ROOT/'.gitattributes'
    raw = attrs.read_bytes()
    rules = set(raw.decode().splitlines())
    additions = []
    for name in [*metadata,self_name]:
        rule = name+(' text eol=lf' if name.endswith('.py') else ' -text')
        if rule not in rules:
            additions.append(rule)
    if additions:
        attrs.write_bytes(raw+(b'' if raw.endswith(b'\n') else b'\n')+
            b'# Exact publication manifest and audit receipt bytes.\n'+
            ('\n'.join(additions)+'\n').encode())
    expected['.gitattributes'] = sha256(attrs.read_bytes()).hexdigest()
    selected = [*metadata,self_name,'.gitattributes']
    pathspec = out/'metadata_paths.nul'
    pathspec.write_bytes(b'\0'.join(n.encode() for n in selected)+b'\0')
    git('add','-f','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul')
    changes = set(git('diff','--cached','--name-only','-z').decode().split('\0'))-{''}
    if not changes <= expected.keys():
        raise ValueError('unexpected staged path outside explicit science/metadata set')
    names = list(expected)
    blobs = git('cat-file','--batch',input=''.join(':'+n+'\n' for n in names).encode())
    view = memoryview(blobs)
    offset = 0
    for name in names:
        end = blobs.index(b'\n',offset)
        header = blobs[offset:end].split()
        if len(header)!=3 or header[1]!=b'blob':
            raise ValueError('missing index blob: '+name)
        size = int(header[2]);offset=end+1
        if sha256(view[offset:offset+size]).hexdigest()!=expected[name]:
            raise ValueError('index byte mismatch: '+name)
        offset += size
        if blobs[offset:offset+1]!=b'\n':
            raise ValueError('invalid batch delimiter')
        offset += 1
    if offset != len(blobs):
        raise ValueError('unexpected batch output')
    print(json.dumps(dict(all_selected_index_bytes_verified=True,
        scientific_files=len(plan['selected_files']),metadata_files=len(metadata)+1,
        verified_index_blobs=len(names),staged_changes=len(changes),
        index_tree=git('write-tree').decode().strip(),
        verification_sha256=expected[self_name])))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.output)
