import test from 'node:test';
import assert from 'node:assert/strict';
import {
  mkdtemp,
  mkdir,
  copyFile,
  readFile,
  writeFile,
  rm,
} from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, dirname, isAbsolute, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

test('standalone AI snapshot retains canonical excerpts and rejects missing or changed provenance', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'bhsm-museum-snapshot-'));
  assert(isAbsolute(directory));
  assert.equal(dirname(resolve(directory)), resolve(tmpdir()));
  assert(basename(directory).startsWith('bhsm-museum-snapshot-'));
  const museum = join(directory, 'museum');
  const root = new URL('../', import.meta.url);
  const run = () =>
    spawnSync(
      process.execPath,
      [join(museum, 'scripts/build-ai-snapshot.mjs')],
      { encoding: 'utf8' },
    );
  try {
    await mkdir(join(museum, 'scripts'), { recursive: true });
    await mkdir(join(museum, 'lib'), { recursive: true });
    for (const name of [
      'scripts/build-ai-snapshot.mjs',
      'lib/ai-source-snapshot.json',
      'lib/ai-source-snapshot.sha256',
    ]) {
      await copyFile(fileURLToPath(new URL(name, root)), join(museum, name));
    }
    const snapshotPath = join(museum, 'lib/ai-source-snapshot.json');
    const before = await readFile(snapshotPath);
    assert.equal(run().status, 0);
    assert.deepEqual(await readFile(snapshotPath), before);
    // Platform newline conversion must not invalidate the documented LF hash.
    await writeFile(
      snapshotPath,
      before.toString('utf8').replaceAll('\r\n', '\n').replaceAll('\n', '\r\n'),
    );
    assert.equal(run().status, 0);
    await writeFile(snapshotPath, `${before.toString('utf8')} `);
    const changed = run();
    assert.notEqual(changed.status, 0);
    assert.match(changed.stderr, /integrity check failed/);
    await writeFile(snapshotPath, before);
    await rm(join(museum, 'lib/ai-source-snapshot.sha256'));
    assert.notEqual(run().status, 0);
    await copyFile(
      fileURLToPath(new URL('lib/ai-source-snapshot.sha256', root)),
      join(museum, 'lib/ai-source-snapshot.sha256'),
    );
    await mkdir(join(directory, 'docs'));
    await writeFile(
      join(directory, 'docs/current_bhsm_status.md'),
      '# incomplete parent',
    );
    const partial = run();
    assert.notEqual(partial.status, 0);
    assert.match(partial.stderr, /Incomplete BHSM source checkout/);
  } finally {
    // Only the exact fresh mkdtemp directory owned by this test is removed.
    await rm(directory, { recursive: true, force: true });
  }
});
