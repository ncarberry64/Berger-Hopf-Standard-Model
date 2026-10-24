"""Join or verify exact numbered PUBLIC evidence parts; never extract/execute.

Default verifies every part and assembled hash without writing. --output uses
a NEW target file and retains a .partial file on any failure. Public-native
observations remain omitted as declared by the separately pinned content manifest.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath


def sha_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--parts-root', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args()
    if args.manifest.stat().st_size > 1024*1024:
        raise ValueError('Manifest resource limit')
    raw = args.manifest.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.manifest_sha256:
        raise ValueError('Manifest identity mismatch')
    manifest = json.loads(raw)
    if manifest['schema'] != 'bhsm.calibration.public_archive_parts.v1':
        raise ValueError('Unsupported parts schema')
    rows = manifest['parts']
    if not isinstance(rows, list) or not 1 <= len(rows) <= 16:
        raise ValueError('Part-count resource limit')
    root = args.parts_root or args.manifest.parent
    names = set()
    for index, row in enumerate(rows, 1):
        name = row['name']
        if (not isinstance(name, str) or str(PurePosixPath(name)) != name or
                PurePosixPath(name).name != name or '\\' in name or ':' in name or
                name in names or row['ordinal'] != index or
                type(row['bytes']) is not int or not 0 < row['bytes'] <= 40*1024**2):
            raise ValueError('Invalid numbered part metadata')
        names.add(name)
    if args.receipt.exists():
        raise FileExistsError('Receipt must be new')
    partial = None
    if args.output is not None:
        if args.output.exists():
            raise FileExistsError('Output must be new')
        partial = args.output.with_name(args.output.name+'.partial')
        if partial.exists():
            raise FileExistsError('Partial output must be new')
    h = hashlib.sha256()
    total = 0
    checked = []
    output = partial.open('xb') if partial is not None else None
    error = None
    try:
        for row in rows:
            ph = hashlib.sha256()
            size = 0
            path = root / row['name']
            if path.stat().st_size != row['bytes']:
                raise ValueError('Part size mismatch: '+row['name'])
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''):
                    size += len(block)
                    if size > row['bytes']:
                        raise ValueError('Part grew beyond budget')
                    h.update(block)
                    ph.update(block)
                    if output is not None:
                        output.write(block)
            if size != row['bytes'] or ph.hexdigest() != row['sha256']:
                raise ValueError('Part identity mismatch: '+row['name'])
            total += size
            checked.append(row)
        if total != manifest['archive_bytes'] or h.hexdigest() != manifest['archive_sha256']:
            raise ValueError('Assembled archive identity mismatch')
        if output is not None:
            output.flush()
            os.fsync(output.fileno())
    except Exception as failure:
        error = {'type': type(failure).__name__, 'message': str(failure)}
    finally:
        if output is not None:
            output.close()
    if error is None and partial is not None:
        # A hard link publishes without replacing an existing destination.
        try:
            os.link(partial, args.output)
            partial.unlink()
        except Exception as failure:
            error = {'type': type(failure).__name__, 'message': str(failure)}
    result = {'schema': 'bhsm.calibration.public_parts_verification.v1',
              'status': 'PASS_EXACT_PUBLIC_ARCHIVE' if error is None else 'UNRESOLVED',
              'manifest_sha256': args.manifest_sha256, 'parts_checked': checked,
              'assembled_bytes': total, 'assembled_sha256': h.hexdigest(),
              'error': error, 'output': str(args.output) if args.output else None,
              'scientific_calls': 0, 'extracts_archived_code': False}
    with args.receipt.open('x', encoding='utf8') as stream:
        json.dump(result, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(result, sort_keys=True))
    return 0 if error is None else 1


if __name__ == '__main__':
    raise SystemExit(main())
