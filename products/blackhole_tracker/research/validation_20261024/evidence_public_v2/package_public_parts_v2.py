"""Split the immutable public archive and package its portable verification kit.

Saved bytes only. No archive extraction, model, RNG, fitting or network call.
Every payload remains in the unchanged original tar.xz. Parts are <=40MiB.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ARCHIVE_SHA = '91f501317821e937d22d52fbea20130995911ed2f1562409b073fc900fa7710e'
ARCHIVE_BYTES = 119420524
PART_BYTES = 40*1024**2


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--transport-root', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path, help='NEW public delivery directory')
    a = p.parse_args()
    source = a.transport_root / 'BHSM_Calibration_PUBLIC_Content_v1.tar.xz'
    if source.stat().st_size != ARCHIVE_BYTES or digest_file(source) != ARCHIVE_SHA:
        raise ValueError('Pinned PUBLIC archive identity mismatch')
    a.output.mkdir(parents=True, exist_ok=False)
    parts = []
    assembled = hashlib.sha256()
    with source.open('rb') as stream:
        ordinal = 0
        while True:
            raw = stream.read(PART_BYTES)
            if not raw:
                break
            ordinal += 1
            name = f'BHSM_Calibration_PUBLIC_Content_v1.tar.xz.part{ordinal:03d}'
            with (a.output / name).open('xb') as target:
                target.write(raw)
            assembled.update(raw)
            parts.append({'ordinal': ordinal, 'name': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    if assembled.hexdigest() != ARCHIVE_SHA or sum(r['bytes'] for r in parts) != ARCHIVE_BYTES:
        raise ValueError('Source changed while splitting; partial parts retained')
    manifest = {'schema': 'bhsm.calibration.public_archive_parts.v1',
                'archive_name': source.name, 'archive_sha256': ARCHIVE_SHA, 'archive_bytes': ARCHIVE_BYTES,
                'part_max_bytes': PART_BYTES, 'parts': parts, 'scope': 'public-synthetic',
                'original_native_complete': False, 'payload_omissions_relative_to_public_archive': 0,
                'public_content_manifest_sha256': '1244b6865dd553b98aff5de78829fc2f176b00ff2f8e8c01f3c0e3dd84dd176d',
                'qualification': 'Transport only. All synthetic cases retained; native originals/parents omitted as declared. Hash integrity is not scientific validity.'}
    manifest_raw = (json.dumps(manifest, sort_keys=True, indent=2)+'\n').encode('utf8')
    manifest_path = a.output / 'PUBLIC_PARTS_MANIFEST_v1.json'
    with manifest_path.open('xb') as stream:
        stream.write(manifest_raw)
    copies = ['TRANSPORT_MANIFEST_PUBLIC_v1.json', 'restore_verify_calibration_v1.py',
              'join_public_evidence_v1.py', 'README_TRANSPORT_v1.txt',
              'README_PUBLIC_RESEARCHER_v3.txt', 'package_public_parts_v2.py']
    for name in copies:
        with (a.output / name).open('xb') as stream:
            stream.write((a.transport_root / name).read_bytes())
    kit_root = a.transport_root / 'cadence_preparation_kit_v2'
    for source_path in sorted(kit_root.rglob('*')):
        if source_path.is_file():
            destination = a.output / 'cadence_preparation_kit_v2' / source_path.relative_to(kit_root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open('xb') as stream:
                stream.write(source_path.read_bytes())
    members = sorted(p for p in a.output.rglob('*') if p.is_file())
    rows = [{'path': p.relative_to(a.output).as_posix(), 'bytes': p.stat().st_size,
             'sha256': digest_file(p)} for p in members]
    delivery = {'schema': 'bhsm.calibration.public_researcher_delivery.v2',
                'scope': 'public-synthetic', 'original_native_complete': False,
                'members': rows, 'total_included_bytes': sum(r['bytes'] for r in rows),
                'archive_sha256': ARCHIVE_SHA, 'parts_manifest_sha256': hashlib.sha256(manifest_raw).hexdigest(),
                'scientific_calls': 0, 'network_calls': 0}
    with (a.output / 'PUBLIC_DELIVERY_MANIFEST_v2.json').open('x', encoding='utf8') as stream:
        json.dump(delivery, stream, sort_keys=True, indent=2)
        stream.write('\n')
    members.append(a.output / 'PUBLIC_DELIVERY_MANIFEST_v2.json')
    target = a.output.parent / 'BHSM_Calibration_PUBLIC_Researcher_v2.zip'
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(members):
            info = zipfile.ZipInfo(path.relative_to(a.output).as_posix(), date_time=(2026, 10, 24, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100644 << 16)
            info.compress_type = zipfile.ZIP_STORED if '.tar.xz.part' in path.name else zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    receipt = {'schema': 'bhsm.calibration.public_parts_package_receipt.v1',
               'status': 'COMPLETE_SAVED_CONTENT_PACKAGING_ONLY', 'output': str(a.output),
               'archive_sha256': ARCHIVE_SHA, 'part_count': len(parts), 'parts': parts,
               'parts_manifest_sha256': digest_file(manifest_path),
               'delivery_manifest_sha256': digest_file(a.output / 'PUBLIC_DELIVERY_MANIFEST_v2.json'),
               'zip_path': str(target), 'zip_bytes': target.stat().st_size, 'zip_sha256': digest_file(target),
               'git_individual_files_below40MiB': all(row['bytes'] <= PART_BYTES for row in rows),
               'zip_is_local_delivery_not_normal_git_blob': True, 'native_observations_included': False,
               'scientific_calls': 0, 'network_calls': 0}
    with (a.output.parent / 'PUBLIC_PARTS_PACKAGE_RECEIPT_v1.json').open('x', encoding='utf8') as stream:
        json.dump(receipt, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
