/* Offline candidate-inventory admission, filtering and integrity-checked replay.
   This module performs no physical fit or classification inference. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.AtlasCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const SCHEMA = 'bhsm.blackhole_tracker.candidate_inventory.v1';
  const REPLAY = 'bhsm.blackhole_tracker.candidate_atlas_replay.v1';
  const REPOSITORY = 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model';
  const TIERS = ['REVIEW_REQUIRED', 'SUPPORTED_LENSING_EVENT', 'BLACK_HOLE_SEARCH_TARGET',
    'BLACK_HOLE_CANDIDATE', 'STRONGLY_SUPPORTED_BLACK_HOLE_IDENTIFICATION'];
  const LENS_FIELDS = ['position', 'position_epoch', 'position_covariance', 'distance_pc',
    'mass_msun', 'proper_motion_mas_yr', 'radial_velocity_km_s'];
  function requireThat(condition, message) { if (!condition) throw new Error(message); }
  function object(value) { return value !== null && typeof value === 'object' && !Array.isArray(value); }
  function finiteTree(value, depth = 0) {
    requireThat(depth < 80, 'The JSON nesting limit was exceeded.');
    if (typeof value === 'number') {
      requireThat(Number.isFinite(value), 'Nonfinite JSON number.');
      requireThat(!Number.isInteger(value) || Number.isSafeInteger(value), 'Integer outside the exact JavaScript range; retain large identity tokens as strings.');
    }
    if (value && typeof value === 'object') {
      for (const key of Object.keys(value)) {
        requireThat(!['__proto__', 'prototype', 'constructor'].includes(key), 'Unsafe JSON key.');
        finiteTree(value[key], depth + 1);
      }
    }
  }
  function stringArray(value, label) {
    requireThat(Array.isArray(value) && value.every(x => typeof x === 'string'), `${label} must be a string array.`);
  }
  function decodeUtf8(bytes) {
    // Fatal decoding prevents a corrupted file from being admitted after the
    // browser silently replaces invalid byte sequences. Preserve a BOM so the
    // strict JSON grammar rejects it rather than changing the hashed bytes.
    return new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(bytes);
  }
  function parseJsonStrict(text) {
    requireThat(typeof text === 'string' && text.length <= 32 * 1024 * 1024, 'JSON text exceeds the admission limit.');
    let i = 0;
    const number = /-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/y;
    const ws = () => { while (i < text.length && /[ \t\r\n]/.test(text[i])) i++; };
    function string() {
      requireThat(text[i] === '"', 'Invalid JSON string.'); const start = i++;
      while (i < text.length) {
        if (text[i] === '\\') { i += 2; continue; }
        if (text[i++] === '"') return JSON.parse(text.slice(start, i));
      }
      throw new Error('Unterminated JSON string.');
    }
    function value(depth) {
      requireThat(depth < 80, 'The JSON nesting limit was exceeded.'); ws();
      if (text[i] === '{') {
        i++; ws(); const keys = new Set(); if (text[i] === '}') { i++; return; }
        while (true) {
          ws(); const key = string(); requireThat(!keys.has(key), `Duplicate JSON key: ${key}`); keys.add(key); ws();
          requireThat(text[i++] === ':', 'Invalid JSON object separator.'); value(depth + 1); ws();
          if (text[i] === '}') { i++; return; } requireThat(text[i++] === ',', 'Invalid JSON object terminator.');
        }
      }
      if (text[i] === '[') {
        i++; ws(); if (text[i] === ']') { i++; return; }
        while (true) { value(depth + 1); ws(); if (text[i] === ']') { i++; return; } requireThat(text[i++] === ',', 'Invalid JSON array terminator.'); }
      }
      if (text[i] === '"') { string(); return; }
      for (const literal of ['true', 'false', 'null']) if (text.startsWith(literal, i)) { i += literal.length; return; }
      number.lastIndex = i; const m = number.exec(text); requireThat(m !== null, 'Invalid JSON value.'); i = number.lastIndex;
    }
    value(0); ws(); requireThat(i === text.length, 'Unexpected content after the JSON value.');
    const parsed = JSON.parse(text); finiteTree(parsed); return parsed;
  }
  function validateInventory(value) {
    finiteTree(value);
    requireThat(object(value) && value.schema_version === SCHEMA, 'Unsupported candidate-inventory schema.');
    requireThat(object(value.metadata), 'Inventory metadata is required.');
    requireThat(value.metadata.formal_BHSM_repository === REPOSITORY, 'The formal BHSM reviewer repository is missing or incorrect.');
    requireThat(Array.isArray(value.events) && value.events.length > 0 && value.events.length <= 20000,
      'Inventory must contain 1–20,000 events.');
    requireThat(value.benchmarks === undefined || Array.isArray(value.benchmarks), 'Benchmarks must be a separate array.');
    const benchmarkRows = value.benchmarks || [];
    const ids = new Set();
    for (const event of [...value.events, ...benchmarkRows]) {
      requireThat(object(event) && typeof event.event_id === 'string' && event.event_id.length > 0,
        'Every event needs an event_id.');
      requireThat(!ids.has(event.event_id), `Duplicate event_id: ${event.event_id}`); ids.add(event.event_id);
      stringArray(event.known_aliases, 'known_aliases'); stringArray(event.cohorts, 'cohorts');
      stringArray(event.quality_flags, 'quality_flags');
      requireThat(TIERS.includes(event.tier), `Unknown tier for ${event.event_id}.`);
      requireThat(event.new_black_hole_interpretation === false && event.accepted_engine_black_hole === false,
        `Version 1 cannot assert a new or engine-accepted black-hole identification: ${event.event_id}`);
      requireThat(Array.isArray(event.provenance) && event.provenance.length > 0, `Missing provenance: ${event.event_id}`);
      requireThat(object(event.source_direction) && event.source_direction.role === 'SOURCE_EVENT_DIRECTION',
        `Direction role is not the source/event direction: ${event.event_id}`);
      const d = event.source_direction;
      const nullDirection = d.ra_deg === null && d.dec_deg === null;
      requireThat(nullDirection || (Number.isFinite(d.ra_deg) && d.ra_deg >= 0 && d.ra_deg < 360 &&
        Number.isFinite(d.dec_deg) && d.dec_deg >= -90 && d.dec_deg <= 90), `Invalid sky direction: ${event.event_id}`);
      requireThat(Object.hasOwn(d, 'epoch') && Object.hasOwn(d, 'uncertainty'), `Direction epoch/uncertainty missing: ${event.event_id}`);
      requireThat(object(event.lens), `Lens availability record missing: ${event.event_id}`);
      // Version 1 supplies no independently inferred lens quantities. A future
      // measurement-bearing schema needs a reviewed admission/rendering route.
      for (const key of LENS_FIELDS) requireThat(Object.hasOwn(event.lens, key) && event.lens[key] === null,
        `Version 1 requires unavailable lens.${key} to remain null: ${event.event_id}`);
      requireThat(object(event.map_eligibility) && event.map_eligibility.three_dimensional === false &&
        event.map_eligibility.propagate_position === false && event.map_eligibility.sky_marker === !nullDirection,
        `Unsupported location/propagation claim: ${event.event_id}`);
    }
    for (const b of benchmarkRows) requireThat(b.classification_source === 'LITERATURE' &&
      typeof b.tracker_recovery_status === 'string' && b.tracker_recovery_status.startsWith('NOT_ESTABLISHED') &&
      b.cohorts.includes('SEPARATE_KNOWN_SYSTEM_BENCHMARK'), 'Benchmark must retain its literature label and unestablished tracker recovery.');
    if (value.metadata.counts !== undefined) {
      const counts = value.metadata.counts;
      requireThat(object(counts) && counts.unique_events === value.events.length &&
        counts.sky_markers === value.events.filter(e => e.source_direction.ra_deg !== null).length &&
        counts.new_BH_interpretations === 0 && counts.independently_measured_lens_mass_in_atlas === 0,
        'Inventory summary counts conflict with the admitted events or unavailable mass policy.');
      requireThat(object(counts.tier_counts) && TIERS.every(t => counts.tier_counts[t] === value.events.filter(e => e.tier === t).length),
        'Evidence-tier summary counts conflict with the admitted events.');
    }
    return value;
  }
  function defaultFilters() { return {query: '', tier: '', cohort: '', flag: '', sort: 'event_id'}; }
  function validateFilters(filters) {
    requireThat(object(filters), 'Replay filters are missing.');
    const keys = Object.keys(defaultFilters());
    requireThat(Object.keys(filters).length === keys.length && keys.every(k => typeof filters[k] === 'string'), 'Invalid filter shape.');
    requireThat(!filters.tier || TIERS.includes(filters.tier), 'Invalid tier filter.');
    requireThat(['event_id', 'ra_deg', 'tier'].includes(filters.sort), 'Invalid sort field.');
    requireThat(Object.values(filters).every(x => x.length <= 1000), 'Filter text too long.');
    return filters;
  }
  function filterEvents(inventory, filters) {
    validateFilters(filters);
    const query = filters.query.trim().toLocaleLowerCase('en');
    const rows = inventory.events.filter(e =>
      (!query || [e.event_id, ...e.known_aliases, ...e.quality_flags].join(' ').toLocaleLowerCase('en').includes(query)) &&
      (!filters.tier || e.tier === filters.tier) && (!filters.cohort || e.cohorts.includes(filters.cohort)) &&
      (!filters.flag || e.quality_flags.includes(filters.flag)));
    return rows.sort((a, b) => {
      let primary = 0;
      if (filters.sort === 'ra_deg') primary = (a.source_direction.ra_deg ?? Infinity) - (b.source_direction.ra_deg ?? Infinity);
      if (filters.sort === 'tier') primary = TIERS.indexOf(b.tier) - TIERS.indexOf(a.tier);
      return primary || (a.event_id < b.event_id ? -1 : a.event_id > b.event_id ? 1 : 0);
    });
  }
  function canonical(value) {
    if (value === null || typeof value !== 'object') return JSON.stringify(value);
    if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
    return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
  }
  async function sha256(value) {
    const webcrypto = globalThis.crypto || (typeof require === 'function' ? require('node:crypto').webcrypto : null);
    requireThat(webcrypto?.subtle, 'SHA-256 requires a secure local browser context. Open the local server URL.');
    const bytes = typeof value === 'string' ? new TextEncoder().encode(value) : value;
    return Array.from(new Uint8Array(await webcrypto.subtle.digest('SHA-256', bytes)), x => x.toString(16).padStart(2, '0')).join('');
  }
  async function createReplay(inventory, filters, source, createdUtc, inventoryText) {
    validateInventory(inventory); validateFilters(filters);
    requireThat(typeof inventoryText === 'string' && canonical(parseJsonStrict(inventoryText)) === canonical(inventory),
      'Replay needs the exact original inventory JSON text.');
    const inventoryHash = await sha256(inventoryText);
    const payload = {schema_version: REPLAY, created_utc: createdUtc, repository: REPOSITORY,
      integrity_scope: 'SHA-256 detects accidental or unreconciled edits; it is not an authenticity signature.',
      data_source: {...source, inventory_utf8_sha256: inventoryHash}, filters: {...filters}, selected_event_ids: filterEvents(inventory, filters).map(e => e.event_id),
      filtered_events: filterEvents(inventory, filters), inventory_utf8_sha256: inventoryHash, inventory_json: inventoryText};
    finiteTree(payload);
    const payloadJson = JSON.stringify(payload, null, 2);
    return {schema_version: REPLAY, payload_json: payloadJson, payload_sha256: await sha256(payloadJson)};
  }
  async function validateReplay(envelope) {
    finiteTree(envelope);
    requireThat(object(envelope) && envelope.schema_version === REPLAY && typeof envelope.payload_json === 'string' &&
      typeof envelope.payload_sha256 === 'string', 'Replay envelope is missing.');
    requireThat(await sha256(envelope.payload_json) === envelope.payload_sha256, 'Replay integrity check failed: payload SHA-256 mismatch.');
    const p = parseJsonStrict(envelope.payload_json);
    requireThat(p.schema_version === REPLAY && p.repository === REPOSITORY, 'Unsupported replay or reviewer repository.');
    requireThat(typeof p.inventory_json === 'string', 'Original inventory bytes are missing.');
    requireThat(await sha256(p.inventory_json) === p.inventory_utf8_sha256, 'Replay inventory SHA-256 mismatch.');
    requireThat(object(p.data_source) && p.data_source.inventory_utf8_sha256 === p.inventory_utf8_sha256, 'Replay source/inventory hash conflict.');
    const inventory = validateInventory(parseJsonStrict(p.inventory_json)); validateFilters(p.filters);
    requireThat(canonical(filterEvents(inventory, p.filters).map(e => e.event_id)) === canonical(p.selected_event_ids),
      'Replay filtered event identities do not match the inventory and filters.');
    requireThat(canonical(filterEvents(inventory, p.filters)) === canonical(p.filtered_events), 'Replay filtered records do not match the complete inventory.');
    return {...p, inventory};
  }
  function csvEscape(value) {
    let s = value === null || value === undefined ? '' : typeof value === 'object' ? canonical(value) : String(value);
    // Prevent spreadsheet formula execution while leaving JSON values untouched.
    if (/^[=+\-@\t\r]/.test(s) && !/^-?\d+(\.\d+)?([eE][+-]?\d+)?$/.test(s)) s = "'" + s;
    return '"' + s.replace(/"/g, '""') + '"';
  }
  function exportCsv(inventory, filters, sourceSha) {
    validateInventory(inventory);
    const columns = ['event_id', 'known_aliases', 'cohorts', 'tier', 'quality_flags', 'source_ra_deg', 'source_dec_deg',
      'source_direction_role', 'source_frame', 'source_equinox', 'source_epoch', 'source_uncertainty', 'lens_position',
      'lens_position_epoch', 'lens_position_covariance', 'lens_distance_pc', 'lens_mass_msun', 'lens_proper_motion_mas_yr',
      'lens_radial_velocity_km_s', 'null_policy', 'photometric_assessment', 'literature_assessment', 'next_actions', 'provenance',
      'inventory_source_sha256', 'reviewer_repository', 'inventory_metadata', 'filters'];
    const lines = [columns.map(csvEscape).join(',')];
    for (const e of filterEvents(inventory, filters)) {
      const d = e.source_direction;
      const row = [e.event_id, e.known_aliases, e.cohorts, e.tier, e.quality_flags, d.ra_deg, d.dec_deg, d.role, d.frame,
        d.equinox, d.epoch, d.uncertainty, e.lens.position, e.lens.position_epoch, e.lens.position_covariance,
        e.lens.distance_pc, e.lens.mass_msun, e.lens.proper_motion_mas_yr, e.lens.radial_velocity_km_s,
        'Empty unavailable scalar fields mean null, never zero; full original data and metadata are in the JSON replay.',
        e.photometric_assessment ?? null, e.literature_assessment ?? null, e.next_actions ?? null, e.provenance, sourceSha, REPOSITORY,
        inventory.metadata, filters];
      lines.push(row.map(csvEscape).join(','));
    }
    return '\ufeff' + lines.join('\r\n') + '\r\n';
  }
  return {SCHEMA, REPLAY, REPOSITORY, TIERS, LENS_FIELDS, decodeUtf8, parseJsonStrict, validateInventory, defaultFilters, validateFilters,
    filterEvents, canonical, sha256, createReplay, validateReplay, exportCsv};
});
