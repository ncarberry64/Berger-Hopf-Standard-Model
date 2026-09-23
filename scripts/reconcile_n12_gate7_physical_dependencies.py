"""Restore missing, hash-verified physical evidence without overwriting state.

Existing provenance differences are reported, never silently rebound. A
subsequent active-lineage producer must validate the complete dependency graph.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def digest(path, canonical=True):
    data = path.read_bytes()
    if canonical and path.suffix.lower() in ('.json', '.py', '.md'):
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest().upper()


def main(source, target, artifact, out):
    record_path = source/artifact
    record = json.loads(record_path.read_bytes())
    required = dict(record['inputs'])
    if 'data_SHA256' in record:
        required[Path(artifact).with_suffix('.npz').as_posix()] = record['data_SHA256']
    required[artifact] = digest(record_path)
    verified, missing, differing, failures = [], [], [], []
    for name, expected in required.items():
        src, dst = source/name, target/name
        if not src.resolve().is_relative_to(source) or not dst.resolve().is_relative_to(target):
            raise ValueError('Repository-relative dependencies required')
        if dst.exists():
            actual = digest(dst)
            (verified if actual == expected else differing).append(dict(path=name, expected=expected, actual=actual))
        elif not src.is_file() or digest(src) != expected:
            failures.append(name)
        else:
            missing.append(dict(path=name, expected=expected, bytes=src.stat().st_size))
    if failures:
        raise ValueError('Unverified missing dependencies: '+repr(failures))
    for item in missing:
        src, dst = source/item['path'], target/item['path']
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            raise ValueError('Destination appeared during restoration')
        shutil.copyfile(src, dst)
        if digest(dst) != item['expected'] or digest(dst, False) != digest(src, False):
            raise ValueError('Copied evidence differs')
    payload = dict(algorithm='GATE7_MISSING_PHYSICAL_DEPENDENCY_RESTORATION_V1',
        source_artifact=artifact, source_artifact_SHA256=digest(record_path),
        restored=missing, existing_verified=verified, existing_binding_differences=differing,
        existing_files_overwritten=False, active_scientific_validation_pending=True,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(payload, sort_keys=True, indent=2)+'\n')
    print(json.dumps(dict(restored=len(missing), bytes=sum(v['bytes'] for v in missing),
        existing_verified=len(verified), existing_binding_differences=[v['path'] for v in differing])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for key in ('source','target','out'):
        parser.add_argument('--'+key, type=Path, required=True)
    parser.add_argument('--artifact', required=True)
    args = parser.parse_args()
    main(args.source.resolve(), args.target.resolve(), args.artifact, args.out.resolve())
