import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { slides } from '../lib/museum-slides.mjs';
import {
  socialImageFile,
  freshSharePath,
  freshShareURL,
  makeFreshShareHTML,
} from '../lib/social-preview.mjs';

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

  const html = sourceHtml.replaceAll('/_next/', './_next/');

  await writeFile(resolve(pagesRoot, 'index.html'), html, 'utf8');
  const shareDirectory = resolve(pagesRoot, freshSharePath);
  await mkdir(shareDirectory, { recursive: true });
  const shareHTML = makeFreshShareHTML(html);
  for (const expected of [
    `<base href="${publicUrl}"`,
    `rel="canonical" href="${freshShareURL}"`,
    `property="og:url" content="${freshShareURL}"`,
  ]) {
    if (!shareHTML.includes(expected))
      throw new Error(`Fresh share is missing: ${expected}`);
  }
  await writeFile(resolve(shareDirectory, 'index.html'), shareHTML, 'utf8');
  await writeFile(resolve(pagesRoot, '.nojekyll'), '', 'utf8');

  const written = await readFile(resolve(pagesRoot, 'index.html'), 'utf8');
  // Social crawlers read this static HTML without running the museum app.
  const socialImage = `${publicUrl}${socialImageFile}`;
  for (const tag of [
    `property="og:image" content="${socialImage}"`,
    'property="og:image:width" content="1200"',
    'property="og:image:height" content="630"',
    'name="twitter:card" content="summary_large_image"',
    `name="twitter:image" content="${socialImage}"`,
  ]) {
    if (!written.includes(tag))
      throw new Error(`Missing social metadata: ${tag}`);
  }
  const preview = await readFile(resolve(pagesRoot, socialImageFile));
  if (preview.readUInt32BE(16) !== 1200 || preview.readUInt32BE(20) !== 630)
    throw new Error('Social preview must be a 1200 × 630 PNG.');
  for (const expected of [
    'BHSM Museum',
    'Published reference',
    'COMPARISON ONLY',
    './_next/',
    'Magnetic moments in motion',
    'Historical screens and reference data',
    'Collision theatre',
    'Five geometric studies',
    'force-atlas',
    'museum-track',
    'Follow the force lines.',
    'r1-realization',
    'cosmology-original',
    'CMS · Data',
    'Original CMS animation',
    'pr98_cms_engine_validation.png',
    'Two mathematical ideas. One deeper question.',
    'The path from geometry to predictive tests',
    'BHSM Transition Diagram',
    'Active boundary imbalance',
    'Download transition record',
  ]) {
    if (!written.includes(expected))
      throw new Error(`Static export is missing: ${expected}`);
  }
  const sections = slides.map(([id]) => id);
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
  const aiIndex = JSON.parse(
    await readFile(resolve(pagesRoot, 'ai/index.json'), 'utf8'),
  );
  const aiPacket = JSON.parse(
    await readFile(resolve(pagesRoot, 'ai/handoff.json'), 'utf8'),
  );
  if (
    aiIndex.exhibits.map(({ id }) => id).join(',') !== sections.join(',') ||
    aiPacket.schema !== 'bhsm-ai-handoff/v2' ||
    !aiPacket.embedded_source_snapshot?.sources?.every(
      (source) => source.text && source.revision,
    ) ||
    !written.includes('Copy BHSM for AI')
  ) {
    throw new Error('Static export lost the AI interface or its exhibit map.');
  }
  await readFile(resolve(pagesRoot, 'llms.txt'), 'utf8');
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
