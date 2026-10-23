import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { inflateRawSync } from 'node:zlib';
import {
  trackerFrame,
  trackerCenter,
  trackerExample,
  trackerCodeRevision,
  trackerPaperRevision,
  trackerAnimationRevision,
  trackerVersion,
  trackerPilot,
  trackerJoint,
  trackerAtlas,
  trackerReviewerRevision,
} from '../lib/blackhole-tracker.ts';

const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
const near = (a, b) => assert(Math.abs(a - b) < 2e-11, `${a} != ${b}`);

test('Museum point-lens view matches all nine pinned product forward rows', () => {
  assert.equal(trackerExample.source_revision, trackerAnimationRevision);
  trackerExample.epochs_yr.forEach((epoch, row) => {
    const pair = trackerFrame(epoch).pairs[row % 3];
    const values = [
      ...pair.plus,
      ...pair.minus,
      pair.lnFluxRatio,
      pair.delaySeconds,
    ];
    values.forEach((value, column) =>
      near(value, trackerExample.forward_reference[row][column]),
    );
  });
  near(trackerFrame(2020).theta, trackerExample.theta_reference_mas);
});

test('every allowed mass/year satisfies its lens equation; inputs stay distinct from estimates', () => {
  for (const epoch of [2015, 2017.25, 2020, 2025])
    for (const mass of [0.5, 1, 1.65, 2]) {
      const frame = trackerFrame(epoch, mass);
      for (const pair of frame.pairs)
        for (const image of [pair.plus, pair.minus]) {
          const relative = image.map((v, i) => v - frame.center[i]);
          const r2 = relative[0] ** 2 + relative[1] ** 2;
          relative.forEach((v, i) =>
            near(
              v - (frame.theta ** 2 * v) / r2,
              pair.source[i] - frame.center[i],
            ),
          );
          assert(pair.delaySeconds > 0 && pair.lnFluxRatio > 0);
        }
      assert.equal(frame.mass, trackerExample.truth.mass_msun * mass);
    }
  near(trackerFrame(2020, 2).theta / trackerFrame(2020, 1).theta, Math.sqrt(2));
  near(trackerCenter(2025)[0] - trackerCenter(2015)[0], 0.65);
  near(trackerCenter(2025)[1] - trackerCenter(2015)[1], -0.38);
  for (const epoch of [NaN, Infinity, 2014, 2026])
    assert.throws(() => trackerFrame(epoch));
  for (const mass of [NaN, Infinity, 0, 0.49, 2.01])
    assert.throws(() => trackerFrame(2020, mass));
});

test('exhibit fixture preserves the pinned product geometry/truth and normalized source hashes', async () => {
  const historicalProduct = zipEntries(await readFile(new URL(
    '../public/research/blackhole-tracker/history/0.2.0rc2/BHSM_Blackhole_Tracker_Product.zip',
    import.meta.url,
  )));
  for (const record of trackerExample.source_records) {
    const path = record.path.replace('products/blackhole_tracker/', 'product/');
    const file = historicalProduct.get(path).toString();
    assert.equal(
      sha(file.replaceAll('\r\n', '\n')),
      record.normalized_source_sha256,
    );
    if (record.path.endsWith('.truth.json'))
      assert.deepEqual(JSON.parse(file), trackerExample.truth);
    else if (record.path.endsWith('/nearby_motion.json')) {
      const data = JSON.parse(file);
      assert.deepEqual(data.geometry, trackerExample.geometry);
      assert.deepEqual(data.epochs_yr, trackerExample.epochs_yr);
      assert.equal(data.reference_epoch_yr, trackerExample.reference_epoch_yr);
    }
  }
});

function zipEntries(bytes) {
  let end = bytes.length - 22;
  while (end >= 0 && bytes.readUInt32LE(end) !== 0x06054b50) end--;
  assert(end >= 0, 'ZIP end directory exists');
  const count = bytes.readUInt16LE(end + 10),
    files = new Map();
  let cursor = bytes.readUInt32LE(end + 16);
  for (let n = 0; n < count; n++) {
    assert.equal(bytes.readUInt32LE(cursor), 0x02014b50);
    const size = bytes.readUInt32LE(cursor + 20),
      plainSize = bytes.readUInt32LE(cursor + 24);
    const nameSize = bytes.readUInt16LE(cursor + 28),
      extra = bytes.readUInt16LE(cursor + 30),
      comment = bytes.readUInt16LE(cursor + 32);
    const name = bytes.subarray(cursor + 46, cursor + 46 + nameSize).toString();
    const local = bytes.readUInt32LE(cursor + 42),
      method = bytes.readUInt16LE(cursor + 10);
    assert.equal(bytes.readUInt32LE(local), 0x04034b50);
    const start =
      local +
      30 +
      bytes.readUInt16LE(local + 26) +
      bytes.readUInt16LE(local + 28);
    const packed = bytes.subarray(start, start + size);
    assert([0, 8].includes(method));
    const unpacked = method === 8 ? inflateRawSync(packed) : packed;
    assert.equal(unpacked.length, plainSize);
    files.set(name, unpacked);
    cursor += 46 + nameSize + extra + comment;
  }
  return files;
}

test('public app downloads are exact reviewed artifacts with both canonical license notices', async () => {
  const base = new URL(
    '../public/research/blackhole-tracker/',
    import.meta.url,
  );
  const receipt = JSON.parse(
    await readFile(new URL('DISTRIBUTION.json', base), 'utf8'),
  );
  assert.equal(receipt.reviewed_product_code_revision, trackerCodeRevision);
  assert.equal(receipt.reviewed_paper_revision, trackerPaperRevision);
  assert.equal(receipt.reviewer_guide_revision, trackerReviewerRevision);
  assert.equal(receipt.version, trackerVersion);
  for (const item of receipt.files) {
    const bytes = await readFile(new URL(item.file, base));
    assert.equal(bytes.length, item.bytes);
    assert.equal(sha(bytes), item.sha256);
  }
  const product = zipEntries(
    await readFile(new URL(`BHSM_Blackhole_Tracker_Product_${trackerVersion}.zip`, base)),
  );
  for (const notice of ['LICENSE.md', 'ACADEMIC_USE.md']) {
    assert.deepEqual(
      product.get(notice),
      await readFile(new URL(notice, base)),
    );
    const canonical = await readFile(
      new URL(`../../${notice}`, import.meta.url),
      'utf8',
    );
    assert.equal(
      product.get(notice).toString().replaceAll('\r\n', '\n'),
      canonical.replaceAll('\r\n', '\n'),
    );
  }
  const manifest = JSON.parse(product.get('PRODUCT_MANIFEST.json').toString());
  assert(manifest, 'Portable source has its own manifest');
  assert.equal(manifest.formal_code_commit, trackerCodeRevision);
  assert.equal(Object.keys(manifest.files).length, receipt.product_source_file_count);
  assert.equal(product.size, receipt.product_source_file_count + 3);
  for (const [name, digest] of Object.entries(manifest.files))
    assert.equal(sha(product.get(name)), digest, name);
  const wheel = zipEntries(
    await readFile(
      new URL(`bhsm_blackhole_tracker-${trackerVersion}-py3-none-any.whl`, base),
    ),
  );
  const metadata = [...wheel]
    .find(([name]) => name.endsWith('.dist-info/METADATA'))[1]
    .toString();
  assert(
    metadata.includes(
      'https://github.com/ncarberry64/Berger-Hopf-Standard-Model',
    ),
  );
  assert(metadata.includes(`Version: ${trackerVersion}`));
  assert(metadata.includes('Provides-Extra: astrometry'));
  assert(metadata.includes('Requires-Dist: astropy>=6; extra == "astrometry"'));
});

test('historical rc2 bytes remain immutable and separate from current downloads', async () => {
  const base = new URL('../public/research/blackhole-tracker/history/0.2.0rc2/', import.meta.url);
  const receipt = JSON.parse(await readFile(new URL('DISTRIBUTION.json', base), 'utf8'));
  assert.equal(receipt.version, '0.2.0rc2');
  const expected = {
    'BHSM_Blackhole_Tracker_Product.zip': '1dac4273060e7795bc025f104d53cb3106574a730f9a4c665b869e11adfa4c78',
    'bhsm_blackhole_tracker-0.2.0rc2-py3-none-any.whl': '323bcf675f6fe1c1262e85be49644d3736c2777788ecf2f92568f1cc6ba92ae3',
  };
  for (const item of receipt.files) {
    const bytes = await readFile(new URL(item.file, base));
    assert.equal(bytes.length, item.bytes); assert.equal(sha(bytes), item.sha256);
    if (expected[item.file]) assert.equal(sha(bytes), expected[item.file]);
  }
});

test('real-pilot downloads retain all100 cases and no mass or discovery claim', async () => {
  assert.equal(trackerPilot.role, 'ACTUAL_HISTORICAL_OBSERVATIONS_DISTINCT_FROM_SYNTHETIC_ANIMATION');
  assert.equal(trackerPilot.event_count, 100);
  assert.equal(trackerPilot.native_measurement_count, 76344);
  assert.equal(trackerPilot.inadequate_model_or_noise_screens, 89);
  assert.equal(trackerPilot.adequate_diagonal_chi_square_screens, 11);
  assert.equal(trackerPilot.new_black_hole_interpretations, 0);
  assert.equal(trackerPilot.mass_status, 'MASS_UNRESOLVED');
  assert.deepEqual(trackerPilot.targets.map((target) => target.event_id), ['OGLE3-ULENS-0585', 'OGLE3-ULENS-3092']);
  assert(trackerPilot.targets.every((target) => target.mass_status === 'MASS_UNRESOLVED'));
  const base = new URL('../public/research/blackhole-tracker/pilot-20261022-v1/', import.meta.url);
  for (const item of trackerPilot.files) {
    const bytes = await readFile(new URL(item.file, base));
    assert.equal(bytes.length, item.bytes); assert.equal(sha(bytes), item.sha256);
  }
  assert.deepEqual(JSON.parse(await readFile(new URL('PILOT_PROVENANCE.json', base), 'utf8')), trackerPilot);
  const csv = await readFile(new URL('all_100_results.csv', base), 'utf8');
  assert.equal(csv.trim().split(/\r?\n/).length, 101);
  assert(csv.includes('OGLE3-ULENS-0337'));
  assert(csv.includes('MASS_UNRESOLVED'));
});


test('historical rc3 receipt and versioned artifacts retain their original bytes', async () => {
  const base = new URL('../public/research/blackhole-tracker/', import.meta.url);
  const receiptBytes = await readFile(new URL('DISTRIBUTION_0.2.0rc3.json', base));
  assert.deepEqual(receiptBytes, await readFile(new URL('history/0.2.0rc3/DISTRIBUTION.json', base)));
  const receipt = JSON.parse(receiptBytes.toString());
  assert.equal(receipt.version, '0.2.0rc3');
  assert.equal(receipt.reviewed_product_code_revision, '002b9ecfe2f1a778b68b7558581997c05919ae93');
  assert.equal(receipt.reviewed_paper_revision, 'b80fd756c285844b6ea90110c4d58db47092830c');
  const expected = {
    'BHSM_Blackhole_Tracker_Product_0.2.0rc3.zip': 'accb46a03b79f86e9df74e1c4c2e7baf7062887b831a087856132f437e03b3e9',
    'bhsm_blackhole_tracker-0.2.0rc3-py3-none-any.whl': '11fbbae7799858667c8b8c2e8956c126c9f5103276ee044f2d5bcf6457d8930f',
    'BHSM_Blackhole_Tracker_Source_0.2.0rc3.zip': '8af0878d3ff647346de2ebb4bf8f0446d382b4ce3e5c2911bdd456c901af1166',
    'BHSM_Blackhole_Tracker_0.2.0rc3.pdf': '94b4193e2b387452348870610f4c7c328234d936a4a59aae5e545c04818fcfb2',
  };
  for (const item of receipt.files) {
    const bytes = await readFile(new URL(item.file, base));
    assert.equal(bytes.length, item.bytes);
    assert.equal(sha(bytes), item.sha256);
    if (expected[item.file]) assert.equal(sha(bytes), expected[item.file]);
  }
});


test('reviewed joint source pack retains exact third-party observations, header evidence and rights', async () => {
  const base = new URL('../public/research/blackhole-tracker/', import.meta.url);
  const bytes = await readFile(new URL('BHSM_OB110462_2023_SourcePack_v1.zip', base));
  assert.equal(bytes.length, 764958);
  assert.equal(sha(bytes), '71d36a03e4ba275e91bea62f4784a5193f34ad32d3777b637453f91151bafa99');
  const files = zipEntries(bytes);
  assert.equal(files.size, 98);
  const prefix = 'portable_2023_benchmark_v1/';
  const manifest = JSON.parse(files.get(`${prefix}ACQUISITION_MANIFEST.json`).toString());
  assert.equal(manifest.files.length, 97);
  assert.equal(manifest.raw_observations_unchanged, true);
  const expected = new Set([`${prefix}ACQUISITION_MANIFEST.json`]);
  for (const item of manifest.files) {
    const name = `${prefix}${item.path}`;
    expected.add(name);
    const content = files.get(name);
    assert.equal(content.length, item.bytes, name);
    assert.equal(sha(content), item.sha256, name);
  }
  assert.deepEqual(new Set(files.keys()), expected);
  assert.equal(manifest.files.filter((item) => item.role === 'bounded_public_HST_FITS_prefix').length, 82);
  assert(manifest.files.some((item) => item.path === 'verify_or_refetch_2023_sources.py'));
  const rights = JSON.parse(files.get(`${prefix}RIGHTS_EVIDENCE.json`).toString());
  assert.match(rights.author_HST_tables, /CC-BY4\.0/);
  assert.match(rights.corrected_OGLE, /CC-BY4\.0/);
  assert.match(rights.third_party_override, /do not replace/);
  const attribution = files.get(`${prefix}CITATIONS_AND_RIGHTS.md`).toString();
  assert(attribution.includes('10.5281/zenodo.20056044'));
  assert(attribution.includes('2308.03302v2'));
});


test('separate joint evidence keeps every inadequate candidate and no supported mass', async () => {
  const base = new URL('../public/research/blackhole-tracker/joint-20261022-v2/', import.meta.url);
  // The frozen rc4 evidence retains its historical provenance, independently
  // of the latest paper/reviewer presentation pins.
  assert.equal(trackerJoint.formal_paper_revision, 'cb79f8693ba5f8e25f0858acc826b6718c974555');
  assert.equal(trackerJoint.original_OGLE_rows_retained, 15533);
  assert.equal(trackerJoint.selected_OGLE_photometric_rows, 12500);
  assert.equal(trackerJoint.fit_photometric_rows, 12521);
  assert.equal(trackerJoint.HST_photometric_rows, 21);
  assert.equal(trackerJoint.HST_angular_rows, 21);
  assert.equal(trackerJoint.HST_dated_visits, 11);
  assert.equal(trackerJoint.bounded_exposure_header_prefixes, 82);
  assert.equal(trackerJoint.adequate_candidates, 0);
  assert.equal(trackerJoint.accepted_mass_intervals, 0);
  assert.equal(trackerJoint.new_black_hole_interpretations, 0);
  assert.equal(trackerJoint.supported_mass_msun, null);
  assert.equal(trackerJoint.calibration_request_status, 'PREPARED_FOR_AUTHOR_REVIEW_NOT_SENT');
  assert.deepEqual(trackerJoint.candidates.map((candidate) => candidate.id), ['G0', 'G1', 'G2']);
  for (const candidate of trackerJoint.candidates) {
    assert.equal(candidate.status, 'JOINT_MODEL_OR_NOISE_INADEQUATE');
    assert.equal(candidate.accepted_mass, false);
    assert.equal(candidate.accepted_black_hole_identification, false);
    assert.equal(candidate.supported_mass_msun, null);
    assert(candidate.failed_structure_bins > 0);
  }
  for (const item of trackerJoint.files) {
    const bytes = await readFile(new URL(item.file, base));
    assert.equal(bytes.length, item.bytes, item.file);
    assert.equal(sha(bytes), item.sha256, item.file);
  }
  assert.deepEqual(JSON.parse(await readFile(new URL('JOINT_PROVENANCE.json', base), 'utf8')), trackerJoint);
  const table = await readFile(new URL('baseline_summary.csv', base), 'utf8');
  const lines = table.trim().split(/\r?\n/);
  const columns = lines.shift().split(',');
  assert.equal(lines.length, 3);
  for (const line of lines) {
    const fields = line.split(',');
    assert.equal(fields[columns.indexOf('status')], 'JOINT_MODEL_OR_NOISE_INADEQUATE');
    assert.equal(fields[columns.indexOf('accepted_mass')], 'False');
    assert.equal(fields[columns.indexOf('accepted_BH')], 'False');
  }
});

test('historical rc4 receipt and every referenced artifact retain their exact reviewed bytes', async () => {
  const base = new URL('../public/research/blackhole-tracker/', import.meta.url);
  const bytes = await readFile(new URL('DISTRIBUTION_0.2.0rc4.json', base));
  assert.equal(sha(bytes), '75ed7ca39eb0d5f0d56ff1db36dcd2ad985065ecd8424413226a0949c0e16cf6');
  assert.deepEqual(bytes, await readFile(new URL('history/0.2.0rc4/DISTRIBUTION.json', base)));
  const receipt = JSON.parse(bytes.toString());
  assert.equal(receipt.version, '0.2.0rc4');
  for (const item of receipt.files) {
    const content = await readFile(new URL(item.file, base));
    assert.equal(content.length, item.bytes, item.file);
    assert.equal(sha(content), item.sha256, item.file);
  }
});

test('static atlas is a faithful subset of the complete155-event inventory, with separate benchmark and unavailable lens quantities', async () => {
  const base = new URL('../public/research/blackhole-tracker/', import.meta.url);
  const metadata = await readFile(new URL('BHSM_Candidate_Atlas_Metadata_v3.zip', base));
  assert.equal(sha(metadata), '84d91dbd3f50edacddb0871f1d63783ca58154225795cc9b509d516c99bef53f');
  const members = zipEntries(metadata);
  assert.equal(members.size, 25);
  const inventoryBytes = members.get('inventory_v3.json');
  assert.equal(sha(inventoryBytes), trackerAtlas.inventory_utf8_sha256);
  const inventory = JSON.parse(inventoryBytes.toString());
  const formal = await readFile(new URL('../../products/blackhole_tracker/bhtracker/web/atlas_data.json', import.meta.url));
  assert.deepEqual(formal, inventoryBytes);
  assert.equal(trackerAtlas.formal_product_revision, trackerCodeRevision);
  assert.equal(trackerAtlas.repository_url, 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model');
  assert.equal(inventory.events.length, 155);
  assert.equal(new Set(inventory.events.map((event) => event.event_id)).size, 155);
  assert.equal(inventory.events.filter((event) => event.cohorts.includes('FROZEN_100_EVENT_PILOT_V1')).length, 100);
  assert.equal(inventory.events.filter((event) => event.cohorts.includes('WYRZYKOWSKI_2016_PARALLAX_59')).length, 59);
  assert.deepEqual(trackerAtlas.counts, inventory.metadata.counts);
  assert.equal(trackerAtlas.counts.pilot_inadequate_simple_model, 89);
  assert.equal(trackerAtlas.counts.older_native_unavailable, 33);
  assert.equal(trackerAtlas.counts.new_BH_interpretations, 0);
  const targets = inventory.events.filter((event) => event.tier === 'BLACK_HOLE_SEARCH_TARGET');
  assert.deepEqual(targets.map((event) => event.event_id), ['OGLE3-ULENS-0585', 'OGLE3-ULENS-3092', 'OGLE3-ULENS-PAR-13']);
  for (let index = 0; index < targets.length; index++) {
    const source = targets[index], shown = trackerAtlas.targets[index];
    for (const key of Object.keys(shown)) assert.deepEqual(shown[key], source[key], key);
    assert.equal(shown.source_direction.role, 'SOURCE_EVENT_DIRECTION');
    assert.equal(shown.source_direction.epoch, null);
    assert.equal(shown.source_direction.uncertainty, null);
  }
  assert.equal(targets.filter((event) => event.photometric_assessment.followup_eligible === true).length, 2);
  assert(targets[2].quality_flags.includes('GAIA_SOURCE_ASTROMETRIC_SOLUTION_UNRELIABLE'));
  for (const event of [...inventory.events, ...inventory.benchmarks])
    assert(Object.values(event.lens).every((value) => value === null));
  assert.equal(inventory.benchmarks.length, 1);
  assert.equal(trackerAtlas.benchmark.classification_source, 'LITERATURE');
  assert.match(trackerAtlas.benchmark.tracker_recovery_status, /^NOT_ESTABLISHED/);
  assert.deepEqual(trackerAtlas, JSON.parse(await readFile(new URL('candidate-atlas-20261023-v3/ATLAS_PROVENANCE.json', base), 'utf8')));
  const figure = await readFile(new URL('candidate-atlas-20261023-v3/candidate_inventory_sky.png', base));
  assert.equal(sha(figure), 'a28ac499e7658227ad2884d9f8f2bb89e3d61af2de6439b7ac5c4fc547b6d483');
});

test('atlas app download includes offline assets, complete inventory and actual launcher, with no hosted inference link', async () => {
  const base = new URL('../public/research/blackhole-tracker/', import.meta.url);
  const files = zipEntries(await readFile(new URL(`BHSM_Blackhole_Tracker_Product_${trackerVersion}.zip`, base)));
  const manifest = JSON.parse(files.get('PRODUCT_MANIFEST.json').toString());
  assert.equal(manifest.input_source_archive_sha256, '972e8f2a60a21bcbf487c013eb07d34ab315660c56f139eee4e6edbdb0d92d3e');
  assert.equal(sha(files.get('product/bhtracker/web/atlas_data.json')), trackerAtlas.inventory_utf8_sha256);
  const launcher = files.get('product/Start_Blackhole_Tracker_Atlas.cmd').toString();
  assert.match(launcher, /--page atlas/);
  for (const name of ['atlas.html', 'atlas.js', 'atlas-core.js', 'atlas.css']) {
    const source = files.get(`product/bhtracker/web/${name}`).toString();
    assert.doesNotMatch(source, /https:\/\/[^\s"']+\.(?:js|css)\b/);
  }
});
