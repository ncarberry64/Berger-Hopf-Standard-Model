import { readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = new URL('../../', import.meta.url);
const snapshotPath = new URL('../lib/ai-source-snapshot.json', import.meta.url);
const digestPath = new URL('../lib/ai-source-snapshot.sha256', import.meta.url);
let previous = [];
try {
  previous = JSON.parse(await readFile(snapshotPath, 'utf8')).sources;
} catch (error) {
  if (error.code !== 'ENOENT') throw error;
}
const selection = [
  ['docs/current_bhsm_status.md', 1, 104],
  ['CLAIMS.md', 1, 55],
  ['docs/BHSM_1_0_DEFINITION_OF_DONE.md', 1, 78],
  ['theory/gate_ledger.md', 1, 40],
  ['theory/ae3_family_mass_ontology_recovery_audit.md', 1, 77],
  ['theory/ae31_c2_local_em_ward_identity.md', 1, 62],
  ['docs/cern_open_data_benchmark.md', 1, 36],
  ['docs/BHSM_AUTHOR_AETHER_SCALE_CLARIFICATION_20260908.md', 1, 39],
];
const available = selection.map(([path]) => existsSync(new URL(path, root)));
if (available.some(Boolean) && !available.every(Boolean)) {
  throw new Error(
    'Incomplete BHSM source checkout; refusing a partial AI snapshot.',
  );
}
if (!available.some(Boolean)) {
  // Standalone Museum source has no scientific monorepo parent. Retain the
  // canonical excerpts rather than inventing source revisions or live status.
  const text = (await readFile(snapshotPath, 'utf8')).replaceAll('\r\n', '\n');
  const digest = (await readFile(digestPath, 'utf8')).trim();
  if (
    !/^[0-9a-f]{64}$/.test(digest) ||
    createHash('sha256').update(text).digest('hex') !== digest
  ) {
    throw new Error('Bundled AI source snapshot integrity check failed.');
  }
  const snapshot = JSON.parse(text);
  if (
    !Array.isArray(snapshot.sources) ||
    snapshot.sources.length !== selection.length
  ) {
    throw new Error(
      'Bundled AI source snapshot has an incomplete source inventory.',
    );
  }
  for (const [index, [path, first, last]] of selection.entries()) {
    const source = snapshot.sources[index];
    if (
      source.path !== path ||
      !/^[0-9a-f]{40}$/.test(source.revision) ||
      !/^[0-9a-f]{64}$/.test(source.normalized_source_sha256) ||
      source.source_url !==
        `https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/${source.revision}/${path}` ||
      source.first_line !== first ||
      !Number.isInteger(source.last_line) ||
      source.last_line < first ||
      source.last_line > last ||
      typeof source.text !== 'string'
    ) {
      throw new Error(`Invalid bundled AI source pin: ${path}`);
    }
  }
  console.log(
    'Verified retained AI source excerpts; full upstream files are not present in this standalone Museum.',
  );
} else {
  const sources = [];
  for (const [path, first, last] of selection) {
    const bytes = await readFile(new URL(path, root));
    const normalized = bytes.toString('utf8').replaceAll('\r\n', '\n');
    const lines = normalized.split('\n');
    const hash = createHash('sha256').update(normalized).digest('hex');
    // Preserve the pinned source commit in shallow CI checkouts when the exact
    // source is unchanged; `git log -- path` would otherwise report the shallow
    // checkout boundary as if it were the file's historical source revision.
    const retained = previous.find(
      (entry) => entry.path === path && entry.normalized_source_sha256 === hash,
    );
    const revision =
      retained?.revision ??
      execFileSync(
        'git',
        [
          '-c',
          'gc.auto=0',
          '-c',
          'maintenance.auto=false',
          'log',
          '-1',
          '--format=%H',
          '--',
          path,
        ],
        { cwd: fileURLToPath(root), encoding: 'utf8' },
      ).trim();
    if (!/^[0-9a-f]{40}$/.test(revision))
      throw new Error(`No source revision: ${path}`);
    sources.push({
      path,
      revision,
      source_url: `https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/${revision}/${path}`,
      first_line: first,
      last_line: Math.min(last, lines.length),
      normalized_source_sha256: hash,
      text: lines.slice(first - 1, last).join('\n'),
    });
  }
  const snapshotText =
    JSON.stringify(
      {
        snapshot_date: '2026-10-22',
        description:
          'Verbatim excerpts. Each file carries its own source revision; this is not a complete repository or a live status lookup.',
        sources,
      },
      null,
      2,
    ) + '\n';
  await writeFile(snapshotPath, snapshotText);
  await writeFile(
    digestPath,
    `${createHash('sha256').update(snapshotText).digest('hex')}\n`,
  );
}
