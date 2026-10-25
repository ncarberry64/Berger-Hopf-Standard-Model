#!/usr/bin/env python3
"""Verify the supplied real observations, or refetch the exact pinned bytes.

Python standard library only. This script does not fit or classify any event.
"""
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import argparse
import datetime
import hashlib
import json
import math
import shutil
import time

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SALT = 'BHSM-OGLE3-pilot-20261022-v1|'


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def safe_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path outside data directory')
    return path


def check_bytes(content, rec):
    assert len(content) == rec['bytes'], 'Byte count differs: ' + rec['relative_path']
    assert hashlib.sha256(content).hexdigest() == rec['sha256'], 'SHA256 differs: ' + rec['relative_path']
    if rec.get('publisher_md5'):
        assert hashlib.md5(content).hexdigest() == rec['publisher_md5'], 'Publisher MD5 differs'


def check_measurements(path, rec):
    expected = len(rec['columns'])
    rows, bad, headers, source_warnings = [], [], [], []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        text = line.strip()
        if not text or text.startswith('#'):
            continue
        if text == 'ERROR: data not sorted in HJD!':
            source_warnings.append({'line': line_no, 'text': text})
            continue
        fields = text.split()
        if fields == rec['columns']:
            headers.append(line_no)
            continue
        try:
            values = [float(v) for v in fields]
            if len(values) != expected or not all(math.isfinite(v) for v in values):
                raise ValueError('Wrong field count or nonfinite value')
            uncertainty_indices = (2, 4, 6) if expected == 7 else (2,)
            if any(values[k] <= 0 for k in uncertainty_indices):
                raise ValueError('Nonpositive uncertainty')
            rows.append(values)
        except ValueError as exc:
            bad.append({'line': line_no, 'reason': str(exc)})
    times = [row[0] for row in rows]
    return {
        'relative_path': rec['relative_path'], 'event_id': rec['event_id'],
        'role': rec['role'], 'valid_numeric_rows': len(rows), 'invalid_rows': bad,
        'recognized_header_lines': headers,
        'source_warning_annotations': source_warnings,
        'time_min_native': min(times) if times else None,
        'time_max_native': max(times) if times else None,
        'epoch_convention': rec['epoch_convention'],
        'duplicate_time_count': len(times) - len(set(times)),
        'decreasing_time_steps': sum(b < a for a, b in zip(times, times[1:])),
        'uncertainty_minima': {rec['columns'][k]: min(row[k] for row in rows)
                               for k in ((2, 4, 6) if expected == 7 else (2,))} if rows else {},
    }


def verify(root):
    manifest = json.loads((root / 'download_manifest.json').read_text())
    selection = json.loads((root / 'pilot_selection.json').read_text())
    checks = []
    for rec in manifest['files']:
        path = safe_path(root, rec['relative_path'])
        check_bytes(path.read_bytes(), rec)
        if 'columns' in rec:
            checks.append(check_measurements(path, rec))

    full_path = root / selection['parent_catalog_path']
    assert hashlib.sha256(full_path.read_bytes()).hexdigest() == selection['parent_catalog_sha256']
    full = [line.split() for line in full_path.read_text().splitlines() if line.strip()]
    basic = [line.split() for line in (root / 'raw/ogle3/catalogA_basic.table').read_text().splitlines() if line.strip()]
    assert len(full) == len(basic) == 3560
    assert all(len(f) == 26 and len(b) == 7 and b == f[:5] + f[24:] for f, b in zip(full, basic))
    ids = [int(f[0]) for f in full]
    assert ids == list(range(1, 3561))
    canonical = lambda row: f'OGLE3-ULENS-{int(row[0]):04d}'
    long_rows = [row for row in full if float(row[8]) >= 150]
    controls = [row for row in full if 10 <= float(row[8]) < 50]
    controls.sort(key=lambda row: (hashlib.sha256((SALT + canonical(row)).encode('ascii')).hexdigest(), int(row[0])))
    chosen = sorted(long_rows + controls[:25], key=lambda row: int(row[0]))
    selected_ids = [canonical(row) for row in chosen]
    assert len(long_rows) == 75 and len(controls) == 2272
    assert selected_ids == [e['event_id'] for e in selection['selected']]
    assert hashlib.sha256(('\n'.join(selected_ids) + '\n').encode('ascii')).hexdigest() == selection['selected_id_list_sha256']
    pilot = [c for c in checks if c['role'] == 'pilot_observational_photometry']
    benchmark_phot = [c for c in checks if c['role'] == 'historical_benchmark_photometry']
    hst = [c for c in checks if c['role'] == 'historical_benchmark_astrometry_and_photometry']
    assert len(pilot) == 100 and len(benchmark_phot) == len(hst) == 2
    invalid = sum(len(c['invalid_rows']) for c in checks)
    source_warnings = sum(len(c['source_warning_annotations']) for c in checks)
    return {
        'schema': 'bhsm_real_observation_integrity_report_v1', 'verified_utc': utcnow(),
        'hash_verified_files': len(manifest['files']), 'raw_bytes': manifest['raw_bytes'],
        'parent_class_A_events': len(full), 'pilot_events': len(pilot),
        'pilot_long_duration_events': 75, 'pilot_control_events': 25,
        'pilot_photometric_rows': sum(c['valid_numeric_rows'] for c in pilot),
        'historical_benchmark_photometric_rows': sum(c['valid_numeric_rows'] for c in benchmark_phot),
        'historical_benchmark_HST_rows': sum(c['valid_numeric_rows'] for c in hst),
        'historical_benchmark_HST_unique_epochs': 8,
        'invalid_measurement_rows': invalid,
        'source_warning_annotations': source_warnings,
        'files_with_decreasing_times': sum(c['decreasing_time_steps'] > 0 for c in checks),
        'all_measurement_rows_finite_with_positive_uncertainties': invalid == 0,
        'selection_reproduced': True,
        'scientific_fits_performed': False, 'new_black_hole_candidates_identified': False,
        'status': ('BYTE_AND_NUMERIC_STRUCTURE_VALIDATED_WITH_SOURCE_WARNINGS' if source_warnings else 'BYTE_AND_NUMERIC_STRUCTURE_VALIDATED') + '; SCIENTIFIC_INFERENCE_NOT_RUN',
        'unresolved_metadata': ['HST numeric epoch origin/format', 'Underlying time scale of photometric HJD',
                                'Full inter-epoch/cross-instrument noise covariance is not supplied'],
        'measurements': checks,
    }


def refetch(root, destination):
    manifest = json.loads((root / 'download_manifest.json').read_text())
    destination.mkdir(parents=True, exist_ok=True)
    receipts = []
    for rec in manifest['files']:
        url = rec['url']
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.netloc not in ('ftp.astrouw.edu.pl', 'zenodo.org'):
            raise ValueError('Unexpected observation source host')
        target = safe_path(destination, rec['relative_path'])
        receipt = {'relative_path': rec['relative_path'], 'url': url, 'started_utc': utcnow()}
        if target.exists():
            check_bytes(target.read_bytes(), rec)
            receipt['status'] = 'existing_matching_bytes'
        else:
            for attempt in range(3):
                try:
                    request = Request(url, headers={'User-Agent': 'BHSM-public-observation-replay/1.0'})
                    with urlopen(request, timeout=35) as response:
                        content = response.read(rec['bytes'] + 1)
                        receipt['resolved_url'] = response.geturl()
                        receipt['http_status'] = response.status
                    check_bytes(content, rec)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
                    receipt.update(status='downloaded_matching_bytes', retrieved_utc=utcnow(), sha256=rec['sha256'])
                    break
                except (HTTPError, URLError, TimeoutError) as exc:
                    if isinstance(exc, HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                        raise
                    if attempt == 2:
                        raise
                    time.sleep(attempt + 1)
        receipts.append(receipt)
        (destination / 'refetch_receipts.json').write_text(json.dumps(receipts, indent=2) + '\n')
    if root.resolve() != destination.resolve():
        for name in ('download_manifest.json', 'pilot_selection.json'):
            shutil.copy2(root / name, destination / name)
    print(json.dumps({'files': len(receipts), 'destination': str(destination.resolve())}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, default=DEFAULT_ROOT)
    subs = parser.add_subparsers(dest='command', required=True)
    check = subs.add_parser('verify')
    check.add_argument('--report', type=Path)
    fetch = subs.add_parser('refetch')
    fetch.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'refetch':
        refetch(args.data_root, args.destination)
    else:
        report = verify(args.data_root)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: v for k, v in report.items() if k != 'measurements'}, indent=2))
        if report['invalid_measurement_rows']:
            raise SystemExit('Invalid observation rows are recorded; no raw data were edited.')


if __name__ == '__main__':
    main()
