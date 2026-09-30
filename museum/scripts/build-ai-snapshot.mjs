import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = new URL('../../', import.meta.url);
const snapshotPath = new URL('../lib/ai-source-snapshot.json', import.meta.url);
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
await writeFile(
  new URL('../lib/ai-source-snapshot.json', import.meta.url),
  JSON.stringify(
    {
      snapshot_date: '2026-09-30',
      description:
        'Verbatim excerpts. Each file carries its own source revision; this is not a complete repository or a live status lookup.',
      sources,
    },
    null,
    2,
  ) + '\n',
);
