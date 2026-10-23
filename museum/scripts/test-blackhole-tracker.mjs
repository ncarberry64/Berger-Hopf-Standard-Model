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
} from '../lib/blackhole-tracker.ts';

const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
const near = (a, b) => assert(Math.abs(a - b) < 2e-11, `${a} != ${b}`);

test('Museum point-lens view matches all nine pinned product forward rows', () => {
  assert.equal(trackerExample.source_revision, trackerCodeRevision);
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
  for (const record of trackerExample.source_records) {
    const file = await readFile(
      new URL(`../../${record.path}`, import.meta.url),
      'utf8',
    );
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
  const expected = {
    'BHSM_Blackhole_Tracker_Product.zip':
      '1dac4273060e7795bc025f104d53cb3106574a730f9a4c665b869e11adfa4c78',
    'bhsm_blackhole_tracker-0.2.0rc2-py3-none-any.whl':
      '323bcf675f6fe1c1262e85be49644d3736c2777788ecf2f92568f1cc6ba92ae3',
  };
  for (const item of receipt.files) {
    const bytes = await readFile(new URL(item.file, base));
    assert.equal(bytes.length, item.bytes);
    assert.equal(sha(bytes), item.sha256);
    if (expected[item.file]) assert.equal(item.sha256, expected[item.file]);
  }
  const product = zipEntries(
    await readFile(new URL('BHSM_Blackhole_Tracker_Product.zip', base)),
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
  assert.equal(
    [...product.keys()].filter((name) => name.startsWith('product/')).length,
    108,
  );
  const wheel = zipEntries(
    await readFile(
      new URL('bhsm_blackhole_tracker-0.2.0rc2-py3-none-any.whl', base),
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
});
