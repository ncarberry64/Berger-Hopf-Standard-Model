"""Catalog directions and qualified follow-up records, without physical fits.

Replay preserves the exact UTF-8 inventory text. Hashes check consistency, not
authenticity, scientific adequacy, or identification of a black hole.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

SCHEMA = 'bhsm.blackhole_tracker.candidate_inventory.v1'
REPLAY = 'bhsm.blackhole_tracker.candidate_atlas_replay.v1'
REPOSITORY = 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model'
TIERS = ('REVIEW_REQUIRED', 'SUPPORTED_LENSING_EVENT', 'BLACK_HOLE_SEARCH_TARGET',
         'BLACK_HOLE_CANDIDATE', 'STRONGLY_SUPPORTED_BLACK_HOLE_IDENTIFICATION')
LENS_FIELDS = ('position', 'position_epoch', 'position_covariance', 'distance_pc',
               'mass_msun', 'proper_motion_mas_yr', 'radial_velocity_km_s')
WEB = Path(__file__).resolve().parent/'web'
MAX_BYTES = 32_000_000


def text_sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def read_json(text):
    """Strict finite JSON, including duplicate-key and size rejection."""
    if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_BYTES:
        raise ValueError('Atlas JSON must be UTF-8 text no larger than32 MB')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError('Duplicate JSON key: '+key)
            result[key] = value
        return result
    def constant(value): raise ValueError('Nonfinite JSON number: '+value)
    value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    _finite_tree(value)
    return value


def _finite_tree(value, depth=0):
    if depth >= 80: raise ValueError('Atlas JSON nesting limit exceeded')
    if isinstance(value, float) and not math.isfinite(value): raise ValueError('Nonfinite atlas value')
    if type(value) in (int, float) and value == math.trunc(value) and abs(value) > 2**53-1:
        raise ValueError('Integral atlas values beyond browser exact precision must be strings')
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ('__proto__', 'prototype', 'constructor'): raise ValueError('Unsupported JSON key')
            _finite_tree(item, depth+1)
    elif isinstance(value, list):
        for item in value: _finite_tree(item, depth+1)


def _strings(value):
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def _same_json(left, right):
    """Match browser JSON numbers while keeping booleans distinct from numbers."""
    if type(left) in (int, float) and type(right) in (int, float): return left == right
    if type(left) is not type(right): return False
    if isinstance(left, dict): return left.keys() == right.keys() and all(_same_json(left[k], right[k]) for k in left)
    if isinstance(left, list): return len(left) == len(right) and all(_same_json(a, b) for a, b in zip(left, right))
    return left == right


def validate_inventory(value):
    """Admit version1 metadata; this version cannot infer lens quantities."""
    _finite_tree(value)
    if not isinstance(value, dict) or value.get('schema_version') != SCHEMA:
        raise ValueError('Unsupported candidate inventory schema')
    metadata = value.get('metadata')
    if not isinstance(metadata, dict) or metadata.get('formal_BHSM_repository') != REPOSITORY:
        raise ValueError('Formal BHSM repository metadata required')
    events = value.get('events')
    if not isinstance(events, list) or not 1 <= len(events) <= 20000:
        raise ValueError('Atlas requires1–20,000 retained events')
    benchmarks = value.get('benchmarks', [])
    if not isinstance(benchmarks, list): raise ValueError('Separate benchmark array required')
    ids = set()
    for event in events+benchmarks:
        if not isinstance(event, dict) or not isinstance(event.get('event_id'), str) or not event['event_id'] or event['event_id'] in ids:
            raise ValueError('Complete unique event identities required')
        ids.add(event['event_id'])
        if not all(_strings(event.get(k)) for k in ('known_aliases', 'cohorts', 'quality_flags')):
            raise ValueError('Aliases/cohorts/flags must be string arrays')
        if event.get('tier') not in TIERS or not isinstance(event.get('provenance'), list) or not event['provenance']:
            raise ValueError('Declared evidence tier and provenance required')
        direction = event.get('source_direction', {})
        if not isinstance(direction, dict) or direction.get('role') != 'SOURCE_EVENT_DIRECTION':
            raise ValueError('Only source/event directions are admitted')
        ra, dec = direction.get('ra_deg'), direction.get('dec_deg')
        missing = ra is None and dec is None
        if not missing and not (type(ra) in (int, float) and type(dec) in (int, float)
                and math.isfinite(ra) and math.isfinite(dec) and 0 <= ra < 360 and -90 <= dec <= 90):
            raise ValueError('Invalid source/event sky coordinates')
        if not all(k in direction for k in ('epoch', 'uncertainty')):
            raise ValueError('Direction epoch and uncertainty must remain explicit')
        lens = event.get('lens')
        if not isinstance(lens, dict) or any(k not in lens or lens[k] is not None for k in LENS_FIELDS):
            raise ValueError('Version1 inferred lens position, mass, distance and motion must remain null')
        location = event.get('map_eligibility', {})
        if (not isinstance(location, dict) or location.get('three_dimensional') is not False or location.get('propagate_position') is not False
                or location.get('sky_marker') is not (not missing)):
            raise ValueError('Unsupported3D location or propagated position claim')
        if event.get('accepted_engine_black_hole') is not False or event.get('new_black_hole_interpretation') is not False:
            raise ValueError('This inventory cannot claim engine identification or a new black hole')
    for benchmark in benchmarks:
        status = benchmark.get('tracker_recovery_status')
        if (benchmark.get('classification_source') != 'LITERATURE' or not isinstance(status, str)
                or not status.startswith('NOT_ESTABLISHED') or 'SEPARATE_KNOWN_SYSTEM_BENCHMARK' not in benchmark['cohorts']):
            raise ValueError('Literature benchmark must remain separate from engine recovery')
    if 'counts' in metadata:
        counts = metadata['counts']
        expected = dict(unique_events=len(events),sky_markers=sum(e['source_direction']['ra_deg'] is not None for e in events),
            new_BH_interpretations=0,independently_measured_lens_mass_in_atlas=0)
        if (not isinstance(counts, dict) or any(type(counts.get(k)) not in (int, float) or counts[k] != v for k,v in expected.items())
                or not isinstance(counts.get('tier_counts'), dict)
                or any(type(counts['tier_counts'].get(t)) not in (int,float) or counts['tier_counts'][t] != sum(e['tier']==t for e in events) for t in TIERS)):
            raise ValueError('Inventory summary counts conflict with retained events or unavailable masses')
    return value


def load_inventory(path=None):
    """Return admitted inventory and its lossless text; verify bundled bytes."""
    source = Path(path) if path is not None else WEB/'atlas_data.json'
    text = source.read_bytes().decode('utf-8')
    if path is None:
        manifest = read_json((WEB/'atlas_manifest.json').read_text(encoding='utf-8'))
        if manifest.get('inventory_utf8_sha256') != text_sha256(text):
            raise ValueError('Bundled atlas inventory bytes differ from its manifest')
    return validate_inventory(read_json(text)), text


def default_filters():
    return dict(query='', tier='', cohort='', flag='', sort='event_id')


def validate_filters(filters):
    if (not isinstance(filters, dict) or set(filters) != set(default_filters())
            or any(not isinstance(x, str) or len(x) > 1000 for x in filters.values())
            or filters['tier'] not in ('', *TIERS) or filters['sort'] not in ('event_id', 'ra_deg', 'tier')):
        raise ValueError('Invalid atlas filter shape or sort')
    return filters


def filter_events(inventory, filters=None):
    filters = default_filters() if filters is None else validate_filters(filters)
    query = filters['query'].strip().lower()
    rows = [e for e in inventory['events']
        if (not query or query in ' '.join([e['event_id'], *e['known_aliases'], *e['quality_flags']]).lower())
        and (not filters['tier'] or e['tier'] == filters['tier'])
        and (not filters['cohort'] or filters['cohort'] in e['cohorts'])
        and (not filters['flag'] or filters['flag'] in e['quality_flags'])]
    if filters['sort'] == 'ra_deg':
        key = lambda e: (math.inf if e['source_direction']['ra_deg'] is None else e['source_direction']['ra_deg'], e['event_id'])
    elif filters['sort'] == 'tier': key = lambda e: (-TIERS.index(e['tier']), e['event_id'])
    else: key = lambda e: e['event_id']
    return sorted(rows, key=key)


def create_replay(inventory_text, filters=None, *, origin='python', created_utc=None):
    inventory = validate_inventory(read_json(inventory_text))
    filters = default_filters() if filters is None else validate_filters(filters)
    source_sha = text_sha256(inventory_text)
    rows = filter_events(inventory, filters)
    payload = dict(schema_version=REPLAY, created_utc=created_utc or datetime.now(timezone.utc).isoformat(),
        repository=REPOSITORY, integrity_scope='SHA-256 detects edits; it is not an authenticity signature.',
        data_source=dict(origin=origin, inventory_utf8_sha256=source_sha), filters=deepcopy(filters),
        selected_event_ids=[e['event_id'] for e in rows], filtered_events=deepcopy(rows),
        inventory_utf8_sha256=source_sha, inventory_json=inventory_text)
    payload_json = json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False)
    return dict(schema_version=REPLAY, payload_json=payload_json, payload_sha256=text_sha256(payload_json))


def validate_replay(envelope):
    """Verify both raw-text hashes and exact retained/filter-selected records."""
    _finite_tree(envelope)
    if (not isinstance(envelope, dict) or envelope.get('schema_version') != REPLAY
            or not isinstance(envelope.get('payload_json'), str)
            or text_sha256(envelope['payload_json']) != envelope.get('payload_sha256')):
        raise ValueError('Atlas replay payload SHA-256 mismatch or unsupported schema')
    payload = read_json(envelope['payload_json'])
    if payload.get('schema_version') != REPLAY or payload.get('repository') != REPOSITORY:
        raise ValueError('Replay schema or formal repository differs')
    raw = payload.get('inventory_json')
    if not isinstance(raw, str) or text_sha256(raw) != payload.get('inventory_utf8_sha256'):
        raise ValueError('Replay original inventory SHA-256 mismatch')
    if not isinstance(payload.get('data_source'), dict) or payload['data_source'].get('inventory_utf8_sha256') != payload['inventory_utf8_sha256']:
        raise ValueError('Replay source and inventory hashes conflict')
    inventory = validate_inventory(read_json(raw))
    rows = filter_events(inventory, validate_filters(payload.get('filters')))
    if payload.get('selected_event_ids') != [e['event_id'] for e in rows] or not _same_json(payload.get('filtered_events'), rows):
        raise ValueError('Replay identities/records differ from full inventory and filters')
    return {**payload, 'inventory': inventory}


def summary(inventory, filters=None):
    from .interpretation import surface_geometry_interpretation
    rows = filter_events(inventory, filters)
    return dict(schema_version=SCHEMA, events=len(inventory['events']), selected=len(rows),
        separate_benchmarks=len(inventory.get('benchmarks', [])),
        tiers={tier: sum(e['tier'] == tier for e in rows) for tier in TIERS},
        source_directions=sum(e['map_eligibility']['sky_marker'] for e in rows),
        independently_inferred_lens_mass=None, new_black_hole_interpretation=False,
        formal_BHSM_repository=REPOSITORY, scientific_status=inventory['metadata'].get('status'),
        surface_geometry_interpretation=surface_geometry_interpretation())
