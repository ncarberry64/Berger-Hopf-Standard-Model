import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const museumRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const distRoot = resolve(museumRoot, 'dist');
const clientRoot = resolve(distRoot, 'client');
const pagesRoot = resolve(distRoot, 'pages');
const serverUrl = 'http://127.0.0.1:8787/';
const publicUrl = 'https://ncarberry64.github.io/Berger-Hopf-Standard-Model/';

if (relative(distRoot, pagesRoot).startsWith('..')) {
  throw new Error('Refusing to export outside museum/dist.');
}

const wranglerCli = resolve(
  museumRoot,
  'node_modules',
  'wrangler',
  'bin',
  'wrangler.js',
);
const server = spawn(
  process.execPath,
  [
    wranglerCli,
    'dev',
    '--config',
    'dist/server/wrangler.json',
    '--port',
    '8787',
  ],
  { cwd: museumRoot, stdio: ['ignore', 'pipe', 'pipe'] },
);

let output = '';
server.stdout.on('data', (chunk) => {
  output += chunk;
});
server.stderr.on('data', (chunk) => {
  output += chunk;
});

async function fetchWhenReady() {
  const deadline = Date.now() + 30_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(serverUrl);
      if (response.ok) return response.text();
    } catch {
      // The local production worker is still starting.
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 250));
  }
  throw new Error(`Timed out waiting for the production build.\n${output}`);
}

try {
  const sourceHtml = await fetchWhenReady();
  await rm(pagesRoot, { recursive: true, force: true });
  await mkdir(pagesRoot, { recursive: true });
  await cp(clientRoot, pagesRoot, { recursive: true });

  const html = sourceHtml
    .replaceAll('/_next/', './_next/')
    .replaceAll('http://localhost:3000/og.png', `${publicUrl}og.png`);

  await writeFile(resolve(pagesRoot, 'index.html'), html, 'utf8');
  await writeFile(resolve(pagesRoot, '.nojekyll'), '', 'utf8');

  const written = await readFile(resolve(pagesRoot, 'index.html'), 'utf8');
  for (const expected of [
    'BHSM Museum',
    'historic stakes',
    'Published reference',
    'COMPARISON ONLY',
    './_next/',
    'Magnetic moments in motion',
    'Standard Model equivalence',
    'Collision theatre',
    'Forces unifying',
    'CMS · Data',
    'Original CMS animation',
    'pr98_cms_engine_validation.png',
  ]) {
    if (!written.includes(expected))
      throw new Error(`Static export is missing: ${expected}`);
  }
  const sections = [
    'potential',
    'exhibits',
    'science-predictions',
    'science-decays',
    'science-magnetic',
    'comparisons',
    'science-unification',
    'research-exhibit',
    'details',
    'creator',
    'other-work',
  ];
  const positions = sections.map((id) => written.indexOf(`id="${id}"`));
  if (
    positions.some(
      (position, index) =>
        position < 0 || (index > 0 && position <= positions[index - 1]),
    )
  ) {
    throw new Error(
      'Static export does not preserve the public science section order.',
    );
  }
  const data = JSON.parse(
    await readFile(resolve(pagesRoot, 'data/sandbox-comparison.json'), 'utf8'),
  );
  if (
    data.classification !== 'COMPARISON_ONLY' ||
    data.rows.length !== 10 ||
    data.physical_prediction !== false
  ) {
    throw new Error(
      'Static export lost the sandbox data or its claim boundary.',
    );
  }
  console.log(
    `Exported GitHub Pages package to ${relative(museumRoot, pagesRoot)}.`,
  );
} finally {
  server.kill();
}
