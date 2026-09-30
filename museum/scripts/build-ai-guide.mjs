import { mkdir, writeFile } from 'node:fs/promises';
await import('./build-ai-snapshot.mjs');
const { catalog, aiHandoffJSON } = await import('../lib/ai-guide.mjs');

const publicRoot = new URL('../public/', import.meta.url);
await mkdir(new URL('ai/', publicRoot), { recursive: true });
await writeFile(new URL('ai/handoff.json', publicRoot), `${aiHandoffJSON}\n`);
await writeFile(
  new URL('ai/index.json', publicRoot),
  `${JSON.stringify(catalog, null, 2)}\n`,
);
const guide = [
  '# BHSM Museum — AI access',
  '',
  '> A source-linked guide to the Berger–Hopf Standard Model museum, its scientific record and open questions.',
  '',
  `Guide updated: ${catalog.updated}. This date applies to the navigation guide, not all linked research.`,
  '',
  `Museum: ${catalog.museum_url}`,
  `Repository: ${catalog.repository_url}`,
  '',
  '## Access',
  '',
  'Fetch this document with an ordinary HTTPS GET. No account, API key or JavaScript is required.',
  `Structured index: ${catalog.museum_url}ai/index.json`,
  'The JSON lists every exhibit in visitor order, with id, title, url, keywords, summary, scope and sources. Search those fields locally, then fetch relevant sources. There is no query endpoint or hosted answer generator.',
  'An exhibit fragment identifies a museum slide. For text retrieval without the interactive page, use the summaries below and their Markdown/JSON sources. Browser-capable assistants can follow the exhibit URL for controls and animations.',
  '',
  '## Reading guidance',
  '',
  ...catalog.reading_rules.map((rule) => `- ${rule}`),
  '',
  '## Search and access fallbacks',
  '',
  catalog.retrieval_plan.objective,
  ...catalog.retrieval_plan.steps.map((step, i) => `${i + 1}. ${step}`),
  '',
  ...catalog.retrieval_plan.suggested_searches.map((query) => `- ${query}`),
  '',
  '## Current scientific record',
  '',
  ...catalog.current_sources.map(
    ({ title, url, github_url }) =>
      `- [${title}](${github_url}) · [Raw text](${url})`,
  ),
  '',
  '## Exhibits',
  ...catalog.exhibits.flatMap((entry) => [
    '',
    `### ${entry.title}`,
    '',
    `[Open exhibit](${entry.url})`,
    '',
    ...(entry.statement
      ? [
          `${entry.classification}: ${entry.statement}`,
          '',
          ...(entry.question ? [`Review question: ${entry.question}`] : []),
          '',
        ]
      : []),
    entry.summary,
    '',
    `Scope: ${entry.scope}`,
    '',
    ...entry.sources.map(({ title, url }) => `- [${title}](${url})`),
  ]),
  '',
].join('\n');
await writeFile(new URL('llms.txt', publicRoot), guide);
console.log(
  `Generated AI guide and index for ${catalog.exhibits.length} exhibits.`,
);
