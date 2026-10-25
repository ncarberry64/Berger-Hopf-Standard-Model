"""Verify normalized complete calibration content; optionally restore originals.

No archived code is executed. No fitting, generation, imports of the tracker,
random numbers or scientific results are changed. Hashes prove consistency.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import sys
import tarfile
import zlib


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def safe_name(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Invalid portable member name')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or '.' in path.parts or str(path) != value:
        raise ValueError('Unsafe archive member path')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--mode', choices=('verify-payloads', 'restore-originals'), default='verify-payloads')
    parser.add_argument('--output', type=Path, help='New directory required for original restoration')
    parser.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    if digest(manifest_bytes) != args.manifest_sha256:
        raise ValueError('External manifest identity mismatch')
    manifest = json.loads(manifest_bytes)
    records = manifest['members']
    if len(records) > 20000:
        raise ValueError('Member resource budget exceeded')
    indexed = {}
    restored_names = set()
    for row in records:
        name = safe_name(row['member_path'])
        original = safe_name(row['restored_path'])
        if name == 'TRANSPORT_MANIFEST_v1.json' or name in indexed or original in restored_names:
            raise ValueError('Duplicate manifest member or restoration path')
        if not 0 <= row['payload_bytes'] <= 64*1024**2:
            raise ValueError('Per-member resource budget exceeded')
        if row['transport'] == 'EXACT_BYTES' and (
                row['payload_bytes'] != row['original_bytes'] or
                row['payload_sha256'] != row['original_sha256']):
            raise ValueError('Contradictory exact-byte metadata')
        indexed[name] = row
        restored_names.add(original)
    if args.receipt.exists():
        raise FileExistsError('Receipt must be a new path')
    if args.mode == 'restore-originals':
        if args.output is None:
            raise ValueError('New output directory required')
        args.output.mkdir(parents=True, exist_ok=False)
        output_root = args.output.resolve()
    else:
        output_root = None
    seen, restored, gzip_count, payload_total = set(), 0, 0, 0
    failures = []
    manifest_seen = False
    events_path = args.receipt.with_suffix(args.receipt.suffix+'.events.jsonl')
    with events_path.open('x', encoding='utf8') as events:
        def log(value):
            events.write(json.dumps(value, sort_keys=True, allow_nan=False)+'\n')
            events.flush()
            os.fsync(events.fileno())
        try:
            with tarfile.open(args.archive, mode='r|xz') as archive:
                for member in archive:
                    name = safe_name(member.name)
                    if not member.isfile() or name in seen:
                        raise ValueError('Only unique regular-file members admitted')
                    seen.add(name)
                    if name == 'TRANSPORT_MANIFEST_v1.json':
                        if member.size != len(manifest_bytes):
                            raise ValueError('Embedded manifest size mismatch')
                        if archive.extractfile(member).read() != manifest_bytes:
                            raise ValueError('Embedded manifest differs from pinned external bytes')
                        manifest_seen = True
                        continue
                    if name not in indexed:
                        raise ValueError('Unexpected archive member: '+name)
                    row = indexed[name]
                    if member.size != row['payload_bytes']:
                        raise ValueError('Declared payload size mismatch: '+name)
                    payload = archive.extractfile(member).read()
                    payload_total += len(payload)
                    if payload_total > 16*1024**3:
                        raise ValueError('Total content resource budget exceeded')
                    if digest(payload) != row['payload_sha256']:
                        raise ValueError('Payload hash mismatch: '+name)
                    if row['transport'] == 'GZIP_JSON_TO_EXACT_PAYLOAD':
                        gzip_count += 1
                        original = gzip.compress(payload, compresslevel=5, mtime=0) if output_root else None
                    elif row['transport'] == 'EXACT_BYTES':
                        original = payload
                    else:
                        raise ValueError('Unsupported transport rule')
                    if output_root:
                        if len(original) != row['original_bytes'] or digest(original) != row['original_sha256']:
                            raise ValueError('GZIP_RUNTIME_BYTE_IDENTITY_UNRESOLVED: '+name)
                        target = output_root.joinpath(*PurePosixPath(row['restored_path']).parts)
                        if not target.resolve().is_relative_to(output_root):
                            raise ValueError('Restoration target escapes new root')
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with target.open('xb') as stream:
                            stream.write(original)
                        restored += 1
                    log({'member': name, 'payload_sha256': row['payload_sha256'],
                         'payload_verified': True, 'original_restored_verified': bool(output_root)})
            if not manifest_seen or seen != set(indexed)|{'TRANSPORT_MANIFEST_v1.json'}:
                raise ValueError('Archive lacks exact complete manifest roster')
        except Exception as error:
            failures.append({'type': type(error).__name__, 'message': str(error)})
            log({'failure': failures[-1], 'partial_outputs_preserved': True})
    status = ('PASS_ALL_INCLUDED_ORIGINAL_BYTES_RECONSTRUCTED' if output_root else 'PASS_NORMALIZED_CONTENT_ONLY') if not failures else 'FAILED_OR_UNRESOLVED'
    receipt = {'schema': 'bhsm.calibration.evidence_transport_verification.v1',
               'status': status, 'mode': args.mode, 'manifest_sha256': args.manifest_sha256,
               'transport_scope': manifest['scope'],
               'original_native_complete': manifest['original_native_complete'],
               'explicit_omitted_native_copy_count': len(manifest['explicit_omitted_native_copies']),
               'archive_sha256': digest(args.archive.read_bytes()),
               'python': platform.python_version(), 'zlib_build': zlib.ZLIB_VERSION,
               'zlib_runtime': zlib.ZLIB_RUNTIME_VERSION,
               'members_expected': len(indexed), 'payload_members_seen': len(seen)-int(manifest_seen),
               'normalized_gzip_members': gzip_count, 'payload_bytes': payload_total,
               'restored_original_members': restored, 'failures': failures,
               'original_gzip_byte_identity_proved': bool(output_root and not failures),
               'events_sha256': digest(events_path.read_bytes()),
               'scientific_model_or_rng_calls': 0,
               'scientific_acceptance_or_authenticity_claim': False}
    encoded = json.dumps(receipt, indent=2, allow_nan=False)+'\n'
    with args.receipt.open('x', encoding='utf8') as stream:
        stream.write(encoded)
    print(json.dumps(receipt))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
